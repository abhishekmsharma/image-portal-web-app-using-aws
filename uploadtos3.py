import boto3
import os
import mimetypes

def upload_files(path):
    session = boto3.Session(
        aws_access_key_id='AKIA2VGGOTNNR26EU3XB',
        aws_secret_access_key='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',
        region_name="us-east-2"
    )
    s3 = session.resource('s3')
    bucket = s3.Bucket('imageportals3')

    for subdir, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(subdir, file)
            file_mime = mimetypes.guess_type(file)[0] or 'binary/octet-stream'
            with open(full_path, 'rb') as data:
                print (full_path[len(path)+1:])
                bucket.put_object(Key=full_path[len(path)+1:], Body=data, ContentType=file_mime, ACL='public-read')

if __name__ == "__main__":
    upload_files('uploads')