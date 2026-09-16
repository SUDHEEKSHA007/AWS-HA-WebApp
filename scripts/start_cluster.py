"""
Cluster Orchestrator & Auto Scaling Group Simulator
---------------------------------------------------
Starts our High Availability Cloud Architecture locally:
- Web Instance A (Port 5001, AZ-A: us-east-1a)
- Web Instance B (Port 5002, AZ-B: us-east-1b)
- Application Load Balancer (Port 8080, routes between A & B)
- Auto Scaling Health Watcher (restarts any crashed instance automatically)
"""

import subprocess
import sys
import os
import time
import signal

PYTHON_EXE = sys.executable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

processes = {}


def start_instance(name, port, zone):
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["INSTANCE_ID"] = name
    env["AVAILABILITY_ZONE"] = zone

    p = subprocess.Popen(
        [PYTHON_EXE, os.path.join(BASE_DIR, "app", "app.py")],
        env=env,
        cwd=BASE_DIR,
    )
    processes[port] = {"name": name, "zone": zone, "process": p}
    print(f" [ASG] Started EC2 Instance: {name} on port {port} ({zone}) [PID: {p.pid}]")
    return p


def main():
    print("=" * 70)
    print(" HIGH AVAILABILITY CLOUD CLUSTER STARTING (LOCAL SIMULATION)")
    print("=" * 70)

    # Launch Instance A (AZ-A)
    start_instance("ec2-instance-az-a-01", 5001, "us-east-1a")

    # Launch Instance B (AZ-B)
    start_instance("ec2-instance-az-b-02", 5002, "us-east-1b")

    # Launch Application Load Balancer
    alb_process = subprocess.Popen(
        [PYTHON_EXE, os.path.join(BASE_DIR, "scripts", "load_balancer.py")],
        cwd=BASE_DIR,
    )
    print(f" [ALB] Started Application Load Balancer on port 8080 [PID: {alb_process.pid}]")
    print("=" * 70)
    print(" * Access the Application Load Balancer URL: http://127.0.0.1:8080")
    print(" * Directly access Instance A: http://127.0.0.1:5001")
    print(" * Directly access Instance B: http://127.0.0.1:5002")
    print(" * Press CTRL+C in this terminal to shut down the entire cluster.")
    print("=" * 70)

    try:
        while True:
            time.sleep(3)
            # Auto Scaling Self-Healing Loop
            for port, info in list(processes.items()):
                poll = info["process"].poll()
                if poll is not None:
                    print(f"\n [ASG ALERT] Instance {info['name']} (port {port}) terminated with code {poll}!")
                    print(f" [ASG RECOVERY] Auto Scaling Group launching replacement instance...")
                    start_instance(info["name"], port, info["zone"])

            if alb_process.poll() is not None:
                print(" [ALERT] Load Balancer terminated. Shutting down cluster.")
                break
    except KeyboardInterrupt:
        print("\n [SHUTDOWN] Terminating all cluster instances and Load Balancer...")
        for port, info in processes.items():
            info["process"].terminate()
        alb_process.terminate()
        print(" [SHUTDOWN] Cluster gracefully stopped.")


if __name__ == "__main__":
    main()
