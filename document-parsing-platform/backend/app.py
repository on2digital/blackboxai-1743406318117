from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from functools import wraps
import jwt
from models import init_db, get_db

app = Flask(__name__)
CORS(app)
init_db()  # Initialize database

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}
app.config['API_BEARER_TOKEN'] = os.getenv('API_BEARER_TOKEN', 'default-token-123')

# Helper Functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != f"Bearer {app.config['API_BEARER_TOKEN']}":
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

# API Endpoints
@app.route('/api/llm-config', methods=['GET', 'POST'])
@verify_token
def handle_llm_config():
    db = get_db()
    if request.method == 'POST':
        config = request.json
        db.execute('''INSERT INTO llm_config 
                     (model_name, temperature, max_tokens)
                     VALUES (?, ?, ?)''',
                     (config['model_name'], config['temperature'], config['max_tokens']))
        db.commit()
        return jsonify({'message': 'LLM config updated'}), 201
    else:
        config = db.execute('SELECT * FROM llm_config ORDER BY created_at DESC LIMIT 1').fetchone()
        return jsonify(dict(config)) if config else jsonify({}), 200

@app.route('/api/upload', methods=['POST'])
@verify_token
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Store document metadata
        db = get_db()
        db.execute('''INSERT INTO documents 
                     (filename, filepath, status)
                     VALUES (?, ?, ?)''',
                     (filename, filepath, 'uploaded'))
        db.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'documentId': filename
        }), 201
        
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/documents', methods=['GET'])
@verify_token
def get_documents():
    db = get_db()
    documents = db.execute('''SELECT d.*, l.model_name 
                            FROM documents d
                            LEFT JOIN llm_config l ON d.llm_config_id = l.id
                            ORDER BY d.created_at DESC''').fetchall()
    return jsonify([dict(d) for d in documents]), 200

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)