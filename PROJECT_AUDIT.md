# CyberGuard AI Project Audit

Audit date: 2026-07-06

Scope: static workspace inspection only. The app, tests, ADK web UI, MCP server, Docker image, and external commands were not run because the audit request prohibited actions that could change the project. Secret files were not opened.

Ignored/generated areas: `.git`, `.venv`, `node_modules`, `__pycache__`, `build`, `dist`, `.pytest_cache`, and large/generated runtime files. The file `cyberguard_agent/.adk/session.db` was noted as runtime state but not inspected.

## 1. Project name and real-world problem

Project name: CyberGuard AI

CyberGuard AI is a defensive cybersecurity triage assistant for small organisations that do not have a dedicated security team. It helps a staff member turn an everyday cyber concern, such as a suspicious email, possible account compromise, lost device, weak password practice, or uncertain phishing click, into a structured incident brief, transparent risk priority, relevant defensive controls, and a human-reviewed action plan. The real-world problem is that small organisations often delay or overreact during cyber incidents because they lack a safe, repeatable first-response process.

## 2. Intended Kaggle track recommendation

Recommended track: Agents for Good

Rationale: the project focuses on social impact, safety, and accessibility for small businesses, charities, schools, clubs, and community organisations. It is more naturally positioned as a defensive public-benefit/security-awareness tool than as a revenue, concierge, or freestyle demo.

## 3. Complete project architecture summary

CyberGuard AI has two related execution paths:

- A working local Streamlit demo path that uses deterministic Python tools directly.
- An ADK multi-agent path that defines four agents and connects one agent to a local stdio MCP server.

The Streamlit app does not currently call the ADK agent workflow. It directly calls the shared local Python tools for redaction, risk scoring, and control lookup. The ADK workflow is defined separately in `cyberguard_agent/agent.py` and is intended to run through `adk web`.

Text architecture diagram:

```text
User
  |
  v
Streamlit UI: app.py
  |
  |-- redact_sensitive_text()
  |      cyberguard_agent/tools/redaction.py
  |
  |-- calculate_risk()
  |      cyberguard_agent/tools/risk.py
  |
  |-- get_control_guidance()
         cyberguard_agent/tools/controls.py
         |
         v
  Human-reviewed triage plan displayed in browser


ADK workflow path:

User prompt in ADK web
  |
  v
root_agent: SequentialAgent
  |
  v
Intake Agent
  creates incident_brief
  |
  v
Risk Agent
  calls local calculate_risk tool
  creates risk_assessment
  |
  v
Controls Agent
  starts stdio MCP server through McpToolset
  calls list_control_categories and get_control_guidance
  creates control_guidance
  |
  v
Report Agent
  creates final_triage_report


MCP server:

mcp_server/server.py
  |
  |-- list_control_categories
  |-- get_control_guidance
  |-- calculate_risk
  |
  v
Shared local catalogue and risk functions
```

Security components:

- User-facing safety notice in `app.py`.
- Defensive-only instructions in each ADK agent prompt.
- Basic redaction for email-like identifiers, common API key patterns, and password/secret assignments in `redaction.py`.
- Risk validation in `risk.py`.
- Read-only MCP tools in `mcp_server/server.py`.
- `.gitignore` excludes `.env`, `.venv`, `__pycache__`, `.pytest_cache`, and `.streamlit/secrets.toml`.

Storage:

- No intentional application database is implemented.
- `cyberguard_agent/.adk/session.db` exists as ADK runtime state and should be treated as generated/private until reviewed.

External APIs:

- ADK workflow requires a Gemini API key via `GOOGLE_API_KEY`.
- The Streamlit demo path is local and does not require an API key.

## 4. Important file/folder tree

