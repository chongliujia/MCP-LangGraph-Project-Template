# MCP LangGraph Framework

An AI system framework based on the MCP (Model-Controller-Planner) protocol architecture, built using LangGraph.

## Architecture Overview

This framework adopts the MCP architecture:
- **Model**: Responsible for interacting with LLMs, handling natural language understanding and generation
- **Controller**: Controls system flow, coordinates interactions between components
- **Planner**: Responsible for task planning, decomposition, and execution strategy

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Project Structure

```
.
├── README.md
├── requirements.txt
├── main.py
├── .env.example
├── src/
│   ├── __init__.py
│   ├── models/         # Model layer implementation
│   ├── controllers/    # Controller layer implementation
│   ├── planners/       # Planner layer implementation
│   ├── agents/         # Composite agent implementation
│   ├── tools/          # Tool collection
│   └── utils/          # Common utility functions
└── examples/           # Usage examples
```
