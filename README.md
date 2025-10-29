# Pokemon Hundo Vision

The project deployment is split into two environment:
- Local: Used Docker Compose to setup 2 containers (MongoDB & Flask server)
- Google Cloud: Cloud Build -> Artifact Registry -> Cloud Run -> Container -> (Firestore + Cloud Vision API)