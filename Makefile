.PHONY: docker configs

python = `./configs/makeve.py`
vebin = `./configs/config.py -p vebin configs/secret-example.json configs/secret.json`
d = `pwd`
vm = docker_web_1


# docker run -ti -v `pwd`:/var/www/pashinin.com pashinin.com
#docker run -p 80:80 -d -v `pwd`:/var/www/pashinin.com pashinin.com
docker: configs
	(cd docker; docker-compose up -d redis db)
	sleep 4
	(cd docker; docker-compose up dbinit)
	sleep 2
	(cd docker; docker-compose up migration)
	(cd docker; docker-compose up -d web)
	docker exec -it $(vm) adduser user --uid `id -u` --quiet --disabled-password --gecos ""

# docker exec -it docker_web_1 userdel user
	# (cd docker; docker-compose up -d db redis)
# docker-compose up --force-recreate
# --no-deps db redis

dev: dev_pkgs

start: docker

dev_pkgs:
	npm install gulp gulp-sass gulp-livereload gulp-shell gulp-sourcemaps

bash:
	docker exec -it $(vm) bash

django:
	docker exec --user user -it $(vm) ./manage.py runserver 0.0.0.0:8000 --settings=pashinin.settings
# docker run -it -v `pwd`:/var/www/pashinin.com pashinin.com ./manage.py runserver 0.0.0.0:8000 --settings=pashinin.settings

glusterfs:
	docker exec $(vm) mount.glusterfs 10.254.239.1:/v3 /mnt/files

gulp:
	docker exec $(vm) gulp

configs:
	(cd configs; make templates)

migrate:
	docker exec --user user -it $(vm) ./manage.py migrate --run-syncdb
	docker exec --user user -it $(vm) ./manage.py makemigrations --settings=pashinin.settings
	docker exec --user user -it $(vm) ./manage.py migrate --settings=pashinin.settings

vm:
	(cd docker; make vm)

psql:
	docker exec -it --user postgres docker_db_1 psql

recreate: stop
	# sudo find -type d -name migrations -exec rm -rf {} \;
	(cd docker; docker rm docker_db_1; docker rm docker_web_1;)
	make docker

stop:
	docker stop $(vm)
	docker stop docker_db_1
	docker stop docker_redis_1

tmux:
	export LANG=en_US.UTF-8
	tmux new-session -s dev -d || echo "session created"
	tmux select-window -t runserver || tmux new-window -n runserver
	tmux send-keys -t runserver C-m 'make django' C-m
	tmux select-window -t gulp || tmux new-window -n gulp
	tmux send-keys -t gulp C-m 'gulp' C-m
	tmux select-window -t runserver
	tmux attach-session -t dev -d

ve:
	./configs/makeve.py
# TODO: upgrade pip

reqs:
	$(vebin)/pip3 install -r docker/requirements.txt

pull:
	sudo -H -u www-data git pull

# TODO: edit pg_hba.conf - put 127.0.0.1 trust
prod: pull
	sudo -H -u www-data make configs
	(cd configs; make ln_nginx)
	mkdir -p /mnt/files
	mount.glusterfs 10.254.239.1:/v3 /mnt/files
	psql -a -f configs/tmp/dbinit.sql -U postgres -p 5434 -h localhost
	(cd src; ./manage.py makemigrations; ./manage.py migrate)
	sudo service nginx reload

# (cd src; ../configs/migrations.sh)

# mkdir -p /var/www/pashinin.com
# cd /var/www/pashinin.com
# sudo -H -u www-data git clone https://github.com/pashinin-com/pashinin.com.git initial
# # sudo -H -u www-data git pull
# cd initial
# sudo -H -u www-data make prod

collectstatic:
	(cd src; ./manage.py collectstatic)

collectstatic-in-dcoker:
	docker exec --user user -it $(vm) ./manage.py collectstatic
