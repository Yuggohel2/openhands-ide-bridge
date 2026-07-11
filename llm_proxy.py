import http.server
import socketserver
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

PORT = 9999
USER_DIR = Path.home()
OPENHANDS_DIR = USER_DIR / ".openhands"

def safe_write_json(file_path: Path, data: Any):
    """Write JSON file with safety retries to prevent Windows locking/access errors."""
    for i in range(5):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return
        except (PermissionError, IOError):
            time.sleep(0.1)
    raise IOError(f"Failed to write file {file_path} after multiple retries.")

def safe_read_json(file_path: Path) -> Any:
    """Read JSON file with safety retries to prevent Windows locking/access errors."""
    for i in range(5):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (PermissionError, IOError, json.JSONDecodeError):
            time.sleep(0.1)
    raise IOError(f"Failed to read file {file_path} after multiple retries.")

def safe_unlink(file_path: Path):
    """Delete a file with safety retries to prevent Windows locking/access errors."""
    if not file_path.exists():
        return
    for i in range(5):
        try:
            file_path.unlink()
            return
        except (PermissionError, IOError):
            time.sleep(0.1)

class LLMProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default logging to keep terminal clean
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        if self.path in ("/v1/chat/completions", "/chat/completions"):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode('utf-8'))
                print(f"\n[Proxy] Received LLM request for model: {payload.get('model')}")
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f"Invalid JSON: {e}".encode())
                return

            # Ensure directory exists
            OPENHANDS_DIR.mkdir(parents=True, exist_ok=True)
            
            # Generate unique request/response ID to support concurrent sessions
            req_id = str(uuid.uuid4())[:8]
            request_file = OPENHANDS_DIR / f"llm_request_{req_id}.json"
            response_file = OPENHANDS_DIR / f"llm_response_{req_id}.json"

            # Save request to file safely
            try:
                safe_write_json(request_file, payload)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Failed to write request file: {e}".encode())
                return
            
            print(f"[Proxy] Saved request to {request_file}. Waiting for orchestrator response...")

            # Wait for response file
            timeout = 180  # 3 minutes timeout
            start_time = time.time()
            response_data = None
            
            while time.time() - start_time < timeout:
                if response_file.exists():
                    try:
                        # Add a tiny delay to ensure file write is completed by orchestrator
                        time.sleep(0.1)
                        response_data = safe_read_json(response_file)
                        safe_unlink(response_file)
                        safe_unlink(request_file)
                        break
                    except Exception:
                        time.sleep(0.2)
                time.sleep(0.5)

            try:
                if response_data:
                    print("[Proxy] Received response from orchestrator. Sending to OpenHands.")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode('utf-8'))
                else:
                    print("[Proxy] Timeout waiting for orchestrator response.")
                    safe_unlink(request_file)
                    self.send_response(504)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    error_resp = {
                        "error": {
                            "message": "Gateway Timeout: Orchestrator agent did not respond in time.",
                            "type": "gateway_timeout",
                            "code": 504
                        }
                    }
                    self.wfile.write(json.dumps(error_resp).encode('utf-8'))
            except OSError as e:
                print(f"[Proxy] Client disconnected before response could be sent: {e}")
        else:
            self.send_response(404)
            self.end_headers()

def kill_process_on_port(port: int):
    """Attempt to terminate any process currently occupying the proxy port."""
    import subprocess
    try:
        if os.name == "nt":
            # Windows: Find and kill the PID on the target port
            output = subprocess.check_output(f"netstat -aon | findstr LISTENING | findstr :{port}", shell=True).decode()
            for line in output.strip().split("\n"):
                parts = line.strip().split()
                if len(parts) >= 5 and parts[1].endswith(f":{port}"):
                    pid = parts[-1]
                    # Don't kill our own process
                    if int(pid) != os.getpid():
                        print(f"[Proxy] Terminating occupying process {pid} on port {port}...")
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                        time.sleep(0.5)  # Give the OS time to release the port
        else:
            # Unix/macOS: Use lsof and kill
            output = subprocess.check_output(f"lsof -t -i:{port}", shell=True).decode()
            for pid in output.strip().split("\n"):
                if pid and int(pid) != os.getpid():
                    print(f"[Proxy] Terminating occupying process {pid} on port {port}...")
                    subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
                    time.sleep(0.5)
    except Exception:
        # Fail silently if commands are missing or permission is denied
        pass

def run_server():
    default_port = PORT
    port = int(os.getenv("LLM_PROXY_PORT", default_port))
    
    # Attempt to kill any orphaned proxy or occupying process on startup
    kill_process_on_port(port)
    
    # Allow address reuse to prevent "Address already in use" errors on restarts
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    
    # Clean up any leftover files on startup
    if OPENHANDS_DIR.exists():
        for f in OPENHANDS_DIR.glob("llm_request_*.json"):
            safe_unlink(f)
        for f in OPENHANDS_DIR.glob("llm_response_*.json"):
            safe_unlink(f)
        # Clean up legacy static files if they exist
        safe_unlink(OPENHANDS_DIR / "llm_request.json")
        safe_unlink(OPENHANDS_DIR / "llm_response.json")
    
    while True:
        try:
            with socketserver.ThreadingTCPServer(("0.0.0.0", port), LLMProxyHandler) as httpd:
                print(f"[Proxy] LLM Local Proxy Server running on port {port}...")
                if port != default_port:
                    print(f"\n[WARNING] Bound to custom port {port} instead of default {default_port}!")
                    print(f"[WARNING] Make sure your OpenHands container is configured to send requests to:")
                    print(f"          http://host.docker.internal:{port}/v1/chat/completions\n")
                httpd.serve_forever()
            break
        except OSError as e:
            # Check for "Address already in use" errors (98 on Unix, 10048 on Windows)
            err_msg = str(e).lower()
            if e.errno in (98, 10048) or "in use" in err_msg or "already bound" in err_msg:
                print(f"[Proxy] Port {port} is busy. Trying {port - 1}...")
                port -= 1
                if port < 1024:
                    print("[Proxy] Error: No available ports found above 1024.")
                    break
            else:
                print(f"[Proxy] Server error binding to port {port}: {e}")
                break

if __name__ == "__main__":
    run_server()
