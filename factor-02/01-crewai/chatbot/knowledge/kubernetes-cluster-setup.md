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
```

### Scaling
- **Cluster Autoscaler**: Automatically adjusts the number of nodes in the cluster based on resource demands.
  #### Configuration:
  1. Install the Cluster Autoscaler using the official Helm chart or YAML manifests:
     ```bash
     kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/cluster-autoscaler-<version>/examples/cluster-autoscaler-autodiscover.yaml
     ```
  2. Annotate your node group with the following tags to enable autoscaling:
     ```bash
     kubectl annotate nodegroup <node-group-name> cluster-autoscaler.kubernetes.io/scale-down-disabled=false
     ```
  3. Ensure IAM roles or permissions are set for the Cluster Autoscaler to interact with your cloud provider.

- **Horizontal Pod Autoscaler (HPA)**: Adjusts the number of pod replicas based on CPU/memory utilization or custom metrics.
  #### Configuration:
  1. Enable the Metrics Server in your cluster:
     ```bash
     kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
     ```
  2. Create an HPA resource for your deployment:
     ```bash
     kubectl autoscale deployment <deployment-name> --cpu-percent=50 --min=1 --max=10
     ```
  3. Verify the HPA status:
     ```bash
     kubectl get hpa
     ```

- **Vertical Pod Autoscaler (VPA)**: Adjusts resource requests and limits for containers in a pod to optimize resource usage.
  #### Configuration:
  1. Install the Vertical Pod Autoscaler components:
     ```bash
     kubectl apply -f https://github.com/kubernetes/autoscaler/releases/latest/download/vertical-pod-autoscaler.yaml
     ```
  2. Create a VPA resource for your deployment:
     ```yaml
     apiVersion: autoscaling.k8s.io/v1
     kind: VerticalPodAutoscaler
     metadata:
       name: <deployment-name>
     spec:
       targetRef:
         apiVersion: "apps/v1"
         kind: "Deployment"
         name: "<deployment-name>"
       updatePolicy:
         updateMode: "Auto"
     ```
  3. Apply the VPA configuration:
     ```bash
     kubectl apply -f vpa-config.yaml
     ```