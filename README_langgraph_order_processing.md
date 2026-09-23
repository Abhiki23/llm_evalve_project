# LangGraph 101 — Order Processing Workflow

A beginner-friendly **LangGraph** project that demonstrates how to build a stateful workflow for processing customer orders.

The application models a simple order-processing pipeline in which an order is validated, inventory availability is checked, and the workflow conditionally confirms or rejects the order based on stock availability.

This project is intentionally small and focused on the core concepts of **LangGraph**, including **StateGraph**, shared state, nodes, edges, conditional routing, and workflow compilation.

---

## Project Overview

The workflow accepts an order containing:

- **Product name**
- **Requested quantity**

The order then moves through a sequence of LangGraph nodes:

1. **Validate Order** — checks whether the product is present and the requested quantity is greater than zero.
2. **Check Stock** — checks the requested quantity against a small in-memory inventory.
3. **Route the Workflow** — determines whether the order should be confirmed or rejected based on stock availability.
4. **Confirm Order** — marks an order as `CONFIRMED` when sufficient stock is available.
5. **Reject Order** — marks an order as `REJECTED` when sufficient stock is not available.

### Workflow

```text
                     ┌───────────────┐
                     │  Order Input  │
                     └───────┬───────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Validate Order  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Check Stock   │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │ Conditional     │
                    │    Router       │
                    └───────┬─────────┘
                            / \
                           /   \
                          ▼     ▼
                 ┌──────────┐ ┌──────────┐
                 │ Confirm  │ │  Reject  │
                 │  Order   │ │  Order   │
                 └────┬─────┘ └────┬─────┘
                      │             │
                      └──────┬──────┘
                             ▼
                           END
```

---

## Key LangGraph Concepts Demonstrated

### 1. Shared State

The workflow uses a `TypedDict` named `OrderState` to define the information passed between nodes.

```python
class OrderState(TypedDict):
    product: str
    quantity: int
    is_valid: bool
    stock_available: bool
    status: str
```

The state contains both the original user input and values produced while the workflow executes.

| State Field | Type | Purpose |
|---|---|---|
| `product` | `str` | Product requested by the customer |
| `quantity` | `int` | Quantity requested |
| `is_valid` | `bool` | Result of order validation |
| `stock_available` | `bool` | Whether inventory can satisfy the request |
| `status` | `str` | Final order status |

---

### 2. Nodes

Each major operation is represented by a Python function and registered as a node in the graph.

The project contains four nodes:

- `validation_order`
- `check_stock`
- `confirm_order`
- `reject_order`

This separation makes the workflow easier to understand and extend.

---

### 3. Sequential Edges

The graph connects the validation and inventory steps using a normal edge:

```python
workflow.add_edge("validate", "check_stock")
```

This means that after the `validate` node completes, execution moves to `check_stock`.

---

### 4. Conditional Routing

The most important LangGraph concept in this project is conditional routing.

The `stock_router()` function examines the shared state:

```python
def stock_router(state):
    if state["stock_available"]:
        return "confirm"

    return "reject"
```

The graph uses this function to decide which node executes next:

```python
workflow.add_conditional_edges("check_stock", stock_router)
```

Therefore, the workflow can dynamically follow different paths based on the current state.

---

## Project Structure

```text
langgraph-101-main/
│
├── app/
│   ├── __init__.py
│   ├── edges.py          # Conditional routing logic
│   ├── graph.py          # LangGraph workflow definition
│   ├── main.py           # Example order execution
│   ├── nodes.py          # Workflow node functions
│   └── state.py          # Shared OrderState definition
│
├── main.py               # Project entry point template
├── requirements.txt      # Python dependencies
├── pyproject.toml         # Project metadata and configuration
├── uv.lock               # Locked dependency versions
└── README.md
```

### File-by-file explanation

#### `app/state.py`

Defines the shared state object used by the LangGraph workflow.

#### `app/nodes.py`

Contains the individual workflow operations:

- `validation_order()` validates the order.
- `check_stock()` checks the requested quantity against the sample inventory.
- `confirm_order()` sets the order status to `CONFIRMED`.
- `reject_order()` sets the order status to `REJECTED`.

