import mysql.connector
from mysql.connector import errorcode

config = {
  'user': 'cs218rds',
  'password': 'cs218rds',
  'host': 'imageportaldb.czkcl5taihag.us-east-2.rds.amazonaws.com',
  'database': 'imageportaldb',
  'raise_on_warnings': True
}

try:
  cnx = mysql.connector.connect(**config)
  cursor = cnx.cursor()

except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)

#cursor.execute("USE mysql") # select the database
#cursor.execute("CREATE TABLE INFO(  Username VARCHAR(200),  Image_Caption VARCHAR(1000),  Image_URL VARCHAR(1000),  Upload_Date timestamp  )")
#print(cursor.execute("SHOW TABLES"))

cursor.execute("CREATE DATABASE imageportaldb")

'''
cursor.execute("DROP DATABASE newdb")
query = ("SELECT EmpID, Name FROM newdb.Employee3")

cursor.execute(query)

for EmpID, Name in cursor:
	print (EmpID, Name)
'''

cnx.close()