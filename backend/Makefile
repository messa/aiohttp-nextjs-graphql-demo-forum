venv_dir=venv
python3=python3

run: $(venv_dir)/packages-installed
	$(venv_dir)/bin/forum-backend

schema.graphql: $(venv_dir)/packages-installed forum_backend/graphql/*
	$(venv_dir)/bin/python3 print_schema.py > $@

$(venv_dir)/packages-installed: requirements.txt setup.py
	test -d $(venv_dir) || $(python3) -m venv $(venv_dir)
	$(venv_dir)/bin/pip install -U pip wheel
	$(venv_dir)/bin/pip install -r requirements.txt
	$(venv_dir)/bin/pip install -e .
	touch $@
