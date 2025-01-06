

import os
import sys
import pytest
from kubernetes import client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from kubectrl_helper import build_kube_config, run_kubectl_command

@pytest.fixture(scope="module")
def k8s_configuration():
    return {
        "cert_file": os.path.expanduser('~/k8s/minikube/downloaded_files/client.crt'),
        "key_file": os.path.expanduser('~/k8s/minikube/downloaded_files/client.key'),
        "host": "http://18.206.231.147:8001/"
    }


def test_namespace_exists(k8s_configuration):
    # Method 1 - kubernetes client
    client_configuration = client.Configuration()
    client_configuration.host = k8s_configuration["host"]
    client_configuration.cert_file = k8s_configuration["cert_file"]
    client_configuration.key_file = k8s_configuration["key_file"]

    # Apply the configuration
    client.Configuration.set_default(client_configuration)

    k8s_client = client.CoreV1Api()
    namespace = "default"
    namespaces = k8s_client.list_namespace()
    namespace_names = [ns.metadata.name for ns in namespaces.items]
    assert namespace in namespace_names, f"Namespace '{namespace}' does not exist"

    # method 2 - kubectl
    # command = f"kubectl get namespace {namespace}"
    # result = os.system(command)
    # assert result == 0, f"Namespace '{namespace}' does not exist"

    kube_config = build_kube_config(
        k8s_configuration["cert_file"], k8s_configuration["key_file"], k8s_configuration["host"])
    command = '/opt/kubectl/kubectl -o json get nodes'
    json_result = run_kubectl_command(kube_config, command)
    print(json_result)
