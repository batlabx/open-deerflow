"""MCP server: python_exec — run untrusted code in a throwaway container.

Why is this a TOOL (and a very carefully written one)?
  Executing model-generated code is the textbook example of an effectful,
  dangerous capability. It MUST be isolated, resource-limited, network-less,
  and return a typed result (stdout / stderr / exit code). Never run agent code
  in the host process.

Open-source swap: DeerFlow provisions sandboxes on a managed Kubernetes
cluster. We use a plain `docker run` with the network disabled and tight
memory/CPU/time limits — the same guarantees, zero cloud.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import textwrap

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("open-deerflow-sandbox")

IMAGE = os.getenv("SANDBOX_IMAGE", "python:3.12-slim")
TIMEOUT_S = int(os.getenv("SANDBOX_TIMEOUT_S", "20"))


@mcp.tool()
def python_exec(code: str) -> dict:
    """Run Python in an isolated Docker container. Returns stdout/stderr/exit_code."""
    with tempfile.TemporaryDirectory() as work:
        script = os.path.join(work, "snippet.py")
        with open(script, "w") as fh:
            fh.write(textwrap.dedent(code))

        try:
            proc = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "--network", "none",         # no exfiltration / no SSRF
                    "--memory", "512m",
                    "--cpus", "1",
                    "--pids-limit", "128",
                    "-v", f"{work}:/work:ro",     # read-only mount
                    IMAGE,
                    "python", "/work/snippet.py",
                ],
                capture_output=True,
                text=True,
                timeout=TIMEOUT_S,
            )
            return {
                "stdout": proc.stdout[-8000:],
                "stderr": proc.stderr[-4000:],
                "exit_code": proc.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": f"timeout after {TIMEOUT_S}s",
                    "exit_code": 124}
        except FileNotFoundError:
            return {"stdout": "", "stderr": "docker not found on PATH",
                    "exit_code": 127}


if __name__ == "__main__":
    mcp.run()
