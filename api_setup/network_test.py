import requests

# Replace with your GCP server's public IP address
API_URL = "http://34.24.17.120:8080"

try:
    # Send an HTTP GET request to the Bash API
    response = requests.get(API_URL, timeout=5)
    response.raise_for_status() 
    
    # Parse the JSON response
    metrics = response.json()

    # Display the metrics in plain text
    print("--- Linux Server Metrics ---")
    print(f"CPU Usage:        {metrics.get('cpu_usage_percent')}%")
    print(f"Memory Usage:     {metrics.get('memory_usage_percent')}%")
    print(f"Disk Usage:       {metrics.get('disk_usage_percent')}")
    print(f"Network RX Bytes: {metrics.get('network_rx_bytes')}")
    print(f"Running Procs:    {metrics.get('running_processes')}")

except requests.exceptions.RequestException as e:
    print(f"Failed to connect to the API: {e}")
