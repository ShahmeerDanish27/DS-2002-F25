.PHONY: Test Run

Test:
	@echo '--- Running Test Pipeline (Built-in Test Modes) ---'
	@python ./update_portfolio.py
	@python ./generate_summary.py
	@echo 'Test complete.'

Run:
	@python ./pipeline.py
