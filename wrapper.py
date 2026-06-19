#!/usr/bin/env python
"""
This wrapper exists to enable Claude Desktop and other MCP Clients that do not natively handle 
Python virtual environments (venv-unaware) to properly load and run server.py.

- It automatically activates the local .venv if present.
- It ensures the correct import path for server.py and its dependencies.
- This allows seamless launching via MCP CLI, Claude Desktop, or other tools, without requiring the 
  user to manually activate the virtual environment or adjust sys.path.
- For most workflows, use this file as the entrypoint (python wrapper.py, mcp run wrapper.py, 
  or mcp dev wrapper.py).
"""

import os
import sys
from pathlib import Path

# Find the current script's directory
current_dir = Path(__file__).parent.absolute()

# Look for the virtual environment relative to current directory
venv_dir = current_dir / ".venv"

# Modern venv handling: if not already in venv, re-invoke using venv's python
venv_python = venv_dir / "Scripts" / "python.exe"
if venv_dir.exists() and venv_python.exists():
    if sys.prefix != str(venv_dir):
        print(f"[wrapper] Not running inside venv, re-invoking with {venv_python}")
        os.execv(str(venv_python), [str(venv_python)] + sys.argv)
    else:
        print(f"[wrapper] Running inside venv at {venv_dir}")
else:
    print(
        f"[wrapper] No venv found at {venv_dir}, running with current Python: {sys.executable}"
    )

# Add the current directory to the path so we can import server.py
sys.path.insert(0, str(current_dir))

# Import the server module
try:
    from server import mcp

    print(f"Successfully imported server module using Python at {sys.executable}")
except ImportError as e:
    print(f"Error importing server: {e}")
    sys.exit(1)

# The wrapper will be called by MCP CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Microsoft Sentinel MCP Server Wrapper"
    )
    parser.add_argument(
        "--sse",
        action="store_true",
        help="Run server in SSE (HTTP) mode instead of STDIO",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port for SSE server (default: 8000)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help=(
            "Host/interface for SSE server (default: 127.0.0.1, loopback only). "
            "The SSE transport has NO authentication and exposes the privileged "
            "Azure identity to anyone who can reach the port. Only bind to a "
            "non-loopback interface (e.g. 0.0.0.0) on a trusted, isolated network."
        ),
    )
    args = parser.parse_args()
    print("Starting MCP server...")
    if args.sse:
        print(f"Launching in SSE mode on {args.host}:{args.port}")
        if args.host not in ("127.0.0.1", "localhost", "::1"):
            print(
                f"[wrapper] WARNING: binding SSE to non-loopback host '{args.host}'. "
                "The SSE transport is unauthenticated and grants credential-free "
                "access to your Azure identity. Only do this on a trusted network."
            )
        try:
            import uvicorn
        except ImportError:
            print(
                "[wrapper] Uvicorn is required for SSE mode. "
                "Please install with: pip install uvicorn"
            )
            sys.exit(1)

        uvicorn.run(mcp.sse_app(), host=args.host, port=args.port, log_level="info")
    else:
        print("Launching in STDIO (JSON-RPC) mode")

        mcp.run()