```text
.
|-- app.py
|   Streamlit UI for the safe local demo. Calls local redaction, risk, and control tools directly.
|
|-- cyberguard_agent/
|   |-- __init__.py
|   |   Marks the package as ADK-discoverable.
|   |
|   |-- agent.py
|   |   Defines the ADK SequentialAgent, four sub-agents, local risk tool use, and MCP toolset.
|   |
|   |-- .env
|   |   Local secret/config file exists. Contents were not inspected.
|   |
|   |-- .adk/session.db
|   |   Generated ADK runtime/session database. Not inspected.
|   |
|   `-- tools/
|       |-- __init__.py
|       |   Empty package marker.
|       |
|       |-- controls.py
|       |   Static defensive control catalogue and control lookup functions.
|       |
|       |-- redaction.py
|       |   Regex-based redaction of emails, common API keys, and password/secret assignments.
|       |
|       `-- risk.py
|           5 x 5 risk scoring and priority labels.
|
|-- mcp_server/
|   |-- __init__.py
|   |   Empty package marker.
|   |
|   `-- server.py
|       FastMCP stdio server exposing read-only security-control and risk tools.
|
|-- tests/
|   `-- test_risk.py
|       Unit tests for risk scoring, risk labels, and redaction.
|
|-- README.md
|   Main project explanation, architecture, safety notes, run commands, Docker instructions, and video flow.
|
|-- PROJECT_PLAN.md
|   Submission plan and remaining Kaggle deliverables.
|
|-- requirements.txt
|   Python dependencies: google-adk, mcp[cli], python-dotenv, streamlit, pytest.
|
|-- Dockerfile
|   Container image for running Streamlit on port 8501.
|
|-- .env.example
|   Template for secret/config variables. Needs syntax correction.
|
|-- .gitignore
|   Ignores environment files, virtualenv, pycache, pytest cache, and Streamlit secrets.
|
`-- LICENSE
    MIT license.
