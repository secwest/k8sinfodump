import json
import os
import datetime
from kubernetes import client, config

# Load Kubernetes config
config.load_kube_config()

# Kubernetes API clients
v1 = client.CoreV1Api()
rbac_v1 = client.RbacAuthorizationV1Api()

# Initialize the output directory with a timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
output_dir = f"k8s_dump_{timestamp}"
os.makedirs(output_dir, exist_ok=True)

# Function to filter roles or cluster roles by specific access
def filter_roles_by_access(role_list, resource):
    return [role.metadata.name for role in role_list if any(
        resource in rule.resources for rule in role.rules if rule.resources)]

# Get all network policies
network_policies = client.NetworkingV1Api().list_network_policy_for_all_namespaces().items
network_policies_data = [{"rule_name": np.metadata.name, "namespace": np.metadata.namespace} for np in network_policies]
with open(os.path.join(output_dir, f"network_policies_{timestamp}.txt"), "w") as file:
    for np in network_policies_data:
        file.write(f'rule_name: {np["rule_name"]} namespace: {np["namespace"]}\n')

# Get Cluster Admin Role Bindings
cluster_role_bindings = rbac_v1.list_cluster_role_binding().items
cluster_admin_bindings = [crb.metadata.name for crb in cluster_role_bindings if "cluster-admin" in crb.role_ref.name]
with open(os.path.join(output_dir, f"cluster_admin_role_bindings_{timestamp}.txt"), "w") as file:
    file.write("\n".join(cluster_admin_bindings))

# Get Cluster Roles with Secrets Access
cluster_roles = rbac_v1.list_cluster_role().items
cluster_roles_secrets_access = filter_roles_by_access(cluster_roles, "secrets")
with open(os.path.join(output_dir, f"cluster_roles_secrets_access_{timestamp}.txt"), "w") as file:
    file.write("\n".join(cluster_roles_secrets_access))

# Get Roles with Secrets Access
roles = rbac_v1.list_role_for_all_namespaces().items
roles_secrets_access = filter_roles_by_access(roles, "secrets")
with open(os.path.join(output_dir, f"roles_secrets_access_{timestamp}.txt"), "w") as file:
    file.write("\n".join(roles_secrets_access))

# Get Cluster Roles with ConfigMaps Access
cluster_roles_configmaps_access = filter_roles_by_access(cluster_roles, "configmaps")
with open(os.path.join(output_dir, f"cluster_roles_configmaps_access_{timestamp}.txt"), "w") as file:
    file.write("\n".join(cluster_roles_configmaps_access))

# Get Roles with ConfigMaps Access
roles_configmaps_access = filter_roles_by_access(roles, "configmaps")
with open(os.path.join(output_dir, f"roles_configmaps_access_{timestamp}.txt"), "w") as file:
    file.write("\n".join(roles_configmaps_access))

# Get Pods with Containers Without Resources Limits
pods = v1.list_pod_for_all_namespaces().items
pods_without_resource_limits = [pod.metadata.name for pod in pods if any(
    container.resources.limits is None for container in pod.spec.containers)]
with open(os.path.join(output_dir, f"pods_without_resource_limits_{timestamp}.txt"), "w") as file:
    file.write("\n".join(pods_without_resource_limits))

# Final message
print(f"Kubernetes information has been dumped into {output_dir}/")
