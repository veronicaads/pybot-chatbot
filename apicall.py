from flask import Flask
from flask import jsonify

import json
import jsonpath

from rajaongkir import RajaOngkirApi

# initialization
api = RajaOngkirApi(api_key='a9650a9ba8a41fea3601d631dc9b49e5')

# initialization 
app = Flask(__name__)

@app.route('/hello')
def helloWorldHandler():
    # get province list
    #list_of_city = api.provinces()
    # returned values will be a list of provinces [{'province': 'Jawa Barat', ...}]

    # get city list
    #cost = api.cost_between_city(55, 23, 1000,'jne')
    list_of_city = api.cities_by_province(9)
    return jsonify(list_of_city)
 
app.run(host='veronica.skripsi.top', port= 8090)