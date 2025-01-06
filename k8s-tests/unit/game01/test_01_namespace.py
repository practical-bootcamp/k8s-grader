
from ..kubectrl_helper import build_kube_config, run_kubectl_command
from kubernetes import client
import logging
logging.basicConfig(level=logging.DEBUG)


def test_namespace_exists_with_library(json_input):

    # Method 1 - kubernetes client
    client_configuration = client.Configuration()
    client_configuration.host = json_input["host"]
    client_configuration.cert_file = json_input["cert_file"]
    client_configuration.key_file = json_input["key_file"]

    logging.debug(json_input)

    # Apply the configuration
    client.Configuration.set_default(client_configuration)

    k8s_client = client.CoreV1Api()
    namespace = "default"
    namespaces = k8s_client.list_namespace()
    namespace_names = [ns.metadata.name for ns in namespaces.items]
    assert namespace in namespace_names, f"Namespace '{namespace}' does not exist"

def test_namespace_exists_with_kubectl(json_input):
    # method 2 - kubectl
    kube_config = build_kube_config(
        json_input["cert_file"], json_input["key_file"], json_input["host"])
    command = 'kubectl get namespace'
    result = run_kubectl_command(kube_config, command)
    logging.info(result)
    namespace = "default"
    assert namespace in result, f"Namespace '{namespace}' does not exist"
