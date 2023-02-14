PYTHON=python3

install:
	${PYTHON} -m pip install .

install-dev:
	${PYTHON} -m pip install -e .

test:
	${PYTHON} pytest tests

build:
	${PYTHON} -m build

publish:
	${PYTHON} -m build
	twine upload dist/yogger-*.tar.gz dist/yogger-*.whl