```

No project-level `.github` directory or workflow files were found.

## 5. Current features actually implemented

Implemented in the Streamlit demo:

- Displays a safety/privacy notice.
- Accepts a plain-language incident description.
- Lets the user estimate likelihood and impact with sliders from 1 to 5.
- Lets the user choose control categories from phishing, account security, device security, patching, backup, and incident response.
- Redacts common sensitive text patterns before showing the incident brief.
- Calculates a transparent risk score as likelihood multiplied by impact.
- Maps the score to Low, Moderate, High, or Critical priority labels.
- Displays defensive control actions from the local catalogue.
- Displays a short human-review action plan.

How a user uses it:

1. Install dependencies.
2. Run `streamlit run app.py`.
3. Enter a non-sensitive cyber concern.
4. Pick likelihood, impact, and relevant control categories.
5. Click `Create safe triage plan`.
6. Review the sanitized brief, risk score, control guidance, and action plan.

Implemented in source for the ADK path:

- A four-agent ADK `SequentialAgent` exists.
- The risk agent has a local Python risk tool.
- The controls agent has an MCP toolset that launches the local MCP server over stdio.
- The report agent composes a final triage report from prior outputs.

Needs proof:

- The ADK workflow was not executed during this audit.
- The MCP server was not executed during this audit.
- The Streamlit app was not launched during this audit.

## 6. AI-agent implementation details

Agent framework used:

- Google ADK is used via `google.adk.agents.Agent` and `google.adk.agents.SequentialAgent`.
- MCP integration is used via `google.adk.tools.mcp_tool.McpToolset`.

Model:

- `cyberguard_agent/agent.py` hardcodes `MODEL = "gemini-flash-latest"`.
- `.env.example` includes `GEMINI_MODEL`, but the source does not currently read it.

Number and roles of agents:

1. `intake_agent`
   - Converts the user concern into a minimal, non-sensitive incident brief.
   - Output key: `incident_brief`.

2. `risk_agent`
   - Produces a conservative risk assessment.
   - Calls `calculate_risk` exactly once according to its prompt.
   - Output key: `risk_assessment`.

3. `controls_agent`
   - Retrieves defensive control guidance via MCP.
   - Calls `list_control_categories` and up to three `get_control_guidance` calls according to its prompt.
   - Output key: `control_guidance`.

4. `report_agent`
   - Produces the final human-reviewed triage report.
   - Output key: `final_triage_report`.

Agent-to-agent workflow:

- The workflow is deterministic and sequential.
- Later agents read prior outputs using ADK output placeholders such as `{incident_brief?}`, `{risk_assessment?}`, and `{control_guidance?}`.
- There is no autonomous planner, parallel branch, or dynamic router.

Tools used by each agent:

- Intake Agent: no tools.
- Risk Agent: local `calculate_risk`.
- Controls Agent: `McpToolset` exposing `get_control_guidance` and `list_control_categories`.
- Report Agent: no tools.

Reasoning, routing, memory, or orchestration approach:

- Orchestration is a fixed `SequentialAgent` pipeline.
- Reasoning is prompt-guided and constrained by explicit safety rules.
- Memory is not implemented as a project feature.
- ADK runtime state exists in `cyberguard_agent/.adk/session.db`, but this audit did not inspect it.
- Routing is not dynamic; every request follows intake, risk, controls, and report.

## 7. MCP implementation details

MCP server location:

- `mcp_server/server.py`

MCP implementation:

- Uses `mcp.server.fastmcp.FastMCP`.
- Runs over stdio with `mcp.run(transport="stdio")`.
- Adds the project root to `sys.path` when launched directly so it can import the shared local modules.

Available MCP tools:

- `list_control_categories()`
  - Returns available defensive control categories.

- `get_control_guidance(category: str)`
  - Returns defensive guidance for an approved category.

- `calculate_risk(likelihood: int, impact: int)`
  - Returns a 5 x 5 risk score and priority.

Available MCP resources:

- None found.

Available MCP prompts:

- None found.

How the agent calls the MCP server:

- `cyberguard_agent/agent.py` creates `control_mcp_toolset = McpToolset(...)`.
- It launches the MCP server with `sys.executable` and the path to `mcp_server/server.py`.
- It uses `StdioConnectionParams` and `StdioServerParameters`.
- The tool filter allows only `get_control_guidance` and `list_control_categories` for the controls agent.

Working or incomplete:

- Source implementation is present and coherent.
- Runtime operation needs proof because it was not executed during this audit.
- Minor mismatch: the MCP server exposes `calculate_risk`, but the ADK MCP tool filter excludes it. This is acceptable because the risk agent uses the local Python tool, but the README says the MCP server exposes both control guidance and the risk matrix. The demo should explain that the ADK controls agent only uses the control-related MCP tools.

## 8. Kaggle requirement checklist

| Requirement | Status | Evidence / gap |
|---|---|---|
| Agent or multi-agent system (ADK) | Implemented | `cyberguard_agent/agent.py` defines a four-agent ADK `SequentialAgent`. Runtime proof still recommended. |
| MCP Server | Implemented | `mcp_server/server.py` defines a FastMCP stdio server with three tools. Runtime proof still recommended. |
| Antigravity demonstration for video | Needs Proof | README says it will be demonstrated in the project video, but no local proof artifact exists. |
| Security features | Partially Implemented | Defensive prompts, redaction, safe UI notice, read-only tools, `.gitignore` for secrets. Prompt injection handling and auth are limited. |
| Deployability | Partially Implemented | Dockerfile and Streamlit command exist. No verified build/run result in this audit. |
| Agent skills / Agents CLI | Partially Implemented | Custom tools and ADK agent source exist. No project-level `.agents` files or Agents CLI artifacts were found. |
| README and setup instructions | Partially Implemented | README is detailed, but has visible text encoding artifacts and `.env.example` syntax appears broken. |
| Public GitHub readiness | Partially Implemented | LICENSE, README, Dockerfile, `.gitignore` exist. Generated ADK session DB and local `.env` presence need review before public release. |
| 5-minute YouTube demo readiness | Partially Implemented | README has a suggested flow. Needs actual recording, screenshots, and proof that ADK/MCP demos run. |
| Kaggle Writeup readiness | Partially Implemented | Project plan has title/subtitle and core positioning. Needs final writeup draft and evidence links. |

## 9. Security review

API-key handling:

- `.env.example` names `GOOGLE_API_KEY` and `GEMINI_MODEL`.
- `cyberguard_agent/.env` exists and was not opened.
- `.gitignore` includes `.env`, which should protect local `.env` files, but public-readiness should still be verified before pushing.
- `.env.example` appears to have an invalid/open quote for `GOOGLE_API_KEY`; fix before users copy it.
- `GEMINI_MODEL` is documented in `.env.example` but not read by the code.

Input validation:

- `calculate_risk` checks that likelihood and impact are integers from 1 to 5.
- `get_control_guidance` normalizes category input with `strip().lower()` and rejects unknown categories.
- Streamlit sliders constrain likelihood and impact to valid ranges.
- Streamlit multiselect constrains categories to known values.
- Incident text length is not capped.
- ADK agent free-text input relies on prompt instructions rather than strict validation.

Risky commands or unsafe tool use:

- No obvious `subprocess`, `os.system`, `shell=True`, `eval`, `exec`, file-writing, deletion, scanner, or network-client code was found in project source.
- MCP tools are read-only and return static guidance or a calculation.
- The project is intentionally defensive and does not execute system changes.

Prompt injection protection:

- Agent prompts include strong defensive instructions and secret-avoidance rules.
- There is no separate prompt-injection classifier, policy layer, allowlist parser, or structured output validator.
- The controls agent is constrained to a small MCP toolset, which reduces blast radius.
- The report agent could still be influenced by malicious user text unless the demo clearly frames it as advisory and human-reviewed.

Logging/privacy issues:

- The Streamlit app displays the sanitized incident brief after redaction.
- Redaction is basic and pattern-based; it is not complete DLP.
- No explicit application logging was found.
- ADK runtime state exists at `cyberguard_agent/.adk/session.db`; this may contain prior session data and should not be published without review.

Authentication or authorization:

- No app authentication is implemented.
- This is acceptable for a local demo, but not for a deployed multi-user cybersecurity assistant.
- A production version would need authentication, authorization, audit logging, tenant isolation, and retention controls.

## 10. Exact commands to run locally from a clean setup

These are recommended commands from static inspection and README alignment. They were not run during this audit.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Run tests:

```powershell
pytest -q
```

Run the ADK multi-agent workflow:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` locally and set `GOOGLE_API_KEY`. Do not commit `.env`.

