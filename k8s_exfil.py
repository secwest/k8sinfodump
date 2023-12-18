import argparse
import datetime
from kubernetes import client, config
from kubernetes.client.rest import ApiException

def parse_arguments():
    parser = argparse.ArgumentParser(description='Kubernetes Storage Setup for Cloud and On-Prem Environments')
    parser.add_argument('--env', choices=['AKS', 'EKS', 'GKE', 'OpenShift'], required=True, help='Environment type')
    return parser.parse_args()

def create_persistent_volume_claim(namespace, pvc_name, storage_class_name, storage_size):
    pvc_spec = client.V1PersistentVolumeClaimSpec(
        access_modes=["ReadWriteOnce"],
        resources=client.V1ResourceRequirements(requests={"storage": storage_size}),
        storage_class_name=storage_class_name
    )
    pvc = client.V1PersistentVolumeClaim(
        api_version="v1",
        kind="PersistentVolumeClaim",
        metadata=client.V1ObjectMeta(name=pvc_name),
        spec=pvc_spec
    )
    try:
        api_instance.create_namespaced_persistent_volume_claim(namespace, pvc)
        print(f"PersistentVolumeClaim {pvc_name} created in namespace {namespace}.")
    except ApiException as e:
        print(f"Exception when creating PersistentVolumeClaim: {e}")

def deploy_pod(namespace, pod_name, pvc_name, mount_path, image='busybox'):
    pod_spec = client.V1PodSpec(
        containers=[client.V1Container(
            name="mypod",
            image=image,
            args=["sleep", "3600"],
            volume_mounts=[client.V1VolumeMount(mount_path=mount_path, name="mypvc")]
        )],
        volumes=[client.V1Volume(
            name="mypvc",
            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name)
        )]
    )
    pod = client.V1Pod(
        api_version="v1",
        kind="Pod",
        metadata=client.V1ObjectMeta(name=pod_name),
        spec=pod_spec
    )
    try:
        api_instance.create_namespaced_pod(namespace, pod)
        print(f"Pod {pod_name} deployed in namespace {namespace}.")
    except ApiException as e:
        print(f"Exception when creating Pod: {e}")

def main():
    args = parse_arguments()
    env = args.env

    # Load Kubernetes config
    config.load_kube_config()
    global api_instance
    api_instance = client.CoreV1Api()

    # Environment-specific configurations
    namespace = "default"
    pvc_name = "mypvc"
    storage_size = "1Gi"
    mount_path = "/mnt/data"

    if env == 'AKS':
        storage_class_name = "azurefile"  # Replace with your Azure storage class
    elif env == 'EKS':
        storage_class_name = "gp2"  # Replace with your AWS storage class
    elif env == 'GKE':
        storage_class_name = "standard"  # Replace with your GCP storage class
    elif env == 'OpenShift':
        storage_class_name = "nfs"  # Replace with your OpenShift storage class

    pod_name = f"test-pod-{env.lower()}"
    create_persistent_volume_claim(namespace, pvc_name, storage_class_name, storage_size)
    deploy_pod(namespace, pod_name, pvc_name, mount_path)

if __name__ == "__main__":
    main()
