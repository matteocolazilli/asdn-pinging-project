import os
import time
import socket
import json
import logging
from datetime import datetime
from ping3 import ping
from prometheus_client import start_http_server, Counter, Gauge
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Configure logging to output JSON
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# Override the default formatter to output JSON
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": os.environ.get("HOSTNAME", "unknown"), # Use hostname as service identifier
            "component": "pinger-a"
        }
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)
        return json.dumps(log_record)

for handler in logger.handlers:
    handler.setFormatter(JsonFormatter())

TARGET_SERVICE = os.environ.get("TARGET_SERVICE", "pinger-b-service.ping-app.svc.cluster.local")

# Prometheus Metrics
PING_SUCCESS_TOTAL = Counter('pinger_a_ping_success_total', 'Total successful pings from Pinger-A', ['target_service'])
PING_FAILURE_TOTAL = Counter('pinger_a_ping_failure_total', 'Total failed pings from Pinger-A', ['target_service'])
PING_LATENCY_MS = Gauge('pinger_a_ping_latency_ms', 'Latency of pings from Pinger-A in milliseconds', ['target_service'])

def ping_service():
    while True:
        log_data = {
            "target_service": TARGET_SERVICE
        }
        try:
            resolved_ip = socket.gethostbyname(TARGET_SERVICE)
            log_data["resolved_ip"] = resolved_ip
            latency = ping(resolved_ip, timeout=2)
            
            if latency is not None:
                latency_ms = latency * 1000
                PING_SUCCESS_TOTAL.labels(target_service=TARGET_SERVICE).inc()
                PING_LATENCY_MS.labels(target_service=TARGET_SERVICE).set(latency_ms)
                log_data["status"] = "success"
                log_data["latency_ms"] = f"{latency_ms:.2f}"
                logger.info(f"Pinger-A pinged {TARGET_SERVICE} ({resolved_ip}): Success, latency={latency_ms:.2f} ms", extra={'extra_data': log_data})
            else:
                PING_FAILURE_TOTAL.labels(target_service=TARGET_SERVICE).inc()
                log_data["status"] = "timeout"
                logger.warning(f"Pinger-A pinged {TARGET_SERVICE} ({resolved_ip}): Timeout/No response", extra={'extra_data': log_data})
        except Exception as e:
            PING_FAILURE_TOTAL.labels(target_service=TARGET_SERVICE).inc()
            log_data["status"] = "error"
            log_data["error"] = str(e)
            logger.error(f"Pinger-A failed to ping {TARGET_SERVICE}: {e}", extra={'extra_data': log_data})
        time.sleep(5)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/healthz':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')

def run_health_check_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    logger.info("Starting health check server on port 8080")
    httpd.serve_forever()

if __name__ == "__main__":
    logger.info("Starting Pinger-A application")
    # Start up the Prometheus client
    start_http_server(8000) # Prometheus metrics on port 8000
    logger.info("Prometheus metrics exposed on port 8000")

    # Start health check server in a separate thread
    health_thread = threading.Thread(target=run_health_check_server)
    health_thread.daemon = True
    health_thread.start()

    # Start pinging service
    ping_service()