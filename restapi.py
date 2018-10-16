from flask import Flask, jsonify
import subprocess
import sys
worker_count = 0
app = Flask(__name__)

@app.route('/createsparkmaster', methods=['GET'])
def create_sparkmaster():
	subprocess.call(["python", "sparknode/ssc-instance-userdata.py", "group2_SM"])
	return "yeah"
@app.route('/createsparkworker', methods=['GET'])
def create_sparkworker():
	global worker_count
	worker_name = "group2_SW" + str(worker_count)
	subprocess.call(["python", "sparknode/ssc-instance-userdata.py", worker_name])
	worker_count += 1
	return "yeah"
if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)
