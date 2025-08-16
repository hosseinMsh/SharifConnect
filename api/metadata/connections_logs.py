import requests
from bs4 import BeautifulSoup

BW_LOGIN_URL ="https://bw.ictc.sharif.edu/login"
BW_LOGS_URL = "https://bw.ictc.sharif.edu/connections"

def get_logs(username ,password):
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
    for table in soup.find('table', attrs={'id': 'csvtable'}):
        print(table.find('td'))
    # print(soup.find('table', attrs={'id': 'csvtable'}))



