#constants file

db_folder = "database/"
db_filename = db_folder + "powerwatch.db"

db_init_script = """CREATE TABLE IF NOT EXISTS account (account_id INT, rate REAL, cool_ratio TEXT, PRIMARY KEY (account_id));
					CREATE TABLE IF NOT EXISTS devices (device_id INT, account_id INT, status INT, PRIMARY KEY (device_id), 
						FOREIGN KEY (account_id) REFERENCES account(account_id));
					CREATE TABLE IF NOT EXISTS device_readings (device_id INT, voltage REAL, current REAL, power REAL, time TEXT, 
						FOREIGN KEY (device_id) REFERENCES devices(device_id)); """

db_insert_reading = """INSERT INTO device_readings(voltage, current, power, time) VALUES(%(volt)f, %(amp)f, %(pow)f, \'%(dt)s\');"""