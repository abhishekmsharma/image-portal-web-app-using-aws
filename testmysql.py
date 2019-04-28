import mysql.connector
from mysql.connector import errorcode

config = {
  'user': 'abhishek',
  'password': '0000',
  'host': '127.0.0.1',
  'database': 'world',
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
  cnx.close()


query = ("SELECT Name, CountryCode FROM city")

cursor.execute(query)

for Name, CountryCode in cursor:
	print (Name, CountryCode)

cnx.close()