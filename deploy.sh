#!/bin/bash
# set -x

cd k8s-grader-api

sam build || { echo "sam build failed"; exit 1; }
if [ -n "$1" ]; then
    sam deploy --parameter-overrides SecretHash="$1" || { echo "sam deploy failed"; exit 1; }
else
    sam deploy || { echo "sam deploy failed"; exit 1; }
fi
