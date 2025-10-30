import cv2
import numpy as np
import io

def numpy_to_flask_file(numpy_image_array, file_extension='.jpg'):
    """
    Converts an OpenCV/NumPy image array into an in-memory file-like object
    that Flask can send as a response.

    Args:
        numpy_image_array (np.array): The image array (e.g., the cropped image).
        file_extension (str): The desired output format (e.g., '.png', '.jpg').
                              PNG is generally better for screenshots/text due to lossless compression.

    Returns:
        io.BytesIO: A file-like object containing the encoded image data.
    """
    # 1. Encode the NumPy array into the desired file format bytes.
    # 'imencode' returns a tuple: (success_flag, encoded_image_array)
    is_success, buffer = cv2.imencode(file_extension, numpy_image_array)

    if not is_success:
        raise ValueError(f"Failed to encode image with format {file_extension}")

    # 2. Convert the NumPy array buffer to a standard Python bytes object.
    image_bytes = buffer.tobytes()
    return image_bytes
"""   
    # 3. Wrap the bytes in a BytesIO object (in-memory file).
    image_file_object = io.BytesIO(image_bytes)
    
    # Reset the pointer to the start of the "file"
    image_file_object.seek(0)
    
    return image_file_object
"""

def detect_dark_oval_banner(file):
	# 1. Decode the image bytes into an OpenCV (NumPy) image array
	nparr = np.frombuffer(file.read(), np.uint8)
	img_full = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
 
    # --- START OF EDIT: Exclude the status bar ---
	# Calculate a safe area to exclude the status bar (e.g., top 8% of the image)
	height, width, _ = img_full.shape
	
    # Define a crop height to exclude the status bar (e.g., 8% of the total height)
    # The '1' in the max() is a safeguard for tiny images.
	status_bar_exclusion_height = max(1, int(height * 0.08)) 
	
    # Create the working image by slicing from below the status bar.
    # We will adjust the final crop coordinates back to the original image's frame of reference later.
	img = img_full[status_bar_exclusion_height:, :]
	
	# Update the working image's dimensions
	height, width, _ = img.shape
    # --- END OF EDIT ---

	# 1. Preprocessing for DARK objects (using the cropped 'img')
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)

	# 2. Thresholding and Inversion (to make the dark banner a white blob)
	threshold_value = 130 
	_, thresh = cv2.threshold(blurred, threshold_value, 255, cv2.THRESH_BINARY) 
	thresh = cv2.bitwise_not(thresh)

	# 3. Find contours
	contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	if not contours:
		print("No contours found after dark object isolation.")
		return

	# 4. Robust Filtering: Find the contour that is reasonably sized and closest to the top.

	# Heuristic for minimum area (to exclude small noise)
	min_area = 500 

	best_match_contour = None
	min_y_center = float('inf') # Initialize with a large number

	for c in contours:
		area = cv2.contourArea(c)

		# Check if the area is above our noise threshold
		if area > min_area:
			# Get the bounding box (x, y, w, h) in the *cropped* image's coordinates
			x, y, w, h = cv2.boundingRect(c)

			# Calculate the y-coordinate of the center of the bounding box
			y_center = y + h / 2

			# The contour with the smallest y_center is the one closest to the top of the working image (y=0)
			if y_center < min_y_center:
				min_y_center = y_center
				best_match_contour = c

	if best_match_contour is None:
		print(f"Could not isolate the text banner contour. No contour found with area > {min_area}.")
		return

	# 5. Get the Bounding Box from the best match contour in the *cropped* image
	x_cropped, y_cropped, w, h = cv2.boundingRect(best_match_contour)

    # --- START OF EDIT: Adjust coordinates back to the original image's frame of reference ---
    # The 'y' coordinate needs to be shifted down by the exclusion height.
	x = x_cropped
	y = y_cropped + status_bar_exclusion_height
    # --- END OF EDIT ---

	# 6. Print the coordinates and draw the box for visualization

	# Define a consistent padding
	padding = 8 

	# Define final crop area: (xmin, ymin, xmax, ymax)
	# Use the full image's dimensions for boundary checks
	full_height, full_width, _ = img_full.shape
	xmin_final = max(0, x - padding)
	ymin_final = max(0, y - padding)
	xmax_final = min(full_width, x + w + padding)
	ymax_final = min(full_height, y + h + padding)

	print("--- Text Banner Bounding Box Results (Final) ---")
	print(f"Crop Coordinates (xmin, ymin, xmax, ymax): ({xmin_final}, {ymin_final}, {xmax_final}, {ymax_final})")
	print("------------------------------------------------")

	# 7. Crop the image (using the full image with the adjusted coordinates)
	banner = img_full[ymin_final:ymax_final, xmin_final:xmax_final]
	
	# 8. Convert the cropped banner to a Flask-compatible file-like object
	cropped_image = numpy_to_flask_file(banner, file_extension='.jpg')

	return cropped_image