# Kubernetes Cluster Architecture

## Production Cluster: k8s-prod-us-east-1

### Node Specifications
- **Master nodes**: 3x m5.xlarge (4 vCPU, 16GB RAM)
- **Worker nodes**: 6x m5.2xlarge (8 vCPU, 32GB RAM)
- **Kubernetes version**: 1.28.4
- **Container runtime**: containerd 1.7.2

### Key Components
- **CNI**: Calico for network policies
- **Ingress**: NGINX Ingress Controller
- **Storage**: EBS CSI driver with gp3 volumes
- **Monitoring**: Prometheus + Grafana stack

### Access & Authentication
```bash
# Connect to cluster
aws eks update-kubeconfig --region us-east-1 --name k8s-prod

# Verify access
kubectl auth can-i get pods --namespace production
Common Operations
Scale deployment: kubectl scale deployment api --replicas=5
Check node resources: kubectl top nodes
Drain node for maintenance: kubectl drain node-name --ignore-daemonsets