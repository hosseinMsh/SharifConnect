
import requests
from bs4 import BeautifulSoup

from api.configurations import log_event

origin = "https://net.sharif.ir"
login_url = "https://net.sharif.ir/en-us/user/login/"
home_url = "https://net.sharif.ir/en-us/user/home/"
connect_url = "https://net.sharif.ir/en-us/user/aaa_ras_connect/"
sessions_url = "https://net.sharif.ir/en-us/user/get_user_online_session/"
disconnect_url = "https://net.sharif.ir/en-us/user/disconnect/"


def get_cookie_value(cookies, name, domain=None, path=None):
    for cookie in cookies:
        if cookie.name == name:
            if domain and cookie.domain != domain:
                continue
            if path and cookie.path != path:
                continue
            return cookie.value
    return None


def get_session(username, password):
    session = requests.session()
    response = session.get(login_url)
    if response.status_code != 200:
        return False, "Failed to load main page"

    soup = BeautifulSoup(response.text, "html.parser")
    csrf_token_input = soup.find("input", attrs={"name": "csrfmiddlewaretoken"})
    if not csrf_token_input:
        return False, "CSRF token input not found in login form"

    csrf_token = csrf_token_input["value"]

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": origin,
        "Referer": login_url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    data = {
        "csrfmiddlewaretoken": csrf_token,
        "username": username,
        "password": password,
    }

    post_resp = session.post(login_url, headers=headers, data=data)
    if post_resp.status_code != 200 and post_resp.status_code != 302:
        return False, f"Login failed: Status {post_resp.status_code}"

    return True, "Login successful", session


def connect_via_requests(username, password) -> (bool,str):
    result, massage, session = get_session(username, password)
    if result is False:
        return False, massage
    # Step 1: Get the home page for test
    response = session.get(home_url)
    if response.status_code != 200:
        return False, "Failed to load main page"

    for cookie in session.cookies:
        log_event(f"{cookie.name, cookie.value, cookie.domain, cookie.path}")
    csrf_token = get_cookie_value(session.cookies, "csrftoken", domain="net.sharif.ir")

    if not csrf_token:
        return False, "CSRF token not found in cookies"
    # Step 2: Send POST request  connect data
    headers = {
        "Referer": login_url,
        "X-CSRFToken": csrf_token,
        "X-Requested-With": "XMLHttpRequest",
        "Origin": origin
    }
    data = {
        "user": username,
        "pass": password,
    }

    try:
        post_response = session.post(connect_url, headers=headers, data=data)
        if post_response.status_code == 200:
            return True, "Login POST sent successfully"
        else:
            return False, f"Failed: Status {post_response.status_code}, Response: {post_response.text}"
    except requests.RequestException as e:
        return False, f"Request failed: {e}"


def get_online_sessions(username, password):

    result, message, session = get_session(username, password)
    if not result:
        return False, message, session

    csrf_token = get_cookie_value(session.cookies, "csrftoken", domain="net.sharif.ir")
    if not csrf_token:
        return False, "CSRF token not found in cookies", session

    try:
        home_resp = session.get(home_url)
        if home_resp.status_code != 200 or "ورود" in home_resp.text.lower():
            return False, "شما وارد نشده‌اید یا صفحه لاگین برگشت داده شده است.", session

        headers = {
            'Referer': home_url,
            'X-CSRFToken': csrf_token,
            'X-Requested-With': 'XMLHttpRequest',

        }

        response = session.get(sessions_url, headers=headers)

        if response.status_code != 200 or "Home" in response.text.lower():
            return False, f"خطا: وضعیت پاسخ {response.status_code}", session

        data = response.json()
        return True, data, session

    except Exception as e:
        log_event(f"❌ Error fetching sessions: {e}")
        return False, f"❌ Error fetching sessions: {e}", session


def disconnect_session(session, ras_ip, session_ip, session_id):
    """
    Disconnect a specific session with the given parameters.
    """
    try:

        url = f"{disconnect_url}?user_id=0&ras={ras_ip}&ip={session_ip}&u_id={session_id}"
        csrf_token = get_cookie_value(session.cookies, "csrftoken", domain="net.sharif.ir")
        headers = {
            "X-CSRFToken": csrf_token,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": home_url,
        }
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            return True, f"✅ Disconnected: {session_id} ({session_ip})"
        else:
            return False, f"❌ Failed to disconnect: {session_id} - Status code {response.status_code}"

    except Exception as e:
        return False, f"❌ Error disconnecting session {session_id}: {e}"


def disconnect_current_session(username, password):
    try:
        success, response_json, session_data = get_online_sessions(username, password)
        if not success:
            raise Exception("Error in get sessions")

        sessions = response_json.get("result", [[]])[0]
        if not sessions:
            raise Exception("Not found any sessions")

        current_ip = response_json.get("ip",None)
        if current_ip is None:
            raise Exception("Cant get ip")

        target_session = next((s for s in sessions if s.get("session_ip") == current_ip), None)
        if not target_session:
            raise Exception(f"Not found any sessions with this IP: {current_ip}")

        ras_ip = target_session.get("ras_ip")
        session_ip = target_session.get("session_ip")
        session_id = target_session.get("session_id")

        success, msg = disconnect_session(session_data, ras_ip, session_ip, session_id)
    except Exception as e:
        success, msg = False, str(e)
    return success, msg
