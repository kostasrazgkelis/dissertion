#!/bin/bash

kubectl delete statefulset --all -n spark-cluster
kubectl delete deployments --all -n spark-cluster
kubectl delete statefulset --all -n spark-cluster
kubectl delete service --all -n spark-cluster
kubectl delete pvc --all -n spark-cluster     
kubectl delete namespace spark-cluster

kubectl apply -f .\kubernetes\namespaces\spark-cluster-namespace.yaml
kubectl apply -f .\kubernetes\deployments\spark-master.yaml
kubectl apply -f .\kubernetes\deployments\spark-worker.yaml
