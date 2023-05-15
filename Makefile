.PHONY: reqs
reqs:
	pipreqs --force --encoding=utf8 ./ --ignore .\venv-sql\

.PHONY: clean
clean:
	rm -rf .\venv-sql\

.PHONY: venv
venv:
	python -m venv venv-sql

.PHONY: install_reqs
install_reqs:
	pip install -r requirements.txt