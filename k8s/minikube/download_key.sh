#!/bin/bash

# Define variables
SSH_KEY="labsuser.pem"
SSH_USER="ec2-user"
SSH_HOST="98.80.223.67"
REMOTE_DIR="/home/ec2-user/.minikube/profiles/minikube"
LOCAL_DIR="./downloaded_files"

# Create local directory if it doesn't exist
mkdir -p $LOCAL_DIR

# Download files
scp -i $SSH_KEY $SSH_USER@$SSH_HOST:$REMOTE_DIR/client.crt $LOCAL_DIR/
scp -i $SSH_KEY $SSH_USER@$SSH_HOST:$REMOTE_DIR/client.key $LOCAL_DIR/

echo "Files downloaded to $LOCAL_DIR"