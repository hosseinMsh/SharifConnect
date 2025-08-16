import subprocess
import requests


def ping(host):
    try:
        subprocess.check_output(
            ["ping", "-n", "1", "-w", "750", host],
            stderr=subprocess.DEVNULL,
            creationflags = subprocess.CREATE_NO_WINDOW
        )
        return True
    except subprocess.CalledProcessError:
        return False

def check_public_internet():
    test_hosts = [
        "https://www.aparat.com",
        "https://www.google.com",
        "https://snap.ir",
    ]
    for host in test_hosts:
        try:
            requests.get(host, timeout=1)
            return True
        except requests.RequestException:
            continue
    return ping("1.1.1.1")


"""
| 0  | Outside - Not connect to Sharif network               |
| 1  | Outside - connect to Sharif network                   |
| 2  | Inside - connect to Sharif network and internet       |
| 3  | Inside - connect to Sharif network - without internet |

"""

def check_sharif_network():
    # G
    if ping("172.26.146.34"):  # ns1
        if ping("net.sharif.ir"):
            if check_public_internet():
                return 2  # Inside + internet
            else:
                return 3  # Inside no internet
        else:
            return 1  # Outside but Sharif reachable
    else:
        if ping("172.26.146.35"):  # ns2
            if ping("net.sharif.ir"):
                if check_public_internet():
                    return 2
                else:
                    return 3
            else:
                return 1
        else:
            return 0  # Outside no Sharif access

def get_ip_address():
    try:
        response = requests.get("https://icanhazip.com/")
        if response.status_code == 200:
            return response.text
        else:
            return ""
    except Exception as e:
        return False