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
aws configure set aws_session_token <Session Token>
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


## Minikube dashboard
For more information on how to make the Minikube dashboard accessible on all IPs (0.0.0.0), refer to [this link](https://unix.stackexchange.com/questions/621369/how-can-i-make-the-minikube-dashboard-answer-on-all-ips-0-0-0-0).

```
kubectl proxy --address=0.0.0.0 --accept-hosts='.*'
minikube dashboard --url
```

Sample Data
```
{
 "email": "cywong@vtc.edu.hk",
 "client_certificate": "-----BEGIN RSA PRIVATE KEY-----XXX-----END RSA PRIVATE KEY-----\n",
 "client_key": "-----BEGIN CERTIFICATE-----XX-----END CERTIFICATE-----\n",
 "endpoint": "http://3.90.40.12:8001"
}
```
