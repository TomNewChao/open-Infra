#!/usr/bin/env bash
set -e

#ADMIN_USER="admin"
#ADMIN_EMAIL="353712216@qq.com"

# Check if we are in the correct directory before running commands.
if [[ ! $(pwd) == '/opt/open_infra' ]]; then
	echo "Running in the wrong directory...switching to /opt/open-infra/open_infra"
	cd /opt/open_infra
fi

# collect static
python3 manage.py collectstatic --noinput
# make migrations and migrate
python3 manage.py makemigrations && python3 manage.py migrate
# mysqldump -u$mysql_user -h $mysql_host -P $mysql_port -p$mysql_password --databases open_infra --skip-lock-tables < /opt/open_infra/scripts/open-infra.sql

#if [[ -v ADMIN_USER ]] && [[ -v ADMIN_EMAIL ]];
#then
#	echo "Creating admin user $ADMIN_USER ..."
#	python3 manage.py createsuperuser --noinput --username "$ADMIN_USER" --email "$ADMIN_EMAIL" 2> /dev/null || \
#		echo "Superuser $ADMIN_USER already exists"
#fi


exec $@
