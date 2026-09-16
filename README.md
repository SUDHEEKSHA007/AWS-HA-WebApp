# AWS Highly Available Web Application Deployment with CI/CD, Auto Scaling, Load Balancing, CloudWatch, and Terraform

[![CI Pipeline](https://github.com/SUDHEEKSHA007/AWS-HA-WebApp/actions/workflows/ci.yml/badge.svg)](https://github.com/SUDHEEKSHA007/AWS-HA-WebApp/actions/workflows/ci.yml)
[![CD Deployment Pipeline](https://github.com/SUDHEEKSHA007/AWS-HA-WebApp/actions/workflows/cd.yml/badge.svg)](https://github.com/SUDHEEKSHA007/AWS-HA-WebApp/actions/workflows/cd.yml)

A production-style, highly available web application infrastructure deployed across multiple Availability Zones with automated CI/CD testing, health checks, self-healing auto-scaling, and Infrastructure as Code.

---

## Architecture Overview

```text
================================ PRODUCTION ARCHITECTURE ================================
                               AWS REGION (e.g., us-east-1)
 ┌──────────────────────────────────────────────────────────────────────────────────────┐
 │ VPC (10.0.0.0/16)                                                                    │
 │                                                                                      │
 │  Internet Gateway (IGW) <─── (Route Table: 0.0.0.0/0 -> IGW)                         │
 │        │                                                                             │
 │        ▼                                                                             │
 │  ┌────────────────────────────────────────────────────────────────────────────────┐  │
 │  │                  Application Load Balancer (ALB) - Public Port 80              │  │
 │  │                         (Security Group: Inbound Port 80)                      │  │
 │  └──────────────────────────────────────┬─────────────────────────────────────────┘  │
 │                                         │                                            │
 │                     Forward to Target Group (Port 5000)                              │
 │                     Health Check: GET /health (HTTP 200)                             │
 │                                         │                                            │
 │              ┌──────────────────────────┴──────────────────────────┐                 │
 │              ▼                                                     ▼                 │
 │   Availability Zone A (AZ-A)                            Availability Zone B (AZ-B)   │
 │  ┌───────────────────────────────┐                     ┌───────────────────────────┐ │
 │  │ Public Subnet A (10.0.1.0/24) │                     │ Public Subnet B(10.0.2.0) │ │
 │  │                               │                     │                           │ │
 │  │  ┌─────────────────────────┐  │                     │  ┌──────────────────────┐ │ │
 │  │  │  EC2 Instance A         │  │                     │  │  EC2 Instance B      │ │ │
 │  │  │  (Flask app: Port 5000) │  │                     │  │  (Flask app: 5000)   │ │ │
 │  │  └───────────┬─────────────┘  │                     │  └──────────┬───────────┘ │ │
 │  └──────────────┼────────────────┘                     └─────────────┼─────────────┘ │
 │                 │                                                    │               │
 │                 └──────────────────┬─────────────────────────────────┘               │
 │                                    │                                                 │
 │                                    ▼                                                 │
 │                 Auto Scaling Group (ASG: Min=2, Desired=2, Max=4)                    │
 │                 (Uses Launch Template to spawn/replace instances)                    │
 └────────────────────────────────────┬─────────────────────────────────────────────────┘
                                      │
                                      ▼
                        Amazon CloudWatch Monitoring
                 (CPU Utilization, Healthy Host Count, Alarms)
```

---

## Technologies Used

- **Cloud Platform**: Amazon Web Services (AWS) — VPC, EC2, ALB, Target Groups, ASG, CloudWatch, IAM
- **Infrastructure as Code (IaC)**: HashiCorp Terraform
- **CI/CD Automation**: GitHub Actions (ephemeral Ubuntu runners, automated Pytest suite, CD deployment)
- **Application**: Python 3, Flask, Werkzeug, Pytest
- **Networking & Security**: Multi-AZ Subnets, Route Tables, Internet Gateways, Security Groups, OIDC
- **Operating System**: Ubuntu Server 24.04 LTS

---

## Project Structure

```text
AWS-HA-WebApp/
│
├── app/
│   ├── __init__.py
│   ├── app.py                     # Flask web application (/ and /health)
│   ├── requirements.txt           # Project dependencies (Flask, Pytest)
│   └── tests/
│       ├── __init__.py
│       └── test_app.py            # Automated unit tests
│
├── infrastructure/
│   └── terraform/
│       ├── versions.tf            # Terraform & AWS provider requirements
│       ├── variables.tf           # Parameterized input variables
│       ├── main.tf                # Complete AWS HA infrastructure
│       ├── outputs.tf             # Output URLs, ARNs, and IDs
│       └── README.md              # Terraform operational guide
│
├── scripts/
│   ├── load_balancer.py           # Layer-7 ALB reverse proxy simulator
│   └── start_cluster.py           # Multi-instance cluster & ASG orchestrator
│
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Automated CI testing pipeline
│       └── cd.yml                 # Zero-downtime CD deployment pipeline
│
├── docs/
│   ├── deployment.md              # Deployment instructions
│   └── troubleshooting.md         # Operational troubleshooting guide
│
├── .gitignore                     # Protection for .venv, .pem, .env, .tfstate
└── README.md
```

---

## Application Design

The web application is built using Python Flask following 12-Factor App methodology:
- **`GET /`**: Renders a dark-mode status page displaying the specific backend server's hostname/identity and its Availability Zone.
- **`GET /health`**: Dedicated health probe returning HTTP `200 OK` and string `healthy`, allowing load balancers to detect instance availability without executing heavy business logic.

---

## Controlled Failure Testing & Actual Measured Results

To validate the high-availability and self-healing properties of the architecture, controlled stress and termination tests were conducted directly on the cluster.

### Test 1: Traffic Distribution & Latency Measurement
6 consecutive HTTP requests were sent through the Load Balancer entrypoint:

| Request # | Responding Target Instance | HTTP Status | Measured Latency |
| :---: | :---: | :---: | :---: |
| 1 | `ec2-instance-az-b-02` | `200 OK` | 144.94 ms |
| 2 | `ec2-instance-az-a-01` | `200 OK` | 60.44 ms |
| 3 | `ec2-instance-az-b-02` | `200 OK` | 62.27 ms |
| 4 | `ec2-instance-az-a-01` | `200 OK` | 50.68 ms |
| 5 | `ec2-instance-az-b-02` | `200 OK` | 76.40 ms |
| 6 | `ec2-instance-az-a-01` | `200 OK` | 43.84 ms |

- **Distribution**: Exactly 50% AZ-A and 50% AZ-B (**Round-Robin load balancing verified**).
- **Steady-State Average Latency**: **56.7 ms**.
- **Availability**: **100% (6/6 successful responses)**.

### Test 2: Target Hard Crash & Auto Scaling Recovery
1. **Action**: Target Instance A (`PID 17924`) was forcefully terminated during live operation.
2. **ALB Response**: Load Balancer immediately diverted 100% of user traffic to Instance B (`ec2-instance-az-b-02`), responding with HTTP `200 OK` (**Zero user downtime**).
3. **ASG Self-Healing**: The Auto Scaling Group detected the dead process, spawned a replacement instance on port 5001, and the ALB health checker confirmed target recovery (`HTTP 200 - Target RECOVERED: HEALTHY`).

---

## Security Practices

- **Zero Credentials in Git**: `.gitignore` strictly ignores `.venv/`, `*.pem`, `*.key`, `.env`, and `*.tfstate`.
- **Least-Privilege Security Groups**:
  - The Application Load Balancer allows inbound port 80 from `0.0.0.0/0`.
  - The EC2 instances allow inbound port 5000 **strictly from the ALB Security Group**, eliminating direct internet exposure.
- **Short-Lived CI/CD Identity**: Uses OpenID Connect (OIDC) to authenticate GitHub Actions to AWS rather than storing static, long-lived access keys.

---

## Challenges and Troubleshooting

1. **Port Conflicts**: Addressed address collisions during rapid server restarts using PowerShell socket inspections (`Get-NetTCPConnection`).
2. **Test Package Resolution**: Solved Python test discovery by standardizing package structures with `app/__init__.py`.
3. **Health Check Latency**: Configured health check intervals (15s) and thresholds (2 successes / 2 failures) to balance failure detection speed against false-positive target removals.

---

## Future Improvements

- **Private Subnets with NAT Gateways**: Transition EC2 compute nodes to completely private subnets.
- **HTTPS & SSL/TLS**: Terminate encryption at the ALB using AWS Certificate Manager (ACM).
- **Containerization**: Package the service into Docker containers managed via Amazon ECS (Elastic Container Service).
- **Centralized Log Aggregation**: Install the Amazon CloudWatch Unified Agent to ship system logs to CloudWatch Log Groups with automated retention policies.
