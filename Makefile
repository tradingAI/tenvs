.PHONY: install update test upload lint build_image

install:
	pip3 install -e . --user

test:
	python3 -m pytest --cov-report=xml:docs/cov/report.xml --cov=tenvs
	coverage report -m

update:
	git pull origin main
	pip3 install -e . --user

upload:
	# 上传到 pypi.org 方便用户使用 pip 安装
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
	rm -rf build
	rm -rf dist

lint:
	flake8 .

build_image:
	docker build --build-arg BUILD_TIME=$(date +%s) . -t tradingai/tenvs:latest
