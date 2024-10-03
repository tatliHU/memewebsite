terraform {
  required_version = "= 1.6.3"
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "1.39.0"
    }
    aws = {
      source = "hashicorp/aws"
      version = "5.69.0"
    }
  }
}
provider "hcloud" {
  token = var.hcloud_token
}

provider "aws" {
  region = var.aws.region
}