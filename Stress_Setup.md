# **1. Add stress.sh under test user**

the path should be something like ```/home/test_user/stress.sh```

also dont forget to give the file execution privileges 
```
sudo chmod +x /home/test_user/stress.sh
```


# **2. Make the systemd service**

```sudo vim /etc/systemd/system/\<name of service like "stress.service"\>```

paste this inside and change the values like path and user accordingly

```
[Unit]
Description=Custom Stress Test
After=multi-user.target

[Service]
Type=notify
User=test_user
WorkingDirectory=/home/test_user
ExecStart=/bin/bash /home/test_user/stress.sh
Restart=always
RestartSec=5
WatchdogSec=30s
NotifyAccess=all
KillMode=control-group
TimeoutStopSec=15s

[Install]
WantedBy=multi-user.target
```
