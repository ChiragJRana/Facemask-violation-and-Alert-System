import threading
from flask import Flask, request, jsonify
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Create a Product
@app.route('/', methods=['POST'])
def add_product():
    status = request.json['status']
    print(status)
    return {'status':'200'}
def flaskapi():
    app.run(debug=True)

def tkinter(text='chirag'):  
    pass
# Run Server
if __name__ == '__main__':
    t2 = threading.Thread(target=tkinter)
    t2.start()
    flaskapi()
    
    