#constants file

db_folder = "database/"
db_filename = db_folder + "powerwatch.db"

db_init_script = """CREATE TABLE IF NOT EXISTS account (account_id INT, rate REAL, cool_ratio TEXT, PRIMARY KEY (account_id));
					CREATE TABLE IF NOT EXISTS devices (device_id INT, account_id INT, status INT, PRIMARY KEY (device_id), 
						FOREIGN KEY (account_id) REFERENCES account(account_id));
					CREATE TABLE IF NOT EXISTS device_readings (device_id INT, voltage REAL, current REAL, watts REAL,
					va REAL, vr REAL, pf REAL,time REAL, FOREIGN KEY (device_id) REFERENCES devices(device_id)); """

2 + 8 * 7

db_insert_reading = """INSERT INTO device_readings(voltage, current, watts, pf, va,vr, time) VALUES(%(volt)f, %(amp)f, %(watts)f,
					%(pf)f, %(va)f, %(vr)f, \'%(dt)s\');"""

#JSON keywords
VOLT = "volt"
AMP = "amp"
WATT = "watts"
VA = "va"
PF = "pf"