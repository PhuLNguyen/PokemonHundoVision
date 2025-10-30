# Pokemon Hundo Vision

## Google Cloud Setup
```bash
gcloud config set project [PROJECT_ID]
gcloud services enable vision.googleapis.com
```

### Set Up Local Credentials for the Vision API
```bash
gcloud auth login
gcloud auth application-default login
```

### IAM policy configuration
```bash
gcloud projects add-iam-policy-binding [PROJECT_NUMBER] \
  --member='serviceAccount:[PROJECT_NUMBER]-compute@developer.gserviceaccount.com' \
  --role='roles/ml.developer'

gcloud beta run services add-iam-policy-binding --region=[REGION] --member=allUsers --role=roles/run.invoker image-ocr-service
```

### Create the MongoDB-Compatible Database
```bash
terraform init
terraform validate
terraform apply
```

### Publish the App on Google Cloud Run
```bash
gcloud builds submit --config=cloudbuild.yaml
```

--------------------------------------------------------

## Clean Up

### Delete the Cloud Run Service
```bash
gcloud run services delete [SERVICE_NAME] --region [REGION]
```

### List repositories to find the name (e.g., 'cloud-run-source-deploy')
```bash
gcloud artifacts repositories list
```

### Command to Delete an Artifact Registry Repository 🗑️
```bash
gcloud artifacts repositories delete [REPOSITORY_NAME] --location=[LOCATION]
```

### Comand to Delete a Firestore database
```bash
gcloud firestore databases delete --database=[DATABASE_ID]
```