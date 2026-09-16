# Troubleshooting Guide

Common issues encountered during development, testing, and deployment, along with root-cause analysis and remediation steps.

---

## 1. Port Conflicts (WinError 10048 / Address Already in Use)
- **Symptom**: `OSError: [WinError 10048] Only one usage of each socket address is normally permitted`
- **Root Cause**: A previous background process crashed or was not terminated cleanly, leaving port 8080, 5001, or 5002 open.
- **Resolution**:
  ```powershell
  # Find process by port
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue).OwningProcess | Stop-Process -Force
  ```

---

## 2. Target Group Unhealthy in Load Balancer
- **Symptom**: Load Balancer logs `502 Bad Gateway (0 healthy targets)` or `Target marked UNHEALTHY`.
- **Root Cause**:
  1. The backend application process terminated or is not listening on the target port.
  2. The health check path does not match the application route (`/health`).
  3. Security Group rules block traffic between the Load Balancer and the backend instance.
- **Resolution**:
  - Test the target directly: `curl http://127.0.0.1:5001/health`
  - Verify Security Group rules allow port 5000 from the ALB Security Group.

---

## 3. GitHub Actions CI Failure
- **Symptom**: CI workflow shows Red (Failed) on step `Run Pytest Suite`.
- **Root Cause**:
  1. A newly introduced test failed assertions.
  2. Missing package in `app/requirements.txt`.
  3. Case sensitivity differences between Windows and Ubuntu runner paths.
- **Resolution**:
  - Run `pytest -v` locally before committing.
  - Verify exact lowercase casing on all imported modules.

---

## 4. SSH Connection Timed Out to EC2
- **Symptom**: `ssh: connect to host 54.x.x.x port 22: Connection timed out`
- **Root Cause**:
  1. Security Group does not allow TCP port 22.
  2. The client's public IP address changed (residential ISPs frequently rotate dynamic IPs).
  3. The EC2 instance is in a private subnet without a public route.
- **Resolution**:
  - In the AWS Console, edit the EC2 Security Group inbound rule for port 22 and select **"My IP"** again.
