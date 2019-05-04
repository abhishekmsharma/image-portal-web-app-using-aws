from flask import Flask, request, Response, render_template, jsonify, redirect, url_for
from warrant import Cognito
import sys
import json
import os
import pymysql
import datetime
import boto3
import mimetypes
from datetime import datetime
import re
import logging
from logging.handlers import RotatingFileHandler

application = Flask(__name__)

handler = RotatingFileHandler('logs.log', maxBytes=10000, backupCount=1)
formatter = logging.Formatter("[%(asctime)s] {Line: %(lineno)d} %(levelname)s - %(message)s")
handler.setFormatter(formatter)
application.logger.setLevel(logging.INFO)
application.logger.addHandler(handler)


# all configurations
region_name = "us-east-2"

os.environ['AWS_DEFAULT_REGION'] = region_name

mySQLConfig = {
	  'user': 'abhishek',
	  'password': '0000',
	  'host': '127.0.0.1',
	  'database': 'cs218imageportal_db',
	  'raise_on_warnings': True
	}

cognitoPoolID = 'us-east-2_4NELA3imh'
cognitoAppClient = '3kl9bhn4bst09fbpo3mc2s3mo6'
IAMAccessKey = 'AKIA2VGGOTNNR26EU3XB'
IAMSecretyKey = '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'
S3Bucket = 'imageportals3'


rds_host  = 'imageportaldb.czkcl5taihag.us-east-2.rds.amazonaws.com'
rds_name = 'cs218rds'
rds_password = 'cs218rds'
db_name = 'mysql'
instance_name = 'imageportaldb'
table_name = 'uploads'
port = 3306


S3Bucket = 'imageportals3'
BUCKET_BASE_URL = "https://s3.us-east-2.amazonaws.com/imageportals3/"

def printf(s):
	print(s, file=sys.stderr)

def getImageData(user = None, keyword = None):
	conn = pymysql.connect(rds_host, user=rds_name, passwd=rds_password, db=db_name, connect_timeout=5)
	data = list()
	query = ("SELECT * from {}.{} ORDER BY UPLOAD_DATE DESC".format(instance_name,table_name))
	if user:
		query = ("SELECT * from {}.{} WHERE USERNAME = '{}' ORDER BY UPLOAD_DATE DESC".format(instance_name,table_name, user))
	if keyword:
		query = ("SELECT * from {}.{} WHERE IMAGE_CAPTION LIKE '%{}%' ORDER BY UPLOAD_DATE DESC".format(instance_name,table_name, keyword))

	with conn.cursor() as cur:
		cur.execute(query)
		for item in cur:
			imgDate = item[3][:14]
			date = datetime.strptime(imgDate, '%Y%m%d%H%M%S').strftime('%b %d %Y, %H:%M')
			currImage = {'name': item[0], 'caption': item[1], 'image_url': item[2], 'date': date}
			data.append(currImage)
			print (item, file=sys.stderr)

	return data

@application.route('/home')
def home():
	application.logger.info("Opened homepage")
	d = request.cookies
	print(d, file=sys.stderr)
	data = getImageData()

	# data=[{'name': 'ABC', 'caption': 'Caption', 'date': '20 April', 'image_url':'https://i.ytimg.com/vi/xpudcGv-KX8/hqdefault.jpg'},
	# {'name': 'ABC2', 'caption': 'Caption2', 'date': '30 April', 'image_url':'https://s3.us-east-2.amazonaws.com/imageportals3/test_20190503044533579898.jpg'}]
	return render_template('home.html', data = data, title="CS 218 Image Portal - Home Feed")

@application.route('/home/user/<string:username>')
def getImagesForUser(username):
	application.logger.info("Searching images for user: " + username)
	data = getImageData(user = username)
	return render_template('home.html', data = data, title="Search results for user - " + username)

@application.route('/home/keyword/<string:word>')
def getImagesForKeyword(word):
	application.logger.info("Searching images for keyword: " + word)
	data = getImageData(keyword = word)
	return render_template('home.html', data = data, title="Search results for keyword - " + word)

@application.route('/', methods=['GET'])
def index():
	application.logger.info("Opened login page")
	return render_template('login.html')

@application.route('/signup', methods=['GET'])
def signUpPage():
	application.logger.info("Opened signup page")
	return render_template('signup.html')

@application.route('/upload', methods=['GET'])
def uploadPage():
	application.logger.info("Opened upload page")
	return render_template('upload.html')



