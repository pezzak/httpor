build_docker:
	find . -path '*/__pycache__/*' -delete
	find . -type d -name '__pycache__' -empty -delete
	find . -name '*.pyc' -delete
	docker build -f Dockerfile -t pezzak/httpor:latest .
