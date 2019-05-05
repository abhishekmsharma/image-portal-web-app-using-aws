from flask import Flask, request, Response, render_template, redirect, url_for
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
import configparser
import sys

# setting up Flask application
application = Flask(__name__)

# setting up logger
handler = RotatingFileHandler('logs.log', maxBytes=10000, backupCount=1)
formatter = logging.Formatter("[%(asctime)s] {Line: %(lineno)d} %(levelname)s - %(message)s")
handler.setFormatter(formatter)
application.logger.setLevel(logging.INFO)
application.logger.addHandler(handler)


# setting up configurations and constants
config = configparser.ConfigParser()
config.read('config.ini')

REGION = config['DEFAULT']['Region']
os.environ['AWS_DEFAULT_REGION'] = REGION

IAMAccessKey = config['DEFAULT']['IAMAccessKey']
IAMSecretyKey = config['DEFAULT']['IAMSecretyKey']

rds_host  = config['RDS']['RDSHost']
rds_name = config['RDS']['RDSName']
rds_password = config['RDS']['RDSPassword']
db_name = config['RDS']['DBName']
instance_name = config['RDS']['InstanceName']
table_name = config['RDS']['TableName']

S3Bucket = config['S3']['S3BucketName']
BUCKET_BASE_URL = "https://s3.{}.amazonaws.com/{}/".format(REGION, S3Bucket)

def getImageData(user = None, keyword = None):
	conn = pymysql.connect(rds_host, user=rds_name, passwd=rds_password, db=db_name, connect_timeout=5)
	data = list()
	query = ("SELECT * from {}.{} ORDER BY UPLOAD_DATE DESC".format(instance_name,table_name))
	if user:
		query = ("SELECT * from {}.{} WHERE USERNAME = '{}' ORDER BY UPLOAD_DATE DESC".format(instance_name,table_name, user))
	print ("Keyword", keyword, file=sys.stderr)
	if keyword:
		query = ("SELECT * from {}.{} WHERE IMAGE_CAPTION LIKE '%{}%' ORDER BY UPLOAD_DATE DESC".format(instance_name,table_name, keyword))

	with conn.cursor() as cur:
		cur.execute(query)
		for item in cur:
			imgDate = item[3][:14]
			date = datetime.strptime(imgDate, '%Y%m%d%H%M%S').strftime('%b %d %Y')
			currImage = {'name': item[0], 'caption': item[1], 'image_url': item[2], 'date': date}
			data.append(currImage)

	return data

@application.route('/home')
def home():
	data = getImageData()
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
	return render_template('index.html')

@application.route('/signup', methods=['GET'])
def signUpPage():
	return render_template('signup.html')

@application.route('/upload', methods=['GET'])
def uploadPage():
	return render_template('upload.html')

@application.route('/about', methods=['GET'])
def aboutPage():
	return render_template('about.html')

def uploadImageToPortal(username, image_caption, image_path, image_name, image_extension):
	application.logger.info(username +" initiated an image upload")
	# upload to S3
	session = boto3.Session(aws_access_key_id=IAMAccessKey, 
		aws_secret_access_key = IAMSecretyKey,
		region_name = REGION)

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
	userName = request.form['username']
	caption = request.form['image_caption']
	stream = request.files['image'].stream
	image_name = request.files['image'].filename
	file_extension = image_name[image_name.rfind(".") : ]
	image_name = image_name[ : image_name.rfind(".")]
	image_name = re.sub(r'\W+', '', image_name)
	uploadImageToPortal(userName, caption, stream, image_name, file_extension)
	return "Image uploaded"

@application.route('/login', methods=['GET'])
def loginPage():
	return render_template('login.html')

@application.route('/confirmUser')
def confirmUser():
	return render_template('confirmUser.html')


@application.route('/check-status', methods=['GET'])
def verify():

	return 'Service running: ' + str(datetime.now())
	

if __name__ == '__main__':
	application.run(debug=True)