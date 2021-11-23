# MySQL Server Operator

MySQL Server Operator to manage Application registration on existing instances



[TOC]

## Installation

### Developers

```bash
python -m venv --prompt myop .venv
source .venv/bin/activate
pip install -r requirements.txt

PYTHONPATH=$(pwd)
kopf run -m myop --liveness=http://0.0.0.0:5000/healthz -A --standalone # --peering=mysql-operator
```

### Docker

```bash
docker build -t myop -f devops/Dockerfile .
```

### Kubernetes

```bash
# peering CRDs - used to start/pause operators
kubectl apply -f peering.yaml

# install operator with helm
# (eg with release/namespace set to mysql-operator-nonprod)
helm upgrade --install --create-namespace mysql-operator-nonprod devops/chart/ -n mysql-operator-nonprod

# check if pods are running
kubectl -n mysql-operator-nonprod get pod -w

# check peering status
kubectl get clusterkopfpeering mysql-operator -o yaml

# check admission configuration
kubectl get validatingwebhookconfigurations admission.mysql.bleuelab.ca -o yaml
```

## Usage

### Instances

An instance is an object that refer to an Axon Server. You can have multiple instances.

Eg:

```yaml
apiVersion: mysql.bleuelab.ca/v1
kind: Instance
metadata:
  name: shared-nonprod
spec:
  host: np-shared-sql.domain.tld
  port: 3306
  ssl: true
  user: admin@np-shared-sql.domain.tld
  pwd:
    hashicorpVault:
      addr: https://vault.domain.tld
      role: mysql-operator-nonprod
      auth: kubernetes-nonprod
      path: teams/devops/mysql/np-shared-sql/users/admin
      mount: bluecross
      field: pwd
```

```bash
kubectl apply -f instances.yaml

# Cluster-wide instances
kubectl get instance.mysql.bleuelab.ca
```

### Apps

An application object permit to register an application, set permissions and get credentials.

Eg:

```yaml
apiVersion: mysql.bleuelab.ca/v1
kind: App
metadata:
  name: test
spec:
  instance: shared-nonprod
```

Application will be registred with the kubernetes App object uid (metadata.uid).

```bash
kubectl -n myns apply -f apps.yaml

kubectl -n myns get app.mysql.bleuelab.ca
kubectl -n myns get all

# connection string is available in a secret created by the operator
# the secret is named with the app object name
kubectl -n myns get secret test -o yaml
# passord
kubectl -n myns get secret test -o json | jq -M -r .data.password | base64 -d
# username
kubectl -n myns get secret test -o json | jq -M -r .data.username | base64 -d
# url
kubectl -n myns get secret test -o json | jq -M -r .data.url | base64 -d
```



## Limitation

### Vault

`myop` **only** support HashiCorp Vault backend to get some secrets. It is using the `hashicorpVault` key.

Your vault needs to be integrated with kubernetes as the service account credential of the pod will be used to connect on it.

## TODO

