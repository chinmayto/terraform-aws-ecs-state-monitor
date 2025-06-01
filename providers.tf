terraform {
  required_version = ">= 1.1"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.43"
    }
  }
}

####################################################
# Configure the AWS Provider
####################################################
provider "aws" {
  region = local.region
}
