from kubernetes import client

def configure_k8s_client(json_input):
    client_configuration = client.Configuration()
    client_configuration.host = json_input["host"]
    client_configuration.cert_file = json_input["cert_file"]
    client_configuration.key_file = json_input["key_file"]
    client.Configuration.set_default(client_configuration)
    return client.CoreV1Api()
