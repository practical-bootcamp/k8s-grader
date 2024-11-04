# k8s-grader
Automatic Grading Tools for k8s exercises


## Setup

### Install the latest AWS SAM.
```
.\aws_sam_setup.sh
```
### Configure AWS Credentials 
Method 1: Configure AWS Account for AWS Academy Learner Lab 
```
export AWS_ACCESS_KEY_ID=ASIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_SESSION_TOKEN=AQoDYXdzEJr...<remainder of session token>
export AWS_DEFAULT_REGION=us-east-1
```
Method 2: Set the token with CLI
```
aws configure
aws configure set aws_session_token  IQoJb3JpZ2luX2VjEGkaCXVzLXdlc3QtMiJHMEUCIDUWMbligXWYVOC+Ys1AdMrTT7EJhhy6dPlBuH2FVYT/AiEAn6q3JvH5A5vVLFjRVoLVjQuEjtoXR26+OaxztYP7q4wqrwII4v//////////ARAAGgw5NzUwNDk4ODcwMTkiDNJWB0V07FC1CWQNtSqDArQL15dsum9zRmNHrV0/iNvVCoV2lgbGjdW1m1KECFVx16q8Vnn2gVdm6iAQiobtDnpxTTUctXxlmeRsab7EvxoLOl4fV+zE5XVi/q1nz5YlMb56hG78BDrh2/js+memjyVHXQ5+FHgjLkfWo9BHseILQ1D2D4v5iEfiwW8nvpF+ktPU/k5JTYlep25FJ4yJb1ib+dC6UjryaMeP0gCBh+HuSjW3RPBT36BiLvpMLWun39Qk1Zlc0es/u9J1imsrx4W4Rf/d69Hoeqym2GlQKYTR8tXeaN3DwW8quh0kfTmUIPC2v+ADGHsumiV6KdOoblfcjVcfx+fxlv4Y6fOw9G4H/QUwy62guQY6nQHW2RSdfAyG7ZwVpHyUG7xe06uC1nz/lh3xmyXgnAFAlR/6YYh1cBaINXi/2q93mB5hJa3D8UaslqxAx7hKzg7S3D+I92IfB2jOgqzID5TF5Wk+vX5ItUoo04zUWxYztZxDhFV/OesNO+v8R5K3yv9OqGYslHn5QpyyLFO1fDWoD5h4g5+YtnhZsvyU8TiXj/XQiquHb8joAShfGN5A
```

## Deploy the SAM project
```
cd k8s-grader-api
sam build
sam deploy
```

## Deploy Minikube
After configure the AWS Credentials, then run
```
cd k8s/minikube
aws cloudformation create-stack --stack-name minikube-stack --template-body file://minikube.yaml
```
Delete Minikube
```
aws cloudformation delete-stack --stack-name minikube-stack
```