#!/bin/bash
# Debian Server Vollständige Einrichtung für DA-KI

set -e

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Starte Debian Server Setup für DA-KI..."

# System aktualisieren
log "Aktualisiere System..."
apt update && apt upgrade -y

# Deutsche Locale konfigurieren
log "Konfiguriere deutsche Locale..."
sed -i 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen
sed -i 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
update-locale LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8

# Zeitzone setzen
log "Setze Zeitzone auf Europe/Berlin..."
timedatectl set-timezone Europe/Berlin
timedatectl set-ntp true

# Basis-Pakete installieren
log "Installiere Basis-Pakete..."
apt install -y \
  curl wget git vim nano \
  htop tree tmux screen \
  unzip zip tar gzip \
  ca-certificates gnupg lsb-release \
  apt-transport-https software-properties-common \
  language-pack-de locales-all \
  manpages-de manpages-de-dev

# Python & Development Tools
log "Installiere Python und Development Tools..."
apt install -y \
  python3 python3-pip python3-venv \
  python3-dev python3-setuptools \
  build-essential pkg-config \
  libffi-dev libssl-dev

# Upgrade pip
pip3 install --upgrade pip setuptools wheel

# Datenbank und Tools
log "Installiere SQLite und weitere Tools..."
apt install -y \
  sqlite3 sqlite3-doc libsqlite3-dev \
  openssl cron logrotate rsync

# DA-KI Benutzer erstellen
log "Erstelle DA-KI Benutzer..."
if ! id "da-ki" &>/dev/null; then
    useradd -m -s /bin/bash da-ki
    usermod -aG sudo da-ki
    log "Benutzer da-ki erstellt"
else
    log "Benutzer da-ki existiert bereits"
fi

# Verzeichnisstruktur erstellen
log "Erstelle Verzeichnisstruktur..."
mkdir -p /opt/da-ki/{app,data,config,certs,logs,scripts,backups/daily,backups/weekly}
mkdir -p /opt/da-ki/app/{src,venv}
mkdir -p /opt/da-ki/data/{models,historical}

# Berechtigungen setzen
chown -R da-ki:da-ki /opt/da-ki
chmod 755 /opt/da-ki
chmod 700 /opt/da-ki/certs /opt/da-ki/config

# Netzwerk konfigurieren (10.1.1.180)
log "Konfiguriere Netzwerk..."
cat > /etc/netplan/00-installer-config.yaml << EOF
network:
  version: 2
  ethernets:
    eth0:
      addresses:
        - 10.1.1.180/24
      gateway4: 10.1.1.254
      nameservers:
        addresses:
          - 10.1.1.254
      dhcp4: false
EOF

# Netplan anwenden
netplan apply

log "Debian Server Setup abgeschlossen!"
log "Nächste Schritte:"
log "1. Als da-ki Benutzer anmelden: su - da-ki"
log "2. Python Virtual Environment einrichten"
log "3. DA-KI Anwendung installieren"