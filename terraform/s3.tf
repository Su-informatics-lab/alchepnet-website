module "website_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 4.0"

  bucket = var.domain

  tags = merge(
    local.common_tags,
    {
      Name = var.domain
    }
  )
}