import subprocess
from datetime import datetime

def log(msg):
    timestamp = datetime.utcnow().isoformat()
    print(f"[{timestamp}] {msg}")

def run_command_in_dir(cmd, cwd, capture_output=True, check=True):
    """
    Run a shell command in a specific directory.
    Returns a dict with stdout, stderr, and returncode.
    """
    log(f"Running command: {' '.join(cmd)} in {cwd}")
    try:
        log_path = '/home/ds/sambashare/GOB/GOB-system/logs/frontend.log'
        with open(log_path, 'w') as f:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                stdout=f,
                stderr=f,
                text=True,
                check=check
            )
        log(f"Command completed with return code {result.returncode}")
        return {"stdout": "", "stderr": "", "returncode": result.returncode}
    except FileNotFoundError:
        log(f"[ERROR] Could not create log file at {log_path}")
        return {"stdout": "", "stderr": "Could not create log file", "returncode": 1}
    except subprocess.CalledProcessError as e:
        log(f"[ERROR] Command failed with return code {e.returncode}")
        return {"stdout": e.stdout, "stderr": e.stderr, "returncode": e.returncode}

# Example usage
if __name__ == "__main__":
    frontend_dir = "/home/ds/sambashare/GOB/GOB-system/frontend"
    # Step 1: Install dependencies
    run_command_in_dir(["npm", "install", "--legacy-peer-deps"], frontend_dir)
    # Step 2: Start the frontend service
    run_command_in_dir(["npm", "start"], frontend_dir)

