# Pokemon Hundo Vision

gcloud config set project [PROJECT_ID]
gcloud services enable vision.googleapis.com

docker build -t image-uploader .
docker run -d -p 8080:8080 -v $(pwd)/uploads:/usr/src/app/uploads --name image-upload-app image-uploader

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