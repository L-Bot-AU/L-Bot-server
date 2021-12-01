# SETUP LINUX, DOCKER, (PORTAINER)

## Linux
	existing timezone
		timedatectl

	set to AEST
		sudo timedatectl set-timezone Australia/Sydney


## Docker + docker-compose Install

	sudo apt install docker.io -y
	https://linuxhandbook.com/docker-permission-denied/

	sudo groupadd docker
	sudo systemctl enable --now docker
	sudo usermod -aG docker $USER

	# log out and log back in

	# testing:
	docker --version

	docker run hello-world
	docker run -it ubuntu bash

    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

    sudo chmod +x /usr/local/bin/docker-compose
    (sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose)



## Portainer Install

	# create portainer_data volume if not done so
	docker volume create portainer_data

	docker run -d -p 8000:8000 -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce
    # http://<host>:9000

# CODE + ENV

## requirements.txt, add these:
eventlet

loguru


## must have these:
Dockerfile

docker-compose.yaml

project.env

on deployment:

change project.env

	WEBSITE_HOST_PORT=80
	HOST_VOLUME=/projects/L-Bot-server-main

for convenience:

	build.sh

	up.sh

	down.sh


## IMPORTANT project.env
modify

	WEBSITE_HOST_PORT

	HOST_VOLUME


## commented out:
kill_port.py

	if platform.system() == "Linux":

		pass


## (optional) add loguru to these:
database/website_client_interface.py

database/database_tasks.py

database/camera_system_interface.py

	from loguru import logger

	print = lambda *args : logger.debug(" ".join(str(i) for i in args))


## VERY VERY IMPORTANT:
website/templates/base.html

	const sio = io("ws://<HOST_IP>:2910");

	eg. const sio = io("ws://192.168.1.9:2910");


## deleted:
website/static/requests.js

## modified
website/static/style.css

span {
	/* something dodgy about it transitioning twice, this turns off one of the transitions */
	transition-duration: 0s;
}

# BUILD / UP / DOWN

## to build - ONLY NEED TO DO THIS ONCE - code is NOT baked in, UNLESS CHANGED requirements.txt
	# build.sh
	docker build --tag 'l-bot' .


## to up:
	# up.sh
	_UID=$(id -u) _GID=$(id -g) docker-compose --env-file project.env up --detach


## to down:
	# down.sh
	_UID=$(id -u) _GID=$(id -g) docker-compose --env-file project.env down


## see logs:
	# https://docs.docker.com/engine/reference/commandline/logs/

	docker logs <CONTAINER_NAME>

	containers are
		l-bot_website
		l-bot_website_client
		l-bot_camera_snr
		l-bot_camera_jnr

	docker logs --follow l-bot_website
	docker logs --follow l-bot_website_client
	docker logs --tail 10 l-bot_website_client
