.PHONY: all

test :
	export PYTHONPATH=$(PWD)/src:$(PWD)/src/test; \
		export MOBILE_DB=$(PWD)/data/ken.sqlite3; \
		python -m simple_test
