import pymysql
import datetime
import boto3
import mimetypes

rds_host  = 'imageportaldb.czkcl5taihag.us-east-2.rds.amazonaws.com'
rds_name = 'cs218rds'
rds_password = 'cs218rds'
db_name = 'mysql'
instance_name = 'imageportaldb'
table_name = 'uploads'
port = 3306

IAMAccessKey = 'AKIA2VGGOTNNR26EU3XB'
IAMSecretyKey = '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'
S3Bucket = 'imageportals3'
region_name = "us-east-2"
BUCKET_BASE_URL = "https://s3.us-east-2.amazonaws.com/imageportals3/"


def uploadImage(username, image_caption, image_path):

	# upload to S3
	session = boto3.Session(aws_access_key_id=IAMAccessKey, 
		aws_secret_access_key = IAMSecretyKey,
		region_name = region_name)

	s3 = session.resource('s3')
	bucket = s3.Bucket(S3Bucket)

	file_mime = mimetypes.guess_type(image_path)[0] or 'binary/octet-stream'
	print (file_mime)
	return
	with open(image_path, 'rb') as data:
		curr_time = str(datetime.datetime.now()).replace("-","").replace(" ",""). replace(":","").replace(".","")
		image_name = "test_" + curr_time + ".jpg"
		bucket.put_object(Key=image_name, Body=data, ContentType=file_mime, ACL='public-read')


	# update in RDS
	conn = pymysql.connect(rds_host, user=rds_name, passwd=rds_password, db=db_name, connect_timeout=5)

	IMAGE_URL = BUCKET_BASE_URL + image_name
	insert_query = "INSERT INTO {}.{} VALUES ('{}','{}','{}','{}')".format(instance_name,table_name,username,image_caption,IMAGE_URL,curr_time)
	with conn.cursor() as cur:
		cur.execute(insert_query)
		conn.commit()

	print ("Uploaded")



	#cur.execute("CREATE TABLE imageportaldb.uploads (Username VARCHAR(255),  Image_Caption VARCHAR(1000),  Image_URL VARCHAR(1000),  Upload_Date VARCHAR(100))")
	# query = "SELECT * FROM {}.{}".format(instance_name, table_name)
	# cur.execute(query)
	# for row in cur:
	#  	item_count += 1
	

	# curr_time = str(datetime.datetime.now()).replace("-","").replace(" ",""). replace(":","").replace(".","")
	# insert_query = "INSERT INTO {}.{} VALUES ('{}','{}','{}','{}')".format(instance_name,table_name,"anand","A dog","abcd.png",curr_time)
	# cur.execute(insert_query)
	# conn.commit()

	# print(query)
	# cur.execute(query)

# 	query = ("SELECT * from {}.{}".format(instance_name,table_name))
# 	cur.execute(query)


# for item in cur:
# 	print (item)


def getAllImages():
	conn = pymysql.connect(rds_host, user=rds_name, passwd=rds_password, db=db_name, connect_timeout=5)
	query = "select * from {}.{}".format(instance_name, table_name)
	with conn.cursor() as cur:
		cur.execute(query)

	for item in cur:
		print (item)

#uploadImage("anand","A cartoon", "uploads/shinchan.png")
#getAllImages()