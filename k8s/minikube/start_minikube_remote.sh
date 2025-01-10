#!/bin/bash

# Define variables
SSH_HOST=$(aws ec2 describe-instances --region us-east-1 --query "Reservations[*].Instances[*].PublicIpAddress" --output text)
SSH_KEY="labsuser.pem"
SSH_USER="ec2-user"

# Upload start_minikube.sh to remote host and run it remotely
scp -o StrictHostKeyChecking=no -i $SSH_KEY ./scripts/start_minikube.sh $SSH_USER@$SSH_HOST:/home/ec2-user/
ssh -o "StrictHostKeyChecking no" -i $SSH_KEY $SSH_USER@$SSH_HOST "minikube stop"
ssh -o "StrictHostKeyChecking no" -i $SSH_KEY $SSH_USER@$SSH_HOST "chmod +x /home/ec2-user/start_minikube.sh && /home/ec2-user/start_minikube.sh"

# Update endpoint.txt with the SSH_HOST IP
echo "http://$SSH_HOST:8001" > /workspaces/k8s-grader/k8s/minikube/endpoint.txt
