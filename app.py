from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Load environment variables from .env
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/data', methods=['POST'])
def api_data():
    data = request.json
    return jsonify({"response": "Received", "data": data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
