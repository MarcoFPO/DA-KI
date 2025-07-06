#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting DA-KI server preparation on minimal Debian LXC..."

# --- 1. System aktualisieren und grundlegende Pakete installieren ---
echo "1. Updating system and installing essential packages..."
sudo apt update -y
sudo apt upgrade -y
sudo apt install -y build-essential git curl wget software-properties-common apt-transport-https ca-certificates gnupg2 python3-dev python3-venv

# --- 2. Node.js und npm installieren (über NodeSource Repository für aktuelle Versionen) ---
echo "2. Installing Node.js and npm..."
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# --- 3. Poetry installieren (Python-Paketmanager) ---
echo "3. Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -

# Fügen Sie Poetry zum PATH hinzu, damit es direkt verwendet werden kann
# Dies ist wichtig für den aktuellen Shell-Kontext und zukünftige Logins
echo 'export PATH="/root/.local/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="/root/.local/bin:$PATH"' >> ~/.profile
export PATH="/root/.local/bin:$PATH" # Für die aktuelle Sitzung

# --- 4. Nginx installieren (Webserver/Reverse Proxy) ---
echo "4. Installing Nginx..."
sudo apt install -y nginx

# --- 5. Certbot installieren (für Let's Encrypt TLS/SSL-Zertifikate) ---
echo "5. Installing Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# --- 6. Entwicklungstools installieren ---
echo "6. Installing development tools..."
sudo apt install -y vim nano mc htop tmux screen jq tree

# --- 7. SSH Server konfigurieren ---
echo "7. Configuring SSH server..."
# Sicherstellen, dass OpenSSH Server installiert ist
sudo apt install -y openssh-server
# Sicherstellen, dass der SSH-Dienst läuft und beim Booten startet
sudo systemctl enable ssh
sudo systemctl start ssh
echo "SSH server is configured and running."

# --- 8. Nginx Standardkonfiguration für DA-KI vorbereiten ---
echo "8. Preparing Nginx configuration for DA-KI..."

# Erstellen der Nginx-Konfigurationsdatei für die DA-KI-Anwendung
# Platzhalter für Domain und LXC-Container IP müssen manuell ersetzt werden
sudo bash -c 'cat << EOF > /etc/nginx/sites-available/daki-app.conf
server {
    listen 80;
    listen [::]:80; # IPv6
    server_name your_domain.com YOUR_LXC_CONTAINER_IPV4 YOUR_LXC_CONTAINER_IPV6; # ERSETZEN SIE DIES!

    # HTTP zu HTTPS Weiterleitung (wird von Certbot hinzugefügt/modifiziert)
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl; # IPv6
    server_name your_domain.com YOUR_LXC_CONTAINER_IPV4 YOUR_LXC_CONTAINER_IPV6; # ERSETZEN SIE DIES!

    # SSL-Konfiguration (wird von Certbot hinzugefügt/modifiziert)
    # ssl_certificate /etc/letsencrypt/live/your_domain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/your_domain.com/privkey.pem;
    # include /etc/letsencrypt/options-ssl-nginx.conf; # Standard-SSL-Optionen von Certbot
    # ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # Diffie-Hellman-Parameter

    location / {
        # Dies wird später auf das Frontend-Build-Verzeichnis zeigen
        # root /home/mdoehler/DA-KI/frontend/build;
        # index index.html index.htm;
        # try_files \$uri \$uri/ /index.html;
        return 200 "Nginx is running. Frontend will be served here via HTTPS."; # Platzhalter
    }

    location /api/v1/ {
        # ERSETZEN SIE YOUR_LXC_CONTAINER_IPV4/IPV6 DURCH DIE TATSÄCHLICHEN IP-ADRESSEN DES CONTAINERS
        proxy_pass http://YOUR_LXC_CONTAINER_IPV4:8000; # Beispiel: Backend auf IPv4
        # proxy_pass http://[YOUR_LXC_CONTAINER_IPV6]:8000; # Beispiel: Backend auf IPv6
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Weitere Locations für andere Backend-Endpunkte oder statische Assets
}
EOF'

# Symlink erstellen, um die Konfiguration zu aktivieren
sudo ln -sf /etc/nginx/sites-available/daki-app.conf /etc/nginx/sites-enabled/daki-app.conf

# Standard Nginx Welcome-Seite deaktivieren, um Konflikte zu vermeiden
if [ -f /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi

# Nginx Konfiguration testen und neu laden
echo "Testing Nginx configuration and reloading service..."
sudo nginx -t && sudo systemctl reload nginx

echo "Server preparation complete. Please remember to:"
echo "1. Replace 'your_domain.com', 'YOUR_LXC_CONTAINER_IPV4', and 'YOUR_LXC_CONTAINER_IPV6' in /etc/nginx/sites-available/daki-app.conf with your actual values."
echo "2. Run Certbot to obtain TLS/SSL certificates after setting up your domain. Example: sudo certbot --nginx -d your_domain.com"
echo "3. Clone your DA-KI application code into /home/mdoehler/DA-KI/."
echo "4. Adjust the 'root' directive in Nginx to point to your frontend build directory."
