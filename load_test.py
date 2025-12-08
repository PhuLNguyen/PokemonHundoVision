import asyncio
import httpx
import time
import pandas as pd
import matplotlib.pyplot as plt
import os

# =================================================================
# CONFIGURATION
# =================================================================
# Your Cloud Run Service URL
SERVICE_URL = "https://image-ocr-service-1093717027896.us-central1.run.app/"
# The name of the file to upload for the test.
IMAGE_FILE = "sample_image.png"
# The form field name your server.py expects for the file (commonly 'file' or 'image')
# Based on the server.py snippet, 'file' is a safe assumption for request.files.get('file')
FORM_FIELD_NAME = "file" 

# --- Load Parameters (Adjust these for a stronger test) ---
# Total number of concurrent users (tasks)
CONCURRENT_USERS = 5
# Total number of requests to send (must be a multiple of CONCURRENT_USERS for simplicity)
TOTAL_REQUESTS = 500 

# Budget Note: TOTAL_REQUESTS is set to 500 to stay safely within the 1000 free tier for Vision API.
# You can increase this, but be aware of the 1000/month free limit.
# =================================================================

def plot_results(results_df, total_duration):
    """Generates and displays latency and throughput graphs."""
    
    # 1. Latency Histogram
    plt.figure(figsize=(12, 6))
    results_df['latency_ms'].hist(bins=50, edgecolor='black')
    plt.title('Latency Distribution (Response Time)')
    plt.xlabel('Latency (ms)')
    plt.ylabel('Frequency (Request Count)')
    
    # 2. Latency Over Time (Scatter)
    plt.figure(figsize=(12, 6))
    plt.scatter(results_df['timestamp_relative'], results_df['latency_ms'], s=10)
    plt.title('Latency Over Time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Latency (ms)')

    # 3. Throughput Calculation and Display
    # Calculate rolling throughput (e.g., 5-second window)
    time_bins = pd.cut(results_df['timestamp_relative'], bins=pd.np.arange(0, total_duration + 5, 5))
    throughput_series = results_df.groupby(time_bins).size() / 5 
    throughput_series.index = throughput_series.index.map(lambda x: x.left)
    
    plt.figure(figsize=(12, 6))
    throughput_series.plot(kind='bar', width=4)
    plt.title('Throughput Over Time (Requests/Second)')
    plt.xlabel('Time Bin Start (seconds)')
    plt.ylabel('Throughput (Req/sec)')

    # Print Key Metrics
    avg_latency = results_df['latency_ms'].mean()
    p95_latency = results_df['latency_ms'].quantile(0.95)
    total_throughput = TOTAL_REQUESTS / total_duration

    print("-" * 50)
    print("TEST SUMMARY")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Total Duration: {total_duration:.2f} seconds")
    print(f"Total Throughput: {total_throughput:.2f} requests/second")
    print("-" * 50)
    # The mathematical expression is enclosed in dollar signs as requested.
    print(f"Average Latency: ${avg_latency:.2f}\text{ ms}$")
    print(f"95th Percentile Latency (P95): ${p95_latency:.2f}\text{ ms}$ (95% of requests were faster than this)")
    print("-" * 50)
    
    plt.tight_layout()
    plt.show()


async def send_request(client, request_id, results):
    """Sends a single POST request with the image file and records metrics."""
    # Since it's a load test, we open the file inside the async function, 
    # but only for the duration of the request, allowing for concurrent file handle use.
    # The 'rb' (read binary) mode is necessary for multipart/form-data.
    try:
        with open(IMAGE_FILE, 'rb') as f:
            files = {FORM_FIELD_NAME: (IMAGE_FILE, f, 'image/png')}
            
            start_time = time.perf_counter()
            response = await client.post(SERVICE_URL, files=files)
            end_time = time.perf_counter()
            
            latency = (end_time - start_time) * 1000  # Convert to milliseconds
            
            results.append({
                "request_id": request_id,
                "latency_ms": latency,
                "timestamp_absolute": start_time,
                "status_code": response.status_code
            })
            
            # Print a progress update
            if request_id % (TOTAL_REQUESTS // 10) == 0:
                 print(f"Request {request_id}/{TOTAL_REQUESTS} completed (Status: {response.status_code}, Latency: {latency:.2f} ms)")

    except httpx.ConnectTimeout:
        print(f"Request {request_id} timed out on connection.")
    except Exception as e:
        # Catch exceptions like file not found, connection errors, etc.
        print(f"Request {request_id} failed with error: {e}")

async def run_load_test():
    """Main function to orchestrate the load test."""
    
    if TOTAL_REQUESTS % CONCURRENT_USERS != 0:
        print("Error: TOTAL_REQUESTS must be a multiple of CONCURRENT_USERS.")
        return

    # Use a high timeout since the Cloud Vision API call might take a while.
    # It also helps capture slow requests instead of false timeouts.
    timeout = httpx.Timeout(60.0, connect=30.0)
    
    # httpx.AsyncClient is used to efficiently reuse connections.
    async with httpx.AsyncClient(timeout=timeout) as client:
        results = []
        all_tasks = []
        
        # Determine the number of requests each user will make
        requests_per_user = TOTAL_REQUESTS // CONCURRENT_USERS
        request_counter = 1
        
        start_test_time = time.perf_counter()
        
        # Create a set of concurrent tasks for the load
        for _ in range(requests_per_user):
            for _ in range(CONCURRENT_USERS):
                task = asyncio.create_task(send_request(client, request_counter, results))
                all_tasks.append(task)
                request_counter += 1
            # You can add a small delay here if you want to pace the injection of tasks
            # await asyncio.sleep(0.01)

        # Wait for all tasks to complete
        await asyncio.gather(*all_tasks)
        
        end_test_time = time.perf_counter()
        total_duration = end_test_time - start_test_time

    # --- Data Processing and Plotting ---
    if not results:
        print("No successful requests were recorded. Cannot generate graphs.")
        return

    # Convert results to a pandas DataFrame for easy processing
    results_df = pd.DataFrame(results)
    
    # Calculate relative timestamp from the start of the test
    first_timestamp = results_df['timestamp_absolute'].min()
    results_df['timestamp_relative'] = results_df['timestamp_absolute'] - first_timestamp
    
    # Only consider successful requests for performance metrics, but keep track of failures
    successful_requests = results_df[results_df['status_code'] == 200]
    
    # If there are successful requests, plot the data
    if not successful_requests.empty:
        plot_results(successful_requests, total_duration)
    
    # Report errors
    error_count = len(results_df[results_df['status_code'] != 200])
    print(f"\nRequests with non-200 status code (Errors): {error_count}")
    if error_count > 0:
        print(results_df[results_df['status_code'] != 200][['request_id', 'status_code']])


if __name__ == '__main__':
    try:
        if not os.path.exists(IMAGE_FILE):
            print(f"ERROR: Image file '{IMAGE_FILE}' not found. Please create it and run again.")
        else:
            print(f"Starting load test on {SERVICE_URL}...")
            print(f"Users: {CONCURRENT_USERS}, Total Requests: {TOTAL_REQUESTS}")
            asyncio.run(run_load_test())
    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")