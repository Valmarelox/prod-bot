terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.52.0"
    }
    klayers = {
      version = "~> 1.0.0"
      source  = "ldcorentin/klayer"
    }
  }
  backend "s3" {
    bucket = "tfremotestate-chatservice"
    key    = "state"
    region = "us-east-1"
  }
}
