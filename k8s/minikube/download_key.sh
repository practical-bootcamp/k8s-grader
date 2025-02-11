#!/bin/bash

# Define variables
SSH_HOST=$(aws cloudformation describe-stacks --stack-name minikube-stack --query "Stacks[0].Outputs[?OutputKey=='InstancePublicIp'].OutputValue" --output text)
SSH_KEY="labsuser.pem"
SSH_USER="ec2-user"
REMOTE_DIR="/home/ec2-user/.minikube/profiles/minikube"
LOCAL_DIR="./downloaded_files"

# Create local directory if it doesn't exist
mkdir -p $LOCAL_DIR

# Download files
scp -o StrictHostKeyChecking=no -i $SSH_KEY $SSH_USER@$SSH_HOST:$REMOTE_DIR/client.crt $LOCAL_DIR/
scp -o StrictHostKeyChecking=no -i $SSH_KEY $SSH_USER@$SSH_HOST:$REMOTE_DIR/client.key $LOCAL_DIR/
# scp -i $SSH_KEY $SSH_USER@$SSH_HOST:/home/ec2-user/.minikube/ca.crt $LOCAL_DIR/
# scp -i $SSH_KEY $SSH_USER@$SSH_HOST:/home/ec2-user/.kube/config $LOCAL_DIR/

echo "Files downloaded to $LOCAL_DIR"