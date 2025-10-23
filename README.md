# Pokemon Hundo Vision


docker build -t image-uploader .
docker run -d -p 3000:3000 -v $(pwd)/uploads:/usr/src/app/uploads --name image-upload-app image-uploader

gcloud projects add-iam-policy-binding 612179929220 \
  --member='serviceAccount:612179929220-compute@developer.gserviceaccount.com' \
  --role='roles/ml.developer'

gcloud builds submit --config=cloudbuild.yaml