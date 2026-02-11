# ==============================================
# BourseChain - Terraform Provider Configuration
# Sprint 6 - Infrastructure as Code (IaC)
# ==============================================

terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.27"
    }
  }

  # Remote state (uncomment for team collaboration)
  # backend "s3" {
  #   bucket         = "boursechain-terraform-state"
  #   key            = "infrastructure/terraform.tfstate"
  #   region         = "me-south-1"
  #   encrypt        = true
  #   dynamodb_table = "boursechain-terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "BourseChain"
      Environment = var.environment
      ManagedBy   = "Terraform"
      University  = "Amirkabir"
      Course      = "SE2"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_ca_certificate)
  token                  = module.eks.cluster_auth_token
}
