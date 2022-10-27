from flask import Flask
import json

app = Flask(__name__)

@app.route('/')
def index():
  return 'Server Works!'
  
@app.route('/health')
def health():
    return app.response_class(
        response=json.dumps({
            "status": "OK",
            "message": "Everything is hunky dory over here, how are you?"}),
        status=200,
        mimetype='application/json'
    )