```powershell
adk web
```

In the ADK UI, select `cyberguard_agent`.

Run the MCP server directly:

```powershell
python mcp_server/server.py
```

Inspect the MCP server:

```powershell
npx @modelcontextprotocol/inspector python mcp_server/server.py
```

Docker:

```powershell
docker build -t cyberguard-ai .
docker run --rm -p 8501:8501 cyberguard-ai
```

Then open:

```text
http://localhost:8501
```

## 11. Bugs, missing files, broken imports, unclear instructions, and likely demo problems

1. `.env.example` appears syntactically broken.
   - `GOOGLE_API_KEY` has an opening quote without a closing quote.
   - This can confuse setup for ADK users.

2. `GEMINI_MODEL` is documented but unused.
   - The code hardcodes `MODEL = "gemini-flash-latest"`.
   - Either use `GEMINI_MODEL` or remove it from the template.

3. Encoding artifacts appear in README/code display.
   - Several characters render as mojibake in terminal output, including dash, shield emoji, multiplication sign, and tree characters.
   - This could look unpolished on GitHub or in the demo if the files are not encoded/displayed consistently.

4. ADK/MCP runtime needs proof.
   - The source is present, but this audit did not run `adk web`, the MCP server, Streamlit, or tests.
   - The README should include actual screenshots or a short verified "known-good" section before submission.

5. Streamlit demo bypasses the ADK agent workflow.
   - This is fine for a safe local demo, but judges may expect the visible app to show agentic behavior.
   - The video should explicitly show the ADK web workflow as the agent demo.

6. MCP server has tools not all used by ADK.
   - `calculate_risk` is exposed by MCP but filtered out of the ADK `McpToolset`.
   - This is not a bug if intentional, but the architecture narrative should be precise.

7. Generated/private runtime state exists.
   - `cyberguard_agent/.adk/session.db` exists and is not ignored by the current `.gitignore`.
   - It should be reviewed before public release.

8. Local secret file exists.
   - `cyberguard_agent/.env` exists and was not inspected.
   - Verify it is ignored and not committed.

9. No GitHub workflow/config files found.
   - There is no `.github` directory, CI workflow, issue template, or PR template.
   - Not mandatory, but helpful for public readiness.

10. No pinned dependency versions.
    - `requirements.txt` uses unpinned package names.
    - Future installs may break if ADK, MCP, or Streamlit APIs change.

11. No deployment-specific Streamlit config.
    - Dockerfile exists, but no `.streamlit/config.toml` or cloud deployment notes were found.

12. No authentication for deployed use.
    - Fine for local capstone demo.
    - Must be clearly stated as a prototype limitation.

## 12. Highest-priority improvements before submission

1. Verify and record the working demo path.
   - Run Streamlit, ADK web, MCP inspector, and tests.
   - Capture screenshots for the README and video.

2. Fix `.env.example`.
   - Ensure `GOOGLE_API_KEY` is a valid placeholder.
   - Decide whether `GEMINI_MODEL` is used or remove it.

3. Review secret/runtime files before public GitHub.
   - Confirm `cyberguard_agent/.env` is not committed.
   - Add ignore coverage for ADK runtime files such as `.adk/` or `*.db` if needed.
   - Remove generated runtime state from the public release if it contains local sessions.

