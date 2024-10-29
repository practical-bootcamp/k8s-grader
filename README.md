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
aws configure set aws_session_token  AQoDYXdzEJr...<remainder of session token>
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
./deploy.sh
```