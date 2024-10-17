#!/bin/bash

# helm uninstall spark-cluster --namespace spark-cluster

# kubectl delete all --all --all-namespaces
# kubectl delete pvc --all --all-namespaces
# kubectl delete pv --all
# kubectl delete rolebinding --all --all-namespaces
# kubectl delete serviceaccount --all --all-namespaces

minikube stop
minikube delete

docker system prune -a -f
docker volume prune -f


minikube start --cpus 6 --memory 11000 --disk-size 10g


kubectl apply -f .\kubernetes\namespaces\spark-cluster-namespace.yaml

kubectl apply -f .\kubernetes\storage\persistent-volumes\spark-cluster-pv.yaml

kubectl apply -f .\kubernetes\storage\persistent-volume-claims\spark-cluster-pvc.yaml

kubectl apply -f .\kubernetes\deployments\flask-deployment.yaml

# Wait for the Flask deployment to be ready
kubectl wait --for=condition=available --timeout=600s deployment/flask-backend -n spark-cluster

# Get the Flask container name and namespace
$FLASK_POD = kubectl get pods -l app=flask-backend -o jsonpath="{.items[0].metadata.name}" -n spark-cluster

# Copy the file to the Flask container
kubectl cp .\data\alice_in_wonderland.txt spark-cluster/${FLASK_POD}:/data/alice_in_wonderland.txt

kubectl port-forward $FLASK_POD 80:8080 -n spark-cluster
#

# helm install spark-cluster bitnami/spark -f .\kubernetes\deployments\spark-cluster-helm.yaml --namespace spark-cluster

