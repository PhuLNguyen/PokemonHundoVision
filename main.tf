# Configure the Google Beta Provider
# The Firestore MongoDB compatibility service is typically managed through the google-beta provider.
terraform {
  required_providers {
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.0"
    }
  }
}

# Provider configuration
provider "google-beta" {
  project = var.PROJECT_ID
  region  = "us-central1" 
}

# 1. Provision the Firestore Database
resource "google_firestore_database" "database" {
  project    = var.PROJECT_ID
  name        = "pogo" 
  location_id = "us-central1"
  type             = "FIRESTORE_NATIVE"
  database_edition = "ENTERPRISE" 
  
  # Lifecycle policies
  delete_protection_state = "DELETE_PROTECTION_DISABLED"
}

# Output the Connection URI for Initialization
# This value must be retrieved manually using the gcloud CLI after deployment
output "firestore_mongodb_connection_guide" {
  value = "Run 'gcloud firestore databases describe pogo --format=\"value(mongodb_uri)\"' to get the connection URI for the next step."
}