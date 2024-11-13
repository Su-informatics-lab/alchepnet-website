data "aws_caller_identity" "current" {}

locals {
  sanitized_domain          = replace(var.domain, ".", "_")
  website_build_project     = "${local.sanitized_domain}-website-deployment"
  invalidation_build_project = "${local.sanitized_domain}-website-invalidation"
}


data "aws_iam_policy_document" "codebuild" {
  statement {
    effect = "Allow"

    resources = [
      "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/codebuild/${local.website_build_project}",
      "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/codebuild/${local.website_build_project}:*",
      "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/codebuild/${local.invalidation_build_project}",
      "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/codebuild/${local.invalidation_build_project}:*"
    ]

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
  }

  statement {
    effect = "Allow"

    resources = [
      module.codepipeline_bucket.s3_bucket_arn,
      "${module.codepipeline_bucket.s3_bucket_arn}/*"
    ]

    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:GetBucketAcl",
      "s3:GetBucketLocation"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "codebuild:CreateReportGroup",
      "codebuild:CreateReport",
      "codebuild:UpdateReport",
      "codebuild:BatchPutTestCases",
      "codebuild:BatchPutCodeCoverages"
    ]

    resources = [
      "arn:aws:codebuild:${var.region}:${data.aws_caller_identity.current.account_id}:report-group/${var.domain}-website-*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "cloudfront:CreateInvalidation"
    ]

    resources = [
      module.cloudfront.cloudfront_distribution_arn
    ]
  }
}

resource "aws_iam_policy" "codebuild" {
  name        = "codebuild-${var.domain}-website-policy"
  path        = "/service-role/"
  description = "Policy used in trust relationship with CodeBuild"
  policy      = data.aws_iam_policy_document.codebuild.json
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "codebuild_website_service_role" {
  name               = "codebuild-${var.domain}-website-service-role"
  path               = "/service-role/"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "codebuild_policy_attach" {
  role       = aws_iam_role.codebuild_website_service_role.name
  policy_arn = aws_iam_policy.codebuild.arn
}

resource "aws_codebuild_project" "website_deployment" {
  name                   = local.website_build_project
  description            = "Deploy ${var.domain} website to S3."
  service_role           = aws_iam_role.codebuild_website_service_role.arn
  concurrent_build_limit = 1
  build_timeout          = "15"

  artifacts {
    type = "CODEPIPELINE"
    name = local.website_build_project
  }

  environment {
    compute_type                = "BUILD_LAMBDA_2GB"
    image                       = "aws/codebuild/amazonlinux-aarch64-lambda-standard:python3.12"
    type                        = "ARM_LAMBDA_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = <<EOT
version: 0.2

artifacts:
  base-directory: 'src'
  files:
    - '**/*'
EOT
  }

  logs_config {
    cloudwatch_logs {
      status = "ENABLED"
    }

    s3_logs {
      status = "DISABLED"
    }
  }
}

resource "aws_codebuild_project" "website_invalidation" {
  badge_enabled        = false
  badge_url            = null
  build_timeout        = 15
  description          = null
  name                 = local.invalidation_build_project
  project_visibility   = "PRIVATE"
  public_project_alias = null
  resource_access_role = null
  service_role         = aws_iam_role.codebuild_website_service_role.arn
  source_version       = null
  tags                 = {}
  tags_all             = {}

  artifacts {
    artifact_identifier    = null
    bucket_owner_access    = null
    encryption_disabled    = false
    location               = null
    name                   = null
    namespace_type         = null
    override_artifact_name = false
    packaging              = null
    path                   = null
    type                   = "NO_ARTIFACTS"
  }

  cache {
    location = null
    modes    = []
    type     = "NO_CACHE"
  }

  environment {
    certificate                 = null
    compute_type                = "BUILD_LAMBDA_1GB"
    image                       = "aws/codebuild/amazonlinux-x86_64-lambda-standard:python3.12"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = false
    type                        = "LINUX_LAMBDA_CONTAINER"

    environment_variable {
      name  = "CACHEID"
      type  = "PLAINTEXT"
      value = module.cloudfront.cloudfront_distribution_id
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = null
      status      = "ENABLED"
      stream_name = null
    }
    s3_logs {
      bucket_owner_access = null
      encryption_disabled = false
      location            = null
      status              = "DISABLED"
    }
  }

  source {
    buildspec           = <<-EOT
            version: 0.2

            phases:
              build:
                commands:
                  - aws cloudfront create-invalidation --distribution-id=$CACHEID --paths "/*"
        EOT
    git_clone_depth     = 0
    insecure_ssl        = false
    location            = null
    report_build_status = false
    type                = "NO_SOURCE"
  }
}

resource "aws_iam_role" "codepipeline_role" {
  name = "codepipeline-${var.domain}-website-deployment-role"
  path = "/service-role/"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codepipeline.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "codepipeline_policy" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:PutObject"
    ]

    resources = [
      "${module.codepipeline_bucket.s3_bucket_arn}/*",
      "${module.website_bucket.s3_bucket_arn}/*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "codebuild:BatchGetBuilds",
      "codebuild:StartBuild",
      "codebuild:StopBuild"
    ]

    resources = [
      aws_codebuild_project.website_deployment.arn,
      aws_codebuild_project.website_invalidation.arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "cloudwatch:PutMetricData"
    ]

    resources = ["*"]
  }

  statement {
    effect = "Allow"

    actions = [
      "iam:PassRole"
    ]

    resources = [
      aws_iam_role.codepipeline_role.arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "cloudfront:CreateInvalidation"
    ]

    resources = [
      module.cloudfront.cloudfront_distribution_arn
    ]
  }
  statement {
    actions = [
      "codestar-connections:UseConnection"
    ]
    resources = [
      aws_codestarconnections_connection.source_connection.arn
    ]
    effect = "Allow"
  }
}