4. Clean encoding artifacts.
   - Ensure README and Python files render correctly in GitHub and the terminal.

5. Add a short "Verified locally" section.
   - Include Python version, OS, commands run, and results.

6. Clarify the two demo paths.
   - Streamlit is deterministic local demo.
   - ADK web is the multi-agent demo.
   - MCP inspector proves the MCP server.

7. Improve public-readiness docs.
   - Add limitations, threat model, privacy notice, architecture, and demo screenshots.

8. Pin dependency versions or add tested version ranges.
   - Especially for `google-adk` and `mcp[cli]`.

9. Add more tests.
   - Cover control category lookup, invalid category handling, and redaction edge cases.

10. Add a Kaggle writeup draft.
    - Keep it under the required word limit and align it with the video.

## 13. Practical 5-minute demo flow

This flow uses only features that are implemented in source. Runtime should be verified before recording.

0:00-0:25 - Problem and audience

- Introduce CyberGuard AI as a defensive triage assistant for small organisations.
- State that it does not scan, exploit, collect credentials, or replace professionals.

0:25-0:55 - Architecture

- Show the README architecture.
- Explain the two paths: Streamlit local demo and ADK multi-agent workflow.

0:55-2:10 - Streamlit demo

- Run `streamlit run app.py`.
- Use the provided suspicious-email/shared-laptop example.
- Adjust likelihood and impact.
- Select phishing, account security, and incident response.
- Click `Create safe triage plan`.
- Show sanitized brief, risk score, recommended controls, and human-review plan.

2:10-3:10 - ADK multi-agent workflow

- Run `adk web`.
- Select `cyberguard_agent`.
- Submit the same safe prompt.
- Show the sequence: intake, risk, controls, report.
- Emphasize the four specialist agents and output keys.

3:10-4:00 - MCP proof

- Run the MCP inspector command.
- Show `list_control_categories`, `get_control_guidance`, and `calculate_risk`.
- Explain that the tools are local and read-only.

4:00-4:35 - Security controls

- Show `redaction.py`, `risk.py`, and the safety notice in `app.py`.
- Mention `.env` handling without showing values.
- Explain human review and defensive-only constraints.

4:35-5:00 - Submission fit and limitations

- State the track: Agents for Good.
- Explain limitations: prototype, no auth, no production DLP, no incident-response replacement.
- End with next steps: verified deployment, screenshots, and Kaggle writeup.

## 14. Suggested GitHub README sections and Kaggle Writeup headings

Suggested GitHub README sections:

- Project overview
- Real-world problem
- Why Agents for Good
- Architecture
- Demo modes: Streamlit, ADK, MCP Inspector
- Safety and privacy model
- Features
- Repository structure
- Setup
- Run Streamlit demo
- Run ADK agent workflow
- Run MCP server / inspector
- Run tests
- Docker
- Verified environment
- Limitations
- Roadmap
- License

Suggested Kaggle Writeup headings:

- Title
- Summary
- Problem and target users
- Why an agentic approach
- Architecture
- ADK multi-agent workflow
- MCP server and tools
- Safety, privacy, and human review
- Demo walkthrough
- Evaluation and testing
- Limitations
- Future work
- Links: GitHub, video, live demo if available

## What is already strong

- Clear social-good cybersecurity use case.
- Real ADK multi-agent source with four meaningful roles.
- Real FastMCP server source with safe, read-only tools.
- Streamlit demo is practical and understandable.
- Risk scoring is transparent and testable.
- Defensive safety posture is present in UI copy, prompts, tools, and README.
- Dockerfile, tests, README, project plan, license, and `.env.example` are present.

## What must be fixed before submission

- Prove the app, ADK workflow, MCP inspector, Docker path, and tests actually run.
- Fix `.env.example`.
- Review/remove/ignore `cyberguard_agent/.adk/session.db` before public release.
- Verify `cyberguard_agent/.env` is ignored and not committed.
- Clean encoding artifacts in README and displayed UI text.
- Make the README precise about Streamlit using direct local tools while ADK demonstrates the multi-agent workflow.
- Add screenshots and a final Kaggle writeup.

## Best next action

Do a clean local verification pass: fix `.env.example`, run Streamlit, run `pytest -q`, run `adk web`, run the MCP inspector, capture screenshots, then update the README with verified commands and results before recording the 5-minute YouTube demo.
