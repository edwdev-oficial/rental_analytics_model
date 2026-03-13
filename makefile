install:
	poetry install

run:
	poetry run streamlit run app.py

format:
	poetry run black src

lint:
	poetry run ruff src

update:
	poetry update