#### `app/edges.py`

Contains the conditional routing function `stock_router()`.

#### `app/graph.py`

Builds and compiles the LangGraph workflow using `StateGraph`.

#### `app/main.py`

Creates a sample order, invokes the compiled graph, and prints the final state.

---

## Technology Stack

- **Python**
- **LangGraph**
- **TypedDict** from Python's `typing` module
- **uv** / `pyproject.toml` / `uv.lock` for project and dependency management

---

## Requirements

The project declares Python `>=3.13` in `pyproject.toml`.

You will need:

- **Python 3.13 or newer**
- **pip** or **uv**
- A terminal such as PowerShell, Command Prompt, Bash, or an integrated VS Code terminal

The project currently requires **LangGraph**.

---

## Installation

### Option 1 — Using a virtual environment with `venv`

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

### Option 2 — Using `uv`

If you use `uv`, create/synchronize the project environment from the project configuration and lock file:

```bash
uv sync
```

Then run the application with:

```bash
uv run python -m app.main
```

Depending on your local `uv` setup, you can also activate the generated environment and run the application normally.

---

## Running the Project

From the project root directory, run:

```bash
python -m app.main
```

Or, after activating your virtual environment:

```bash
python app/main.py
```

With `uv`:

```bash
uv run python -m app.main
```

The program creates the following sample order in `app/main.py`:

```python
order = {
    "product": "laptop",
    "quantity": 2,
    "is_valid": False,
    "stock_available": False,
    "status": ""
}
```

The graph then processes the order and prints the final state.

---

## Sample Inventory

The stock-checking node currently uses a hard-coded in-memory inventory:

```python
inventory = {
    "laptop": 5,
    "keyboard": 10,
    "wires": 20,
}
```

For example:

| Product | Available Stock |
|---|---:|
| Laptop | 5 |
| Keyboard | 10 |
| Wires | 20 |

The requested quantity is compared with the available quantity.

If:

```text
available stock >= requested quantity
```

the router returns `confirm`.

Otherwise, it returns `reject`.

---

## Example Execution

For the default order:

```text
Product: laptop
Quantity: 2
```

The inventory contains five laptops, so the requested quantity can be fulfilled.

The workflow follows:

```text
START
  ↓
Validate
  ↓
Check Stock
  ↓
Confirm
  ↓
END
```

The final state contains a `status` of:

```text
CONFIRMED
```

For an order such as:

```python
{
    "product": "laptop",
    "quantity": 10,
    "is_valid": False,
    "stock_available": False,
    "status": ""
}
```

the requested quantity exceeds the five laptops available, so the workflow follows:

```text
START
  ↓
Validate
  ↓
Check Stock
  ↓
Reject
  ↓
END
```

The resulting status is:

```text
REJECTED
```

---

## How the Graph Is Built

The graph is constructed in `app/graph.py`.

### Step 1 — Create the StateGraph

```python
workflow = StateGraph(OrderState)
```

The graph is told that `OrderState` represents the shared state.

### Step 2 — Add Nodes

```python
workflow.add_node("validate", validation_order)
workflow.add_node("check_stock", check_stock)
workflow.add_node("confirm", confirm_order)
workflow.add_node("reject", reject_order)
```

### Step 3 — Set the Entry Point

```python
workflow.set_entry_point("validate")
```

The workflow starts with order validation.

### Step 4 — Add Edges

```python
workflow.add_edge("validate", "check_stock")
```

### Step 5 — Add Conditional Routing

```python
workflow.add_conditional_edges("check_stock", stock_router)
```

### Step 6 — Define Terminal Nodes

```python
workflow.add_edge("confirm", END)
workflow.add_edge("reject", END)
```

### Step 7 — Compile

```python
graph = workflow.compile()
```

The compiled graph can then be invoked with an initial state.

---

## Important Implementation Note

The project currently calculates an `is_valid` value during the validation step, but the graph does **not currently use `is_valid` as a conditional routing decision**.

The current graph always moves from:

