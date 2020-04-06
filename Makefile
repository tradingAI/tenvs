.PHONY: install update test

install:
	pip3 install -e . --user

update:
	git pull origin master
	pip3 install -e . --user

test:
	docker-compose up

dist:
	python3 setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*

clean:
	rm -rf build
	rm -rf dist
