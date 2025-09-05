# Variables
MAIN_BRANCH := main
DEV_BRANCH := dev

# Merge dev into main
merge:
	@echo "🔄 Starting merge process..."
	@echo "📍 Current branch: $$(git branch --show-current)"
	@echo "🚀 Switching to $(MAIN_BRANCH)..."
	git checkout $(MAIN_BRANCH)
	@echo "⬇️  Pulling latest changes from $(MAIN_BRANCH)..."
	git pull origin $(MAIN_BRANCH)
	@echo "🔀 Merging $(DEV_BRANCH) into $(MAIN_BRANCH)..."
	git merge $(DEV_BRANCH) --no-edit
	@echo "⬆️  Pushing changes to $(MAIN_BRANCH)..."
	git push origin $(MAIN_BRANCH)
	@echo "🔄 Returning to $(DEV_BRANCH)..."
	git checkout $(DEV_BRANCH)
	@echo "✅ Merge completed successfully!"

debug:
	export $$(grep -v '^#' .env.local | xargs) && FLASK_APP=website.py flask run --debug