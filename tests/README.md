# Testing

This repository uses `pytest` with `pytest-cov` extension as the testing tool.

## Run all tests with coverage report

    python -m pytest --cov=./Taipower --cov-report term-missing --cov-report xml

## Run all tests including the slow ones

    python -m pytest --runslow

## Run a specific test

    python -m pytest -q ./Taipower/tests/TEST_FILE