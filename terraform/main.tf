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

# Create lambda layer

data "archive_file" "layer_obfuscator_zip" {
  type = "zip"
  source_dir = "${path.module}/../tmp/layer_obfuscator"
  output_path = "${path.module}/../tmp/layer_obfuscator.zip"
}

resource "aws_s3_object" "layer_obfuscator" {
  bucket = aws_s3_bucket.s3_code.bucket
  key = "awslayer_obfuscator.zip"
  source = data.archive_file.layer_obfuscator_zip.output_path
  etag = filemd5(data.archive_file.layer_obfuscator_zip.output_path)
  depends_on = [data.archive_file.layer_obfuscator_zip]
}

resource "aws_lambda_layer_version" "layer_obfuscator" {
  layer_name = "layer_obfuscator"
  s3_bucket = aws_s3_object.layer_obfuscator.bucket
  s3_key = aws_s3_object.layer_obfuscator.key
  s3_object_version = aws_s3_object.layer_obfuscator.version_id
  source_code_hash = data.archive_file.layer_obfuscator_zip.output_base64sha256
  description = "Layer containing obfuscator library"
  compatible_runtimes = ["python3.12"]
}

# Create lambda

data "archive_file" "obfuscator_lambda_file" {
  type = "zip"
  source_file = "${path.module}/${var.obfuscator_lambda_file}"
  output_path = "${path.module}/${var.tmp_location}/obfuscator_lambda.zip"
}

resource "aws_s3_object" "obfuscator_lambda" {
  bucket = aws_s3_bucket.s3_code.bucket
  key = "obfuscator_lambda.zip"
  source = data.archive_file.obfuscator_lambda_file.output_path
  etag = filemd5(data.archive_file.obfuscator_lambda_file.output_path)
  depends_on = [data.archive_file.obfuscator_lambda_file]
}

resource "aws_lambda_function" "obfuscator_lambda" {
  function_name = "obfuscator"
  s3_bucket = aws_s3_bucket.s3_code.bucket
  s3_key = aws_s3_object.obfuscator_lambda.key
  role = aws_iam_role.role_obfuscator.arn
  handler = "example_lambda.lambda_handler"
  timeout = 180
  source_code_hash = data.archive_file.obfuscator_lambda_file.output_base64sha256
  runtime = "python3.12"
  layers = [aws_lambda_layer_version.layer_obfuscator.arn]
  #depends_on = ADD CLOUDWATCH FOR LOGGING
  environment {
    variables = {
      INGESTION_BUCKET = aws_s3_bucket.s3_ingestion.bucket
      OBFUSCATED_BUCKET = aws_s3_bucket.s3_obfuscated.bucket
      INGESTION_KEY = aws_s3_object.csv_dummydata.key
    }
  }
}

# Lambda permissions to automatically run on upload to ingestion bucket

resource "aws_lambda_permission" "execute_from_ingestion_s3" {
  statement_id = "AllowExecutionFromS3Bucket"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.obfuscator_lambda.arn
  principal = "s3.amazonaws.com"
  source_arn = aws_s3_bucket.s3_ingestion.arn
}

resource "aws_s3_bucket_notification" "s3_notification" {
  bucket = aws_s3_bucket.s3_ingestion.id
  lambda_function {
    lambda_function_arn = aws_lambda_function.obfuscator_lambda.arn
    events = ["s3:ObjectCreated:*"]
    filter_suffix = "-fields.json"
  }
  depends_on = [aws_lambda_permission.execute_from_ingestion_s3]
}

# Lambda IAM Policy

data "aws_iam_policy_document" "policy_document_obfuscator" {
  statement {
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "role_obfuscator" {
  name = "role_obfuscator"
  assume_role_policy = data.aws_iam_policy_document.policy_document_obfuscator.json
}

resource "aws_iam_policy" "policy_obfuscator" {
  name = "policy_obfuscator"
  description = "IAM policy for Lambda to access S3 buckets"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = ["s3:GetObject", "s3:PutObject"],
        Effect = "Allow",
        Resource = "arn:aws:s3:::${aws_s3_bucket.s3_code.bucket}/*"
      },
      {
        Action = ["s3:GetObject", "s3:DeleteObject" "s3:PutObject"],
        Effect = "Allow",
        Resource = "arn:aws:s3:::${aws_s3_bucket.s3_ingestion.bucket}/*"
      },
      {
        Action = ["s3:PutObject"],
        Effect = "Allow",
        Resource = "arn:aws:s3:::${aws_s3_bucket.s3_obfuscated.bucket}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "policy_obfuscator_attachment" {
  role = aws_iam_role.role_obfuscator.name
  policy_arn = aws_iam_policy.policy_obfuscator.arn
}

# Upload dummy CSV file

resource "aws_s3_object" "csv_dummydata" {
  bucket = aws_s3_bucket.s3_ingestion.bucket
  key = "dummydata.csv"
  source = "${var.dummy_csv_file}"
  etag = filemd5("${var.dummy_csv_file}")
}

