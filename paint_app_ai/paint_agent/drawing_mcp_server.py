# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
import pyautogui
from mcp.server import Server
import subprocess
import time
from mcp.server.stdio import stdio_server
import asyncio 
from PIL import Image as PILImage, ImageDraw, ImageFont
# instantiate an MCP server client
mcp = FastMCP("mac-drawing-server")

drawing_app = None
 
app_process = None


# Global to store the canvas


canvas_image = None
canvas_draw = None
last_rectangle = None  # Add this

# Safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

PRIMARY_MONITOR_WIDTH = 1512
USE_SECONDARY_MONITOR = False
SECONDARY_MONITOR_OFFSET_X = 0

# DEFINE TOOLS

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]

def log(message: str):
    """Log to stderr"""
    print(f"[MAC-SERVER] {message}", file=sys.stderr, flush=True)

@mcp.tool()
async def open_drawing_app() -> dict:
    """Create a blank canvas"""
    global drawing_app, canvas_image, canvas_draw
    
    try:
        log("Creating blank canvas...")
        
        # Create a white canvas
        canvas_image = PILImage.new('RGB', (800, 600), color='white')
        canvas_draw = ImageDraw.Draw(canvas_image)
        
        drawing_app = True
        log("Canvas created successfully")
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Canvas created successfully"
                )
            ]
        }
    
    except Exception as e:
        log(f"Error creating canvas: {e}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }


@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle on canvas"""
    global drawing_app, canvas_draw, last_rectangle
    
    try:
        if not drawing_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Canvas not ready. Call open_drawing_app first."
                    )
                ]
            }
        
        log(f"Drawing rectangle: ({x1},{y1}) to ({x2},{y2})")
        
        # Draw rectangle on canvas
        canvas_draw.rectangle([x1, y1, x2, y2], outline='black', width=3)
        
        # Store rectangle coordinates for text placement
        last_rectangle = (x1, y1, x2, y2)
        
        log("Rectangle drawn successfully")
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2})"
                )
            ]
        }
    
    except Exception as e:
        log(f"Error drawing rectangle: {e}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def add_text_in_drawing_app(text: str) -> dict:
    """Add text to canvas and display result"""
    global drawing_app, canvas_image, canvas_draw, last_rectangle
    
    try:
        if not drawing_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Canvas not ready. Call open_drawing_app first."
                    )
                ]
            }
        
        log(f"Adding text: '{text}'")
        
        # Load font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position - center of last rectangle
        if last_rectangle:
            x1, y1, x2, y2 = last_rectangle
            # Center of rectangle
            text_x = (x1 + x2) // 2
            text_y = (y1 + y2) // 2
            
            # Get text size to center it properly
            bbox = canvas_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Adjust to center the text
            text_x -= text_width // 2
            text_y -= text_height // 2
        else:
            # Default to canvas center if no rectangle
            text_x, text_y = 300, 280
        
        canvas_draw.text((text_x, text_y), text, fill='black', font=font)
        
        # Save and open the image
        output_path = "/tmp/drawing_result.png"
        canvas_image.save(output_path)
        
        # Open in Preview
        subprocess.run(['open', output_path])
        
        log("Text added and image displayed successfully")
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text '{text}' added successfully. Image opened in Preview."
                )
            ]
        }
    
    except Exception as e:
        log(f"Error adding text: {e}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }

if __name__ == "__main__":
    print(f"[MAC-SERVER] Starting Mac Drawing MCP Server...", file=sys.stderr)
   
    print(f"[MAC-SERVER] Screen size: {pyautogui.size()}", file=sys.stderr)
    
    mcp.run()