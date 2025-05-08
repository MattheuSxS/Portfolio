terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.34.0"
    }
    archive = {
      source = "hashicorp/archive"
      version = "2.7.0"
    }
    local = {
      source = "hashicorp/local"
      version = "2.5.2"
    }
  }

  backend "gcs" {
      bucket = "bkt-mts-tf-state"
      prefix = "tf-portfolio"
  }
}

provider "google" {
  project     = var.project[terraform.workspace]
  region      = var.region
}