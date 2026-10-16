#!/bin/bash

PIPE="/tmp/metrics_pipe"
PORT=8080

#create the named pipe if needed
if [[ ! -p "$PIPE" ]]; then
    mkfifo "$PIPE" || exit 1

fi

echo "Starting Bash API on port $PORT..."

#clean up when stopping the service
trap 'exit 0' TERM INT

while true; do

        #collect metrics in a separate process

        (
            cpu=$(top -bn2 -d 0.2 | grep 'Cpu(s)' |
                tail -1 | awk '{print $2 + $4}')

            mem=$(free | awk '/^Mem:/ {
                printf "%.2f", ($2-$7)*100/$2
           }')

           disk=$(df -P / | awk 'NR==2 {print $5}')
           net_rx=$(cat /sys/class/net/ens4/statistics/rx_bytes)
           procs=$(ps -e --no-headers | wc -l)

           printf '{"cpu_usage_percent":"%s","memory_usage_percent":"%s","disk_usage_percent":"%s","network_rx_bytes":"%s","running_processes":"%s"}\n' \
                        "$cpu" "$mem" "$disk" "$net_rx" "$procs" > "$PIPE"

        ) &

        #read metrics from named pipe
        IFS= read -r json < "$PIPE"


        #build HTTP response and pass it to Netcat
        {
                printf 'HTTP/1.1 200 OK\r\n'
                printf 'Content-Type: application/json\r\n'
                printf 'Content-Length: %s\r\n' "${#json}"
                printf 'Connection: close\r\n'
                printf '\r\n'
                printf '%s' "$json"
        } | nc -l -p "$PORT" -q 1

done
