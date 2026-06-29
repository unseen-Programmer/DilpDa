# DilpDa Backend

This is the Django REST API for DilpDa.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file:

```bash
copy .env.example .env
```

Create a PostgreSQL database matching the `.env` values, then run:

```bash
python manage.py migrate
python manage.py runserver
```

The API will run at `http://127.0.0.1:8000/`.
