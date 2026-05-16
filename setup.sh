#!/bin/bash
set -e
echo "=== EngineSwap Autos — Server Setup ==="

cd /var/www/engineswap

# 1. Virtual environment
echo "[1/5] Creating virtual environment..."
python3 -m venv venv
venv/bin/pip install --quiet -r requirements.txt
echo "      Packages installed."

# 2. Systemd service
echo "[2/5] Creating service..."
cat > /etc/systemd/system/engineswap.service << SERVICE
[Unit]
Description=EngineSwap Autos
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/engineswap
ExecStart=/var/www/engineswap/venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE
echo "      Service file created."

# 3. Nginx config
echo "[3/5] Configuring Nginx..."
cat > /etc/nginx/sites-available/engineswap << NGINX
server {
    listen 80;
    server_name engineswapautos.com www.engineswapautos.com;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/engineswap /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
echo "      Nginx configured."

# 4. Start services
echo "[4/5] Starting services..."
systemctl daemon-reload
systemctl enable engineswap
systemctl restart engineswap
systemctl reload nginx
echo "      Services started."

# 5. Status check
echo "[5/5] Status check..."
sleep 2
systemctl is-active engineswap && echo "      Site is RUNNING on port 8000!" || echo "ERROR: Site failed to start — run: journalctl -u engineswap -n 20"

echo ""
echo "=== Setup complete! ==="
echo "Next: Create your .env file then run: systemctl restart engineswap"
