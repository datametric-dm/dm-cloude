# Production deploy — 217.198.9.199

## Подготовка сервера (Ubuntu 22.04+)
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu   $(. /etc/os-release && echo $VERSION_CODENAME) stable" |   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

## Деплой проекта
```bash
sudo mkdir -p /opt/dmcloud
sudo chown -R $USER:$USER /opt/dmcloud
cd /opt/dmcloud

# Скопируйте сюда распакованный проект (содержимое архива)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

- Frontend:  http://217.198.9.199
- Backend docs:  http://217.198.9.199/docs
- Healthcheck:  http://217.198.9.199/api/healthz

## Автозапуск (systemd)
```bash
cat >/etc/systemd/system/dmcloud.service <<'UNIT'
[Unit]
Description=DataMetrics Cloud (Mongo) - Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/dmcloud
ExecStart=/usr/bin/docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
ExecStop=/usr/bin/docker compose -f docker-compose.yml -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable dmcloud --now
```

## Файрволл (ufw)
```bash
sudo ufw allow 80/tcp
sudo ufw allow 22/tcp
# порт 27017 наружу НЕ открываем
```
