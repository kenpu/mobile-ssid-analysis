.PHONY: test try
DB = $(PWD)/data/ken.sqlite3
DB2 = $(PWD)/src/data/mobile-ssid-1a1c7011d61ca870.sq3

test :
	export PYTHONPATH=$(PWD)/src; \
	export MOBILE_DB=$(DB); \
	python -m test.simple_test; \
	python -m test.cluster;

try:
	@export PYTHONPATH=$(PWD)/src; \
	export MOBILE_DB=$(PWD)/data/ken.sqlite3; \
	python -m cmd.try

json :
	export PYTHONPATH=$(PWD)/src; \
	export MOBILE_DB=$(DB2); \
	python -m gen_hierarchy_json;

ken:
	@export PYTHONPATH=$(PWD)/src; \
	python src/algo.py $(DB)

http:
	python2 -m SimpleHTTPServer
