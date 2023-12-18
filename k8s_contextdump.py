import json
import os
import datetime
from kubernetes import client, config

# Load Kubernetes config
config.load_kube_config()

# Kubernetes API clients
v1 = client.CoreV1Api()
rbac_v1 = client.RbacAuthorizationV1Api()
apps_v1 = client.AppsV1Api()
networking_v1 = client.NetworkingV1Api()
storage_v1 = client.StorageV1Api()
apiextensions_v1 = client.ApiextensionsV1Api()

# Initialize the output directory with a timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
output_dir = f"k8s_dump_{timestamp}"
os.makedirs(output_dir, exist_ok=True)

# Save the current context
current_context = config.list_kube_config_contexts()[1]['context']
context_name = current_context['name']
context_json = json.dumps(current_context, indent=4)
with open(os.path.join(output_dir, f"context_{timestamp}.txt"), "w") as file:
    file.write(f"Current context: {context_name}")
with open(os.path.join(output_dir, f"context_{timestamp}.json"), "w") as file:
    file.write(context_json)

# Dump nodes information
nodes = v1.list_node().items
nodes_info = [f"{node.metadata.name} {node.status.addresses[0].address} {node.status.node_info.kubelet_version}" for node in nodes]
nodes_json = json.dumps([node.to_dict() for node in nodes], indent=4)
with open(os.path.join(output_dir, f"nodes_info_{timestamp}.txt"), "w") as file:
    file.write("\n".join(nodes_info))
with open(os.path.join(output_dir, f"nodes_{timestamp}.json"), "w") as file:
    file.write(nodes_json)

# Dump pods information across all namespaces
pods = v1.list_pod_for_all_namespaces().items
pods_info = [f"{pod.metadata.namespace} {pod.metadata.name} {pod.status.phase}" for pod in pods]
pods_json = json.dumps([pod.to_dict() for pod in pods], indent=4)
with open(os.path.join(output_dir, f"pods_info_{timestamp}.txt"), "w") as file:
    file.write("\n".join(pods_info))
with open(os.path.join(output_dir, f"pods_{timestamp}.json"), "w") as file:
    file.write(pods_json)

# Dump various resources across all namespaces
def dump_resources(resource_list, file_name):
    resource_data = json.dumps([resource.to_dict() for resource in resource_list], indent=4)
    with open(os.path.join(output_dir, f"{file_name}_{timestamp}.json"), "w") as file:
        file.write(resource_data)

# Services, ConfigMaps, Secrets, Deployments, ReplicaSets, StatefulSets, DaemonSets, Endpoints
dump_resources(v1.list_service_for_all_namespaces().items, "services")
dump_resources(v1.list_config_map_for_all_namespaces().items, "configmaps")
dump_resources(v1.list_secret_for_all_namespaces().items, "secrets")
dump_resources(apps_v1.list_deployment_for_all_namespaces().items, "deployments")
dump_resources(apps_v1.list_replica_set_for_all_namespaces().items, "replicasets")
dump_resources(apps_v1.list_stateful_set_for_all_namespaces().items, "statefulsets")
dump_resources(apps_v1.list_daemon_set_for_all_namespaces().items, "daemonsets")
dump_resources(v1.list_endpoints_for_all_namespaces().items, "endpoints")

# Dump Network Policies
dump_resources(networking_v1.list_network_policy_for_all_namespaces().items, "networkpolicies")

# Dump RBAC Policies
dump_resources(rbac_v1.list_cluster_role_binding().items, "clusterrolebindings")
dump_resources(rbac_v1.list_cluster_role().items, "clusterroles")
dump_resources(rbac_v1.list_role_binding_for_all_namespaces().items, "rolebindings")
dump_resources(rbac_v1.list_role_for_all_namespaces().items, "roles")

# Dump Storage Class and Persistent Volumes
dump_resources(storage_v1.list_storage_class().items, "storageclasses")
dump_resources(v1.list_persistent_volume().items, "persistentvolumes")
dump_resources(v1.list_persistent_volume_claim_for_all_namespaces().items, "persistentvolumeclaims")

# Dump Custom Resource Definitions
dump_resources(apiextensions_v1.list_custom_resource_definition().items, "customresourcedefinitions")

# Dump Container Runtime Versions
container_runtime_versions = [node.status.node_info.container_runtime_version for node in nodes]
with open(os.path.join(output_dir, f"cri_{timestamp}.txt"), "w") as file:
    file.write("\n".join(container_runtime_versions))

# Dump CNI DaemonSets
dump_resources(apps_v1.list_namespaced_daemon_set("kube-system").items, "cni_daemonsets")

# Dump CSI Drivers and Nodes
dump_resources(storage_v1.list_csi_driver().items, "csidrivers")
dump_resources(storage_v1.list_csi_node().items, "csinodes")

# Dump Kubelet Plugins Allocatable Resources
kubelet_plugins_allocatable = [node.status.allocatable for node in nodes]
kubelet_plugins_json = json.dumps(kubelet_plugins_allocatable, indent=4)
with open(os.path.join(output_dir, f"kubelet_plugins_{timestamp}.txt"), "w") as file:
    file.write(kubelet_plugins_json)

# Print completion message
print(f"Kubernetes state and node information have been dumped into {output_dir}/")

