import os
import urllib.request
from pathlib import Path
import tempfile

def ensure_model_file(filename: str, dest_dir: Path, base_env: str = "MODEL_BASE_URL") -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / filename
    if target.exists():
        return target
    base = os.getenv(base_env)
    if not base:
        return target
    url = base.rstrip('/') + '/' + filename
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            urllib.request.urlretrieve(url, tmp.name)
            tmp_path = Path(tmp.name)
        tmp_path.replace(target)
    except Exception:
        # Leave missing; caller will handle fallback or error
        pass
    return target

def bulk_ensure(filenames, dest_dir: Path, base_env: str = "MODEL_BASE_URL"):
    return {name: ensure_model_file(name, dest_dir, base_env) for name in filenames}
