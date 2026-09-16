# AWS Highly Available Web Application

A production-grade, highly available web application deployed on AWS using Terraform, Application Load Balancers, Auto Scaling Groups across multiple Availability Zones, CloudWatch monitoring, and GitHub Actions CI/CD.

## Architecture Overview

Traffic flows from public users into an Application Load Balancer spanning multiple Availability Zones, which routes requests across self-healing EC2 instances running a Python Flask application.

## Directory Structure

```text
AWS-HA-WebApp/
│
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── tests/
│       ├── __init__.py
│       └── test_app.py
│
├── infrastructure/
│   └── terraform/
│
├── scripts/
│
├── .github/
│   └── workflows/
│
├── docs/
│
├── .gitignore
└── README.md
```
