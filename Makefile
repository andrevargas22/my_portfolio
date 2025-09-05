# Variables
MAIN_BRANCH := main
DEV_BRANCH := dev

# Merge dev into main
merge:
	git checkout $(MAIN_BRANCH)
	git pull origin $(MAIN_BRANCH)
	git merge $(DEV_BRANCH) --no-edit
	git push origin $(MAIN_BRANCH)
	git checkout $(DEV_BRANCH)
	@echo "✅ Merge completed successfully!"

debug:
	export $$(grep -v '^#' .env.local | xargs) && FLASK_APP=website.py flask run --debug

test:
	curl -X POST https://andrevargas.com.br/websub/callback \
	-H "Content-Type: application/atom+xml" \
	-H "User-Agent: FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)" \
	-d @test_notification.xml \
	-v