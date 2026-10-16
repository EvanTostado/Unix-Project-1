# **1. add the service health script to test user**
Then ensure it has execute priviliges
```
sudo chmod +x /home/test_user/service_health_check.sh
```


# **2. add this to the cronjob**

This will be in the system crontab
```
sudo crontab -e
```

```
*/5 * * * * /home/test_user/service_health_check.sh api.service
*/5 * * * * /home/test_user/service_health_check.sh stress.service
```
