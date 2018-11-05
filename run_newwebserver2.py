#!/usr/bin/env python3
import time
import boto3
import subprocess
import sys
bucket_name ='20071063'
key_name = '/home/testfile.jpg'
file_name = 'testfile.jpg'
data = open(file_name, 'rb')
s3 = boto3.resource("s3")
key = 'MyKey1910.pem'

#create the instance
ec2 = boto3.resource('ec2')
instance = ec2.create_instances(
	ImageId='ami-0c21ae4a3bd190229',
	KeyName='MyKey1910',
	MinCount=1,
	MaxCount=1,
	SecurityGroupIds=['sg-0d8985ab6c34f63f8'], #HTTP and SSH
	UserData='''#!/bin/bash
		    yum update -y
		    yum install python3 -y
		    amazon-linux-extras install nginx1.12 -y
		    service nginx start
		    touch /home/ec2-user/testfile''',
	InstanceType='t2.micro')

print ("Instance: ", instance[0].id, "has been created.")
time.sleep(15)
instance[0].reload()
print("Public IP address:",instance[0].public_ip_address)

#Wait 60 seconds before attempting scp and ssh
time.sleep(60)

scpcmd = 'scp -i '+key+ ' -o StrictHostKeyChecking=no check_webserver.py ec2-user@'+instance[0].public_ip_address + ':.'
sshcmd = 'ssh -t  -i ' +key+' ec2-user@'+instance[0].public_ip_address+ " 'python3 check_webserver.py'"
uploadhtml = 'scp -i '+key+' -o StrictHostKeyChecking=no index.html ec2-user@'+instance[0].public_ip_address+':.'
#Reference: James O'Rourke
deleteRestart = 'ssh -i '+key+' ec2-user@'+instance[0].public_ip_address+" 'cd /usr/share/nginx/html; sudo rm index.html;cd ~;sudo mv index.html /usr/share/nginx/html/index.html; sudo service nginx stop; sudo service nginx start'"

#SCP - check_webserver
try:
	print("--Trying SCP command--")
	subprocess.run(scpcmd, check=True, shell=True)
	print("--SCP Successful--")
except: 
	print("--SCP Unsuccessful--")

#SSH - check_webserver
try:
	print("--Trying SSH command--")
	subprocess.run(sshcmd, check=True, shell=True)
	print("--SSH Successful--")

except subprocess.CalledProcessError:
	print("--SSH Unsuccessful--")

#Wait 20 seconds before attempting to create bucket
time.sleep(20)

#Create bucket
try:
	print("--Creating bucket--")
	s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
	print("--Bucket created--")
except:
	print("--Bucket not created--")

#Upload image to bucket
try:
	print("--Uploading image to bucket--")
	s3.Bucket(bucket_name).put_object(Key=file_name, Body=data, ACL='public-read')
	print("--Image uploaded--")
except:
	print("--Image not uploaded--")

#Create index file
#Reference: Darren Clarke
try: 
	link = "https://s3-eu-west-1.amazonaws.com/"+bucket_name+ '/' +file_name
	print("--Creating index.html--")
	myIndex = open("index.html", "w+")
	myIndex.write('<HEAD><h1>DevOps Assignment 1</h1></HEAD><img src="'+link+'"/>'+ '<br>click image: <a href = "' +link+'">HERE</a></body>')
	myIndex.close()
except:
	print(":(((((")

#Upload html file
try:
	print("--Uploading HTML--")
	subprocess.run(uploadhtml, shell=True, check=True)
	print("--HTML uploaded--")
except:
	print("--HTML not uploaded--")

#Move and restart
try:
	print("--Attempting restart--")
	subprocess.run(deleteRestart, shell=True, check=True)
	print("--Restart successful--")
except:
	print("--Restart unsuccessful--")
