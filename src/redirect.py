#!/usr/bin/env python3
"""
HTTP zu HTTPS Redirect Server für DA-KI
Läuft auf Port 80 und leitet alle Anfragen zu Port 443 weiter
"""

import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/da-ki/logs/redirect.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class RedirectHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler für HTTPS Redirect"""
    
    def do_GET(self):
        """Handle GET requests - redirect to HTTPS"""
        self.redirect_to_https()
    
    def do_POST(self):
        """Handle POST requests - redirect to HTTPS"""
        self.redirect_to_https()
    
    def do_HEAD(self):
        """Handle HEAD requests - redirect to HTTPS"""
        self.redirect_to_https()
    
    def redirect_to_https(self):
        """Redirect any HTTP request to HTTPS"""
        https_url = f'https://10.1.1.180{self.path}'
        
        # Log the redirect
        logger.info(f"Redirecting {self.client_address[0]} from http://10.1.1.180{self.path} to {https_url}")
        
        # Send 301 Permanent Redirect
        self.send_response(301)
        self.send_header('Location', https_url)
        self.send_header('Connection', 'close')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override default logging to use our logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")

def main():
    """Start the HTTP redirect server"""
    server_address = ('10.1.1.180', 80)
    
    try:
        httpd = HTTPServer(server_address, RedirectHandler)
        logger.info(f"HTTP Redirect Server gestartet auf {server_address[0]}:{server_address[1]}")
        logger.info("Alle HTTP-Anfragen werden zu HTTPS://10.1.1.180 weitergeleitet")
        
        httpd.serve_forever()
        
    except PermissionError:
        logger.error("FEHLER: Berechtigung verweigert. Port 80 benötigt Root-Rechte oder CAP_NET_BIND_SERVICE.")
        logger.error("Führe das Script als Root aus oder weise die Berechtigung zu:")
        logger.error("sudo setcap 'cap_net_bind_service=+ep' /opt/da-ki/app/venv/bin/python")
        sys.exit(1)
        
    except OSError as e:
        logger.error(f"FEHLER: Kann Server nicht starten: {e}")
        logger.error("Möglicherweise läuft bereits ein anderer Service auf Port 80")
        sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("HTTP Redirect Server wird beendet...")
        httpd.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()