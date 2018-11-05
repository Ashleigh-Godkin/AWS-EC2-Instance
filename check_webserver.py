#!/usr/bin/env python3
import subprocess

def checknginx():
	try:
		cmd = 'ps -A | grep nginx'
		subprocess.run(cmd, shell=True, check=True, stdout = subprocess.PIPE)
		print ("--Nginx Server IS running--")
	except subprocess.CalledProcessError:
		print ("--Nginx Server IS NOT running--")

#Define a main() function
def main():
	checknginx()

#boilerplate
if __name__ == '__main__':
	main()
