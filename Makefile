.PHONY: help serve moderate test test-docker tunnel-init tunnel-up dns-check

PY := .venv/bin/python

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "} {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}'

serve: ## Levanta el Provider (server.py) en 0.0.0.0
	@$(PY) server.py

moderate: ## Prueba el cliente: make moderate TEXT="..." [HOST=.. PORT=..]
	@$(PY) client.py host $(or $(HOST),127.0.0.1) port $(or $(PORT),8010) text "$(TEXT)"

test: ## Corre las pruebas local (requiere server vivo + pytest en .venv)
	@PYTHONPATH=. $(PY) -m pytest

test-docker: ## Corre el set de pruebas en contenedores (provider + pytest)
	@docker compose up --build --abort-on-container-exit --exit-code-from tests

tunnel-init: ## Bootstrap del tunel Cloudflare (una sola vez)
	@./scripts/tunnel_init.sh

tunnel-up: ## Levanta el tunel Cloudflare (Ctrl+C para detener)
	@./scripts/tunnel_up.sh

dns-check: ## Diagnostico de DNS / endpoint / proceso del tunel
	@./scripts/check_dns.sh
