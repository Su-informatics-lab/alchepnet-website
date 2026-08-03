data "aws_iam_openid_connect_provider" "github_actions" {
  url = "https://token.actions.githubusercontent.com"
}

data "aws_caller_identity" "github_actions" {}

data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github_actions.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.repository}:ref:refs/heads/develop"]
    }
  }
}

resource "aws_iam_role" "github_actions_deployer" {
  name               = "github-actions-alchepnet-website-deployer"
  description        = "Deploys the alchepnet-website develop branch from GitHub Actions"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json
}

data "aws_iam_policy_document" "github_actions_deploy" {
  statement {
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::test.alchepnet.org"]
  }

  statement {
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["arn:aws:s3:::test.alchepnet.org/*"]
  }

  statement {
    effect    = "Allow"
    actions   = ["cloudfront:CreateInvalidation"]
    resources = ["arn:aws:cloudfront::${data.aws_caller_identity.github_actions.account_id}:distribution/EAIFBVSW6O5UF"]
  }
}

resource "aws_iam_role_policy" "github_actions_deploy" {
  name   = "deploy-website"
  role   = aws_iam_role.github_actions_deployer.id
  policy = data.aws_iam_policy_document.github_actions_deploy.json
}

import {
  to = aws_iam_role.github_actions_deployer
  id = "github-actions-alchepnet-website-deployer"
}

import {
  to = aws_iam_role_policy.github_actions_deploy
  id = "github-actions-alchepnet-website-deployer:deploy-website"
}
