#!/usr/bin/env python3
# Fixes port from 8000 to 8001 in service and nginx config

service_path = "/etc/systemd/system/engineswap.service"
nginx_path = "/etc/nginx/sites-available/engineswap"

# Fix service file
with open(service_path) as f:
    content = f.read()
content = content.replace("--port 8000", "--port 8001")
with open(service_path, "w") as f:
    f.write(content)
print("Service file updated")

# Fix nginx config
with open(nginx_path) as f:
    content = f.read()
content = content.replace("8000", "8001")
with open(nginx_path, "w") as f:
    f.write(content)
print("Nginx config updated")

print("Done! Now run: systemctl daemon-reload && systemctl restart engineswap && systemctl reload nginx")
