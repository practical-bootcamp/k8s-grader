import json

import boto3


def get_stack_outputs(stack_name):
    client = boto3.client("cloudformation", region_name="us-east-1")
    response = client.describe_stacks(StackName=stack_name)

    outputs = {}
    for stack in response["Stacks"]:
        for output in stack["Outputs"]:
            outputs[output["OutputKey"]] = output["OutputValue"]

    return outputs


def read_env_template(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    stack_name = "k8s-grader-api"
    output_values = get_stack_outputs(stack_name)

    template_path = "/workspaces/k8s-grader/k8s-grader-api/events/env.template.json"
    env_template = read_env_template(template_path)

    def update_env_template(env_template, output_values):
        if isinstance(env_template, dict):
            for key, value in env_template.items():
                if key in output_values:
                    env_template[key] = output_values[key]
                else:
                    update_env_template(value, output_values)
        elif isinstance(env_template, list):
            for item in env_template:
                update_env_template(item, output_values)

    update_env_template(env_template, output_values)

    with open(
        "/workspaces/k8s-grader/k8s-grader-api/events/env.json", "w", encoding="utf-8"
    ) as file:
        json.dump(env_template, file, indent=4)

    print("Environment variables updated successfully")
