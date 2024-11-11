install:
	rye pin 3.12
	rye sync
	rye build

run:
	python -m src.main
