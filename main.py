from cryptography.fernet import Fernet
from flask import Flask, request, jsonify
from pyzbar.pyzbar import decode
import cv2
import numpy as np
import sqlite3

app = Flask(__name__)

def load_decryption_key(key_file):
    with open(key_file, 'rb') as file:
        key = file.read()
    return key

def decrypt_text(decryption_key, encrypted_text):
    fernet = Fernet(decryption_key)
    decrypted_text = fernet.decrypt(encrypted_text.encode()).decode()
    return decrypted_text

def search_database(search_string):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    results = []

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        for column in columns:
            column_name = column[1]
            query = f"SELECT * FROM {table_name} WHERE {column_name} LIKE ?"
            cursor.execute(query, ('%' + search_string + '%',))
            rows = cursor.fetchall()
            
            if rows:
                results.append({
                    "table": table_name,
                    "column": column_name,
                    "rows": rows
                })

    conn.close()
    if not results:
        return {"message": "No matching data found"}
    return results

@app.route('/scan_qr_code', methods=['POST'])
def scan_qr_code():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image = np.fromstring(image_file.read(), np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    decoded_objects = decode(image)

    if decoded_objects:
        encrypted_text = decoded_objects[0].data.decode('utf-8')
        key_file = 'decryption_key.key'
        decryption_key = load_decryption_key(key_file)
        decrypted_text = decrypt_text(decryption_key, encrypted_text)
        return jsonify({"decrypted_text": decrypted_text})
    else:
        return jsonify({"error": "No QR code detected"}), 400

@app.route('/decrypt_text', methods=['POST'])
def decrypt_text_endpoint():
    data = request.get_json()
    if 'encrypted_text' not in data:
        return jsonify({"error": "No encrypted text provided"}), 400

    encrypted_text = data['encrypted_text']
    key_file = 'decryption_key.key'
    decryption_key = load_decryption_key(key_file)
    try:
        decrypted_text = decrypt_text(decryption_key, encrypted_text)
        return jsonify({"decrypted_text": decrypted_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/search', methods=['POST'])
def search_endpoint():
    data = request.get_json()
    if 'search_string' not in data:
        return jsonify({"error": "No search string provided"}), 400

    search_string = data['search_string']
    try:
        results = search_database(search_string)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/')
def home():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
