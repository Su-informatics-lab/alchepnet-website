terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0.0"

  backend "s3" {
    key     = "alchepnet-website/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region  = var.region
  profile = var.profile

}

locals {
  common_tags = {
    Environment = var.environment
    IaC         = "True"
  }
}