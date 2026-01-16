import os
import multiprocessing

# Bind to the PORT environment variable (Render sets this)
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Number of worker processes - strictly 1 for 512MB environments
workers = 1

# Worker class
worker_class = 'sync'

# Timeout for workers
timeout = 120

# Preload app to share models across workers
preload_app = True

# Access log
accesslog = '-'

# Error log
errorlog = '-'

# Log level
loglevel = 'info'

# Preload app
preload_app = True
