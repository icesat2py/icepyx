# activate virtual environment
# install dependencies listed in the requirments.txt file
# install the project (for development or testing)
# run tests
# clean files and directories
# build wheel and tar distributions

venv: venv/bin/activate
venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv
	venv/bin/pip install -Ur requirements.txt
	touch venv/bin/activate

install: venv
	venv/bin/python setup.py install

dev: venv
	venv/bin/pip install --editable .

test: venv
	venv/bin/pytest tests/test_*.py -v

clean:
	rm -rfv venv
	find -iname "*.pyc" -delete

activate: venv
	. venv/bin/activate && exec zsh
