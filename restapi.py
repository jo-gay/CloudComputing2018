from flask import Flask, jsonify, render_template, request
import subprocess
import sys
worker_count = 0
app = Flask(__name__, static_url_path='')

@app.route('/createsparkmaster', methods=['POST'])
def create_sparkmaster():
	subprocess.call(["python", "sparknode/ssc-instance-userdata.py", "group2sm"])
	return render_template('index.html')


@app.route('/createsparkworkers', methods=['POST'])
def create_sparkworker():
	amount = int(request.form['amt'])
	global worker_count
	for _ in range(0, amount): 
		worker_name = "group2sw" + str(worker_count)
		subprocess.call(["sudo", "python", "sparknode/ssc-instance-userdata.py", worker_name])
                subprocess.call(["sleep", "20"])
                subprocess.call(["sudo", "ansible-playbook", "-b", "spark_addworker.yml"])
		worker_count += 1
	return render_template('index.html')

@app.route('/token', methods=['GET'])
def get_token():
        f = open('jupyter_token', 'r')
        lines = f.readlines()
        f.close()
        return lines[0]


@app.route('/')
def root():
	print "here" 
   	#return app.send_static_file('~/CloudComputing2018/index.html')
	return render_template('index.html')


if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)
