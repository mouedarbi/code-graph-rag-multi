import subprocess
import json
import sys
import os

def test_server():
    # Construct command to run the server
    cmd = [sys.executable, "-m", "codebase_rag.mcp.server"]
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    print(f"Starting server with command: {cmd}")
    
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.getcwd(),
        env=env
    )

    # JSON-RPC Initialize Request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    }

    try:
        # Send request
        json_req = json.dumps(init_request) + "\n"
        print(f"Sending: {json_req.strip()}")
        process.stdin.write(json_req)
        process.stdin.flush()

        # Read response
        print("Waiting for response...")
        response_line = process.stdout.readline()
        print(f"Received: {response_line}")

        # Check stderr
        errors = process.stderr.read()
        if errors:
            print(f"Stderr:\n{errors}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_server()
