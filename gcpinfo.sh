#!/bin/bash

# Fetching the current GCP project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "Project ID could not be determined. Ensure you have set the project in gcloud."
    exit 1
fi
echo "Project ID: $PROJECT_ID"

# Getting the list of clusters in the project
CLUSTERS=$(gcloud container clusters list --project "$PROJECT_ID" --format "value(name, location)")

# Check if any clusters are available
if [ -z "$CLUSTERS" ]; then
    echo "No clusters found in project $PROJECT_ID."
    exit 1
fi

# If there are multiple clusters, you might want to select one
# For simplicity, this script assumes the first one is the target
CLUSTER_INFO=($(echo $CLUSTERS | head -n1))

CLUSTER_NAME=${CLUSTER_INFO[0]}
CLUSTER_ZONE=${CLUSTER_INFO[1]}

# Outputting selected cluster
echo "Selected Cluster: $CLUSTER_NAME"
echo "Cluster Zone: $CLUSTER_ZONE"

# Getting credentials for the selected cluster
gcloud container clusters get-credentials "$CLUSTER_NAME" --zone "$CLUSTER_ZONE" --project "$PROJECT_ID"
