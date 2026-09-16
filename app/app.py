from flask import Flask
import socket

app = Flask(__name__)


@app.route("/")
def home():
    hostname = socket.gethostname()
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
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>AWS Highly Available Web App</h1>
            <div class="badge">Application Status: Online (HTTP 200)</div>
            <p>This web application is being served by backend instance:</p>
            <div class="server-box">{hostname}</div>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 1.5rem;">
                When behind an AWS Application Load Balancer, refresh to see load balancing across Availability Zones.
            </p>
        </div>
    </body>
    </html>
    """


@app.route("/health")
def health():
    return "healthy", 200


if __name__ == "__main__":
    # 0.0.0.0 binds to all available network interfaces
    # Port 5000 is our application listening port
    app.run(host="0.0.0.0", port=5000)
