import json
import os
import datetime
from kubernetes import client, config

# Load Kubernetes config
config.load_kube_config()

# Kubernetes API clients
v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()

# Initialize the output directory with a timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
output_dir = f"k8s_dump_{timestamp}"
os.makedirs(output_dir, exist_ok=True)

# Dynamically determine the API Server
api_server = None
try:
    kubernetes_service = v1.read_namespaced_service("kubernetes", "default")
    ip = kubernetes_service.spec.cluster_ip
    port = kubernetes_service.spec.ports[0].port
    api_server = f"{ip}:{port}"
except Exception as e:
    print(f"Error getting API Server details: {e}")

# Get list of all namespaces
namespaces = v1.list_namespace().items

# Loop through each namespace
for namespace_obj in namespaces:
    namespace = namespace_obj.metadata.name
    ns_dir = os.path.join(output_dir, namespace)
    os.makedirs(ns_dir, exist_ok=True)

    pods = v1.list_namespaced_pod(namespace).items

    for pod in pods:
        pod_name = pod.metadata.name
        pod_dir = os.path.join(ns_dir, pod_name)
        os.makedirs(pod_dir, exist_ok=True)

        # Finds the audit log path
        kube_apiserver_pods = v1.list_namespaced_pod("kube-system", field_selector="metadata.name=kube-apiserver").items
        for kap in kube_apiserver_pods:
            audit_log_paths = [arg for container in kap.spec.containers for arg in container.args if "--audit-log-path" in arg]
            with open(os.path.join(pod_dir, f'apiserver_audit_log_path_{timestamp}.txt'), 'w') as file:
                file.writelines(audit_log_paths)

        # Get load balancers
        services = v1.list_service_for_all_namespaces(field_selector="spec.type=LoadBalancer").items
        load_balancers = [f"{svc.status.load_balancer.ingress[0].hostname}:{svc.spec.ports[0].port}" for svc in services if svc.status.load_balancer and svc.status.load_balancer.ingress]
        with open(os.path.join(ns_dir, f'load_balancers_{timestamp}.txt'), 'w') as file:
            file.write("\n".join(load_balancers))

        # Get external IPs of all nodes
        nodes = v1.list_node().items
        external_ips = [address.address for node in nodes for address in node.status.addresses if address.type == "ExternalIP"]
        with open(os.path.join(ns_dir, f'external_node_ips_{timestamp}.txt'), 'w') as file:
            file.write("\n".join(external_ips))

        # Get Kubernetes API server config
        # Assuming pod_name refers to an API server pod
        # Note: This might need adjustments based on your specific cluster setup
        if 'kube-apiserver' in pod_name:
            apiserver_config = v1.read_namespaced_pod(pod_name, "kube-system")
            with open(os.path.join(ns_dir, f'apiserver_config_{timestamp}.txt'), 'w') as file:
                file.write(str(apiserver_config))

            # Get Kubernetes API server container args
            apiserver_args = [container.args for container in apiserver_config.spec.containers if container.name == "kube-apiserver"]
            with open(os.path.join(ns_dir, f'apiserver_container_args_{timestamp}.json'), 'w') as file:
                json.dump(apiserver_args, file)

# Uncomment only when ready for exfiltration; security concerns
# This part is omitted due to its sensitive nature

# Note: Some operations like extracting API server config may require adjustments based on your specific cluster setup.
