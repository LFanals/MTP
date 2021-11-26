install:
	pip install -r requirements.txt

run:
	cd protocol && python3 main.py
	
push:
	git add .
	git commit -m "tweak"
	git push

pull:
	git pull
	cd protocol && python3 main.py