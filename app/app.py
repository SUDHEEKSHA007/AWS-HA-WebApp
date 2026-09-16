import os
import socket
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    # Fetch identity: reads INSTANCE_ID (e.g., ec2-az-a-instance-1) or defaults to system hostname
    instance_id = os.environ.get(
        "INSTANCE_ID", os.environ.get("HOSTNAME", socket.gethostname())
    )
    availability_zone = os.environ.get("AVAILABILITY_ZONE", "us-east-1a (simulated)")

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AWS Highly Available Web Application</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #0f172a;
                color: #f8fafc;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background-color: #1e293b;
                padding: 2.5rem;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.5);
                border: 1px solid #334155;
                text-align: center;
                max-width: 550px;
            }}
            h1 {{
                color: #38bdf8;
                margin-bottom: 0.5rem;
            }}
            .badge {{
                display: inline-block;
                background-color: #065f46;
                color: #34d399;
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-weight: bold;
                font-size: 0.875rem;
                margin-bottom: 1.5rem;
            }}
            .server-box {{
                background-color: #0f172a;
                border: 1px solid #475569;
                padding: 1rem;
                border-radius: 8px;
                font-family: monospace;
                font-size: 1.1rem;
                color: #facc15;
                word-break: break-all;
                margin-bottom: 1rem;
            }}
            .zone-badge {{
                display: inline-block;
                background-color: #1e1b4b;
                color: #a5b4fc;
                padding: 0.2rem 0.6rem;
                border-radius: 6px;
                font-size: 0.85rem;
                border: 1px solid #4338ca;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>AWS Highly Available Web App</h1>
            <div class="badge">Application Status: Online (HTTP 200)</div>
            <p>Served by backend instance:</p>
            <div class="server-box">{instance_id}</div>
            <p>Availability Zone: <span class="zone-badge">{availability_zone}</span></p>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 1.5rem;">
                When behind the Application Load Balancer, refresh to observe round-robin routing across instances and zones.
            </p>
        </div>
    </body>
    </html>
    """


@app.route("/health")
def health():
    return "healthy", 200


if __name__ == "__main__":
    # Support dynamic port binding via PORT env var (default to 5000)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

