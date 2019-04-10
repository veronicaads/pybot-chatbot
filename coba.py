from flask import Flask,redirect

app = Flask(__name__)

@app.route('/kuisioner')
def helloIndex():
    return  redirect("https://docs.google.com/forms/d/e/1FAIpQLScii_V8wJFRx8AMXmSPetxYG0GsbcfmZFgBeq-SElQYvC5ClQ/viewform?usp=sf_link-")

app.run(host='veronica.skripsi.top', port= 8090)