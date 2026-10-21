#!/bin/bash

LOG="$HOME/stress_log.log"

systemd-notify --ready

run_stress() {
        stress-ng "$@" >> "$LOG" 2>&1 &
        pid=$!

        while kill -0 "$pid" 2>/dev/null; do
        systemd-notify WATCHDOG=1
        sleep 5
    done

        wait "$pid"
}

trap 'exit 0' TERM INT



while true; do
        echo "$(date): CPU stress" >>" $LOG"
        run_stress --cpu 1 --timeout 30s --metrics-brief

        echo "$(date): Memory stress" >> "$LOG"
        run_stress --vm 1 --vm-bytes 64M --timeout 45s --metrics-brief

        echo "$(date): Disk stress" >> "$LOG"
        run_stress -hdd 1 -hdd-bytes 64M --timeout 30s --metrics-brief

        echo "$(date): Starting network socket stress" >> "$LOG"
        run_stress --sock 1 --timeout 30s --metrics-brief

        echo "$date: Starting context switchinng stress" >> "$LOG"
        run_stress --switch 1 --timeout 30s --metrics-brief

done
