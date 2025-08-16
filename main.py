import webview
import os
from pathlib import Path

# Import your existing API class
from api.sharif_api import SharifConnectAPI

class Api:
    def load_page(self, page_name):
        """Load a specific page"""
        page_path = os.path.join(os.getcwd(), 'static', page_name)
        window.load_url(f'file:///{page_path}')

if __name__ == '__main__':
    # Create API instances
    api = Api()
    sharif_api = SharifConnectAPI()
    
    # Get absolute path to HTML file
    current_dir = Path(__file__).parent
    html_file = current_dir / 'static' / 'index.html'
    
    # Create webview window
    window = webview.create_window(
        'Sharif Connect',
        str(html_file),
        width=700,
        height=850,
        resizable=False,
        js_api=sharif_api  # Use your existing API
    )
    
    webview.start(debug=True)
