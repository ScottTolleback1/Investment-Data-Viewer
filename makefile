PYTHON = python3
SCRIPT = main.py

.PHONY: run 

run:
	$(PYTHON) $(SCRIPT)

clean:
	rm -f *.pyc
	rm -rf __pycache__
