terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "7.42.0"
        }
        archive = {
            source = "hashicorp/archive"
            version = "2.8.0"
        }
        local = {
            source = "hashicorp/local"
            version = "2.9.0"
        }
    }

    backend "gcs" {
        bucket = "bkt-mts-tf-state"
        prefix = "tf-portfolio"
    }
}

provider "google" {
    project = local.project
    region  = var.region
    alias   = "default_project"
}