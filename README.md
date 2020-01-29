# kis_tools
Queries the Kismet device by-mac API every x amount of seconds and records basic information to csv or sql.
The data can be used to create your own reports / scripts / timelines to plot timestamp and signal strength information about a mac address

### Requirements
	python3
	pip3 install pymysql
	pip3 install kismet_rest

### Setup
	chmod +x ./kistrack_mac_sql.py
	chmod +x ./kistrack_mac_csv.py
	Run SQL query to setup logging table

### kistrack_mac_sql.py
Track MAC addresses of interest and log to MySQL

Output: device_key, mac_addr, last_seen, signal_rssi, seenby_uuid

### kistrack_mac_csv.py
Track MAC addresses of interest and log to CSV

Output: device_key, mac_addr, last_seen, signal_rssi, seenby_uuid

### Usage
	./kistrack_mac_sql.py -m 00:00:00:00:00:00 -dbu sqlusername -dbn nameofdatabase
	./kistrack_mac_csv.py -m 00:00:00:00:00:00

### Tips
By default the scripts will query the API every 2 seconds. Use -i to specify custom interval in seconds

### SQL Query
	CREATE TABLE `kis_tracked_mac` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `device_key` varchar(255) DEFAULT NULL,
	  `mac_addr` varchar(255) DEFAULT NULL,
	  `last_seen` varchar(45) DEFAULT NULL,
	  `signal_rssi` varchar(45) DEFAULT NULL,
	  `seenby_uuid` varchar(45) DEFAULT NULL,
	  PRIMARY KEY (`id`)
	) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

### Future
- add support for self signed ssl certs
- add the Kismet server name and uuid to the records for historical value
