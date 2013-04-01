.PHONY : check

check:
	PYTHONPATH=`pwd`/test:$$PYTHONPATH zopectl run test/__init__.py
