from flask import Flask
 
app = Flask(__name__)
 
@app.route('/hello')
def helloWorldHandler():
    return 'Hello Eska & William'
 
app.run(host='veronica.skripsi.top', port= 8090)