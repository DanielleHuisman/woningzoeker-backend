#!/bin/sh

# Start bots
pipenv run python manage.py shell -c "import notifications.bots"
