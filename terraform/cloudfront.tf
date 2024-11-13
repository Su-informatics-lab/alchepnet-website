module "cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "~> 3.0"

  comment             = "CloudFront distribution for ${var.domain}"
  enabled             = true
  staging             = false # If you want to create a staging distribution, set this to true
  http_version        = "http2and3"
  is_ipv6_enabled     = true
  price_class         = "PriceClass_All"
  retain_on_delete    = false
  wait_for_deployment = false
  default_root_object = "index.html"

  default_cache_behavior = {
    target_origin_id       = "s3-website"  # This needs to match origin_id below
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    forwarded_values = {
      query_string = false
      cookies = {
        forward = "none"
      }
    }
  }

  create_origin_access_control = true
  origin_access_control = {
    s3-website = {
      description      = "CloudFront access to S3 (${var.domain})"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  origin = {
    s3-website = {
      domain_name           = module.website_bucket.s3_bucket_bucket_regional_domain_name
      origin_access_control = "s3-website"  # Must match the key in origin_access_control
    }
  }

  geo_restriction = {
    restriction_type = "none"
  }

  viewer_certificate = {
    cloudfront_default_certificate = true
  }

  tags = local.common_tags
}

# Add bucket policy to allow access from the OAI
resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = module.website_bucket.s3_bucket_id

  policy = jsonencode({
    "Version" : "2008-10-17",
    "Id" : "PolicyForCloudFrontPrivateContent",
    "Statement" : [
      {
        "Sid" : "AllowCloudFrontServicePrincipal",
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "cloudfront.amazonaws.com"
        },
        "Action" : "s3:GetObject",
        "Resource" : "${module.website_bucket.s3_bucket_arn}/*",
        "Condition" : {
          "StringEquals" : {
            "AWS:SourceArn" : module.cloudfront.cloudfront_distribution_arn
          }
        }
      }
    ]
  })
}