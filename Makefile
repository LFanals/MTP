install:
	pip install -r requirements.txt

run:
	python3 main.py
	
push:
	git add .
	git commit -m "tweak"
	git push