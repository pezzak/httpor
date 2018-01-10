VERSION := $(shell cat httpor/server.py | grep -i "SERVER_VERSION =" | cut -d'=' -f2 | tr -d '" \n')

build_docker:
	find . -path '*/__pycache__/*' -delete
	find . -type d -name '__pycache__' -empty -delete
	find . -name '*.pyc' -delete
	docker build -f Dockerfile -t pezzak/httpor:latest .
	docker build -f Dockerfile -t pezzak/httpor:${VERSION} .
