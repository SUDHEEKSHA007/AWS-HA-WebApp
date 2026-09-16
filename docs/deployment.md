# Deployment Guide

This guide outlines both the local cluster deployment and automated cloud provisioning.

## 1. Local High-Availability Cluster Deployment

### Prerequisites
- Python 3.10+
- Virtual Environment activated

### Steps
```powershell
# 1. Activate environment
.\.venv\Scripts\Activate.ps1

# 2. Run automated test suite
pytest -v

# 3. Launch the high-availability cluster
python scripts/start_cluster.py
```

### Accessing Endpoints
- **Application Load Balancer**: `http://127.0.0.1:8080`
- **Instance A (AZ-A)**: `http://127.0.0.1:5001`
- **Instance B (AZ-B)**: `http://127.0.0.1:5002`
- **Health Check Endpoint**: `http://127.0.0.1:8080/health`

---

## 2. Cloud Infrastructure Deployment (Terraform)

### Prerequisites
- AWS CLI configured with least-privilege IAM credentials
- Terraform CLI >= 1.5.0

### Steps
```bash
cd infrastructure/terraform

# Initialize provider plugins
terraform init

# Validate syntax
terraform fmt
terraform validate

# Review plan
terraform plan

# Provision cloud resources
terraform apply -auto-approve
```

### Teardown
```bash
terraform destroy -auto-approve
```
