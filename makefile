install:
	poetry install

run:
	poetry run streamlit run src/rental_analytics_model/app.py

format:
	poetry run black src

lint:
	poetry run ruff src

update:
	poetry update