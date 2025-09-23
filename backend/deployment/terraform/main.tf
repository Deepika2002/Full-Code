# Terraform configuration for ImpactAnalyzer infrastructure on Google Cloud

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Google Cloud Zone"
  type        = string
  default     = "us-central1-a"
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sql.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudscheduler.googleapis.com",
    "secretmanager.googleapis.com"
  ])

  service = each.value
  project = var.project_id

  disable_dependent_services = true
}

# Cloud SQL instance for main database
resource "google_sql_database_instance" "main" {
  name             = "impact-analyzer-db"
  database_version = "MYSQL_8_0"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    
    backup_configuration {
      enabled                        = true
      start_time                     = "02:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
      }
    }

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }

    database_flags {
      name  = "cloudsql_iam_authentication"
      value = "on"
    }
  }

  deletion_protection = false
}

# Cloud SQL database
resource "google_sql_database" "impact_analyzer" {
  name     = "impact_analyzer"
  instance = google_sql_database_instance.main.name
}

# Cloud SQL user
resource "google_sql_user" "impact_user" {
  name     = "impact_user"
  instance = google_sql_database_instance.main.name
  password = "impact_password_123"  # Change this in production
}

# Cloud SQL instance for vector database
resource "google_sql_database_instance" "vector" {
  name             = "impact-analyzer-vector-db"
  database_version = "POSTGRES_14"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
      }
    }

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }
  }

  deletion_protection = false
}

# Vector database
resource "google_sql_database" "vectors" {
  name     = "vectors"
  instance = google_sql_database_instance.vector.name
}

# Vector database user
resource "google_sql_user" "vector_user" {
  name     = "vector_user"
  instance = google_sql_database_instance.vector.name
  password = "vector_password_123"  # Change this in production
}

# Cloud Storage buckets
resource "google_storage_bucket" "main" {
  name     = "${var.project_id}-impact-analyzer-storage"
  location = var.region

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "vectors" {
  name     = "${var.project_id}-impact-analyzer-vectors"
  location = var.region

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

resource "google_storage_bucket" "logs" {
  name     = "${var.project_id}-impact-analyzer-logs"
  location = var.region

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

# Service account for microservices
resource "google_service_account" "microservices" {
  account_id   = "impact-analyzer-services"
  display_name = "ImpactAnalyzer Microservices"
  description  = "Service account for ImpactAnalyzer microservices"
}

# IAM bindings for service account
resource "google_project_iam_member" "microservices_storage" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.microservices.email}"
}

resource "google_project_iam_member" "microservices_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.microservices.email}"
}

resource "google_project_iam_member" "microservices_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.microservices.email}"
}

# Secret Manager secrets
resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "openai-api-key"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "impact_analyzer_api_key" {
  secret_id = "impact-analyzer-api-key"

  replication {
    automatic = true
  }
}

# Cloud Scheduler job for daily refresh
resource "google_cloud_scheduler_job" "daily_refresh" {
  name        = "daily-dependency-refresh"
  description = "Daily refresh of dependency graphs and metrics"
  schedule    = "0 2 * * *"  # 2 AM daily
  time_zone   = "UTC"

  http_target {
    http_method = "POST"
    uri         = "https://ms-index-${random_id.suffix.hex}-uc.a.run.app/index/daily-refresh"
    
    headers = {
      "Content-Type" = "application/json"
      "X-Impact-Analyzer-Api-Key" = "dev-key-123"  # Use secret in production
    }
  }

  retry_config {
    retry_count = 3
  }
}

# Random suffix for unique resource names
resource "random_id" "suffix" {
  byte_length = 4
}

# Outputs
output "database_connection_name" {
  value = google_sql_database_instance.main.connection_name
}

output "vector_database_connection_name" {
  value = google_sql_database_instance.vector.connection_name
}

output "storage_bucket_main" {
  value = google_storage_bucket.main.name
}

output "storage_bucket_vectors" {
  value = google_storage_bucket.vectors.name
}

output "storage_bucket_logs" {
  value = google_storage_bucket.logs.name
}

output "service_account_email" {
  value = google_service_account.microservices.email
}

output "database_ip" {
  value = google_sql_database_instance.main.public_ip_address
}

output "vector_database_ip" {
  value = google_sql_database_instance.vector.public_ip_address
}