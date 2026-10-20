# **1. Ensure that netcat is installed**

```
sudo apt update && sudo apt install netcat-traditional -y
sudo update-alternatives --set nc /bin/nc.traditional
```

# **2. Add the api under test user**

the path should be something like ```/home/test_user/api.sh```

also dont forget to give the file execution privileges 
```
sudo chmod +x /home/test_user/api.sh
```


# **3. Make the systemd service**

```sudo vim /etc/systemd/system/\<name of service like "api.service"\>```

paste this inside and change the values like path and user accordingly

```
[Unit]
Description=Bash API Agent
After=network.target

[Service]
ExecStart=/home/test_user/api.sh
Restart=always
WatchdogSec=60s
User=test_user

[Install]
WantedBy=multi-user.target
```
Then reload the daemon and start the service by hand
```
sudo systemctl daemon-reload
sudo systemctl enable api.service
sudo systemctl start api.service
```
# **4. Setup the firewall**
- First Obtain your IP
- Second in the google cloud console navigate to **VPC Network** > **Firewall**
- Set target tags to Allow all Network Targets
- Third (for testing there is allow-evan-laptop) Create a rule allowing Ingress traffic on tcp:8080, 8081, 8082, 8083, 8084
- Fourth Set the Source IPv4 ranges to your client machine's IP address with a /32

# **5. Test the Connection**
You can run this command to test the connection (the external ip of the vm needs to be added to the firewall to work)
```
curl -v http://<server-public-ip>:8080
```
# **6. Python external connection**
After verifying the connection you can use the network_test.py script 
to test the vm external connection make sure to change the ip in the script to be the vm's


