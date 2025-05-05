PROJECT_NAME = gdpr-obfuscator
REGION = eu-west-2
PYTHON_INTERPRETER = python
WD=$(shell pwd)
PYTHONPATH=${WD}:${WD}/src/
SHELL := /bin/bash
PROFILE = default
PIP:=pip
ZIP:=zip

## Run all commands aside from Terraform deployment
all: create-environment requirements dev-setup run-checks layer-setup

## Create python interpreter environment.
create-environment:
	@echo ">>> About to create environment: $(PROJECT_NAME)..."
	@echo ">>> check python3 version"
	( \
		$(PYTHON_INTERPRETER) --version; \
	)
	@echo ">>> Setting up VirtualEnv."
	( \
	    $(PIP) install -q virtualenv virtualenvwrapper; \
	    virtualenv venv --python=$(PYTHON_INTERPRETER); \
	)

# Define utility variable to help calling Python from the virtual environment
ACTIVATE_ENV := source venv/bin/activate

# Execute python related functionalities from within the project's environment
define execute_in_env
	$(ACTIVATE_ENV) && $1
endef

## Build the environment requirements
requirements: create-environment
	$(call execute_in_env, $(PIP) install pip-tools)
	$(call execute_in_env, pip-compile requirements.in)
	$(call execute_in_env, $(PIP) install -r requirements.txt)

###############################################################################
# Set Up

## Install bandit
bandit:
	$(call execute_in_env, $(PIP) install bandit)

## Install pip-audit
pip-audit:
	$(call execute_in_env, $(PIP) install pip-audit)

## Install flake8
flake8:
	$(call execute_in_env, $(PIP) install flake8)

## Install pytest-cov
pytest-cov:
	$(call execute_in_env, $(PIP) install pytest-cov)

## Set up dev requirements (bandit, pip-audit, black)
dev-setup: bandit pip-audit flake8 pytest-cov

# Build / Run

## Run the security test (bandit + pip-audit)
security-test:
	$(call execute_in_env, pip-audit -r requirements.txt) 

	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} bandit -lll \
									src/*.py test/*.py --skip B101,B311)

## Run flake8 code check
run-flake8:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} flake8 src/*.py test/*.py)

## Run the unit tests
unit-test:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest -vv)

## Run the coverage check
check-coverage:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest --cov=src)

check-terraform:
	$(call execute_in_env, terraform -chdir=terraform validate)

## Run all checks
run-checks: security-test run-flake8 unit-test check-coverage check-terraform

## Prepare lambda layers
layer-setup:
	$(call execute_in_env, mkdir -p ${WD}/tmp/layer_obfuscator/python && \
					cp -r ${WD}/src/obfuscator \
					${WD}/tmp/layer_obfuscator/python/ && \
					echo "Obfuscator library ready for Terraform deployment")


