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
	bash -c 'set -a && source .env.local && DEBUG=1 FLASK_APP=website.py flask run --debug'

test:
	curl -X POST https://andrevargas.com.br/websub/callback \
	-H "Content-Type: application/atom+xml" \
	-H "User-Agent: FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)" \
	-d @test_notification.xml \
	-v

# Teste HMAC com assinatura válida
test-local:
	@echo "🧪 Testing HMAC validation with valid signature..."
	curl -X POST http://localhost:5000/websub/callback \
	-H "Content-Type: application/atom+xml" \
	-H "User-Agent: FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)" \
	-H "X-Hub-Signature: sha1=7aec651cb69a4ca65a147ad26586b5af4bbb96ea" \
	-d @test_notification.xml \
	-v

# Teste HMAC com assinatura inválida
test-local-invalid:
	@echo "🧪 Testing HMAC validation with INVALID signature..."
	curl -X POST http://localhost:5000/websub/callback \
	-H "Content-Type: application/atom+xml" \
	-H "User-Agent: FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)" \
	-H "X-Hub-Signature: sha1=fakeinvalidsignature123" \
	-d @test_notification.xml \
	-v