terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "~> 0.100"
    }
  }
  required_version = ">= 1.0"
}

provider "yandex" {
  # Service account key file is only used locally
  # In CI/CD, authentication is skipped (validation only)
  service_account_key_file = fileexists("${path.module}/key.json") ? "${path.module}/key.json" : null
  cloud_id                 = var.cloud_id
  folder_id                = var.folder_id
  zone                     = var.zone
}