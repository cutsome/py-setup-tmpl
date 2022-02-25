PACKAGE_DIR := app/

# lists all available targets
.PHONY: list
list:
	@sh -c "$(MAKE) -p no_targets__ | \
		awk -F':' '/^[a-zA-Z0-9][^\$$#\/\\t=]*:([^=]|$$)/ {\
			split(\$$1,A,/ /);for(i in A)print A[i]\
		}' | grep -v '__\$$' | grep -v 'make\[1\]' | grep -v 'Makefile' | sort"
# required for list
no_targets__:

.PHONY: install
install:
	@poetry install
	@poetry run pre-commit install

.PHONY: update
update:
	@poetry update
	@poetry run pre-commit autoupdate

.PHONY: clean
clean:
	@rm -rf build dist .eggs *.egg-info
	@rm -rf .benchmarks .coverage coverage.xml htmlcov report.xml .tox
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -exec rm -rf {} +

.PHONY: lint
lint:
	@poetry run pre-commit run --all-files

.PHONY: test
test:
	@poetry run pytest $(PACKAGE_DIR) tests/ -s

.PHONY: check-all
check-all: update lint test

.PHONY: seeds
seeds:
	@poetry run python scripts/make_seeds.py
