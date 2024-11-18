dev:
    uv run flask --app main run --debug

install:
    uv sync

run-preview:
    uv run gunicorn main:app
