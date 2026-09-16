"""
Application Load Balancer (ALB) Simulator
-----------------------------------------
Emulates an AWS Application Load Balancer (Layer 7):
- Listens on public port (8080)
- Manages a Target Group (Port 5001 & Port 5002)
- Performs automated background Health Checks (/health every 5s)
- Distributes traffic via Round-Robin across HEALTHY targets only
- Emulates AWS CloudWatch metrics (RequestCount, HealthyHostCount, UnhealthyHostCount)
"""

import http.server
import socketserver
import urllib.request
import urllib.error
import threading
import time
import uuid

# ALB Configuration
ALB_PORT = 8080
TARGETS = [
    {"name": "EC2-AZ-A (Port 5001)", "url": "http://127.0.0.1:5001", "healthy": True, "consecutive_fails": 0},
    {"name": "EC2-AZ-B (Port 5002)", "url": "http://127.0.0.1:5002", "healthy": True, "consecutive_fails": 0},
]

HEALTH_CHECK_PATH = "/health"
HEALTH_CHECK_INTERVAL = 5  # seconds
HEALTH_THRESHOLD = 2
UNHEALTHY_THRESHOLD = 2

# Round Robin Counter
target_index = 0
lock = threading.Lock()

# Metrics (CloudWatch emulation)
metrics = {
    "total_requests": 0,
    "healthy_hosts": len(TARGETS),
    "unhealthy_hosts": 0,
}


def health_checker():
    """Background thread performing periodic ALB health checks on target group."""
    global metrics
    while True:
        healthy_count = 0
        unhealthy_count = 0

        for target in TARGETS:
            check_url = f"{target['url']}{HEALTH_CHECK_PATH}"
            try:
                req = urllib.request.Request(check_url, headers={"User-Agent": "ELB-HealthChecker/2.0"})
                with urllib.request.urlopen(req, timeout=2) as response:
                    if response.status == 200:
                        if not target["healthy"]:
                            print(f"[ALB HEALTH CHECK] >>> Target RECOVERED: {target['name']} is now HEALTHY")
                        target["healthy"] = True
                        target["consecutive_fails"] = 0
                        healthy_count += 1
                    else:
                        raise Exception(f"HTTP {response.status}")
            except Exception:
                target["consecutive_fails"] += 1
                if target["consecutive_fails"] >= UNHEALTHY_THRESHOLD and target["healthy"]:
                    print(f"[ALB HEALTH CHECK] !!! Target FAILED: {target['name']} marked UNHEALTHY")
                    target["healthy"] = False
                if not target["healthy"]:
                    unhealthy_count += 1
                else:
                    healthy_count += 1

        with lock:
            metrics["healthy_hosts"] = healthy_count
            metrics["unhealthy_hosts"] = unhealthy_count

        time.sleep(HEALTH_CHECK_INTERVAL)


class ALBRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Custom logging format matching AWS ALB access logs
        return

    def do_GET(self):
        global target_index, metrics
        with lock:
            metrics["total_requests"] += 1
            healthy_targets = [t for t in TARGETS if t["healthy"]]

        if not healthy_targets:
            # 502 Bad Gateway if no targets are healthy (just like AWS ALB)
            self.send_response(502)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>502 Bad Gateway</h1><p>AWS ALB: No healthy upstream targets in target group.</p>")
            print(f"[ALB ACCESS LOG] GET {self.path} -> 502 Bad Gateway (0 healthy targets)")
            return

        # Round Robin selection
        with lock:
            target_index = (target_index + 1) % len(healthy_targets)
            chosen_target = healthy_targets[target_index]

        forward_url = f"{chosen_target['url']}{self.path}"
        trace_id = f"Root=1-{int(time.time())}-{uuid.uuid4().hex[:24]}"

        # Forward request to chosen backend EC2 instance
        try:
            req = urllib.request.Request(forward_url)
            req.add_header("X-Forwarded-For", self.client_address[0])
            req.add_header("X-Forwarded-Proto", "http")
            req.add_header("X-Amzn-Trace-Id", trace_id)

            start_time = time.time()
            with urllib.request.urlopen(req, timeout=5) as response:
                latency_ms = (time.time() - start_time) * 1000
                content = response.read()

                self.send_response(response.status)
                for header, val in response.getheaders():
                    if header.lower() not in ["transfer-encoding", "content-length"]:
                        self.send_header(header, val)
                self.send_header("X-Amzn-Trace-Id", trace_id)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)

                print(f"[ALB ACCESS LOG] GET {self.path} -> Routed to: {chosen_target['name']} | Status: {response.status} | Latency: {latency_ms:.1f}ms")

        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"502 Bad Gateway: {str(e)}".encode("utf-8"))
            print(f"[ALB ACCESS LOG] GET {self.path} -> FAILED forwarding to {chosen_target['name']}: {e}")


def run_alb():
    # Start background health checking thread
    health_thread = threading.Thread(target=health_checker, daemon=True)
    health_thread.start()

    print("=" * 70)
    print(" AWS APPLICATION LOAD BALANCER (ALB) SIMULATOR RUNNING")
    print("=" * 70)
    print(f" * Public Entrypoint URL: http://127.0.0.1:{ALB_PORT}")
    print(" * Target Group Targets:")
    for t in TARGETS:
        print(f"   - {t['name']} -> {t['url']}")
    print(f" * Health Check Path   : {HEALTH_CHECK_PATH}")
    print(f" * Health Check Interval: {HEALTH_CHECK_INTERVAL} seconds")
    print("=" * 70)

    server = socketserver.ThreadingTCPServer(("0.0.0.0", ALB_PORT), ALBRequestHandler)
    server.allow_reuse_address = True
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Load Balancer...")
        server.server_close()


if __name__ == "__main__":
    run_alb()
