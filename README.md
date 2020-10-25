# AsusRouterMonitor
Monitor your Asus router with Grafana.

![](https://github.com/jphilll/AsusRouterMonitor/raw/main/asusMonitor.png)
This is what it looks like.

## HowTo

### The `DATA` part, how to extract data from Asus router
Using `asusMonitor.py` to get all the data. It provides all the data shown in the picture above.

1. Python version I am using == Python 3.9.0, all versions of python 3 is probably fine. And I am using it on Debian 9.
2. Install all the required python packages `pip3 install -r ./requirements.txt`
3. Modify the basic information part of `asusMonitor.py`.

```python
# Input basic information below..
## Your router's address (format: http://ip_address or https://ip_address)
asusAddr = '' # eg. http://192.168.1.1
## Your Asus router's management web page login user and password
asusUser = ''
asusPasswd = ''
## Your MySQL infomation (IP address, user, password, database, table)
sqlIP = '' # MySQL IP address, eg. 127.0.0.1
sqlPort = '3306' # Default port is 3306
sqlUser = '' # MySQL Username
sqlPasswd = '' # MySQL Password
sqlDb = '' # MySQL Database you're gonna use
sqlTable = '' # MySQL Table you're gonna use 
```
4. Run the python script `python3 asusMonitor.py`
5. (Optional) You can also run it as a system service, modify the `asusMonitor.service` and put it to `/usr/lib/systemd/system/` or `/usr/local/lib/systemd/system/`, then `systemctl daemon-reload`, `systemctl start asusMonitor.service`.
6. Log is redirected to `/var/log/asusMonitor.log`.

### The `DATABASE` part, how to store the data
Using MySQL to store data. Percisely, I use MySQL docker for convenience.

1. Install Docker.
2. Modify the mysql part of `docker-compose.yaml` to meet your demand.
3. `docker-compose -f ./docker-compose.yaml up -d` and MySQL in running as docker container.
4. If you would like to install MySQL, I use mysql == 5.7.31 here to avoid problems in newer versions.
5. Create a database named `db_name`.
  ```mysql
  mysql> CREATE DATABASE db_name;
  ```
6. Create a table named `table_name` with these columns in the database.
  ```mysql
  mysql> CREATE TABLE table_name (
            internetRXSpeed FLOAT, 
            internetTXSpeed FLOAT, 
            wiredRXSpeed FLOAT, 
            wiredTXSpeed FLOAT, 
            wireless2gRXSpeed FLOAT, 
            wireless2gTXSpeed FLOAT, 
            wireless5gRXSpeed FLOAT, 
            wireless5gTXSpeed FLOAT, 
            coretemp2g INT, 
            coretemp5g INT, 
            coretempCPU INT, 
            cpu1Percentage FLOAT, 
            cpu2Percentage FLOAT, 
            ramUsage INT, 
            timeStamp TIMESTAMP NOT NULL PRIMARY KEY);
  ```

### The `VISUAL` part, how to show the data
Using Grafana to show the data. Again, I use Grafana docker for convenience.

1. Install docker.
2. Modify the grafana part of `docker-compose.yaml` to meet your demand. More environment settings can be found on Grafana website.
3. `docker-compose -f ./docker-compose.yaml up -d` and Grafana in running as docker container.
4. Add MySQL as data source.
5. I also put my Grafana config here(`asusMonitor.json`), it's exactly like the image above.
