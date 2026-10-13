#!/bin/bash

# Define the named pipe location
PIPE="/tmp/metrics_pipe"

# Create the named pipe if it does not already exist
if [[ ! -p $PIPE ]]; then
    mkfifo $PIPE
fi

echo "Starting Bash API Agent on port 8080..."

# Continuous loop to keep the API listening
while true; do
    # Netcat listens on port 8080. Input from the network is piped to our processing block.
    # Output from the processing block is routed back to netcat via the named pipe.
    nc -q 0 -l -p 8080 < $PIPE | {
        # Read the first line of the HTTP request
        read request 
        
        # Discard the remaining HTTP headers to prevent hanging
        while read -t 1 header; do
            [ "$header" == $'\r' ] && break
        done

        # 1. Collect 5 System Metrics using native Linux commands
        cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
        mem=$(free -m | awk 'NR==2{printf "%.2f", $3*100/$2 }')
        disk=$(df -h / | awk '$NF=="/"{printf "%s", $5}')
        net_rx=$(cat /sys/class/net/ens4/statistics/rx_bytes)
        procs=$(ps aux | wc -l)

        # 2. Construct the HTTP Response
        echo -e "HTTP/1.0 200 OK\r"
        echo -e "Content-Type: application/json\r"
        echo -e "Connection: close\r\n\r"
        
        # 3. Output the metrics as a JSON payload
        echo "{"
        echo "  \"cpu_usage_percent\": \"$cpu\","
        echo "  \"memory_usage_percent\": \"$mem\","
        echo "  \"disk_usage_percent\": \"$disk\","
        echo "  \"network_rx_bytes\": \"$net_rx\","
        echo "  \"running_processes\": \"$procs\""
        echo "}"
    } > $PIPE
done
