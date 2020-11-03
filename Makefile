NAME = bridge
LAMBDA_FUNCTIONS = aws_lambda
CDK = cdk

FILES_PY = $(shell find $(CURDIR)/$(NAME) $(CURDIR)/$(LAMBDA_FUNCTIONS) $(CURDIR)/$(CDK) $(CURDIR)/cdk_app.py -type f -name "*.py")
OUTPUT = $(CURDIR)/output

setup-dev:
	pip install -r requirements.txt && \
	python3 setup.py build_ext --inplace

flake8:
	@echo "Running flake8"
	@flake8 $(FILES_PY)

mypy:
	@echo "Running mypy"
	@mypy $(FILES_PY)

isort:
	@echo "Running isort"
	@isort -c $(FILES_PY)

validate: flake8 mypy isort

clean:
	rm -rf $(DEP_BUILD)
