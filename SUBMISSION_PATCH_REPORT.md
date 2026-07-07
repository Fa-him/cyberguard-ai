# Submission Patch Report

Patch date: 2026-07-06

Scope: safe submission-readiness edits only. No `.env`, secret values, API keys,
tokens, credentials, or ADK session database contents were read or printed. No
packages were installed, no external APIs were called, and Streamlit, ADK web,
Docker, and the MCP server were not launched.

## Files changed and why

- `.env.example`
  - Fixed the malformed `GOOGLE_API_KEY` placeholder.
  - Clarified that the copyable `.env` file belongs in the repository root.
  - Kept `GEMINI_MODEL` optional and blank by default.

- `.gitignore`
  - Added coverage for root and nested local `.env` files while keeping
    `.env.example` trackable.
  - Added ignores for ADK runtime folders, local session databases, Python cache
    files, virtual environments, Streamlit secrets, and build outputs.

- `cyberguard_agent/agent.py`
  - Loads the repository-root `.env` with `python-dotenv`.
  - Allows `GEMINI_MODEL` to override the model when set.
  - Keeps `gemini-flash-latest` as the fallback model.
  - Clarified the limited MCP toolset comment.

- `README.md`
  - Clarified the two execution paths: Streamlit uses deterministic local tools,
    while ADK web demonstrates the four-agent workflow and MCP integration.
  - Added a concise text architecture section with agents and MCP tools.
  - Expanded the security and privacy section with redaction limitations, human
    review, and prototype limitations.
  - Documented the repository-root `.env` location and optional `GEMINI_MODEL`.
  - Added a "Verified locally" template without claiming runtime proof.

- `app.py`
  - Removed display-sensitive emoji/dash characters from title/caption text.

- `cyberguard_agent/tools/risk.py`
  - Converted display-sensitive punctuation in labels/docstrings/method text to
    ASCII.

- `mcp_server/server.py`
  - Converted one display-sensitive docstring character to ASCII.

- `requirements.txt`
  - Added comments explaining that versions are intentionally flexible for the
    prototype and should be recorded after local verification.

- `tests/test_risk.py`
  - Expanded deterministic unit tests for valid risk scoring, invalid risk input,
    known and unknown control categories, sorted category listing, and basic
    redaction.

## Exact validation commands run

| Command | Result |
|---|---|
| `python -m compileall -q app.py cyberguard_agent mcp_server` | Passed with exit code 0 and no output. |
| `pytest -q` | Failed to start in this shell: `pytest` was not recognized as a command. No package installation or alternate test command was run. |
| `git diff --check` | Passed with exit code 0. Git also printed Windows line-ending warnings that LF will be replaced by CRLF next time Git touches the modified text files. |
| `git status --short` | Showed modified `.env.example`, `.gitignore`, `README.md`, `app.py`, `cyberguard_agent/agent.py`, `cyberguard_agent/tools/risk.py`, `mcp_server/server.py`, `requirements.txt`, `tests/test_risk.py`, plus untracked `SUBMISSION_PATCH_REPORT.md`. |

## Remaining issues requiring manual runtime proof

- Run the Streamlit UI and capture a screenshot of the deterministic local demo.
- Run the ADK web workflow with a local `GOOGLE_API_KEY` set in the repository-root
  `.env`.
- Inspect the MCP tools with MCP Inspector.
- Build and run the Docker image.
- Confirm the YouTube demo flow works end to end.
- Confirm any Kaggle Writeup claims match observed runtime behavior.

## Secret and runtime hygiene status

- A local `cyberguard_agent/.env` file appears to exist. Its contents were not read.
- `.gitignore` now ignores root and nested `.env` files while keeping
  `.env.example` trackable.
- `.gitignore` now ignores `.adk/` folders and common session database extensions.
- `cyberguard_agent/.adk/session.db` appears to already be tracked by Git. This
  patch does not remove it because the request prohibited deleting runtime files
  or user data. Review it manually before public submission.

## Next-step checklist

- Streamlit: run `streamlit run app.py`, test the sample prompt, and capture a UI
  screenshot.
- pytest: activate the intended virtual environment and run `pytest -q`.
- ADK web: copy `.env.example` to repository-root `.env`, set `GOOGLE_API_KEY`,
  run `adk web`, and record the four-agent workflow.
- MCP Inspector: run
  `npx @modelcontextprotocol/inspector python mcp_server/server.py` and show the
  safe local tools.
- Docker: run `docker build -t cyberguard-ai .` and
  `docker run --rm -p 8501:8501 cyberguard-ai`.
- GitHub: review tracked files before publishing, especially
  `cyberguard_agent/.adk/session.db`.
- Video: record the 5-minute flow using only verified behavior.
- Kaggle Writeup: draft the submission with links to GitHub, video, and runtime
  evidence.
