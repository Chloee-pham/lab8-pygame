# Lab 8 - Pygame Moving Squares

Simple Pygame project for practicing game-loop fundamentals.

## What this project does

- Opens a Pygame window
- Targets 10 moving squares (implementation skeleton currently in `main.py`)
- Uses a local virtual environment for dependencies

## Project structure

- `main.py`: App entry point and game skeleton
- `requirements.txt`: Python dependencies
- `REPORT.md`: Project report template

## Setup

1. Create and activate virtual environment (if not already created):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

From the workspace root, you can also run:

```bash
python3 main.py
```

## Code Explorer

Launch the lightweight browser-based code explorer for this project:

```bash
python code-explorer/serve.py
```

Then open:

```text
http://127.0.0.1:8000
```

## Flash Quiz

Test your knowledge of the Pygame project with an interactive learning tool:

```bash
python quiz/serve.py
```

Then open:

```text
http://127.0.0.1:8001
```

The quiz includes 6 modules covering:

- Pygame Fundamentals
- Physics & Movement
- Architecture & Design
- Code Organization
- Code Explorer Utility
- Advanced Pygame Concepts

See [quiz/README.md](quiz/README.md) for detailed information.

## Notes

- On macOS/Linux, activate with:

```bash
source .venv/bin/activate
```

- To deactivate:

```bash
deactivate
```
