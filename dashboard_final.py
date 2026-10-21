import streamlit as st
import pandas as pd
import requests
from datetime import datetime
#each server and ip with port number, this may change depending on the user using python dictionary
SERVERS =  {
    "VM 1:": "http://127.0.0.1:8081/",
    "VM 2": "http://127.0.0.1:8082/",
    "VM 3": "http://127.0.0.1:8083/",
    "VM 4": "http://127.0.0.1:8084/",
}
#configure dashboard layout and title
st.set_page_config(page_title="Linux Performance Monitor Dashboard", layout="wide")
st.title("Linux Performance Monitor Dashboard")
st.caption("Four Google Cloud Vms - Live System Statistics")

#initialize separate historical metrics for each vm
if "vm_history" not in st.session_state: #checks whether the historical data has already been initialized
    st.session_state.vm_history = {name: [] for name in SERVERS} #creates a dictionary containing one empty list for each vm

#allow the user to select a VM for detailed graphs
selected_vm = st.selectbox("Detailed graphs for", list(SERVERS)) #creates dropdown menu
#automatically refresh dashboard metrics every five seconds
@st.fragment(run_every="5s")#decorator to run dashboard every 5 seconds
def update_dashboard():
    #store current metrics and connection errors
    latest = {}#creates empty dictionary for the most recent successful measurement for each vm
    errors = {} #creates dictionary to track erros
#request current system metrics from each VM's API
    for name, url in SERVERS.items():
        try:
            response = requests.get(url, timeout=10)
            #raise an exception if the API request fails
            response.raise_for_status()
            #convert the API's JSON response into a dictionary
            data = response.json()
            #Extract and format system metrics for visualization
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

            st.session_state.vm_history[name].append(reading) #appends measurement to the correct vm history
            st.session_state.vm_history[name] = st.session_state.vm_history[name][-120:] #keeps 120 most recent measurements
            latest[name] = reading #store newest measurement for the current metrics display

        except (requests.RequestException, ValueError, KeyError, TypeError) as error: #records error and does not crash dashboard
            errors[name] = error

    #display the latest available measurements for all four Vms
    st.subheader("Current Metrics")
    columns = st.columns(4) #display vm cards

    for column, name in zip(columns, SERVERS): #pair each column with one vm
        with column: #tell streamlit where to display the elements
            st.markdown(f"**{name}**")
            #mark unavailable Vms without interrupting the other displays.
            if name not in latest:
                st.error("Unavailable")
                continue
            m = latest[name]
            st.metric("CPU", f"{m['CPU']:.1f}%")
            st.metric("Memory", f"{m['Memory']:.1f}%")
            st.metric("Disk Space Used", f"{m['Disk']:.1f}%")
            st.metric("Network Rx (total)", f"{m['Network']:,} B")
            st.metric("Process count", m["Processes"])
    #show the reason for each failed api request in an expandable section
    if errors:
        with st.expander(f"Connection details ({len(errors)} unavailable"):
            for name, error in errors.items():
                st.warning(f"{name}: {error}")


        #sample indexes allow a side by side comparison without changing the api
        #these are not synchronized timestamps if a vm misses a sample
        #compare CPU and memory history across the four VM's
    for metric in ("CPU", "Memory"):
        comparison = pd.DataFrame({
            name: pd.Series([entry[metric] for entry in st.session_state.vm_history[name]])
                for name in SERVERS
            })
        st.subheader(f"{metric} utilization - all VMs")
        if comparison.notna().any().any:
            st.line_chart(comparison, x_label="Sample (approximately every 5 seconds", y_label="Percent") #create a line chart containing one line for each vm
        else:
            st.info("No readings yet")
        #display separate historical graphs for the selected VM
        st.subheader(f"Detailed history - {selected_vm}")
        history = st.session_state.vm_history[selected_vm]
        #avoid drawing graphs until measurements have been collected
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
#show when the dashboard last completed its refresh
        st.caption(f"Last refresh: {datetime.now():%H:%M:%S}")


#show the live dashboard
update_dashboard()
