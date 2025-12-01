import os

# Production Gunicorn Configuration
# This file is used by Gunicorn to configure the server
# Run with: gunicorn -c app/server.py app.main:app

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = int(os.getenv("WORKERS", "3"))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 300  # 5 minutes timeout for long generation tasks
keepalive = 5

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"
