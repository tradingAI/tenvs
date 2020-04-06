.PHONY: install update test upload lint

install:
	pip3 install -e . --user

update:
	git pull origin master
	pip3 install -e . --user

test:
	docker-compose up

upload:
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
	rm -rf build
	rm -rf dist

lint:
	buildifier WORKSPACE
	find ./ -name 'BUILD' | xargs buildifier
