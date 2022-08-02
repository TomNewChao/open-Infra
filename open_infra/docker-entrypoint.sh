#!/usr/bin/env bash
set -e

#ADMIN_USER="admin"
#ADMIN_EMAIL="353712216@qq.com"

# Check if we are in the correct directory before running commands.
if [[ ! $(pwd) == '/opt/open_infra' ]]; then
	echo "Running in the wrong directory...switching to /opt/open-infra/open_infra"
	cd /opt/open_infra
fi

# python3 manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate


#if [[ -v ADMIN_USER ]] && [[ -v ADMIN_EMAIL ]];
#then
#	echo "Creating admin user $ADMIN_USER ..."
#	python3 manage.py createsuperuser --noinput --username "$ADMIN_USER" --email "$ADMIN_EMAIL" 2> /dev/null || \
#		echo "Superuser $ADMIN_USER already exists"
#fi


exec $@
