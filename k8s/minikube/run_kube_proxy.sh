#!/bin/bash

# Define variables
SSH_HOST=$(aws cloudformation describe-stacks --stack-name minikube-stack --query "Stacks[0].Outputs[?OutputKey=='InstancePublicIp'].OutputValue" --output text)
SSH_KEY="labsuser.pem"
SSH_USER="ec2-user"

ssh -o "StrictHostKeyChecking no" -i $SSH_KEY $SSH_USER@$SSH_HOST "pkill -f 'kubectl proxy'"
ssh -o "StrictHostKeyChecking no" -i $SSH_KEY $SSH_USER@$SSH_HOST "kubectl proxy --address=0.0.0.0 --accept-hosts='.*'"
