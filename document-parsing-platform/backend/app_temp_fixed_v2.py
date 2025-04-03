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

# Proper configuration setup
app.config.update({
    'UPLOAD_FOLDER': 'uploads',
    'ALLOWED_EXTENSIONS': {'pdf', 'docx', 'txt'},
    'API_BEARER_TOKEN': os.getenv('API_BEARER_TOKEN', 'default-token-123'),
    'SECRET_KEY': os.getenv('SECRET_KEY', 'default-secret-key')
})

# Initialize database after config
init_db()

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

@app.route('/upload', methods=['POST'])
@verify_token
def upload_file():
    """Handle file uploads with validation and secure storage"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'path': filepath
        }), 201
    except Exception as e:
        app.logger.error(f"File upload failed: {str(e)}")
        return jsonify({'error': 'File upload failed'}), 500

@app.route('/parse', methods=['POST'])
@verify_token
def parse_document():
    """Parse uploaded document using appropriate parser"""
    data = request.get_json()
    if not data or 'filepath' not in data:
        return jsonify({'error': 'Missing filepath'}), 400

    try:
        filepath = data['filepath']
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
            
        if filepath.endswith('.pdf'):
            from parsers.pdf_parser import PDFParser
            parser = PDFParser()
        elif filepath.endswith('.docx'):
            from parsers.docx_parser import DOCXParser
            parser = DOCXParser()
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        result = parser.parse(filepath)
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"Document parsing failed: {str(e)}")
        return jsonify({'error': 'Document parsing failed'}), 500

@app.route('/status')
def status():
    """Return service health status"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)