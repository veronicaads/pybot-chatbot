import http.client
import jsonpath
import json

conn = http.client.HTTPSConnection("api.rajaongkir.com")

headers = { 'key': "040823d1664ea0661eb227d54a7f87d0" }

header = { 'key': "040823d1664ea0661eb227d54a7f87d0",'content-type': "application/x-www-form-urlencoded" }

conn.request("GET", "/starter/city?id=", headers=headers)

res = conn.getresponse()
print(res)
data = res.read()
print(data)
something = data.decode("utf-8")
print(something)
json_string = json.loads(something)
print(json_string)
print(type(json_string))

Lokasi = 'jakarta barat'

result = jsonpath.jsonpath(json_string,"$..results[?(@.city_name=='" + Lokasi.title() + "')]")
print(result)
result_id = jsonpath.jsonpath(result,"$..city_id")

print(result_id)

print(type(result_id))
str1 = ''.join(result_id)
if len(str1) > 3:
    result_id = [d['city_id'] for d in result]
    result_id.pop(0)
    str1 = ''.join(result_id)
print(str1)

logistik = 'jne'
payload = 'origin=55&destination=' + str1 + ' &weight=1000&courier=' +logistik + ''

conn.request("POST", "/starter/cost", payload, header)

resu = conn.getresponse()
datas = resu.read()

data_converts = datas.decode("utf-8")

json_strings = json.loads(data_converts)

service = jsonpath.jsonpath(json_strings,"$..results..service")
str2 = ' '.join(service)
print(str2)


cost = jsonpath.jsonpath(json_strings,"$..results..cost..value")
print(cost)

etd = jsonpath.jsonpath(json_strings,"$..results..cost..etd")
str4 = ' '.join(etd)
print(str4)



        
            