```text
validate → check_stock
```

and the conditional router makes its decision using `stock_available`.

Therefore, the current implementation demonstrates **validation as a state update** and **stock availability as the actual routing condition**.

A future version could add a conditional edge after validation so invalid orders are rejected before the stock-checking step.

---

## Learning Objectives

This project is useful for learning the fundamentals of **LangGraph** before moving to more advanced AI-agent workflows.

By studying this project, you can understand:

- How **StateGraph** works
- How to define shared workflow state
- How to create LangGraph nodes
- How nodes update state
- How sequential edges work
- How conditional edges work
- How routers determine the next workflow step
- How to compile a graph
- How to invoke a compiled graph
- How state moves through a workflow
- How deterministic business workflows can be represented as graphs

---

## Possible Extensions

The current project intentionally uses a simple hard-coded inventory. It can be extended into a more realistic workflow by adding:

### 1. Database-backed Inventory

Replace the in-memory dictionary with an inventory database such as PostgreSQL, MySQL, or SQLite.

### 2. Validation Routing

Add a conditional route after validation:

```text
             Validate
             /      \
          Valid    Invalid
            |         |
            ▼         ▼
       Check Stock   Reject
```

### 3. Order Database

Persist confirmed and rejected orders for later tracking.

### 4. Payment Node

Add a payment-processing step before final confirmation.

### 5. Human Approval

Introduce a human-in-the-loop step for high-value orders.

### 6. LLM Integration

Use an LLM to interpret natural-language customer requests and convert them into structured order state.

For example:

```text
"I need three laptops"
        ↓
LLM / Parser
        ↓
product = laptop
quantity = 3
        ↓
LangGraph Workflow
```

### 7. API Layer

Expose the workflow through **FastAPI** so external applications can submit orders programmatically.

### 8. Web Interface

Build a **Streamlit** or frontend application on top of the workflow.

---

## GitHub Setup

Before pushing this project to GitHub, make sure unnecessary generated files are excluded.

A recommended `.gitignore` includes:

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo

# Virtual environments
.venv/
venv/
env/

# IDE
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

# Build artifacts
build/
dist/
*.egg-info/
```

If you create environment files later, also exclude them:

```gitignore
.env
.env.*
```

Do **not** commit passwords, API keys, database credentials, or other secrets to GitHub.

---

## Git Commands

Initialize Git if the repository is not already initialized:

```bash
git init
```

Check the project files:

```bash
git status
```

Add the files:

```bash
git add .
```

Create the first commit:

```bash
git commit -m "Add LangGraph order processing workflow"
```

Connect your GitHub repository:

```bash
git remote add origin https://github.com/<your-username>/<repository-name>.git
```

Push the project:

```bash
git branch -M main
git push -u origin main
```

Replace `<your-username>` and `<repository-name>` with your actual GitHub details.

---

## Suggested Repository Name

A clean repository name could be:

```text
langgraph-order-processing
```

Other options:

```text
langgraph-101
langgraph-order-workflow
langgraph-stateful-workflow
```

---

## Suggested GitHub Repository Description

> Beginner-friendly LangGraph order processing workflow demonstrating shared state, nodes, sequential edges, conditional routing, and inventory-based order confirmation.

---

## Architecture Summary

At a high level, the application follows this pattern:

```text
Input State
    │
    ▼
Validation Node
    │
    ▼
Stock Check Node
    │
    ▼
Conditional Router
   / \
  /   \
 ▼     ▼
Confirm Reject
  \     /
   \   /
    ▼ ▼
    END
```

This is a simple example of how **LangGraph can model stateful, branching workflows**. The same concepts can be applied to larger applications such as **AI agents**, **multi-agent systems**, customer-support workflows, document-processing pipelines, and other state-driven applications.

---

## License

No license is currently specified in the project files. If you plan to make the repository publicly reusable, consider adding an appropriate open-source license such as the MIT License.

---

## Author

**Abhishek Kundley**

AI / Generative AI Engineer

- GitHub: Add your GitHub profile URL
- LinkedIn: Add your LinkedIn profile URL
