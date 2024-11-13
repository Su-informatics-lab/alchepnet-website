variable "tf_state_bucket" {
  description = "Name of the S3 bucket for Terraform state storage"
  type        = string
}

variable "tf_lock_table" {
  description = "Name of the DynamoDB table for state locking"
  type        = string
}

variable "region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "profile" {
  description = "The AWS CLI profile to use"
  type        = string
  default     = "default"
}

variable "domain" {
  description = "Domain name for the website"
  type        = string
}

variable "environment" {
  description = "Environment to deploy resources"
  type        = string
}

variable "repository" {
  description = "Name of the GitHub repository (org/repo)"
  type        = string
}

variable "codestar" {
  description = "Name of the CodeStar connection"
  type        = string
}
