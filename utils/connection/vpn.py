import subprocess

VPN_NAME = "sharif"
VPN_SERVER = "access2.sharif.edu"
PRE_SHARED_KEY = "access1.sharif.ir"

def connect_vpn(username, password):
    try:
        subprocess.run(["rasphone", "-R", VPN_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)

        subprocess.run([
            "powershell", "-Command",
            f"Add-VpnConnection -Name '{VPN_NAME}' -ServerAddress '{VPN_SERVER}' -TunnelType L2tp "
            f"-L2tpPsk '{PRE_SHARED_KEY}' -AuthenticationMethod PAP -Force"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW, check=True)

        subprocess.run(["rasdial", VPN_NAME, username, password], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW, check=True)
        return True, "VPN connected successfully."
    except subprocess.CalledProcessError as e:
        return False, "VPN failed"

def disconnect_vpn():
    try:
        subprocess.run(["rasdial", "/disconnect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW, check=True)
        return True, "VPN disconnected successfully."
    except subprocess.CalledProcessError as e:
        return False, "Failed to disconnect VPN"
