debug:
	export $$(grep -v '^#' .env.local | xargs) && FLASK_APP=website.py flask run --debug