.PHONY: install update test upload lint build_image

install:
	pip3 install -e . --user

update:
	git pull origin master
	pip3 install -e . --user

test:
	docker-compose up

upload:
	# 上传到 pypi.org 方便用户使用 pip 安装
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
	rm -rf build
	rm -rf dist

lint:
	buildifier WORKSPACE
	find ./ -name 'BUILD' | xargs buildifier

build_image:
	# 需要先在环境变量中设置 TUSHARE_TOKEN
	docker build --build-arg TUSHARE_TOKEN=$TUSHARE_TOKEN --build-arg BUILD_TIME=$(date +%s) . -t tradingai/tenvs:latest
	# 重新 build
	# docker build --no-cache --build-arg TUSHARE_TOKEN=$TUSHARE_TOKEN . -t tradingai/bazel:latest
