#!/bin/bash

# Define variables
SSH_HOST="3.82.190.80"
SSH_KEY="labsuser.pem"
SSH_USER="ec2-user"

# Upload start_minikube.sh to remote host and run it remotely
scp -i $SSH_KEY ./start_minikube.sh $SSH_USER@$SSH_HOST:/home/ec2-user/
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "minikube stop"
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "chmod +x /home/ec2-user/start_minikube.sh && /home/ec2-user/start_minikube.sh"