resource "aws_iam_policy" "codepipeline_policy" {
  name        = "codepipeline_${var.domain}_website_deployment_policy"
  description = "Policy for CodePipeline to deploy ${var.domain}-website"
  policy      = data.aws_iam_policy_document.codepipeline_policy.json
}

resource "aws_iam_role_policy_attachment" "codepipeline_policy_attachment" {
  role       = aws_iam_role.codepipeline_role.name
  policy_arn = aws_iam_policy.codepipeline_policy.arn
}

module "codepipeline_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 4.0"

  bucket_prefix = "${var.domain}-website-codepipeline"

  tags = local.common_tags

}

resource "aws_codestarconnections_connection" "source_connection" {
  name          = var.codestar
  provider_type = "GitHub"
}

resource "aws_codepipeline" "codepipeline" {
  name           = "${var.domain}-website-deployment"
  role_arn       = aws_iam_role.codepipeline_role.arn
  pipeline_type  = "V2"
  execution_mode = "QUEUED"

  artifact_store {
    location = module.codepipeline_bucket.s3_bucket_arn
    type     = "S3"
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      namespace        = "SourceVariables"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["SourceArtifact"]

      configuration = {
        ConnectionArn        = aws_codestarconnections_connection.source_connection.arn
        FullRepositoryId     = var.repository
        BranchName           = "main"
        DetectChanges        = "false"
        OutputArtifactFormat = "CODE_ZIP"
      }
    }
  }

  stage {
    name = "Build"

    action {
      name             = "Build"
      namespace        = "BuildVariables"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      output_artifacts = ["BuildArtifact"]
      input_artifacts  = ["SourceArtifact"]

      configuration = {
        ProjectName = aws_codebuild_project.website_deployment.name
      }
    }
  }

  stage {
    name = "Deploy"

    action {
      name            = "Deploy"
      namespace       = "DeployVariables"
      category        = "Deploy"
      owner           = "AWS"
      provider        = "S3"
      version         = "1"
      input_artifacts = ["BuildArtifact"]

      configuration = {
        BucketName = var.domain
        Extract    = "true"
      }
    }
  }

  stage {
    name = "Invalidate"

    action {
      name            = "Invalidate"
      namespace       = "InvalidateVariables"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      version         = "1"
      input_artifacts = ["BuildArtifact"]

      configuration = {
        ProjectName = aws_codebuild_project.website_invalidation.name
      }
    }
  }

  trigger {
    provider_type = "CodeStarSourceConnection"

    git_configuration {
      source_action_name = "Source"

      push {
        tags {
          includes = [
            "v[0-9]*.[0-9]*.[0-9]*",
          ]
        }
      }
    }
  }
}