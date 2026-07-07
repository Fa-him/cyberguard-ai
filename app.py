from __future__ import annotations

import streamlit as st

from cyberguard_agent.tools.controls import get_control_guidance
from cyberguard_agent.tools.redaction import redact_sensitive_text
from cyberguard_agent.tools.risk import calculate_risk, risk_label


st.set_page_config(page_title="CyberGuard AI", layout="wide")

st.title("CyberGuard AI")
st.caption("Defensive cyber-risk triage for small organisations - human review required.")

with st.expander("Safety and privacy notice", expanded=True):
    st.warning(
        "Do not enter passwords, API keys, recovery codes, full customer records, "
        "or confidential files. This prototype provides awareness and triage guidance "
        "only; it does not scan, access, or modify any system."
    )

example = (
    "A staff member clicked a suspicious email link on a shared laptop. "
    "They did not enter a password, but the email looked like it came from payroll."
)

incident = st.text_area(
    "Describe the concern in plain language",
    value=example,
    height=150,
    help="Use only non-sensitive information. The text is processed locally by this demo.",
)

left, right = st.columns(2)
with left:
    likelihood = st.slider(
        "Estimated likelihood of harm (1 = rare, 5 = almost certain)",
        min_value=1,
        max_value=5,
        value=3,
    )
with right:
    impact = st.slider(
        "Estimated impact (1 = minimal, 5 = severe)",
        min_value=1,
        max_value=5,
        value=3,
    )

categories = st.multiselect(
    "Select relevant control areas",
    [
        "phishing",
        "account_security",
        "device_security",
        "patching",
        "backup",
        "incident_response",
    ],
    default=["phishing", "account_security", "incident_response"],
)

if st.button("Create safe triage plan", type="primary"):
    clean_text, redaction_count = redact_sensitive_text(incident)
    result = calculate_risk(likelihood, impact)
    label = risk_label(result["score"])

    st.subheader("1. Sanitised incident brief")
    st.write(clean_text)
    if redaction_count:
        st.info(f"{redaction_count} possible sensitive item(s) were redacted before display.")

    st.subheader("2. Transparent risk priority")
    a, b, c = st.columns(3)
    a.metric("Likelihood", likelihood)
    b.metric("Impact", impact)
    c.metric("Risk score", f'{result["score"]}/25')
    st.markdown(f"**Priority:** {label}")

    st.subheader("3. Recommended defensive controls")
    if categories:
        for category in categories:
            guidance = get_control_guidance(category)
            st.markdown(f"### {guidance['title']}")
            for action in guidance["actions"]:
                st.markdown(f"- {action}")
    else:
        st.info("Select at least one control area to receive guidance.")

    st.subheader("4. Human-review action plan")
    priority_steps = [
        "Preserve relevant non-sensitive facts and record the time of the report.",
        "Tell the affected staff member not to enter credentials or continue interacting with suspicious content.",
        "Ask the responsible manager or IT/security contact to review and approve any action before changes are made.",
        "Follow your organisation's incident-response process; seek qualified support immediately if accounts, devices, or sensitive information may be compromised.",
    ]
    for index, step in enumerate(priority_steps, start=1):
        st.markdown(f"{index}. {step}")

    st.caption(
        "For the capstone demonstration, the ADK workflow performs the same sequence "
        "using specialised agents and retrieves controls through the local MCP server."
    )
