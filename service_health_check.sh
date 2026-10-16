#!/bin/bash

# checks if an argument was provided
if [ -z "$1" ]; then
    echo "Error: No service name provided."
    exit 1
fi

# variable to first argument for readability
SERVICE_NAME=$1

# check and restart using the variable
# uses the exit codes of the program to know its output, silences output with --quiet
# ! flips the result only running when the program is not active
if ! systemctl is-active --quiet "$SERVICE_NAME"; then
    systemctl restart "$SERVICE_NAME"
    echo "$(date): $SERVICE_NAME was down and successfully restarted." >> /var/log/service_restarts.log
fi
