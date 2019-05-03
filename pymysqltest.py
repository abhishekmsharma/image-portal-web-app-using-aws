import sys
import logging
import pymysql

rds_host  = 'imageportaldb.czkcl5taihag.us-east-2.rds.amazonaws.com'
name = 'cs218rds'
password = 'cs218rds'
db_name = 'mysql'
port = 3306

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rds_host, user=name,
                           passwd=password, db=db_name, connect_timeout=5)
except:
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
    sys.exit()

logger.info("SUCCESS: Connection to RDS mysql instance succeeded")
item_count = 0

with conn.cursor() as cur:
	#cur.execute("CREATE DATABASE newdb");
	cur.execute("create table newdb.Employee3 (EmpID  int NOT NULL, Name varchar(255) NOT NULL, PRIMARY KEY (EmpID))")
	cur.execute('insert into newdb.Employee3 (EmpID, Name) values(1, "Joe")')
	cur.execute('insert into newdb.Employee3 (EmpID, Name) values(2, "Bob")')
	cur.execute('insert into newdb.Employee3 (EmpID, Name) values(3, "Mary")')
	conn.commit()
	cur.execute("select * from newdb.Employee3")
	for row in cur:
		item_count += 1
		logger.info(row)

print ("Added %d items to RDS MySQL table" %(item_count))
	
