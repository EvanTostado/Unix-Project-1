import streamlit as st
import pandas as pd
import requests
from datetime import datetime

SERVERS =  {
    "VM 1:": "http://127.0.0.1:8081/",
    "VM 2": "http://127.0.0.1:8082/",
    "VM 3": "http://127.0.0.1:8083/",
    "VM 4": "http://127.0.0.1:8084/",
}

st.set_page_config(page_title="Linux Performance Monitor Dashboard", layout="wide")
st.title("Linux Performance Monitor Dashboard")
st.caption("Four Google Cloud Vms - Live System Statistics")

#separate historical measurements for each vm

if "vm_history" not in st.session_state:
    st.session_state.vm_history = {name: [] for name in SERVERS}

selected_vm = st.selectbox("Detailed graphs for", list(SERVERS))

@st.fragment(run_every="5s")
def update_dashboard():
    latest = {}
    errors = {}

    for name, url in SERVERS.items():
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            reading = {
                "Time": datetime.now(),
                "CPU": float(data["cpu_usage_percent"]),
                "Memory": float(data["memory_usage_percent"]),
                "Disk": float(str(data["disk_usage_percent"]).replace("%", "")),
                "Network": int(data["network_rx_bytes"]),
                "Processes": int(data["running_processes"]),
            }
            #cpu threshold alert
            if reading["CPU"] > 80:
                st.warning(
                    f"{name}: high cpu usage! ({reading['CPU']:.1f})"
                )

            #memory threshold alert
            if reading["Memory"] > 70:
                st.error(
                    f"{name}: high memory usage! ({reading['Memory']:.1f})"
                )

            st.session_state.vm_history[name].append(reading)
            st.session_state.vm_history[name] = st.session_state.vm_history[name][-120:]
            latest[name] = reading

        except (requests.RequestException, ValueError, KeyError, TypeError) as error:
            errors[name] = str(error)

    st.subheader("Current Metrics")
    columns = st.columns(4)

    for column, name in zip(columns, SERVERS):
        with column:
            st.markdown(f"**{name}**")

            if name not in latest:
                st.error("Unavailable")
                continue
            m = latest[name]
            st.metric("CPU", f"{m['CPU']:.1f}%")
            st.metric("Memory", f"{m['Memory']:.1f}%")
            st.metric("Disk Space Used", f"{m['Disk']:.1f}%")
            st.metric("Network Rx (total)", f"{m['Network']:,} B")
            st.metric("Process count", m["Processes"])

    if errors:
        with st.expander(f"Connection details ({len(errors)} unavailable"):
            for name, error in errors.items():
                st.warning(f"{name}: {error}")


        #sample indexes allow a side by side comparison without changing the api
        #these are not synchronized timestamps if a vm misses a sample

    for metric in ("CPU", "Memory"):
        comparison = pd.DataFrame({
            name: pd.Series([entry[metric] for entry in st.session_state.vm_history[name]])
                for name in SERVERS
            })
        st.subheader(f"{metric} utilization - all VMs")
        if comparison.notna().any().any:
            st.line_chart(comparison, x_label="Sample (approximately every 5 seconds", y_label="Percent")
        else:
            st.info("No readings yet")

        st.subheader(f"Detailed history - {selected_vm}")
        history = st.session_state.vm_history[selected_vm]
        if history:
            df = pd.DataFrame(history).set_index("Time")
            st.write("CPU and Memory Utilization (%)")
            st.line_chart(df[["CPU", "Memory"]])
            st.write("Disk Space Used (%) ")
            st.line_chart(df["Disk"])
            st.write("Network Received (cumulative bytes)")
            st.line_chart(df["Network"])
            st.write("Process Count")
            st.line_chart(df["Processes"])

        else:
            st.info("No readings yet from this vm")

        st.caption(f"Last refresh: {datetime.now():%H:%M:%S}")



update_dashboard()
