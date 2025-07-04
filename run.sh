kind delete cluster
kind create cluster --config kind/kind-config.yaml
kubectl apply -f k8s/app/

kubectl apply -f k8s/runner/namespace.yaml
kubectl apply -f k8s/runner/rbac.yaml    

kubectl create secret generic github-runner-secret --namespace=github-runner --from-literal=runner-token='' # <-- inserire il token del runner qui

export MACHINE_ID="matteo" #<-- da cambiare in base alla macchina
cat k8s/runner/runner-deployment.yaml | sed "s/MACHINE_IDENTIFIER/$MACHINE_ID/g" | kubectl apply -f -

