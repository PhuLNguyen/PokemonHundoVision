# Pokemon Hundo Vision

## Google Cloud Setup
gcloud config set project [PROJECT_ID]
gcloud services enable vision.googleapis.com


## Run Locally

### Set Up Local Credentials for the Vision API
gcloud auth application-default login

### Copy your Application Default Credentials file to current directory
sudo cp ~/.config/gcloud/application_default_credentials.json ./

### Grants read permission (r) to all users (a+) for that specific file. This is usually sufficient to let the Docker daemon read it.
sudo chmod a+r ./application_default_credentials.json

### Build Docker image
docker build -t ocr-app .

### Run the container
docker run -d -p 8080:8080 \
  --mount type=bind,source="./application_default_credentials.json",target="/root/.config/gcloud/application_default_credentials.json",readonly \
  -e GOOGLE_APPLICATION_CREDENTIALS="/root/.config/gcloud/application_default_credentials.json" \
  --name ocr-container \
  ocr-app

## Clean Up

### Stop and remove the container
docker rm -f ocr-app

### Delete ADC file in current directory 
sudo rm application_default_credentials.json

gcloud projects add-iam-policy-binding [PROJECT_NUMBER] \
  --member='serviceAccount:[PROJECT_NUMBER]-compute@developer.gserviceaccount.com' \
  --role='roles/ml.developer'

gcloud beta run services add-iam-policy-binding --region=[REGION] --member=allUsers --role=roles/run.invoker image-ocr-service

gcloud builds submit --config=cloudbuild.yaml

## Clean Up

### Delete the Cloud Run Service
gcloud run services delete [SERVICE_NAME] --region [REGION]

### List repositories to find the name (e.g., 'cloud-run-source-deploy')
gcloud artifacts repositories list

### Command to Delete an Artifact Registry Repository 🗑️
gcloud artifacts repositories delete [REPOSITORY_NAME] --location=[LOCATION]