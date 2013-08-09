#constants file

db_folder = "database/"
db_filename = db_folder + "powerwatch.db"

db_test_accounts = """INSERT INTO account(account_name) VALUES (\'TEST ACCOUNT\');
                      INSERT INTO account(account_name) VALUES (\'PLDT DataCenter\');
                      INSERT INTO account(account_name) VALUES (\'Google Servers\');
                      INSERT INTO account(account_name) VALUES (\'UP DILNET\');
                      INSERT INTO account(account_name) VALUES (\'Amazon Web Services\');"""

db_init_script = """CREATE TABLE IF NOT EXISTS account (account_id INTEGER PRIMARY KEY, account_name TEXT, UNIQUE (account_name));
					CREATE TABLE IF NOT EXISTS devices (device_id INTEGER PRIMARY KEY, account_id INT, device_name TEXT, ip_address TEXT, 
                  FOREIGN KEY (account_id) REFERENCES account(account_id));
					CREATE TABLE IF NOT EXISTS device_readings (device_id INT, voltage REAL, current REAL, watts REAL,
					va REAL, vr REAL, pf REAL,time REAL, FOREIGN KEY (device_id) REFERENCES devices(device_id)); """

db_insert_reading = """INSERT INTO device_readings(device_id, voltage, current, watts, pf, va,vr, time) VALUES(\'%(device_id)s\', %(volt)f, %(amp)f, %(watts)f,
					%(pf)f, %(va)f, %(vr)f, \'%(dt)s\');"""

db_insert_pdu = """INSERT INTO devices(account_id, device_name, ip_address) VALUES (%(account_id)d, \'%(pdu_name)s\', \'%(ip_address)s\')"""

#JSON keywords
VOLT = "volt"
AMP = "amp"
WATT = "watts"
VA = "va"
PF = "pf"