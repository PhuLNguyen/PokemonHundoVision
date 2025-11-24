# Pokemon Hundo Vision

---

## Install Terraform
- You can skip this section if Terraform already installed

```bash
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null
gpg --no-default-keyring --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg --fingerprint
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
sudo apt-get install terraform
```

---

## Google Cloud CLI (gcloud) Installation
- You can skip this section if gcloud already installed

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

###
```bash
gcloud auth application-default login
```
- select all checkboxes to allow gcloud access

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

- Replace **[PROJECT_NUMBER]** with your actual number found in command above 

```bash
gcloud projects add-iam-policy-binding [PROJECT_NUMBER] \
  --member='serviceAccount:[PROJECT_NUMBER]-compute@developer.gserviceaccount.com' \
  --role='roles/ml.developer'

gcloud beta run services add-iam-policy-binding --region=us-central1 --member=allUsers --role=roles/run.invoker image-ocr-service
```

- Replace **[PROJECT_ID]** with your actual project name (not Project Number)

### Create the MongoDB-Compatible Database
```bash
terraform validate
terraform init
export TF_VAR_PROJECT_ID=pokemon-hundo-vision
terraform apply -auto-approve
```



### Publish the App on Google Cloud Run
```bash
gcloud builds submit --config=cloudbuild.yaml
```

--------------------------------------------------------

## Clean Up

### Delete the Cloud Run Service
```bash
gcloud run services delete image-ocr-service --region us-central1
```

### List repositories to find the name (e.g., 'cloud-run-source-deploy')
```bash
gcloud artifacts repositories list
```

### Command to Delete an Artifact Registry Repository 🗑️
```bash
gcloud artifacts repositories delete [REPOSITORY_NAME] --location=us-central1
```

### Comand to Delete a Firestore database
```bash
gcloud firestore databases delete --database=[DATABASE_ID]
```

### 
- Delete Snapshots in Compute Engine