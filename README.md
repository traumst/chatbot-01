# Ollama wrapper for local chat

## Prerequisites

### Install Ollama

[Official website](https://ollama.com/download) and run it.
Once live, you should be able to run `ollama` to see help message.
Some useful commands are below, any of them rnning without error means ollama is running:
* `ollama run deepseek-r1:8b` which also pulls image if needed
* `ollama ps` to see active models
* `ollama list` to see locally available models
* `ollama stop deepseek-r1:8b` to disable specified model

We can also query it via an API to get streamed response with
```shell
curl http://localhost:11434/api/generate -d '{
    "model": "deepseek-r1:8b",
    "prompt": "Why is the sky blue?"
}' | jq  --unbuffered -r '.response'
```
or
```shell
curl http://localhost:11434/api/chat -d '{
    "model": "deepseek-r1:8b",
    "messages": [
      {"role": "system","content": "user is experienced physicist, give deeply technical explanation" },
      {"role": "user","content": "why is the sky blue?" }
    ],
    "options": { "json": true }
}' | jq  --unbuffered -r ".message.content"
```

### Install Dependencies

Create venv, source it and install dependencies:
```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 
```

### Run application

Start up application, listens on port specified in `.env` file
```shell
python server.py
```
Run all unit tests, which implies test module naming convention.
`-v` option prints file and test names with results.
```shell
python -m unittest -v src/**/test_*.py
```

## Alembic DB Migrations

By far, the most annoying part is the alembic.
I've already complicated myself just renaming tables...
Anyways, the main DB is created as `test.db` at the root of the working folder.
It is checked and created on startup.
Alembic migrations were initiated with
```shell
alembic init migrations
```
Initial migration was created like below and then adjusted manually
```shell
alembic revision --autogenerate -m "Initial migration"
```
Initial and consequent migrations are all applied using
```shell
alembic upgrade head
```
Finally, we can see current state using
```shell
alembic history --verbose
```
and
```shell
alembic current
```
That being said, good luck lmao.