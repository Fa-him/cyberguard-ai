from __future__ import annotations

import sys
from pathlib import Path

# Allow this server to import the shared local control catalogue when launched
# directly via `python mcp_server/server.py`.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP

from cyberguard_agent.tools.controls import (
    get_control_guidance as _get_control_guidance,
    list_control_categories as _list_control_categories,
)
from cyberguard_agent.tools.risk import calculate_risk as _calculate_risk

mcp = FastMCP("CyberGuard Security Controls")

@mcp.tool()
def list_control_categories() -> dict:
    """List the read-only defensive control categories available to the agent."""
    return _list_control_categories()

@mcp.tool()
def get_control_guidance(category: str) -> dict:
    """Get human-readable defensive guidance for one approved control category.

    Allowed categories: phishing, account_security, device_security, patching,
    backup, incident_response. This tool is read-only and does not modify systems.
    """
    return _get_control_guidance(category)

@mcp.tool()
def calculate_risk(likelihood: int, impact: int) -> dict:
    """Calculate a transparent 5 x 5 risk score without accessing any system."""
    return _calculate_risk(likelihood, impact)

if __name__ == "__main__":
    # Important for stdio MCP servers: FastMCP owns stdout for JSON-RPC.
    # Do not print ordinary application logs to stdout.
    mcp.run(transport="stdio")
