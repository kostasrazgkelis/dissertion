kubectl delete deployment flask-backend

kubectl delete service flask-backend

kubectl apply -f ./deployments/basic-deployment.yaml






helm unistall spark-cluster -n spark-cluster

 helm install spark-cluster bitnami/spark -f  .\kubernetes\deployments\spark-cluster-helm.yaml --namespace spark-cluster
 
kubectl port-forward --namespace spark-cluster svc/spark-cluster-master-svc 80:80 7077:7077



