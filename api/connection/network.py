import subprocess
import requests


def ping(host, timeout=200):
    """Ping host quickly (timeout in ms)."""
    try:
        subprocess.check_output(
            ["ping", "-n", "1", "-w", str(timeout), host],
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_public_internet():
    """Check fast internet access."""
    test_hosts = [
        "https://www.google.com",
        "https://www.cloudflare.com",
    ]
    for host in test_hosts:
        try:
            requests.head(host, timeout=0.5)
            return True
        except requests.RequestException:
            continue
    return ping("1.1.1.1", timeout=200)


"""
| 0  | Outside - Not connect to Sharif network               |
| 1  | Outside - connect to Sharif network                   |
| 2  | Inside - connect to Sharif network and internet       |
| 3  | Inside - connect to Sharif network - without internet |
"""

def check_sharif_network():
    """Return Sharif connection state as quickly as possible."""
    sharif_ns1 = "172.26.146.34"
    sharif_ns2 = "172.26.146.35"

    if ping(sharif_ns1) or ping(sharif_ns2):
        if ping("net.sharif.ir"):
            return 2 if check_public_internet() else 3
        else:
            return 1
    return 0

def get_ip_address():
    try:
        response = requests.get("https://icanhazip.com/")
        if response.status_code == 200:
            return response.text
        else:
            return ""
    except Exception as e:
        return False