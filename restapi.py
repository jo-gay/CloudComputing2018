from flask import Flask, jsonify
import subprocess
import sys
worker_count = 0
app = Flask(__name__)

@app.route('/createsparkmaster', methods=['GET'])
def create_sparkmaster():
	subprocess(["python", "ssc-instance-userdata.py", "group2_SM"])
      	
@app.route('/createsparkworker', methods=['GET'])
def create_sparkworker():
	worker_name = "group2_SW" + str(worker_count)
	subprocess(["python", "ssc-instance-userdata.py", worker_name)
	worker_count += 1

if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)