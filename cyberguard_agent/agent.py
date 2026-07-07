from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from cyberguard_agent.tools.risk import calculate_risk

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_MODEL = "gemini-flash-latest"
MODEL = os.getenv("GEMINI_MODEL", "").strip() or DEFAULT_MODEL
SERVER_PATH = PROJECT_ROOT / "mcp_server" / "server.py"

# This read-only MCP toolset is intentionally limited for the controls agent. It
# cannot browse, scan, access files, or execute shell commands.
control_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[str(SERVER_PATH)],
        ),
        timeout=15,
    ),
    tool_filter=["get_control_guidance", "list_control_categories"],
)

intake_agent = Agent(
    name="intake_agent",
    model=MODEL,
    description="Creates a minimal, non-sensitive brief from a cyber concern.",
    instruction="""
    You are CyberGuard AI's intake specialist. Convert the user's cyber concern
    into a short incident brief with: observed event, affected asset type,
    possible exposure, and unknown facts. Never ask for passwords, API keys,
    recovery codes, personal records, raw logs, private IP addresses, or
    confidential documents. Do not provide offensive cybersecurity instructions.
    State clearly when facts are uncertain. This is defensive triage only.
    """,
    output_key="incident_brief",
)

risk_agent = Agent(
    name="risk_agent",
    model=MODEL,
    description="Produces a transparent, conservative risk priority.",
    instruction="""
    Review the incident brief below and produce a conservative risk assessment.
    Use the calculate_risk tool exactly once with likelihood and impact values from
    1 to 5. Explain the values in plain language and list the assumptions. Do not
    claim certainty, scan systems, or recommend system changes.

    INCIDENT BRIEF:
    {incident_brief?}
    """,
    tools=[calculate_risk],
    output_key="risk_assessment",
)

controls_agent = Agent(
    name="controls_agent",
    model=MODEL,
    description="Retrieves safe, actionable cybersecurity controls through MCP.",
    instruction="""
    Use the available MCP tools to retrieve only relevant defensive control guidance.
    First call list_control_categories. Then call get_control_guidance for no more
    than three relevant categories. Summarise the returned guidance without adding
    harmful technical commands. Never execute actions or request secrets.

    INCIDENT BRIEF:
    {incident_brief?}

    RISK ASSESSMENT:
    {risk_assessment?}
    """,
    tools=[control_mcp_toolset],
    output_key="control_guidance",
)

report_agent = Agent(
    name="report_agent",
    model=MODEL,
    description="Creates a concise human-reviewed cyber-triage plan.",
    instruction="""
    Create a final, non-alarmist triage report using the information below.

    Required headings:
    1. What we know
    2. Risk priority and assumptions
    3. Immediate safe actions
    4. Controls to review
    5. When to escalate

    Important rules:
    - State that a responsible human must review and approve all actions.
    - Never give instructions for hacking, credential theft, persistence, evasion,
      malware, exploit development, or unauthorised access.
    - Never invent evidence or claim that a compromise definitely occurred.
    - Do not request or include secrets or personal data.
    - Encourage qualified incident-response support when there may be an active
      compromise, fraud, regulated data exposure, or business disruption.

    INCIDENT BRIEF:
    {incident_brief?}

    RISK ASSESSMENT:
    {risk_assessment?}

    CONTROL GUIDANCE:
    {control_guidance?}
    """,
    output_key="final_triage_report",
)

# The deterministic sequence makes the process easy to inspect and explain in the video.
root_agent = SequentialAgent(
    name="cyberguard_triage_workflow",
    description="A safe, multi-agent cyber-risk triage workflow for small organisations.",
    sub_agents=[
        intake_agent,
        risk_agent,
        controls_agent,
        report_agent,
    ],
)
