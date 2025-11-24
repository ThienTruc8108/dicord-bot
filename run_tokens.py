#!/usr/bin/env python3
"""Launch one `main_fixed.py` process per token in `TOKEN_LIST`.

Usage:
  - Ensure `.env` contains `TOKEN_LIST` (comma-separated) or export `TOKEN_LIST`.
  - Run: `python run_tokens.py`

This script sets `DISCORD_TOKEN` in each subprocess's environment so
`main_fixed.py` can read it normally.
"""
import os
import sys
import subprocess
from time import sleep


def load_tokens():
    raw = os.environ.get("TOKEN_LIST")
    if not raw:
        # try loading .env via dotenv if available
        try:
            from dotenv import load_dotenv
            load_dotenv()
            raw = os.environ.get("TOKEN_LIST")
        except Exception:
            pass

    if not raw:
        print("ERROR: TOKEN_LIST not set in environment or .env")
        sys.exit(1)

    # remove surrounding quotes and split
    raw = raw.strip().strip('"').strip("'")
    tokens = [t.strip().strip('"').strip("'") for t in raw.split(",") if t.strip()]
    if not tokens:
        print("ERROR: TOKEN_LIST is empty after parsing")
        sys.exit(1)
    return tokens


def main():
    tokens = load_tokens()
    python = sys.executable or "python"
    script = os.path.join(os.getcwd(), "main_fixed.py")
    if not os.path.exists(script):
        print(f"ERROR: {script} not found")
        sys.exit(1)

    procs = []
    for i, token in enumerate(tokens):
        env = os.environ.copy()
        env["DISCORD_TOKEN"] = token
        # for clarity keep TOKEN_LIST in subprocess env as the single token
        env["TOKEN_LIST"] = token
        logfile = open(f"bot_{i}.log", "a", encoding="utf-8")
        print(f"Starting bot #{i}, log -> bot_{i}.log")
        p = subprocess.Popen([python, script], env=env, stdout=logfile, stderr=subprocess.STDOUT)
        procs.append((p, logfile))
        sleep(0.5)

    try:
        for p, _ in procs:
            p.wait()
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt — terminating children")
        for p, _ in procs:
            try:
                p.terminate()
            except Exception:
                pass
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
