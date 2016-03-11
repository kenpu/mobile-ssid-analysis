.PHONY: test try
DB = $(PWD)/data/ken.sqlite3

test :
	export PYTHONPATH=$(PWD)/src; \
	export MOBILE_DB=$(DB); \
	python -m test.simple_test; \
	python -m test.cluster;

try:
	@export PYTHONPATH=$(PWD)/src; \
	export MOBILE_DB=$(PWD)/data/ken.sqlite3; \
	python -m cmd.try
