.PHONY: install search run clean

install:               ## install the package + deps (editable)
	pip install -e .

search:                ## start the self-hosted SearxNG search backend
	docker compose up -d

run:                   ## run a task: make run TASK="..."
	python -m open_deerflow.main "$(TASK)"

clean:
	rm -f checkpoints.sqlite
