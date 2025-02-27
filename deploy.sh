#!/bin/bash
# set -x

cd k8s-grader-api

sam build || { echo "sam build failed"; exit 1; }
if [ -n "$1" ]; then
    sam deploy --parameter-overrides SecretHash="$1" || { echo "sam deploy failed"; exit 1; }
else
    sam deploy || { echo "sam deploy failed"; exit 1; }
fi

LoadNpcBackgroundApi=$(aws cloudformation describe-stacks --stack-name k8s-grader-api --query "Stacks[0].Outputs[?OutputKey=='LoadNpcBackgroundApi'].OutputValue" --output text)

response=$(curl "$LoadNpcBackgroundApi")
echo "$response"