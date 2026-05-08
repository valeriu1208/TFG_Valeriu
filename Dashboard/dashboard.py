import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

ORCHESTRATOR_URL = "http://127.0.0.1:8000"

QUANTUM_SERVERS = [
    {"host": "192.168.1.200", "name": "Q-Server 1", "qbits": 127, "shots": 10000, "circuit_depth": 5000, "qstorage": 127 * 10000 // 8},
    {"host": "192.168.1.201", "name": "Q-Server 2", "qbits": 127, "shots": 10000, "circuit_depth": 5000, "qstorage": 127 * 10000 // 8},
]

st.set_page_config(
    page_title="Hybrid Datacenter Orchestrator",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
    }
    .badge-success { background: #d4edda; color: #155724; }
    .badge-error   { background: #f8d7da; color: #721c24; }
    .badge-pending { background: #fff3cd; color: #856404; }
    .badge-quantum { background: #cce5ff; color: #004085; }
    .badge-classical { background: #e2e3e5; color: #383d41; }
    .metric-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .flow-step {
        background: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        margin: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "petition_history" not in st.session_state:
    st.session_state.petition_history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_petition" not in st.session_state:
    st.session_state.last_petition = None


# ── Helpers ────────────────────────────────────────────────────────────────────
def post_petition(payload: dict):
    try:
        r = requests.post(f"{ORCHESTRATOR_URL}/process", json=payload, timeout=15)
        return r.status_code, r.json()
    except requests.exceptions.ConnectionError:
        return None, {"detail": "Cannot reach orchestrator at " + ORCHESTRATOR_URL}
    except Exception as e:
        return None, {"detail": str(e)}


def get_quantum_status():
    try:
        r = requests.get(f"{ORCHESTRATOR_URL}/process/quantum_status", timeout=8)
        return r.json() if r.ok else None
    except Exception:
        return None


def delete_server(server_name: str):
    try:
        r = requests.delete(f"{ORCHESTRATOR_URL}/process/delete", params={"server_name": server_name}, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return None, {"detail": str(e)}


def resource_gauge(label: str, used: float, total: float, unit: str = "", color: str = "#4e79a7"):
    pct = used / total if total > 0 else 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=used,
        delta={"reference": total, "relative": False, "valueformat": ".0f"},
        title={"text": f"{label}<br><span style='font-size:11px;color:#888'>{unit}</span>"},
        gauge={
            "axis": {"range": [0, total]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, total * 0.6], "color": "#d4edda"},
                {"range": [total * 0.6, total * 0.85], "color": "#fff3cd"},
                {"range": [total * 0.85, total], "color": "#f8d7da"},
            ],
            "threshold": {"line": {"color": "red", "width": 2}, "thickness": 0.75, "value": total * 0.9},
        },
    ))
    fig.update_layout(height=200, margin=dict(t=40, b=10, l=10, r=10))
    return fig


def flow_diagram(path: str | None = None):
    """Return a graphviz source string with highlighted path."""
    quantum_color  = '#cce5ff' if path == 'quantum'   else '#ffffff'
    classical_color = '#d4edda' if path == 'classical' else '#ffffff'
    active_edge = 'color="#0066cc" penwidth=2' if path else 'color="#888888"'
    q_edge  = f'color="#0066cc" penwidth=2' if path == 'quantum'   else 'color="#888888"'
    cl_edge = f'color="#28a745" penwidth=2' if path == 'classical' else 'color="#888888"'

    return f"""
digraph G {{
    rankdir=LR;
    node [shape=box style=filled fontname="Helvetica" fontsize=11];
    edge [fontname="Helvetica" fontsize=9];

    Dashboard   [label="Dashboard\\n(Streamlit)"       fillcolor="#ffe8cc"];
    NBI         [label="NorthBound Interface\\n(FastAPI :8000)" fillcolor="#fff3cd"];
    Decision    [label="Decision Algorithm\\n(First-Fit)"      fillcolor="#e2e3e5"];
    OpenStack   [label="OpenStack\\nDevStack"         fillcolor="{classical_color}" color="#28a745"];
    QuantumAgent[label="Quantum Agent\\n(:8001)"      fillcolor="{quantum_color}"  color="#0066cc"];
    QServer1    [label="Q-Server 1\\n192.168.1.200"   fillcolor="{quantum_color}"  color="#0066cc"];
    QServer2    [label="Q-Server 2\\n192.168.1.201"   fillcolor="{quantum_color}"  color="#0066cc"];

    Dashboard    -> NBI          [{active_edge} label="POST /process"];
    NBI          -> Decision     [{active_edge}];
    Decision     -> OpenStack    [{cl_edge} label="classical"];
    Decision     -> QuantumAgent [{q_edge}  label="quantum"];
    QuantumAgent -> QServer1     [{q_edge}];
    QuantumAgent -> QServer2     [{q_edge}];
}}
"""


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚡ Hybrid Orchestrator")
    st.caption("TFG — Datacenter Dashboard")
    st.divider()

    backend_ok = False
    try:
        requests.get(ORCHESTRATOR_URL + "/docs", timeout=2)
        backend_ok = True
    except Exception:
        pass

    if backend_ok:
        st.success("Orchestrator online")
    else:
        st.warning("Orchestrator offline")

    st.divider()

    total = len(st.session_state.petition_history)
    successful = sum(1 for p in st.session_state.petition_history if p.get("status") == "allocated")
    failed     = total - successful

    st.metric("Petitions sent",  total)
    st.metric("Allocated",       successful)
    st.metric("Failed",          failed)

    if st.button("Clear history", use_container_width=True):
        st.session_state.petition_history = []
        st.session_state.last_result = None
        st.session_state.last_petition = None
        st.rerun()


# ── Main tabs ──────────────────────────────────────────────────────────────────
tab_form, tab_infra, tab_flow = st.tabs(["📋 Submit Petition", "🖥️ Infrastructure", "🔀 Petition Flow"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SUBMIT PETITION
# ══════════════════════════════════════════════════════════════════════════════
with tab_form:
    st.header("Submit Service Petition")
    st.caption("Fill in the resource requirements for the legacy service to be migrated/allocated.")

    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        with st.form("petition_form", clear_on_submit=False):
            st.subheader("Service Parameters")

            service_name   = st.text_input("Service Name", placeholder="e.g. my-service-01")
            cpu            = st.number_input("CPU (vCPUs)", min_value=1, max_value=32,  value=1, step=1)
            memory         = st.number_input("Memory (MB)", min_value=256, max_value=65536, value=1024, step=256)
            storage        = st.number_input("Storage (GB)", min_value=1, max_value=1000, value=10, step=1)
            execution_time = st.number_input("Execution Time (s)", min_value=1, max_value=86400, value=60, step=1)

            st.divider()
            col_sub, col_hint = st.columns([1, 2])
            with col_sub:
                submitted = st.form_submit_button("Submit →", use_container_width=True, type="primary")
            with col_hint:
                flavor_hint = "ds2G (2 vCPU / 2 GB)" if (cpu > 1 or memory > 1024) else "ds1G (1 vCPU / 1 GB)"
                st.info(f"Expected flavor: **{flavor_hint}**")

            if submitted:
                if not service_name.strip():
                    st.error("Service name cannot be empty.")
                else:
                    payload = {
                        "service_name": service_name.strip(),
                        "cpu": cpu,
                        "memory": memory,
                        "storage": storage,
                        "execution_time": execution_time,
                    }
                    with st.spinner("Sending petition to orchestrator…"):
                        status_code, response = post_petition(payload)

                    entry = {
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "service_name": service_name.strip(),
                        "cpu": cpu,
                        "memory": memory,
                        "storage": storage,
                        "status": response.get("status", "error"),
                        "type": response.get("type", "—"),
                        "server_id": response.get("server_id", response.get("detail", "—")),
                        "http_code": status_code,
                    }
                    st.session_state.petition_history.insert(0, entry)
                    st.session_state.last_result = (status_code, response)
                    st.session_state.last_petition = payload

    with col_result:
        st.subheader("Last Response")
        if st.session_state.last_result:
            status_code, response = st.session_state.last_result
            if status_code == 200:
                alloc_type = response.get("type", "")
                badge = "quantum" if alloc_type == "quantum" else "classical"
                st.success(f"Allocated ({alloc_type})")
                st.json(response)
            else:
                st.error(f"HTTP {status_code}: {response.get('detail', 'Unknown error')}")
                st.json(response)
        else:
            st.info("Submit a petition to see the response here.")

        st.divider()
        # Delete section
        st.subheader("Delete Server")
        del_name = st.text_input("Server name to delete", placeholder="e.g. my-service-01", key="del_name")
        if st.button("Delete →", type="secondary"):
            if del_name.strip():
                with st.spinner("Deleting…"):
                    code, resp = delete_server(del_name.strip())
                if code == 200:
                    st.success(f"Deleted: {resp}")
                else:
                    st.error(f"Error: {resp.get('detail', resp)}")

    # History table
    st.divider()
    st.subheader("Petition History")
    if st.session_state.petition_history:
        df = pd.DataFrame(st.session_state.petition_history)
        df.index = range(1, len(df) + 1)

        def color_status(val):
            if val == "allocated":
                return "background-color: #d4edda"
            elif val == "error":
                return "background-color: #f8d7da"
            return ""

        styled = df.style.applymap(color_status, subset=["status"])
        st.dataframe(styled, use_container_width=True)
    else:
        st.caption("No petitions submitted yet.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — INFRASTRUCTURE
# ══════════════════════════════════════════════════════════════════════════════
with tab_infra:
    st.header("Infrastructure Status")

    col_refresh, col_auto = st.columns([1, 3])
    with col_refresh:
        refresh = st.button("🔄 Refresh status", use_container_width=True)
    with col_auto:
        st.caption("Connect the orchestrator and click Refresh to pull live data.")

    st.divider()

    # ── Quantum servers ────────────────────────────────────────────────────────
    st.subheader("⚛️ Quantum Servers")

    q_status = None
    if refresh:
        q_status = get_quantum_status()

    q_col1, q_col2 = st.columns(2)

    for idx, (col, qsrv) in enumerate(zip([q_col1, q_col2], QUANTUM_SERVERS)):
        with col:
            st.markdown(f"**{qsrv['name']}** — `{qsrv['host']}`")

            used_qbits = 0
            used_shots = 0
            if q_status and "quantum" in q_status:
                qdata = q_status["quantum"]
                if isinstance(qdata, list) and len(qdata) > idx:
                    used_qbits = qdata[idx].get("used_qbits", 0)
                    used_shots = qdata[idx].get("used_shots", 0)

            g1, g2 = st.columns(2)
            with g1:
                st.plotly_chart(
                    resource_gauge("Qbits used", used_qbits, qsrv["qbits"], "qubits", "#0066cc"),
                    use_container_width=True, key=f"q_qbits_{idx}"
                )
            with g2:
                st.plotly_chart(
                    resource_gauge("Shots used", used_shots, qsrv["shots"], "shots", "#6610f2"),
                    use_container_width=True, key=f"q_shots_{idx}"
                )

            with st.expander("Full capacity"):
                st.table(pd.DataFrame([{
                    "Resource": "Qbits",          "Total": qsrv["qbits"],         "Unit": "qubits"},
                    {"Resource": "Shots",          "Total": qsrv["shots"],         "Unit": "shots"},
                    {"Resource": "Circuit depth",  "Total": qsrv["circuit_depth"], "Unit": "gates"},
                    {"Resource": "Q-Storage",      "Total": qsrv["qstorage"],      "Unit": "bytes"},
                ]))

    st.divider()

    # ── Classical (OpenStack/DevStack) servers ─────────────────────────────────
    st.subheader("🖥️ Classical Servers (OpenStack / DevStack)")

    col_classic, col_flavor = st.columns([2, 1])

    with col_classic:
        if refresh and backend_ok:
            st.info("Live data requires orchestrator online and OpenStack connection.")

        if st.session_state.petition_history:
            allocated = [p for p in st.session_state.petition_history if p["status"] == "allocated" and p["type"] == "classical"]
            if allocated:
                df_servers = pd.DataFrame(allocated)[["timestamp", "service_name", "cpu", "memory", "storage", "server_id"]]
                df_servers.columns = ["Allocated at", "Name", "vCPU", "RAM (MB)", "Storage (GB)", "Server ID"]
                st.dataframe(df_servers, use_container_width=True)
            else:
                st.caption("No classical servers allocated in this session.")
        else:
            st.caption("No petitions submitted yet.")

    with col_flavor:
        st.markdown("**Available Flavors**")
        flavors_df = pd.DataFrame([
            {"Flavor": "ds1G", "vCPU": 1, "RAM (MB)": 1024, "Disk (GB)": 10},
            {"Flavor": "ds2G", "vCPU": 2, "RAM (MB)": 2048, "Disk (GB)": 20},
        ])
        st.dataframe(flavors_df, use_container_width=True, hide_index=True)

        st.markdown("**Selection rule**")
        st.markdown("- `cpu > 1` or `memory > 1024` → **ds2G**\n- Otherwise → **ds1G**")

    st.divider()

    # ── Session summary chart ──────────────────────────────────────────────────
    if st.session_state.petition_history:
        st.subheader("Session Allocation Summary")

        history = st.session_state.petition_history
        classical_count = sum(1 for p in history if p["type"] == "classical")
        quantum_count   = sum(1 for p in history if p["type"] == "quantum")
        failed_count    = sum(1 for p in history if p["status"] != "allocated")

        fig_pie = go.Figure(go.Pie(
            labels=["Classical", "Quantum", "Failed"],
            values=[classical_count, quantum_count, failed_count],
            marker_colors=["#28a745", "#0066cc", "#dc3545"],
            hole=0.45,
        ))
        fig_pie.update_layout(title="Allocations by type", height=280, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PETITION FLOW
# ══════════════════════════════════════════════════════════════════════════════
with tab_flow:
    st.header("Petition Flow")
    st.caption("The diagram highlights the path taken by the last submitted petition.")

    last_type = None
    if st.session_state.last_result:
        _, resp = st.session_state.last_result
        last_type = resp.get("type")  # "classical" | "quantum" | None

    col_diag, col_steps = st.columns([3, 2], gap="large")

    with col_diag:
        st.graphviz_chart(flow_diagram(last_type), use_container_width=True)

    with col_steps:
        st.subheader("Step-by-step status")

        steps = [
            ("1", "Dashboard",            "Petition submitted by user",           True),
            ("2", "NorthBound Interface", "POST /process received by FastAPI",    bool(st.session_state.last_result)),
            ("3", "Decision Algorithm",   "First-Fit allocation computed",        bool(st.session_state.last_result and st.session_state.last_result[0] == 200)),
            ("4", "Allocation",           f"Server created ({last_type or '…'})", bool(last_type)),
        ]

        for num, title, desc, done in steps:
            icon = "✅" if done else "⏳"
            with st.container():
                st.markdown(f"{icon} **Step {num}: {title}**")
                st.caption(desc)
            if num != "4":
                st.markdown("↓")

        if st.session_state.last_petition:
            st.divider()
            st.subheader("Last petition payload")
            st.json(st.session_state.last_petition)

        if st.session_state.last_result:
            code, resp = st.session_state.last_result
            st.divider()
            st.subheader("Orchestrator response")
            if code == 200:
                st.success(f"HTTP {code} — {resp.get('status', 'ok')}")
            else:
                st.error(f"HTTP {code} — {resp.get('detail', 'error')}")
            st.json(resp)

    # ── Flow explanation ───────────────────────────────────────────────────────
    st.divider()
    st.subheader("Architecture overview")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**Dashboard**\n\nStreamlit UI. Submits petitions via HTTP to the orchestrator and displays results.")
    with c2:
        st.markdown("**NorthBound Interface**\n\nFastAPI service on port 8000. Validates the request and forwards it to the Decision Algorithm.")
    with c3:
        st.markdown("**Decision Algorithm**\n\nFirst-Fit: checks DevStack capacity. Selects flavor (ds1G / ds2G) and provisions via OpenStack SDK.")
    with c4:
        st.markdown("**Quantum Agent**\n\nPort 8001. Converts legacy resource specs to qubit requirements and allocates on Q-Server 1 or 2 (127 qubits each).")
