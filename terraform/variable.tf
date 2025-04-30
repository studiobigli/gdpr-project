variable "prefix" {
  type = string
  default = "gdpr-project"
  description = "Prefix for bucket names to remain unique. (Use tfvars)"
}

variable "src_location" {
  type = string
  default = "../src"
  description = "Location of project source code"
}

variable "tmp_location" {
  type = string
  default = "../tmp"
  description = "Location of files generated for deployment"
}

variable "obfuscator_lambda_file" {
  type = string
  default = "../src/example_lambda.py"
  description = "Lambda source file"
}

variable "awslayer_obfuscator_file" {
  type = string
  default = "../src/obfuscator.py"
  description = "Obfuscator source file"
}

