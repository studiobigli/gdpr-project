#Requirements:
#***Configure a provider
#***Deploy backend s3
#***Create S3 buckets code, ingest, output
#***Create Zips for module and lambda script
#***Create layer for module
#***Deploy lambda script and module


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
    key = "terraform.tfstate"
  }
}

#S3 buckets

resource "aws_s3_bucket" "s3_code" {
  bucket = "${var.prefix}-code"
  tags = {
    name = "s3_code"
    environment = "dev"
    description = "S3 for storage and handling of lambda code"
  }
}

resource "aws_s3_bucket" "s3_ingestion" {
  bucket = "${var.prefix}-ingestion"
  tags = {
    name = "s3_ingestion"
    environment = "dev"
    description = "S3 for storage of CSVs to be obfuscated by lambda"
  }
}

resource "aws_s3_bucket" "s3_obfuscated" {
  bucket = "${var.prefix}-obfuscated"
  tags = {
    name = "s3_obfuscated"
    environment = "dev"
    description = "S3 for storage of obfuscated CSVs"
  }
}


