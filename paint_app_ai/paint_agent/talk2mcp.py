"""
AI Agent that uses Gemini to control Mac drawing via MCP server
Exact match to your Windows Paint example structure
"""
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp import stdio_client
import asyncio
from google import genai
from concurrent.futures import TimeoutError
from functools import partial
import pyautogui
import sys 

# Load environment
load_dotenv()

# Initialize Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)

# Global state
max_iterations = 10
last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(client, prompt, timeout=15):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

async def main():
    reset_state()
    print("Starting main execution...")
    
    # Get screen info
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    
    print(f"Screen size: {screen_width}x{screen_height}")
    print(f"Center: ({center_x}, {center_y})\n")
    
    try:
        # Create MCP server connection
        print("Establishing connection to MCP server...")
        server_params = StdioServerParameters(
    command=sys.executable, 
    args=["drawing_mcp_server.py"]
)
        
        async with stdio_client(server_params) as (read, write):
            print("Connection established, creating session...")
            async with ClientSession(read, write) as session:
                print("Session created, initializing...")
                await session.initialize()
                
                # Get available tools
                print("Requesting tool list...")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"Successfully retrieved {len(tools)} tools\n")
                
                # Build tools description for LLM
                tools_description = []
                for i, tool in enumerate(tools):
                    try:
                        params = tool.inputSchema
                        desc = getattr(tool, 'description', 'No description available')
                        name = getattr(tool, 'name', f'tool_{i}')
                        
                        # Format the input schema
                        if 'properties' in params:
                            param_details = []
                            for param_name, param_info in params['properties'].items():
                                param_type = param_info.get('type', 'unknown')
                                param_desc = param_info.get('description', '')
                                param_details.append(f"{param_name}: {param_type} - {param_desc}")
                            params_str = ', '.join(param_details)
                        else:
                            params_str = 'no parameters'
                        
                        tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                        tools_description.append(tool_desc)
                        print(f"Tool: {name}")
                    except Exception as e:
                        print(f"Error processing tool {i}: {e}")
                        tools_description.append(f"{i+1}. Error processing tool")
                
                tools_description_text = "\n".join(tools_description)
                print("\n" + "="*60)
                
                system_prompt = f"""You are a drawing agent solving tasks in iterations. You have access to various drawing tools on Mac.

Available tools:
{tools_description_text}

Canvas information:
- Canvas size: 800x600 pixels (not screen size!)
- Good rectangle coordinates: (200, 150) to (600, 450)
- Text will be automatically centered inside the rectangle

You must respond with EXACTLY ONE line in one of these formats (no additional text):

1. For function calls:
FUNCTION_CALL: function_name|param1|param2|...

2. For final answers:
FINAL_ANSWER: Task completed

Important:
- ALWAYS call open_drawing_app FIRST before any drawing
- When a function returns success, proceed to next step
- Only give FINAL_ANSWER when you have completed all necessary actions
- Do not repeat function calls with the same parameters
- Use coordinates near the screen center

Examples:
- FUNCTION_CALL: open_drawing_app
- FUNCTION_CALL: draw_rectangle|{center_x-150}|{center_y-100}|{center_x+150}|{center_y+100}
- FUNCTION_CALL: add_text_in_drawing_app|Hello World
- FINAL_ANSWER: Task completed

DO NOT include any explanations or additional text.
Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_ANSWER:"""

                # The task query
                query = """Open the drawing app, draw a rectangle at coordinates (200, 150) to (600, 450), 
                        then call the add function with the numbers 50 and 75,
                        and write the result inside the rectangle."""
                
                print("TASK:", query)
                print("="*60 + "\n")
                
                # Iteration loop
                global iteration, last_response
                
                while iteration < max_iterations:
                    print(f"\n--- Iteration {iteration + 1} ---")
                    
                    # Build current query with history
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = query + "\n\n" + "\n".join(iteration_response)
                        current_query = current_query + "\n\nWhat should I do next?"
                    
                    # Get model's response with timeout
                    print("Preparing to generate LLM response...")
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    
                    try:
                        response = await generate_with_timeout(client, prompt)
                        response_text = response.text.strip()
                        print(f"LLM Response: {response_text}")
                        
                        # Find the FUNCTION_CALL or FINAL_ANSWER line
                        command_line = None
                        for line in response_text.split('\n'):
                            line = line.strip()
                            if line.startswith("FUNCTION_CALL:") or line.startswith("FINAL_ANSWER:"):
                                command_line = line
                                break
                        
                        if not command_line:
                            print("Warning: LLM response doesn't match expected format")
                            print("Retrying...")
                            iteration += 1
                            continue
                        
                        response_text = command_line
                        
                    except Exception as e:
                        print(f"Failed to get LLM response: {e}")
                        break
                    
                    # Handle FUNCTION_CALL
                    if response_text.startswith("FUNCTION_CALL:"):
                        _, function_info = response_text.split(":", 1)
                        parts = [p.strip() for p in function_info.split("|")]
                        func_name, params = parts[0], parts[1:]
                        
                        print(f"\nCalling function: {func_name}")
                        print(f"Parameters: {params}")
                        
                        try:
                            # Find the matching tool
                            tool = next((t for t in tools if t.name == func_name), None)
                            if not tool:
                                print(f"Unknown tool: {func_name}")
                                print(f"Available tools: {[t.name for t in tools]}")
                                raise ValueError(f"Unknown tool: {func_name}")
                            
                            # Prepare arguments according to the tool's schema
                            arguments = {}
                            schema_properties = tool.inputSchema.get('properties', {})
                            
                            for param_name, param_info in schema_properties.items():
                                if not params:
                                    break
                                value = params.pop(0)
                                param_type = param_info.get('type', 'string')
                                
                                # Convert to correct type
                                if param_type == 'integer':
                                    arguments[param_name] = int(value)
                                elif param_type == 'number':
                                    arguments[param_name] = float(value)
                                elif param_type == 'array':
                                    if isinstance(value, str):
                                        value = value.strip('[]').split(',')
                                    arguments[param_name] = [int(x.strip()) for x in value]
                                else:
                                    arguments[param_name] = str(value)
                            
                            print(f"Calling tool with arguments: {arguments}")
                            
                            # Call the tool via MCP
                            result = await session.call_tool(func_name, arguments=arguments)
                            
                            # Get result content
                            if hasattr(result, 'content'):
                                if isinstance(result.content, list):
                                    iteration_result = [
                                        item.text if hasattr(item, 'text') else str(item)
                                        for item in result.content
                                    ]
                                else:
                                    iteration_result = str(result.content)
                            else:
                                iteration_result = str(result)
                            
                            # Format response
                            if isinstance(iteration_result, list):
                                result_str = f"[{', '.join(iteration_result)}]"
                            else:
                                result_str = str(iteration_result)
                            
                            print(f"Result: {result_str}")
                            
                            iteration_response.append(
                                f"In iteration {iteration + 1} you called {func_name} with {arguments} parameters, "
                                f"and the function returned: {result_str}."
                            )
                            last_response = iteration_result
                            
                        except Exception as e:
                            print(f"Error executing function: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                            break
                    
                    # Handle FINAL_ANSWER
                    elif response_text.startswith("FINAL_ANSWER:"):
                        print("\n" + "="*60)
                        print("=== Agent Execution Complete ===")
                        print("="*60)
                        print(response_text)
                        print("\nCheck your drawing app to see the result!")
                        break
                    
                    iteration += 1
                
                if iteration >= max_iterations:
                    print(f"\nReached maximum iterations ({max_iterations})")
    
    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        reset_state()

if __name__ == "__main__":
    asyncio.run(main())