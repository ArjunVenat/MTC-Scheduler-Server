from flask import Flask, request, jsonify
from flask_cors import CORS
from solution import *

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    # Process or save the file as needed
    # For example, you can save it to a specific directory
    file.save('uploads/' + file.filename)

    return 'File uploaded successfully'

if __name__ == '__main__':
    app.run(debug=True)
