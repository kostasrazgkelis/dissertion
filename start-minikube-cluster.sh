#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

docker compose down

docker system prune -a -f

docker build --no-cache -t konstantinosrazgkelisonelity/flask_backend:latest ./containers/flask-container

docker push konstantinosrazgkelisonelity/flask_backend:latest

docker build --no-cache -t konstantinosrazgkelisonelity/ts_frontend:latest ./containers/front

docker push konstantinosrazgkelisonelity/ts_frontend:latest


# Variables for deployments and services
FLASK_DEPLOYMENT="flask-backend"
FRONTEND_DEPLOYMENT="frontend"
FRONTEND_SERVICE="frontend"

# Delete existing deployments and services
echo "Deleting existing deployments and services..."
kubectl delete deployment $FLASK_DEPLOYMENT || true
kubectl delete service $FLASK_DEPLOYMENT || true
kubectl delete deployment $FRONTEND_DEPLOYMENT || true
kubectl delete service $FRONTEND_SERVICE || true

# Apply new configurations
echo "Applying new configurations..."
kubectl apply -f ./kubernetes/deployments/flask-deployment.yaml
kubectl apply -f ./kubernetes/deployments/front-deployment.yaml

# Wait for the frontend pod to be up and running
echo "Waiting for frontend pod to be ready..."
kubectl wait --for=condition=ready pod -l app=$FRONTEND_DEPLOYMENT --timeout=60s

# Get the frontend pod name
FRONTEND_POD=$(kubectl get pods -l app=$FRONTEND_DEPLOYMENT -o jsonpath="{.items[0].metadata.name}")

# Check if pod name was found
if [ -z "$FRONTEND_POD" ]; then
    echo "Error: Frontend pod not found."
    exit 1
fi

# Port forward to the frontend pod
echo "Port forwarding to frontend pod: $FRONTEND_POD"
kubectl port-forward "$FRONTEND_POD" 80:80

# minikube service flask-backend --url
# minikube service frontend-service --url
