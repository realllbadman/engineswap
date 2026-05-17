#!/usr/bin/env python3
# Writes a clean .env file to the server

env_content = """SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=Engineswapsupplies@gmail.com
SMTP_PASSWORD=jjrrklxmaqoscsun
OWNER_EMAIL=Engineswapsupplies@gmail.com
BUSINESS_EMAIL=Engineswapsupplies@gmail.com
OWNER_PHONE=+1 (210) 595-9453
BUSINESS_NAME=EngineSwap Autos
ADMIN_USERNAME=admin
ADMIN_PASSWORD=2uvAfq_o1epSjE1Ffro12_X3EqQ
DATABASE_URL=sqlite:///./cars.db
"""

with open("/var/www/engineswap/.env", "w") as f:
    f.write(env_content)

print("env file fixed successfully")
print("Verifying...")
with open("/var/www/engineswap/.env") as f:
    print(f.read())
