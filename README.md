# Pokemon Hundo Vision

## Google Cloud CLI (gcloud) Installation
You can skip this section if gcloud already installed

### Install dependencies and GPG Key
```bash
sudo apt update
sudo apt install apt-transport-https ca-certificates gnupg curl -y
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
```
### Add Cloud SDK
```bash
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
```

### Install SDK
```bash
sudo apt update
sudo apt install google-cloud-sdk -y
```

---

### Google Cloud Authentication & Setup for CLI
- sign-in/select a Google Account
- select/create a project
- follow instruction on-screen
```bash
gcloud init
```

### Link Billing Account to Project
```bash
gcloud billing accounts list
gcloud alpha billing projects link [PROJECT_ID] \
    --billing-account [YOUR_BILLING_ACCOUNT_ID]
``` 

### Enable APIs (Cloud Vision, Firestore, Cloud Build, Artifact Registry, Cloud Run) 
```bash
gcloud services enable \
    vision.googleapis.com \
    firestore.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    run.googleapis.com
```

### IAM policy configuration
- Get Project Number
```bash
gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)"
```

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

### 
- Delete Snapshots in Compute Engine