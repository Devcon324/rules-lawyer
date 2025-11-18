# Rules Lawyer Backend

FastAPI backend for the Rules Lawyer application.

## Setup

1. Create a virtual environment:
```bash
python -m venv ./.venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and configure your environment variables:
```bash
cp .env.example .env
```

4. Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry point
│   ├── config.py        # Configuration settings
│   ├── routers/         # API route handlers
│   ├── models/          # Database models
│   └── schemas/         # Pydantic schemas
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore
└── README.md
```

