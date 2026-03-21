# Stanza

Stanza is a custom, interpreted programming language built entirely from scratch in Python. It features a clean, simple syntax and handles its own memory—so you don't have to deal with pointers. 

## Features
* **Interpreted:** Runs directly via the custom Python interpreter.
* **No Pointers:** Zero memory-management headaches. 
* **Custom Booleans:** True and False are evaluated as `fact` and `cap`.
* **Functions:** First-class support for named and anonymous functions.
* **Detailed Error Handling:** Points exactly to where you messed up in the code with visual arrows.

## Architecture
Stanza evaluates code in three main steps:
1. **Lexer:** Reads the raw text and breaks it down into understandable `Tokens`.
2. **Parser:** Takes those tokens and builds an Abstract Syntax Tree (AST) using specific `Nodes`.
3. **Interpreter:** Traverses the AST, managing the `Context` and `SymbolTable` to execute the logic.

## Syntax Crash Course

### Variables
Declare variables using the `let` keyword. 
```stanza
let age = 20
age = 21 
```

### Booleans & Logic
Standard comparators (`<`, `>`, `==`, `!=`, `<=`, `>=`) are supported. Booleans evaluate to `fact` (True) or `cap` (False).
```stanza
let is_valid = not (10 == 5)
```

### Control Flow
Use `if`, `then`, `elif`, and `else` to handle logic branches.
```stanza
if age >= 18 then 
    let status = 1 
elif age == 17 then 
    let status = 2
else 
    let status = 0
```

### Loops
Stanza supports both `while` and `for` loops.
```stanza
while x < 10 do let x = x + 1

for i in 0 to 10 step 2 do 
    let result = result + i
```

### Functions
Define functions using the `fn` keyword and an `->` arrow pointing to the return expression.
```stanza
fn add_numbers(a, b) -> a + b

let sum = add_numbers(5, 10)
```

## Running Stanza
*(Add your installation or execution instructions here, e.g., how to run `shell.py`)*

---
**Author:** Pratham Patel
