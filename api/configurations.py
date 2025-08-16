import json
import platform
import uuid
from pathlib import Path
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
import base64
import os
from datetime import datetime
import shutil
from dotenv import load_dotenv

load_dotenv()

MAX_LOG_SIZE = 1 * 1024 * 1024  # 1 MB

def get_config_path():
    if os.name == "nt":  # Windows
        appdata = Path(os.getenv("APPDATA"))
        config_dir = appdata / "SharifConnect"
    else:  # Linux / Mac
        home = Path.home()
        config_dir = home / ".sharif_connect"

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "sharif_config.enc"

CONFIG_FILE = get_config_path()
LOG_FILE = CONFIG_FILE.with_suffix(".log")
LOGS_DIR = CONFIG_FILE.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
if SECRET_KEY is None:
    raise ValueError("SECRET_KEY environment variable is not set")
def get_system_identity():
    user = os.getlogin().encode()
    hostname = platform.node().encode()
    mac = uuid.getnode().to_bytes(6, 'big')
    return user + hostname + mac

def derive_key(salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt = SECRET_KEY.encode(),
        iterations=100_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(salt))

def get_fernet():
    identity = get_system_identity()
    key = derive_key(identity)
    return Fernet(key)

def rotate_log():
    """Rotate log file if too big, move to logs folder"""
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > MAX_LOG_SIZE:
        backup_name = LOGS_DIR / f"sharif_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log.bak"
        shutil.move(LOG_FILE, backup_name)

def log_event(message: str):
    """Write log message to file with rotation"""
    rotate_log()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def mask_and_encrypt_values(data: dict) -> dict:
    """Encrypt only values, keep keys in plain text"""
    fernet = get_fernet()
    masked = {}
    for k, v in data.items():
        if isinstance(v, (str, int, float, bool)):
            val_str = str(v)
            masked[k] = fernet.encrypt(val_str.encode()).decode()
        else:
            masked[k] = fernet.encrypt(json.dumps(v).encode()).decode()
    return masked

def save_config(data: dict):
    fernet = get_fernet()
    json_data = json.dumps(data).encode()
    encrypted = fernet.encrypt(json_data)
    CONFIG_FILE.write_bytes(encrypted)

    # Log with keys visible, values encrypted
    masked_data = mask_and_encrypt_values(data)
    log_event(f"Config saved. Data: {json.dumps(masked_data)}")

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        log_event("Config file not found.")
        return {}
    try:
        fernet = get_fernet()
        decrypted = fernet.decrypt(CONFIG_FILE.read_bytes())
        data = json.loads(decrypted.decode())

        masked_data = mask_and_encrypt_values(data)
        log_event(f"Config loaded. Data: {json.dumps(masked_data)}")
        return data
    except Exception as e:
        log_event(f"Error loading config: {e}")
        return {}
