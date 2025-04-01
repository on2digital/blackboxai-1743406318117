# Developer Guide

## Project Structure
```
document-parsing-platform/
├── backend/               # Flask backend
│   ├── app.py             # Main application entry
│   ├── models.py          # Database models
│   ├── parsers/           # Document parsers
│   ├── services/          # Business logic services
│   └── .env              # Environment config
├── frontend/              # React frontend
│   ├── public/            # Static assets
│   ├── src/               # Application source
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── App.jsx        # Main app component
│   │   └── main.jsx       # Entry point
│   └── package.json      # Frontend dependencies
├── Dockerfile            # Backend Docker config
├── Dockerfile.frontend   # Frontend Docker config
└── docker-compose.yml    # Full stack deployment
```

## Development Workflow

### Prerequisites
- Node.js v18+ (frontend)
- Python 3.9+ (backend)
- Tesseract OCR (for document processing)

### Setup
1. Clone repository
2. Install dependencies:
   ```bash
   # Frontend
   cd frontend
   npm install

   # Backend
   cd ../backend
   pip install -r requirements.txt
   ```

3. Configure environment:
   - Copy `.env.example` to `.env` and set values
   - Create `uploads` directory in backend

### Running Locally
```bash
# Start backend (in backend directory)
flask run --host=0.0.0.0 --port=5000

# Start frontend (in frontend directory)
npm start
```

## Coding Standards

### Frontend
- Use functional components with hooks
- Follow React best practices
- Use Tailwind CSS for styling
- Prefer named exports over default exports
- TypeScript recommended for new components

### Backend
- Follow Flask best practices
- Use Blueprints for route organization
- Keep business logic in services/
- Use type hints for new code
- Document API endpoints with docstrings

## API Design
- RESTful conventions
- JSON request/response format
- JWT authentication
- Standardized error responses:
  ```json
  {
    "error": "Error message",
    "code": "ERROR_CODE"
  }
  ```

## Testing
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd ../backend
pytest
```

## Deployment
See `DEPLOYMENT.md` for production deployment instructions.

## Contribution Guidelines
1. Create feature branch from `main`
2. Follow coding standards
3. Write tests for new features
4. Update documentation
5. Submit pull request

## Troubleshooting
- **Missing dependencies**: Run `npm install`/`pip install`
- **Port conflicts**: Check running processes
- **Tesseract errors**: Verify installation and paths