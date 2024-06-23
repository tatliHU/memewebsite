terraform {
  required_version = "= 1.6.3"
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "1.39.0"
    }
  }
}
provider "hcloud" {
  token = var.hcloud_token
}