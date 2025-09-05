terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "7.1.0" # old version "6.44.0" # new version "7.1.0"
    }
    archive = {
      source = "hashicorp/archive"
      version = "2.7.1"
    }
    local = {
      source = "hashicorp/local"
      version = "2.5.3"
    }
  }

  backend "gcs" {
      bucket = "bkt-mts-tf-state"
      prefix = "tf-portfolio"
  }
}

provider "google" {
  project     = local.project
  region      = var.region
  alias       = "default_project"
}

provider "google" {
  project = local.project_data_tools
  alias   = "data_tools_project"
}