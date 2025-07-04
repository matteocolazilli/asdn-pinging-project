import os
import time
import socket
from ping3 import ping

def main():
    pod_name = os.environ.get("POD_NAME")
    if not pod_name:
        print("Error: POD_NAME environment variable not set.")
        return

    try:
        ordinal = pod_name.split('-')[-1]
        int(ordinal) # Check if the last part is a number
    except (ValueError, IndexError):
        print(f"Error: Could not extract ordinal from pod name: {pod_name}")
        return

    target_app = os.environ.get("TARGET_APP", "pinger-b")
    target_service = os.environ.get("TARGET_SERVICE", "pinger-b-service")
    namespace = os.environ.get("NAMESPACE", "ping-app")

    target_host = f"{target_app}-{ordinal}.{target_service}.{namespace}.svc.cluster.local"

    print(f"Starting pinger {pod_name}. Target: {target_host}")

    while True:
        try:
            resolved_ip = socket.gethostbyname(target_host)
            latency = ping(resolved_ip, timeout=2)

            if latency is not None:
                latency_ms = latency * 1000
                print(f"Ping from {pod_name} to {target_host} ({resolved_ip}): Success, latency={latency_ms:.2f} ms")
            else:
                print(f"Ping from {pod_name} to {target_host} ({resolved_ip}): Timeout")

        except socket.gaierror:
            print(f"Ping from {pod_name} to {target_host}: FAILED (Name or service not known)")
        except Exception as e:
            print(f"Ping from {pod_name} to {target_host}: FAILED ({e})")
        
        time.sleep(5)

if __name__ == "__main__":
    main()
