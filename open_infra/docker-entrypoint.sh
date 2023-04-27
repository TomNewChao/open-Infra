#!/usr/bin/env bash
set -e

# Check if we are in the correct directory before running commands.
if [[ ! $(pwd) == '/opt/open_infra' ]]; then
	echo "Running in the wrong directory...switching to /opt/open-infra/open_infra"
	cd /opt/open_infra
fi

# collect static
python3 manage.py collectstatic --noinput

python3 manage.py migrate


exec $@
