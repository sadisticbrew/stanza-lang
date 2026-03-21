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
