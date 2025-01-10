#!/bin/bash

# Define variables
SSH_HOST=$(aws ec2 describe-instances --region us-east-1 --query "Reservations[*].Instances[*].PublicIpAddress" --output text)
SSH_KEY="labsuser.pem"
SSH_USER="ec2-user"

ssh -o "StrictHostKeyChecking no" -i $SSH_KEY $SSH_USER@$SSH_HOST "minikube status"


