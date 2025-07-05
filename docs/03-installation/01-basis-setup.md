# DA-KI Basis-Setup

## Voraussetzungen

### LXC Container-Erstellung
```bash
# Sie erstellen den LXC Container mit:
# - Debian 12 (bookworm) Template
# - IP: 10.1.1.110/24
# - Gateway: 10.1.1.254
# - DNS: 10.1.1.254
# - RAM: 6GB, CPU: 4 Cores, Storage: 30GB
# - Hostname: da-ki
```

## 1. Deutsche Lokalisierung

### 1.1 Locale-Pakete installieren
```bash
# System updaten
apt update && apt upgrade -y

# Locale-Pakete installieren
apt install -y locales locales-all

# Deutsche Locales generieren
sed -i '/de_DE.UTF-8/s/^# //g' /etc/locale.gen
sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen
locale-gen

# System-Locale auf Deutsch setzen
echo "LANG=de_DE.UTF-8" > /etc/locale.conf
echo "LC_ALL=de_DE.UTF-8" >> /etc/locale.conf
update-locale LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8
```

### 1.2 Zeitzone konfigurieren
```bash
# Zeitzone auf Deutschland setzen
timedatectl set-timezone Europe/Berlin
ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime

# Keyboard Layout auf Deutsch
echo "KEYMAP=de" > /etc/vconsole.conf
```

### 1.3 Deutsche Sprachpakete
```bash
# Deutsche Sprachpakete installieren
apt install -y \
  language-pack-de \
  manpages-de \
  manpages-de-dev

# Deutsche Fehlermeldungen aktivieren
echo "export LANG=de_DE.UTF-8" >> /etc/environment
echo "export LC_ALL=de_DE.UTF-8" >> /etc/environment
echo "export LC_MESSAGES=de_DE.UTF-8" >> /etc/environment
```

## 2. LXC-Optimierungen

### 2.1 Kernel-Module deaktivieren
```bash
# Unnötige Kernel-Module für LXC deaktivieren
echo "blacklist floppy" >> /etc/modprobe.d/blacklist-lxc.conf
echo "blacklist pcspkr" >> /etc/modprobe.d/blacklist-lxc.conf
```

### 2.2 systemd-Services optimieren
```bash
# LXC-spezifische Service-Optimierungen
systemctl mask systemd-udev-trigger.service
systemctl mask systemd-udev-settle.service
systemctl mask systemd-udevd.service

# Unnötige Services deaktivieren
systemctl disable apt-daily.service
systemctl disable apt-daily.timer
systemctl disable apt-daily-upgrade.service
systemctl disable apt-daily-upgrade.timer
```

### 2.3 System-Parameter optimieren
```bash
# Container-spezifische Optimierungen
cat >> /etc/sysctl.conf << 'EOF'
# LXC-Optimierungen
net.ipv4.ip_forward=0
net.ipv6.conf.all.disable_ipv6=1
vm.swappiness=10
EOF

# Logging für LXC optimieren
cat >> /etc/systemd/journald.conf << 'EOF'
Storage=volatile
RuntimeMaxUse=100M
EOF
```

## 3. Basis-Pakete installieren

### 3.1 System-Tools
```bash
# Basis-Pakete installieren (LXC-optimiert)
apt install -y \
  curl \
  wget \
  git \
  vim \
  htop \
  net-tools \
  dnsutils \
  ca-certificates \
  gnupg \
  lsb-release \
  supervisor
```

### 3.2 Development-Tools
```bash
# Python und Development-Tools
apt install -y \
  python3 \
  python3-pip \
  python3-venv \
  python3-dev \
  build-essential \
  pkg-config \
  libpq-dev
```

### 3.3 Service-Pakete
```bash
# Web-Services
apt install -y \
  nginx \
  postgresql \
  postgresql-contrib \
  redis-server

# Services aktivieren
systemctl enable postgresql
systemctl enable redis-server
systemctl enable nginx
systemctl enable supervisor
```

## 4. Benutzer-Konfiguration

### 4.1 daki-Benutzer erstellen
```bash
# Benutzer für die Anwendung erstellen
useradd -m -s /bin/bash -c "DA-KI Application User" daki

# Deutsche Umgebung für daki-User
echo "export LANG=de_DE.UTF-8" >> /home/daki/.bashrc
echo "export LC_ALL=de_DE.UTF-8" >> /home/daki/.bashrc
echo "export TZ=Europe/Berlin" >> /home/daki/.bashrc
```

