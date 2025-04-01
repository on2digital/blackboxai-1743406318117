# Windows with WSL Setup Guide

## Prerequisites
1. **WSL 2** installed and configured
   ```powershell
   wsl --install -d Ubuntu
   ```
2. **Python 3.9** (Windows native or WSL)
3. **Node.js v18+** (Windows native or WSL)
4. **Tesseract OCR** (Install in both Windows and WSL)
   ```powershell
   # Windows
   choco install tesseract
   # WSL
   sudo apt install tesseract-ocr tesseract-ocr-ben
   ```

## Option 1: Windows Native Development

### Backend Setup
1. Install Python dependencies:
   ```powershell
   pip install flask pyjwt Werkzeug python-dotenv gunicorn
   ```

2. Set environment variables (PowerShell):
   ```powershell
   $env:FLASK_APP="backend/app.py"
   $env:FLASK_ENV="development"
   ```

3. Run backend:
   ```powershell
   flask run --host=0.0.0.0 --port=5000
   ```

### Frontend Setup
1. Install Node.js dependencies:
   ```powershell
   cd frontend
   npm install
   ```

2. Run frontend:
   ```powershell
   npm start
   ```

## Option 2: WSL Development (Recommended)

### Initial WSL Setup
1. Update packages:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. Install system dependencies:
   ```bash
   sudo apt install -y build-essential libpoppler-cpp-dev tesseract-ocr tesseract-ocr-ben libleptonica-dev
   ```

### Backend Setup in WSL
1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install Python packages:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Run backend:
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```

### Frontend Setup in WSL
1. Install Node.js:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt install -y nodejs
   ```

2. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Run frontend:
   ```bash
   npm start
   ```

## Hybrid Approach (Frontend in Windows, Backend in WSL)

1. In WSL (backend):
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```

2. In Windows (frontend):
   ```powershell
   cd frontend
   npm install
   npm start
   ```

## Accessing the Application
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5000`

## WSL Specific Notes
1. File system performance:
   - For better performance, clone repo in WSL filesystem (`~/projects`)
   - Not in Windows filesystem (`/mnt/c/...`)

2. Port forwarding:
   - WSL ports are automatically forwarded to Windows
   - No additional configuration needed

3. Environment variables:
   - Set in `.bashrc` or `.zshrc` for WSL:
     ```bash
     export FLASK_APP=backend/app.py
     export FLASK_ENV=development
     ```

## Troubleshooting
1. If ports are unavailable:
   ```bash
   sudo netstat -tulnp | grep <port>
   sudo kill <pid>
   ```

2. For Tesseract issues:
   ```bash
   sudo apt install tesseract-ocr-all
   ```

3. For Python package conflicts:
   ```bash
   pip freeze | xargs pip uninstall -y
   pip install -r backend/requirements.txt