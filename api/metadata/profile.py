import requests
from bs4 import BeautifulSoup
LOGIN_URL = "https://accounts.sharif.edu/cas/login"
USER_URL = "https://register.sharif.edu/profile/index/User"

def get_data(username, password):
    session = requests.Session()

    res = session.get(LOGIN_URL)
    if res.status_code != requests.codes.ok:
        return False, {}
    soup = BeautifulSoup(res.text, 'html.parser')
    execution = soup.find('input', attrs={'name': 'execution'})
    if not execution:
        return False, {}
    data = {
        'username': username,
        'password': password,
        'execution': execution['value'],
        '_eventId': 'submit',
        'geolocation': ''
    }
    session.post(LOGIN_URL, data=data,allow_redirects=True)
    response = session.get(url=f"{LOGIN_URL}?service=https://register.sharif.edu/profile",allow_redirects=True)
    if response.status_code != requests.codes.ok:
        return False, {}
    soup = BeautifulSoup(response.text, 'html.parser')

    return  True , {
        "fullname": soup.find('input', attrs={'name': 'cn'})['value'],
        "fullname_en": soup.find('input', attrs={'name': 'cn;lang-en-US'})['value'],
        "national_id" : soup.find('input', attrs={'name': 'nationalid'})['value'],
        "gender": soup.find('input', attrs={'name': 'gender'})['value'],
        "father_name": soup.find('input', attrs={'name': 'fathername'})['value'],
        "postal_address" : soup.find('input', attrs={'name': 'postaladdress'})['value'],
        "postalcode" : soup.find('input', attrs={'name': 'postalcode'})['value'],
        "account_status" : soup.find('input', attrs={'name': 'accountstatus'})['value'],
        "telephone_number" : soup.find('input', attrs={'name': 'telephonenumber'})['value'],
        "mobile": soup.find('input', attrs={'name': 'mobile'})['value'],
        "dc_submail_address" : soup.find('input', attrs={'name': 'dcsubmailaddress'})['value'],
        "param": soup.find('input', attrs={'name': 'param'})['value'],
    }

