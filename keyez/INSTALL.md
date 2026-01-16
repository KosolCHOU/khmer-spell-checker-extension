# KeyEZ - Installation Guide

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

## Installation

### 1. Create Virtual Environment

```bash
cd keyez
python -m venv .venv
```

### 2. Activate Virtual Environment

**Linux/Mac:**

```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

**For GPU support (with CUDA):**

```bash
pip install -r requirements.txt
```

**For CPU only (lighter, no GPU):**
```bash
pip install -r requirements-cpu.txt
```

### 4. Setup Django

**Apply database migrations:**

```bash
python manage.py migrate
```

**Collect static files:**
```bash
python manage.py collectstatic --noinput
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## Project Structure

```text
keyez/
├── keyez_site/          # Django settings
├── landing/             # Main app
│   ├── model/          # ML models
│   │   ├── emnist_letters_traced.pt
│   │   └── idx_to_char.json
│   ├── static/         # CSS, JS files
│   ├── templates/      # HTML templates
│   └── views.py        # API endpoints
├── manage.py
└── requirements.txt
```

## Features

- **SingKhmer Input**: Type Latin Khmer, get real Khmer script
- **Handwriting Recognition**: Draw English letters, get Khmer transliteration
- **Real-time Predictions**: AI-powered character recognition
- **Offline Support**: Works without internet (after initial load)

## API Endpoints

- `GET /` - Main landing page
- `POST /predict/` - Handwriting recognition endpoint
  - Input: `{"image": "base64_png_data"}`
  - Output: `{"predictions": [{"char": "a", "confidence": 0.95}, ...]}`

## Troubleshooting

### ImportError: No module named 'django'
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

### Model not found error
- Ensure `emnist_letters_traced.pt` exists in `landing/model/`
- Ensure `idx_to_char.json` exists in `landing/model/`

### PIL/Pillow errors
- Run `pip install Pillow` separately if needed

## Production Deployment

**Using Gunicorn:**

```bash
gunicorn keyez_site.wsgi:application --bind 0.0.0.0:8000
```

**Environment Variables:**

- Set `DEBUG=False` in production
- Configure `ALLOWED_HOSTS` in settings.py
- Use PostgreSQL or MySQL instead of SQLite

## Dokku Deployment

Follow these steps to deploy on a self-hosted Dokku instance (Heroku-like workflow):

### 1. Server Provisioning
Provision an Ubuntu 22.04+ VPS (>=2GB RAM recommended if loading ML models). Set a domain (e.g. `yourdomain.com`). Point DNS A record to the server IP.

### 2. Install Dokku

```bash
wget https://raw.githubusercontent.com/dokku/dokku/v0.32.0/bootstrap.sh
sudo DOKKU_TAG=v0.32.0 bash bootstrap.sh
```
Complete the interactive setup (domain, SSH key).

### 3. Create App

```bash
dokku apps:create keyez
```

### 4. (Optional) Add Postgres

```bash
dokku plugin:install https://github.com/dokku/dokku-postgres.git
dokku postgres:create keyez_db
dokku postgres:link keyez_db keyez
```

### 5. Configure Environment
Generate a secret key:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(50))'
```
Set variables:
```bash
dokku config:set keyez \
  DJANGO_SETTINGS_MODULE=keyez_site.settings \
  SECRET_KEY=<<generated>> \
  DEBUG=False \
  ALLOWED_HOSTS=yourdomain.com
```

### 6. Dockerfile Builder (using existing Dockerfile)

```bash
dokku builder-dockerfile:set keyez dockerfile-path Dockerfile
```

### 7. Deploy via Git Push
Add remote locally:

```bash
git remote add dokku dokku@yourdomain.com:keyez
git push dokku main
```

### 8. Database & Static Assets
Run migrations and collect static (if not baked into image):

```bash
dokku run keyez python manage.py migrate
dokku run keyez python manage.py collectstatic --noinput
```

### 9. Domain & HTTPS

```bash
dokku domains:add keyez yourdomain.com
dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku letsencrypt:enable keyez
```

### 10. Scaling / Tuning
For low memory environments set Gunicorn flags in `Dockerfile` CMD (or Procfile alternative):
```
--workers 1 --threads 4 --max-requests 500 --max-requests-jitter 50
```
This reduces memory spikes and recycles potentially leaky workers.

### 11. Healthcheck (Optional)
Add to Dockerfile (requires curl):

```Dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fs http://localhost:8000/ || exit 1
```

### 12. Large Model Files
The `landing/model` directory inflates build context (& pushes). To optimize:
- Move model artifacts to object storage (e.g. S3, Spaces).
- Download at container start or first request.
- Exclude them via `.dockerignore` after externalization.

### Environment Variable Summary

| Variable | Purpose |
|----------|---------|
| DJANGO_SETTINGS_MODULE | Points Django to settings module |
| SECRET_KEY | Crypto signing key (never share) |
| DEBUG | Must be `False` in production |
| ALLOWED_HOSTS | Comma list of allowed domains |
| DATABASE_URL / linked service vars | Provided if using Postgres plugin |

### Quick Verification
After deploy:

```bash
dokku logs keyez --tail
curl -I https://yourdomain.com
```
Expect `200 OK` and Gunicorn startup in logs.

### Rollbacks
Dokku retains previous image; rollback with:

```bash
dokku ps:rebuild keyez   # rebuild current
dokku tags:list keyez     # list deploys (if using tags)
```

If a deploy fails, diagnose with:

```bash
dokku logs keyez
dokku trace on   # temporarily increases verbosity
```

---

## Cloud / Alternative Hosting (Brief)
Fly.io / Railway / Cloud Run also work; ensure image is small (externalize models) and set `PORT` env & bind Gunicorn to `$PORT`. For Cloud Run use a build/push to GCR and deploy with min instances 1 to warm models.

## License
© 2025 AstroAI • Made in Cambodia
