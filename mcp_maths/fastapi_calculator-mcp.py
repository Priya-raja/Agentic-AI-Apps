from fastapi import FastAPI

app = FastAPI()

app.title = "FastAPI Calculator"
app.version = "1.0.0"
app.description = "A simple calculator API built with FastAPI."

@app.get("/add")
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

@app.get("/subtract")
def subtract(a: float, b: float) -> float:
    """Subtract two numbers"""
    return a - b

@app.get("/multiply")
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b

@app.get("/divide")
def divide(a: float, b: float) -> float:    
    """Divide two numbers"""
    if b == 0:
        return {"error": "Division by zero is not allowed."}
    return a / b
        