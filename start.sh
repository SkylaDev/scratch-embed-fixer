#!/bin/bash

source venv/bin/activate
uvicorn run:app --host 0.0.0.0 --port 5008