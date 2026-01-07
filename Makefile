# Variables
MAIN_BRANCH := main
DEV_BRANCH := dev

merge:
	git checkout $(MAIN_BRANCH)
	git pull origin $(MAIN_BRANCH)
	git merge $(DEV_BRANCH) --no-edit
	git push origin $(MAIN_BRANCH)
	git checkout $(DEV_BRANCH)
	@echo "Merge completed successfully!"

debug:
	bash -c 'set -a && source .env.local && DEBUG=1 FLASK_APP=website.py flask run --debug'

test:
	@echo "Generating HMAC signature for production test..."
	@bash -c 'set -a && source .env.local && \
	SIGNATURE=$$(python3 -c "import hmac,hashlib,os; \
	content=open(\"test_notification.xml\", \"rb\").read(); \
	secret=os.getenv(\"WEBHOOK_HMAC_SECRET\"); \
	print(hmac.new(secret.encode(), content, hashlib.sha1).hexdigest())"); \
	echo "Using signature: sha1=$$SIGNATURE"; \
	curl -X POST https://andrevargas.com.br/websub/callback \
	-H "Content-Type: application/atom+xml" \
	-H "User-Agent: FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)" \
	-H "X-Hub-Signature: sha1=$$SIGNATURE" \
	--data-binary @test_notification.xml \
	-v'

test-local:
	@echo "Generating HMAC signature for local test..."
	@bash -c 'set -a && source .env.local && \
	SIGNATURE=$$(python3 -c "import hmac,hashlib,os; \
	content=open(\"test_notification.xml\", \"rb\").read(); \
	secret=os.getenv(\"WEBHOOK_HMAC_SECRET\"); \
	print(hmac.new(secret.encode(), content, hashlib.sha1).hexdigest())"); \
	echo "Using signature: sha1=$$SIGNATURE"; \
	curl -X POST http://localhost:5000/websub/callback \
	-H "Content-Type: application/atom+xml" \
	-H "User-Agent: FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)" \
	-H "X-Hub-Signature: sha1=$$SIGNATURE" \
	--data-binary @test_notification.xml \
	-v'

test-local-invalid:
	curl -X POST http://localhost:5000/websub/callback \
	-H "Content-Type: application/atom+xml" \
	-H "User-Agent: FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)" \
	-H "X-Hub-Signature: sha1=fakeinvalidsignature123" \
	-d @test_notification.xml \
	-v