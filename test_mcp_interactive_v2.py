import subprocess
import json
import sys
import os

def test_server():
    cmd = [sys.executable, "-m", "codebase_rag.mcp.server"]
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    print(f"Starting server with command: {cmd}")
    
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
    
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    input_str = json.dumps(init_request) + "\n" + json.dumps(tools_request) + "\n"

    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd(),
            env=env
        )
        
        print(f"Sending input...")
        process.stdin.write(input_str)
        process.stdin.flush()
        
        print("Reading stdout line 1 (init)...")
        line1 = process.stdout.readline()
        print(f"STDOUT 1: {line1.strip()}")
        
        print("Reading stdout line 2 (tools)...")
        line2 = process.stdout.readline()
        print(f"STDOUT 2: {line2.strip()}")
        
        if not line1 or not line2:
            print("STDOUT was empty or partial!")
            # Check stderr
            print("Reading stderr...")
            stderr_out = process.stderr.read()
            print(f"STDERR:\n{stderr_out}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'process' in locals():
            process.terminate()
            try:
                outs, errs = process.communicate(timeout=2)
                if errs:
                    print(f"Final STDERR:\n{errs}")
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    test_server()