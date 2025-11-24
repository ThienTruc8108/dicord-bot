#!/usr/bin/env python3
"""Simple runner to start one `main_fixed.py` process per token in `TOKEN_LIST`.

It reads `TOKEN_LIST` from the environment (or from a .env if you use python-dotenv),
splits on commas, and starts a subprocess for each token. Each subprocess gets
its own `DISCORD_TOKEN` environment variable set so `main_fixed.py` can use it.

Logs are written to `bot_<index>.log` in the current directory.
"""
import os
import sys
import subprocess
from time import sleep

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def load_tokens():
    raw = os.environ.get("TOKEN_LIST")
    if not raw:
        print("ERROR: TOKEN_LIST not set in environment or .env")
        sys.exit(1)
    # remove surrounding quotes if present and split
    raw = raw.strip().strip('"').strip("'")
    tokens = [t.strip().strip('"').strip("'") for t in raw.split(",") if t.strip()]
    if not tokens:
        print("ERROR: TOKEN_LIST is empty after parsing")
        sys.exit(1)
    return tokens


def main():
    tokens = load_tokens()
    procs = []
    python = sys.executable or "python"
    script = os.path.join(os.getcwd(), "main_fixed.py")
    if not os.path.exists(script):
        print(f"ERROR: {script} not found")
        sys.exit(1)

    for i, token in enumerate(tokens):
        env = os.environ.copy()
        env["DISCORD_TOKEN"] = token
        # optional: set TOKEN_LIST for subprocess to single token or leave as-is
        env["TOKEN_LIST"] = token
        logfile = open(f"bot_{i}.log", "a", encoding="utf-8")
        print(f"Starting bot #{i}, log -> bot_{i}.log")
        p = subprocess.Popen([python, script], env=env, stdout=logfile, stderr=subprocess.STDOUT)
        procs.append((p, logfile))
        # small stagger to avoid simultaneous connections at once
        sleep(0.5)

    try:
        # wait for child processes
        for p, _ in procs:
            p.wait()
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt — terminating children")
        for p, f in procs:
            try:
                p.terminate()
            except Exception:
                pass
        # give them a moment
        sleep(1)
    finally:
        for p, f in procs:
            try:
                if p.poll() is None:
                    p.terminate()
            except Exception:
                pass
            try:
                f.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Helper to launch multiple instances of `main.py`, one per token in `TOKEN_LIST`.

Usage:
1. Copy `.env.example` to `.env` and set `TOKEN_LIST` to comma-separated tokens.
2. Install dependencies: `pip install python-dotenv`
3. Run: `python run_all.py`

Security: Do NOT commit `.env` to git. This script DOES NOT store tokens anywhere.
"""
import os
import sys
import shlex
import subprocess
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:
    print("Please install python-dotenv: pip install python-dotenv")
    raise


ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

token_list = os.environ.get("TOKEN_LIST")
if not token_list:
    print("No TOKEN_LIST found. Create a `.env` file from `.env.example` and set TOKEN_LIST.")
    sys.exit(1)

tokens = [t.strip() for t in token_list.split(",") if t.strip()]
if not tokens:
    print("TOKEN_LIST appears empty after parsing.")
    sys.exit(1)

processes = []
for i, token in enumerate(tokens, 1):
    env = os.environ.copy()
    env["DISCORD_TOKEN"] = token
    env.setdefault("DEFAULT_DELAY", os.environ.get("DEFAULT_DELAY", "3"))

    print(f"Starting instance {i} with DISCORD_TOKEN=***hidden***")

    # Launch a separate Python process running main.py with the chosen env var
    p = subprocess.Popen([sys.executable, str(ROOT / "main.py")], env=env)
    processes.append(p)

try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("Stopping all child processes...")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
