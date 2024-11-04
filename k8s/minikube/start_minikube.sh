
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
        -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
PRIVATE_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4 \
            -H "X-aws-ec2-metadata-token: $TOKEN")
minikube start --apiserver-ips=$PRIVATE_IP --driver=docker --force
minikube addons enable metrics-server
minikube status