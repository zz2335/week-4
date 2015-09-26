from flask import Flask
from flask import render_template
from flask import request

import json
import time
import sys
import random

import pyorient

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/getData/")
def getData():

	lat1 = str(request.args.get('lat1'))
	lng1 = str(request.args.get('lng1'))
	lat2 = str(request.args.get('lat2'))
	lng2 = str(request.args.get('lng2'))

	print "received coordinates: [" + lat1 + ", " + lat2 + "], [" + lng1 + ", " + lng2 + "]"
	
	client = pyorient.OrientDB("localhost", 2424)
	session_id = client.connect("root", "password")
	db_name = "property_test"
	db_username = "admin"
	db_password = "admin"

	if client.db_exists( db_name, pyorient.STORAGE_TYPE_MEMORY ):
		client.db_open( db_name, db_username, db_password )
		print db_name + " opened successfully"
	else:
		print "database [" + db_name + "] does not exist! session ending..."
		sys.exit()

	query = 'SELECT FROM Listing WHERE latitude BETWEEN {} AND {} AND longitude BETWEEN {} AND {}'

	records = client.command(query.format(lat1, lat2, lng1, lng2))

	random.shuffle(records)
	records = records[:100]

	numListings = len(records)
	print 'received ' + str(numListings) + ' records'

	client.db_close()

	output = {"type":"FeatureCollection","features":[]}

	for record in records:
		feature = {"type":"Feature","properties":{},"geometry":{"type":"Point"}}
		feature["id"] = record._rid
		feature["properties"]["name"] = record.title
		feature["properties"]["price"] = record.price
		feature["geometry"]["coordinates"] = [record.latitude, record.longitude]

		output["features"].append(feature)

	return json.dumps(output)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True,threaded=True)