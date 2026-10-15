import streamlit as st
import pandas as pd
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8080/"

st.set_page_config(
    page_title="Linux Performance Monitor",
    layout="wide"
)

st.title("Linux Performance Monitoring Dashboard")
st.caption("Google Cloud VM - Live System Statistics")

if "history" not in st.session_state:
    st.session_state.history = []

@st.fragment(run_every="5s")
def update_dashboard():
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()

        cpu = float(data["cpu_usage_percent"])
        memory = float(data["memory_usage_percent"])
        disk = float(data["disk_usage_percent"].replace("%", ""))
        network = int(data["network_rx_bytes"])
        processes = int(data["running_processes"])

        st.session_state.history.append({
            'Time': datetime.now(),
            'CPU': cpu,
            'Memory': memory,
            'Disk': disk,
            'Network': network,
            'Processes': processes
        })

        st.session_state.history = st.session_state.history[-120:]

        col1, col2, col3 = st.columns(3)
        col1.metric("CPU Usage", f"{cpu:.1f}%")
        col2.metric("Memory Usage", f"{memory:.1f}%")
        col3.metric("Disk Usage", f"{disk:.1f}%")

        col4, col5, = st.columns(2)
        col4.metric("Network Received", f"{network:,} bytes")
        col5.metric("Process Count", processes)

        df = pd.DataFrame(st.session_state.history)
        df = df.set_index("Time")

        st.subheader("CPU and Memory Utilization")
        st.line_chart(df[["CPU", "Memory"]])

        st.subheader("Disk Utilization")
        st.line_chart(df[["Disk"]])

        st.subheader("Process Count")
        st.line_chart(df[["Processes"]])

        st.caption(f"Last updated: {datetime.now():%H:%M:%S}")

    except (requests.RequestException, ValueError, KeyError) as error:
        st.error(f"API connection error: {error}")

update_dashboard()