def uploadImageToPortal(username, image_caption, image_path, image_name, image_extension):
	application.logger.info(username +" initiated an image upload")
	# upload to S3
	session = boto3.Session(aws_access_key_id=IAMAccessKey, 
		aws_secret_access_key = IAMSecretyKey,
		region_name = region_name)

	s3 = session.resource('s3')
	bucket = s3.Bucket(S3Bucket)

	#file_mime = mimetypes.guess_type(image_path)[0] or 'binary/octet-stream'
	file_mime = 'image/png'
	# with open(image_path, 'rb') as data:
	data = image_path
	curr_time = str(datetime.now()).replace("-","").replace(" ",""). replace(":","").replace(".","")
	img_name = image_name + "_" + curr_time + image_extension
	bucket.put_object(Key=img_name, Body=data, ContentType=file_mime, ACL='public-read')
	application.logger.info("Image successfully put to S3")

	# update in RDS
	conn = pymysql.connect(rds_host, user=rds_name, passwd=rds_password, db=db_name, connect_timeout=5)

	IMAGE_URL = BUCKET_BASE_URL + img_name
	insert_query = "INSERT INTO {}.{} VALUES ('{}','{}','{}','{}')".format(instance_name,table_name,username,image_caption,IMAGE_URL,curr_time)
	with conn.cursor() as cur:
		cur.execute(insert_query)
		conn.commit()

	application.logger.info("Record added in RDS")

	application.logger.info(username + "'s image upload completed. S3 link at " + IMAGE_URL)

@application.route('/upload', methods=['POST'])
def uploadImage():
	printf ("In upload method post")
	printf (request.files['image'])
	printf (request.files['image'].filename)
	printf (request.files['image'].stream)
	userName = request.form['username']
	caption = request.form['image_caption']
	stream = request.files['image'].stream
	image_name = request.files['image'].filename
	file_extension = image_name[image_name.rfind(".") : ]
	image_name = image_name[ : image_name.rfind(".")]
	image_name = re.sub(r'\W+', '', image_name)
	uploadImageToPortal(userName, caption, stream, image_name, file_extension)
	return "Image uploaded"

# @app.route('/signup', methods=['POST'])
# def signUpProcess():
# 	printf ("In signup process")
# 	values = dict()
# 	email = request.form['email']
# 	username = request.form['username']
# 	password = request.form['password']
# 	print (username, email, password, file=sys.stderr)

# 	if username and email and password:
# 		printf ("Creating object for " + username)
# 		u = Cognito(cognitoPoolID,cognitoAppClient, access_key=IAMAccessKey, 
# 			secret_key=IAMSecretyKey)

# 		printf ("Cognito object created, trying to add user")
# 		u.add_base_attributes(email=email)
# 		try:
# 			u.register(username, password)
# 			values['success'] = "Account created for user " + username \
# 			+ ". Click on the link below to verify your email."
# 			printf ("Returning " + str(values))
# 			return jsonify(values)
# 		except Exception as e:
# 			printf ("Signup failed, Error: " +  str(e))
# 			values['error'] = str(e)
# 			return jsonify(values)


# 	printf ("Returning " + values)
# 	values['error'] = 'Please enter all the fields'
# 	return jsonify(values)

@application.route('/login', methods=['GET'])
def loginPage():
	return render_template('login.html')

# @app.route('/login', methods=['POST'])
# def loginProcess():
# 	printf("In login process")
# 	values = dict()
# 	username = request.form['username']
# 	password = request.form['password']
# 	printf("Username: " + username)
# 	u = Cognito(cognitoPoolID,cognitoAppClient, username=username)
# 	try:
# 		u.authenticate(password = password)
# 		printf("---------Authenticated-------------")
# 		values['success'] = "Logged in as " + username
# 		printf("ID_Token: " + u.id_token)
# 		return jsonify(values)
# 	except Exception as e:
# 		printf (e)
# 		values['error'] = str(e)
# 		return jsonify(values)

@application.route('/confirmUser')
def confirmUser():
	return render_template('confirmUser.html')

# @app.route('/confirmUser', methods=['POST'])
# def confirmUserProcess():
# 	printf("In confirm process")
# 	values = dict()
# 	username = request.form['username']
# 	code = request.form['code']
# 	u = Cognito(cognitoPoolID, cognitoAppClient)
# 	try:
# 		u.confirm_sign_up(code,username=username)
# 		printf("--------VERIFIED-----------")
# 		values['success'] = "Your account is verified, you can now log in"
# 		return jsonify(values)
# 	except Exception as e:
# 		printf (e)
# 		values['error'] = str(e)
# 		return jsonify(values)

@application.route('/check-status', methods=['GET'])
def verify():
	return 'Service running!'
	
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

@application.route('/users', methods=['GET'])
def getUsers():

	try:
		cnx = mysql.connector.connect(**mySQLConfig)
		cursor = cnx.cursor()

	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			printf("Invalid credentials")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			printf("Database does not exist")
		else:
			printf(err)
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
	application.run(debug=True)