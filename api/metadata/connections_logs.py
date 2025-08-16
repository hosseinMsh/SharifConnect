import requests
from bs4 import BeautifulSoup

BW_LOGIN_URL ="https://bw.ictc.sharif.edu/login"
BW_LOGS_URL = "https://bw.ictc.sharif.edu/connections"

def get_bandwidth_logs(username ,password):
    session = requests.Session()
    session.get(BW_LOGIN_URL)
    headers = {
        "Referer": BW_LOGIN_URL,
        "Content-Type": "application/x-www-form-urlencoded",

    }
    data = f"normal_username={username}&normal_password={password}"
    session.post(BW_LOGIN_URL, data=data,headers=headers,allow_redirects=True)
    response=session.get(BW_LOGS_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        table = soup.find("table", id="csvtable")
        rows = table.find("tbody").find_all("tr")
        logs = []

        for row in rows[:30]:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue
            logs.append({
                "index": cols[0].get_text(strip=True),
                "login_time": cols[1].get_text(strip=True),
                "logout_time": cols[2].get_text(strip=True),
                "upload": cols[3].get_text(strip=True),
                "download": cols[4].get_text(strip=True),
            })

        return True, logs
    except Exception as e:
        return False, {"error": str(e)}




