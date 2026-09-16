# Terraform Infrastructure as Code (AWS HA WebApp)

This directory defines the entire AWS cloud architecture as declarative code using HashiCorp Terraform.

## Architecture Provisioned

- **VPC**: Isolated custom network (`10.0.0.0/16`)
- **Subnets**: 2 Public Subnets across 2 Availability Zones (`us-east-1a` & `us-east-1b`)
- **Internet Gateway & Route Tables**: Direct public routing
- **Security Groups**:
  - ALB Security Group: Inbound Port 80 from `0.0.0.0/0`
  - EC2 Security Group: Inbound Port 5000 strictly restricted to ALB Security Group
- **Application Load Balancer**: Layer-7 HTTP reverse proxy with `/health` health checks
- **Target Group**: Dynamic target pool on port 5000
- **Launch Template**: Automated cloud-init User Data script configuring Python, Flask, and systemd
- **Auto Scaling Group**: Multi-AZ pool (Min=2, Desired=2, Max=4) with ELB health checks
- **Amazon CloudWatch**: Metric Alarm alerting on `HealthyHostCount < 2`

## Usage Commands

### 1. Initialize
Downloads the AWS provider plugin:
```bash
terraform init
```

### 2. Format & Validate
Ensures clean syntax and validates resource configuration:
```bash
terraform fmt
terraform validate
```

### 3. Plan
Generates an execution plan showing exactly what resources will be created:
```bash
terraform plan
```

### 4. Apply
Provisions the complete cloud infrastructure on AWS:
```bash
terraform apply -auto-approve
```

### 5. Destroy
Tears down all provisioned resources to guarantee $0 cost:
```bash
terraform destroy -auto-approve
```

## Security Note

- The `.gitignore` file automatically excludes `*.tfstate`, `*.tfstate.backup`, and `.terraform/`.
- Never commit Terraform state files to source control, as they can contain sensitive resource attributes.
