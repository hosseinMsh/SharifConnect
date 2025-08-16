import json
import time

from api.configurations import load_config, save_config
from api.connection.inside import connect_via_requests, disconnect_current_session, disconnect_session, \
    get_online_sessions
from api.connection.network import check_sharif_network, get_ip_address
from api.connection.vpn import connect_vpn, disconnect_vpn
from api.metadata.connections_logs import get_bandwidth_logs
from api.metadata.profile import get_data

config = load_config()


class SharifConnectAPI:
    def __init__(self):
        self.connected = False
        self.current_language = 'fa'
        self.logged_in = False
        self.password = ''
        self.username = ''
        self.remember_me = False
        if config.get("remember"):
            self.username = config.get("username", "")
            self.password = config.get("password", "")
            self.remember_me = True
        self.state = -1
        self.load_languages()

    def load_languages(self):
        """Load language files"""
        try:
            with open('../static/lang/languages.json', 'r', encoding='utf-8') as f:
                self.languages = json.load(f)
        except FileNotFoundError:
            # Fallback if language file doesn't exist
            self.languages = {
                'fa': {'app_name': 'شریف کانکت'},
                'en': {'app_name': 'Sharif Connect'}
            }

    def get_language_data(self):
        """Return current language data"""
        return {
            'current': self.current_language,
            'data': self.languages.get(self.current_language, {})
        }

    def switch_language(self, lang_code):
        """Switch application language"""
        if lang_code in self.languages:
            self.current_language = lang_code
            return True
        return False

    def config_data(self):
        """Load configuration file"""
        if self.remember_me:
            return config
        return {}

    def login(self, username, password, remember_me):
        """Login to Sharif Connect"""
        # Simulate login validation
        if username and password:
            self.logged_in = True
            self.username = username
            self.password = password
            self.remember_me = remember_me
            save_config({"username": username, "password": password, "remember": remember_me})
            return {
                'success': True,
                'message': 'Login successful',
                'user': username
            }
        return {
            'success': False,
            'message': 'Invalid credentials'
        }

    def logout(self):
        """Logout from Sharif Connect"""
        self.logged_in = False
        return {}

    def profile(self):
        """Get user profile information"""
        if not self.logged_in:
            return {'error': 'Not logged in'}
        status, data = get_data(self.username, self.password)
        if status is False:
            return {'error': 'Username or password incorrect'}
        return {
            'username': self.username,
            'fullname': data['fullname'] if data['fullname'] else "نامشخص",
            'fullname_en': data['fullname_en'] if data['fullname_en'] else "Not defined",
            'gender': data['gender'] if data['gender'] else "نامشخص",
            'mobile': data['mobile'] if data['mobile'] else "نامشخص",
            'account_status': data['account_status'],
            'param': data['param'] if data['param'] else "نامشخص",
        }

    def info(self):
        """Get application and system information"""
        return {
            'app_version': '2.0.0',
            'build_date': '2025-08-01',
            'platform': 'Windows',
            'python_version': '3.12+',
            'server_status': 'Online',
            'total_users': '18,000',
            'server_load': '45%'
        }

    def sessions(self):
        """Get session history (0 to 3 sessions)"""
        result, message, session = get_online_sessions(self.username, self.password)
        print(message)
        return {'result': result, 'data': message}

    def update_state(self):
        """Get current connection state"""
        self.state = check_sharif_network()  # return 0, 1, 2, 3
        return self.state

    def connect(self):
        """Connect to SHARIF"""
        # Connect with request (inside)
        if not self.logged_in:
            return {'success': False, 'message': 'Please login again'}
        self.update_state()
        if self.state == 2 or self.state == 1:
            res = True
        elif self.state == 3:

            res, data = connect_via_requests(self.username, self.password)
        # Connect with Vpn (outside)
        elif self.state == 0:

            res, data = connect_vpn(self.username, self.password)
        else:

            return {'success': False, 'message': 'Check the network can not get the SHARIF network'}
        return {
            'success': res,
            'status': 'connected',
            'message': 'Successfully connected to Sharif Connect',
            'server': 'Sharif',
            'ip': get_ip_address(),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def disconnect(self):
        """Disconnect from VPN"""
        success = False
        self.update_state()
        if self.state == 0 or self.state == 3:
            success, msg = True, ""
        elif self.state == 1:  # vpn is on
            success, msg = disconnect_vpn()
        elif self.state == 2:  # connect in inside
            success, msg = disconnect_current_session(self.username, self.password)

        if success is True:
            self.connected = False
            return {
                'success': True,
                'status': 'disconnected',
                'message': 'Disconnected from Sharif Connect',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        return {'success': False, 'massage': 'Disconnect is not successful'}

    def disconnect_one_sessions(self, ras_ip, session_ip, session_id):
        print(ras_ip, session_ip, session_id)
        a, b, session = get_online_sessions(self.username, self.password)
        if a is True:
            success, msg = disconnect_session(session, ras_ip, session_ip, session_id)
            if success is True:
                return {'success': True, 'messages': f'Disconnected IP: {session_ip}'}
            else:
                return {'success': False, 'messages': 'Disconnect is not successful'}
        else:
            return {'success': False, 'messages': 'Cant load sessions'}

    def change(self, new_username=None, new_password=None, current_password=None):
        """Change username or password"""
        if not self.logged_in:
            return {'success': False, 'message': 'Not logged in'}

        # Verify current password for security
        if current_password != self.password:
            return {'success': False, 'message': 'Current password is incorrect'}

        changes_made = []

        if new_username:
            self.username = new_username
            changes_made.append('username')

        if new_password:
            self.password = new_password
            changes_made.append('password')
        save_config(
            {"username": self.username, "password": self.password, "remember": True})  # Todo : add remember me in front
        if changes_made:
            return {
                'success': True,
                'message': f'Successfully updated {", ".join(changes_made)}',
                'changes': changes_made
            }

        return {'success': False, 'message': 'No changes specified'}

    def get_logs(self):
        """Get application logs"""
        success, data = get_bandwidth_logs(self.username, self.password)
        if success is False:
            return {'success': False, 'message': 'Cant get logs'}
        return {
            'success': True,
            'data': data
        }

    def get_settings(self):
        """Get current settings"""
        return {
            'auto_connect': False,
            'kill_switch': True,
            'start_with_os': False,  # Start with OS option
            'notifications': True,
            'auto_update': True,
            'language': self.current_language,
            'theme': 'auto'
        }

    def update_settings(self, settings):
        """Update application settings"""
        # Here you would typically save settings to a file or registry
        # For now, we'll just return success
        return {
            'success': True,
            'message': 'Settings updated successfully',
            'settings': settings
        }
