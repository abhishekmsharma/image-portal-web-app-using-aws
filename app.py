from flask import Flask, request, Response, render_template, jsonify
from warrant import Cognito
import sys
import json
import mysql.connector
from mysql.connector import errorcode

app = Flask(__name__)

# all configurations
mySQLConfig = {
	  'user': 'abhishek',
	  'password': '0000',
	  'host': '127.0.0.1',
	  'database': 'cs218imageportal_db',
	  'raise_on_warnings': True
	}

cognitoPoolID = 'us-east-2_4NELA3imh'
cognitoAppClient = '3kl9bhn4bst09fbpo3mc2s3mo6'
cognitoAccessKey = 'AKIA2VGGOTNNR26EU3XB'
cognitoSecretyKey = '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'

HEADER = {'Access-Control-Allow-Origin': '*'}

@app.route('/')
def index():
	#print('in Home',username, file=sys.stderr)
	return render_template('signup.html')

@app.route('/signup', methods=['GET'])
def signUpPage():
	return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signUpProcess():
	print ("In signup process", file=sys.stderr)
	values = dict()
	email = request.form['email']
	username = request.form['username']
	password = request.form['password']
	print (username, email, password, file=sys.stderr)

	if username and email and password:
		print ("In if", file=sys.stderr)
		print ("Creating object")
		u = Cognito(cognitoPoolID,cognitoAppClient, access_key=cognitoAccessKey, 
			secret_key=cognitoSecretyKey)

		print ("here", file=sys.stderr)
		u.add_base_attributes(email=email)
		try:
			u.register(username, password)
			values['success'] = "Account created for user " + username
			print ("Returning", values, file=sys.stderr)
			return jsonify(values)
		except Exception as e:
			print ("Signup failed, Error:", e, file=sys.stderr)
			values['error'] = str(e)
			return jsonify(values)


	print ("Returning", values, file=sys.stderr)
	values['error'] = 'Please enter all the fields'
	return jsonify(values)

@app.route('/check-status', methods=['GET'])
def verify():
	return 'service is up'
	
# @app.route('/welcome/<string:username>', methods=['GET'])
# def welcome(username):
# 	print('in Welcome',username, file=sys.stderr)
# 	values = {"Browser":"Chrome", "Names":username}
# 	return jsonify(values)
	
# @app.route('/welcome/add/<int:a>', methods=['POST'])
# def addNumbers():
# 	a = request.args.get('a', 0, type=int)
# 	b = request.args.get('a', 0, type=int)
# 	c = a+b
# 	print ("Sum is ",c, file=sys.stderr)
# 	values = {"result": c}
# 	return json.dumps(values)

# @app.route('/welcome/add/<int:a>', methods=['GET'])
# def addSelfNumbers(a):
# 	c = a + a
# 	print ("Sum is ",c, file=sys.stderr)
# 	values = {"sum": c}
# 	response = app.response_class(response=json.dumps(values),
#                                   status=200,
#                                   mimetype='application/json')
# 	return response
	
# @app.route('/process', methods=['POST'])
# def process():

# 	values = dict()
# 	email = request.form['email']
# 	name = request.form['name']

# 	if name and email:
# 		newName = name[::-1]
# 		values['name'] = newName
# 		print ("Returning", values, file=sys.stderr)
# 		#return json.dumps(values)
# 		return jsonify(values)

# 	print ("Returning", values, file=sys.stderr)
# 	values['error'] = 'Missing data!'
# 	return jsonify({'error' : 'Missing data!'})
# 	return json.dumps(values)

@app.route('/users', methods=['GET'])
def getUsers():

	try:
		cnx = mysql.connector.connect(**mySQLConfig)
		cursor = cnx.cursor()

	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Invalid credentials")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exist")
		else:
			print(err)
		cnx.close()

	query = ("SELECT name,email FROM users")

	cursor.execute(query)

	values = dict()
	for name, email in cursor:
		values[name] = email

	response = app.response_class(response=json.dumps(values),
                                  status=200,
                                  mimetype='application/json')
	return response
	
# @app.route('/getCities', methods=['GET'])
# def getCities():
# 	import mysql.connector
# 	from mysql.connector import errorcode

# 	try:
# 	  cnx = mysql.connector.connect(**mySQLConfig)
# 	  cursor = cnx.cursor()

# 	except mysql.connector.Error as err:
# 	  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
# 	    print("Something is wrong with your user name or password")
# 	  elif err.errno == errorcode.ER_BAD_DB_ERROR:
# 	    print("Database does not exist")
# 	  else:
# 	    print(err)
# 	  cnx.close()


# 	query = ("SELECT Name, CountryCode FROM city")

# 	cursor.execute(query)
# 	values = dict()

# 	for Name, CountryCode in cursor:
# 		values[Name] = CountryCode

# 	return jsonify(values)

if __name__ == '__main__':
	app.run(port='319', debug=True)