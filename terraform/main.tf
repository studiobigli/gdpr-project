#Configure Provider

terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 5.68.0"
        }
    }
}

provider "aws" {
  region = "eu-west-2"
}

terraform {
  backend "s3" {
    bucket = "lc-backend-gdpr"
    key = "terraform.tfstate"
    region = "eu-west-2"
  }
}

#S3 buckets

resource "aws_s3_bucket" "s3_code" {
  bucket = "lc-gdpr-code"
  tags = {
    name = "s3_code"
    environment = "dev"
    description = "S3 for storage and handling of lambda code"
  }
}

resource "aws_s3_bucket" "s3_ingestion" {
  bucket = "lc-gdpr-ingestion"
  tags = {
    name = "s3_ingestion"
    environment = "dev"
    description = "S3 for storage of CSVs to be obfuscated by lambda"
  }
}

resource = "aws_s3_bucket" "s3_obfuscated" {
  bucket = "lc-gdpr-obfuscated"
  tags = {
    name = "s3_obfuscated"
    environment = "dev"
    description = "S3 for storage of obfuscated CSVs"
  }
}


