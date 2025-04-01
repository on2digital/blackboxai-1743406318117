from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from functools import wraps
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'xlsx', 'txt', 'jpg', 'jpeg', 'png', 'tiff'}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

# Authentication
@app.route('/api/auth/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('email') or not auth.get('password'):
        return jsonify({'message': 'Email and password required'}), 400
    
    # TODO: Replace with actual user validation
    if auth['email'] == 'admin@example.com' and auth['password'] == 'password':
        token = jwt.encode(
            {'email': auth['email'], 'exp': datetime.utcnow() + timedelta(hours=24)},
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({'token': token}), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

# API Endpoints
@app.route('/api/upload', methods=['POST'])
@token_required
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
        
        metadata = {
            'filename': filename,
            'upload_time': datetime.utcnow().isoformat(),
            'size': os.path.getsize(filepath),
            'status': 'queued'
        }
        
        return jsonify({
            'message': 'File uploaded successfully',
            'metadata': metadata
        }), 201
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/config', methods=['GET', 'POST'])
@token_required
def manage_config():
    if request.method == 'POST':
        config_data = request.json
        # TODO: Validate and save configuration
        return jsonify({'message': 'Configuration updated'}), 200
    else:
        # TODO: Return current configuration
        return jsonify({'config': {}}), 200

@app.route('/api/process', methods=['POST'])
@token_required
def process_document():
    data = request.json
    if not data or 'document_id' not in data:
        return jsonify({'error': 'Document ID required'}), 400
    
    # TODO: Implement actual processing
    return jsonify({
        'status': 'processing',
        'document_id': data['document_id']
    }), 202

@app.route('/api/results/<document_id>', methods=['GET'])
@token_required
def get_results(document_id):
    # TODO: Implement results retrieval
    return jsonify({
        'document_id': document_id,
        'status': 'completed',
        'content': {},
        'metadata': {}
    }), 200

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)