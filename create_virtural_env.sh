#!/bin/bash

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip to the latest version
pip install --upgrade pip

pip install -r k8s-grader-api/common-layer/requirements.txt

echo "Virtual environment created and activated. Pip upgraded to the latest version."