from flask import Flask
import socket

app = Flask(__name__)


@app.route("/")
def home():
    hostname = socket.gethostname()

    return f"""
    <html>
        <head>
            <title>AWS HA Web Application</title>
        </head>
        <body>
            <h1>AWS Highly Available Web Application</h1>
            <p>Application is running successfully.</p>
            <p>Server: {hostname}</p>
        </body>
    </html>
    """


@app.route("/health")
def health():
    return "healthy", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)