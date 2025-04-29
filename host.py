from flask import Flask, request, jsonify
import os
from main2 import *

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/get-lab-tests', methods=['POST'])
def get_lab_tests():
    try:
        if 'image' not in request.files:
            return jsonify({
                "is_success": False,
                "data": [],
                "error": "No image file provided"
            }), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                "is_success": False,
                "data": [],
                "error": "No selected file"
            }), 400

        image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(image_path)

        result = process_lab_image(image_path)

        os.remove(image_path)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "is_success": False,
            "data": [],
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)