### 4.2 Verzeichnis-Struktur
```bash
# Anwendungsverzeichnisse erstellen
mkdir -p /opt/daki/{app,logs,data,backups}
chown -R daki:daki /opt/daki

# Frontend-Verzeichnis
mkdir -p /var/www/daki-frontend
chown -R www-data:www-data /var/www/daki-frontend
```

## 5. SSH-Konfiguration

### 5.1 SSH-Sicherheit
```bash
# SSH-Konfiguration anpassen
cat >> /etc/ssh/sshd_config << 'EOF'
# DA-KI SSH-Konfiguration
PermitRootLogin yes
PasswordAuthentication yes
PubkeyAuthentication yes
Port 22
EOF

# SSH-Service neu starten
systemctl restart sshd
```

### 5.2 SSH-Keys (Optional)
```bash
# SSH-Keys für sicheren Zugang
# (Wird später konfiguriert)
```

## 6. Netzwerk-Validierung

### 6.1 Netzwerk-Tests
```bash
# Grundlegende Netzwerk-Tests
ping -c 3 10.1.1.254   # Gateway erreichbar?
ping -c 3 8.8.8.8       # Internet erreichbar?
nslookup google.com     # DNS funktioniert?

# IP-Konfiguration prüfen
ip addr show
ip route show
```

### 6.2 Service-Ports prüfen
```bash
# Prüfen welche Ports bereits belegt sind
netstat -tlnp
ss -tlnp

# Spezifische Ports für DA-KI prüfen
nc -zv 10.1.1.110 22    # SSH
nc -zv 10.1.1.110 80    # HTTP (noch nicht aktiv)
nc -zv 10.1.1.110 5432  # PostgreSQL (noch nicht aktiv)
```

## 7. Deutsche Bash-Aliase

### 7.1 Hilfreiche Aliase
```bash
# Deutsche Bash-Aliase für alle Benutzer
cat >> /etc/bash.bashrc << 'EOF'
# Deutsche Aliase
alias ll='ls -la'
alias la='ls -la'
alias l='ls -l'
alias ..='cd ..'
alias ...='cd ../..'
alias h='history'
alias df='df -h'
alias du='du -h'
alias free='free -h'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# DA-KI spezifische Aliase
alias daki-status='systemctl status postgresql redis-server nginx'
alias daki-logs='journalctl -f'
alias daki-top='htop'
EOF
```

## 8. System-Validierung

### 8.1 Lokalisierung prüfen
```bash
# Deutsche Einstellungen validieren
locale
date
timedatectl status

# Ausgabe sollte deutsch sein:
# LANG=de_DE.UTF-8
# Local time: Mi 2024-01-10 15:30:00 CET
# Time zone: Europe/Berlin (CET, +0100)
```

### 8.2 Service-Status prüfen
```bash
# LXC-optimierte Services prüfen
systemctl list-unit-files --state=enabled | grep -E "(postgresql|redis|nginx|supervisor)"
systemctl list-unit-files --state=masked | grep -E "(udev|floppy)"

# Memory-Usage prüfen
free -h
ps aux --sort=-%mem | head -10
```

### 8.3 Debugging-Tools
```bash
# Nützliche Debugging-Befehle
echo "=== System-Info ==="
hostnamectl
echo "=== Netzwerk ==="
ip addr show
echo "=== Services ==="
systemctl --failed
echo "=== Logs ==="
journalctl -p err --no-pager
```

## 9. Nächste Schritte

Nach erfolgreichem Basis-Setup:

1. **Service-Konfiguration** → [02-services-konfiguration.md](02-services-konfiguration.md)
2. **Tests und Validierung** → [03-tests-validierung.md](03-tests-validierung.md)

## Checkliste

- [ ] Container läuft mit IP 10.1.1.110
- [ ] Deutsche Lokalisierung aktiv
- [ ] LXC-Optimierungen angewendet
- [ ] Basis-Pakete installiert
- [ ] daki-Benutzer erstellt
- [ ] SSH-Zugang funktioniert
- [ ] Netzwerk-Connectivity bestätigt
- [ ] Services sind aktiviert (aber noch nicht konfiguriert)

---

**Status:** Basis-System ist bereit für Service-Konfiguration
