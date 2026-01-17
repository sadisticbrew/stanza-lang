# Design Document: Stanza Programming Language

### **1. Motivation**

I’m building **Stanza** because I want to understand how programming languages actually work "under the hood." I’m currently a first-year student, and while I’m learning systems programming concepts, I **hate** manual memory management with a passion (pointers are a nightmare). So, I’m writing this interpreter in **Python** to focus on the logic of parsing and executing code without worrying about `malloc` or `free`.

The name "Stanza" comes from my interest in rap lyrics.

### **2. Core Architecture**

I designed Stanza as a classic tree-walk interpreter with three main stages:

* **Lexer (Tokenizer):** Breaks raw source code into manageable chunks (Tokens).
* **Parser (AST Generator):** Organizes tokens into a tree structure that represents the logic (Abstract Syntax Tree).
* **Interpreter (Runtime):** Walks through the tree and executes the code.

### **3. Implementation Details**

#### **The Lexer (`lexer.py`)**

My lexer reads the input character by character. It ignores whitespace and groups characters into tokens like `TT_INT`, `TT_FLOAT`, or keywords.

* **Numbers:** It handles both integers and floats by tracking decimal points.
* **Operators:** Standard math (`+`, `-`, `*`, `/`) plus comparison operators (`==`, `!=`, `<=`, etc.).
* **Keywords:** I’ve reserved specific words like `let`, `NOT`, `AND`, and `OR`.

#### **The Parser (`parser.py`)**

This was the tricky part. I used a **Recursive Descent Parser** to handle order of operations (BODMAS).

* **Precedence:** I structured the methods (`expression`, `term`, `factor`) so that multiplication and division happen before addition and subtraction.
* **AST Nodes:** The parser outputs nodes like `BinOpNode` (binary operations), `NumberNode`, and `VarAssignmentNode` that the interpreter can understand.
* **Error Handling:** If the syntax is wrong (like missing a parenthesis), it throws an `InvalidSyntaxError`.

#### **The Interpreter (`interpreter.py`)**

This is where the magic happens. The interpreter "visits" every node in the AST and produces a value.

* **The Vibe (Booleans):** instead of standard `True`/`False`, I mapped my boolean values to **`fact`** (True) and **`cap`** (False) to match the slang/rap theme.
* **Variables:** I implemented a `SymbolTable` to store variables. When I run `let x = 5`, it saves `x` in the table. If I try to access `y` without defining it, it throws a runtime error.
* **Math:** It supports basic arithmetic, powers (`^`), and comparisons.

### **4. Current Features**

* **Arithmetic:** `+`, `-`, `*`, `/`, `^`, `%`.
* **Logic:** Comparisons (`>`, `<`, `==`, `!=`) and `NOT` logic.
* **Variables:** Declaration using `let`.
* **Shell:** A REPL (Read-Eval-Print Loop) in `main.py` that lets me type `stanza >>` and run code instantly.

### **5. Future Plans**

* Implement variable **reassignment** (currently stuck on `VarReassignmentNode`).
* Add `if/else` conditionals.
* Add loop structures (`for`/`while`).

---
## Decision Log:


|      Date      |                  Decision                   | Rationale or Context                                                                                                                                                                                                                 |
| :------------: | :-----------------------------------------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **2025-12-25** |   **Added Exponentiation Operator (`^`)**   | Needed a way to perform power operations. Decided on `^` syntax (common in math) rather than `**` (common in Python) to keep the syntax distinct.                                                                                    |
| **2026-01-02** | **Adopted Visitor Pattern for Interpreter** | To execute code, we needed a way to traverse the AST. We chose the **Visitor Pattern**, where the `Interpreter` class defines a `visit_NodeName` method for every node type. This keeps execution logic separate from parsing logic. |
| **2026-01-02** |   **Centralized Runtime Error Handling**    | We needed a way to catch logic errors (like dividing by zero) without crashing the whole program. Created a specific `RTError` class to handle these.                                                                                |
| **2026-01-06** |     **Implemented Global Symbol Table**     | To support variables, we needed a way to store state. Decided on a `SymbolTable` dictionary. Currently, it is a single global scope, meaning all variables are accessible everywhere.                                                |




