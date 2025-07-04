kind delete cluster
kind create cluster --config kind/kind-config.yaml
kubectl apply -f k8s/app/

echo "Waiting for all pods to be ready..."
kubectl wait --for=condition=Ready pods --all -n ping-app --timeout=300s



#echo $RUNNER_TOKEN 
#kubectl create secret generic github-runner-secret --namespace=github-runner --from-literal=runner-token='' 
