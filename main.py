# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pydantic-ai",
#     "click",
#     "rich",
#     "pandas",
# ]
# ///
import asyncio
import os
import sys
import tempfile
import subprocess
from pathlib import Path
import click
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from pydantic_ai import Agent

console = Console()

agent = Agent(
    'anthropic:claude-sonnet-4-0',
    instructions="""
    You are an intelligent assistant that can handle various types of queries. Analyze the user's request and respond appropriately:

    RESPONSE MODES:
    1. DIRECT_ANSWER: For questions that need direct responses (explanations, facts, analysis)
    2. CODE_EXECUTION: For tasks that require code execution (calculations, file processing, data analysis)

    FORMAT YOUR RESPONSE:
    Start with either "DIRECT_ANSWER:" or "CODE_EXECUTION:" followed by your response.

    DIRECT_ANSWER Examples:
    Query: "What is machine learning?"
    Response: DIRECT_ANSWER: Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed...

    Query: "Explain the difference between lists and tuples in Python"
    Response: DIRECT_ANSWER: Lists and tuples are both sequence types in Python, but lists are mutable (can be changed) while tuples are immutable...

    CODE_EXECUTION Examples:
    Query: "calculate fibonacci of 10"
    Response: CODE_EXECUTION:
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    result = fibonacci(10)
    print(f"Fibonacci of 10: {result}")

    Query: "how many rows in data.csv"
    Response: CODE_EXECUTION:
    import pandas as pd
    import os
    
    if os.path.exists('data.csv'):
        df = pd.read_csv('data.csv')
        print(f"Number of rows in data.csv: {len(df)}")
        print(f"Number of columns: {len(df.columns)}")
        print(f"Columns: {list(df.columns)}")
    else:
        print("data.csv file not found in current directory")

    Query: "preview first 5 rows of sales.json"
    Response: CODE_EXECUTION:
    import json
    import pandas as pd
    import os
    
    if os.path.exists('sales.json'):
        with open('sales.json', 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
            print("First 5 rows:")
            print(df.head())
        else:
            print("JSON structure preview:")
            for i, (key, value) in enumerate(data.items()):
                if i < 5:
                    print(f"{key}: {value}")
                else:
                    print("...")
                    break
    else:
        print("sales.json file not found")

    RULES:
    - For CODE_EXECUTION: Generate clean, executable Python code
    - Include proper error handling for file operations
    - Use pandas for CSV/Excel files, json for JSON files
    - For file analysis, check if file exists first
    - Always use print() to show results
    - Keep code focused and minimal
    """
)

@click.command()
@click.argument('query', nargs=-1, required=True)
@click.option('--execute/--no-execute', '-e/-n', default=True, help='Execute the generated code')
@click.option('--save', '-s', help='Save generated code to file')
@click.option('--show-code/--no-show-code', default=True, help='Show generated code before execution')
def main(query, execute, save, show_code):
    """
    Smart CLI: Generate and execute Python code from natural language queries.
    
    Examples:
    smart-cli "calculate the sum of first 10 prime numbers"
    smart-cli "create a simple web scraper for quotes" --no-execute
    smart-cli "generate random password of length 12" --save password_gen.py
    """
    query_text = ' '.join(query)
    
    if not query_text.strip():
        console.print("[red]Error: Please provide a query[/red]")
        sys.exit(1)
    
    asyncio.run(process_query(query_text, execute, save, show_code))

async def process_query(query_text: str, execute: bool, save: str, show_code: bool):
    console.print(f"[blue]Query:[/blue] {query_text}")
    console.print("[yellow]Processing...[/yellow]")
    
    try:
        result = await agent.run(query_text)
        response = result.output.strip()
        
        # Clean up markdown formatting if present
        if response.startswith('```python'):
            response = response.replace('```python', '', 1)
        if response.startswith('```'):
            response = response.replace('```', '', 1)
        if response.endswith('```'):
            response = response.rsplit('```', 1)[0]
        
        response = response.strip()
        
        # Check if it's a direct answer or code execution
        if response.startswith('DIRECT_ANSWER:'):
            # Handle direct answer
            answer = response.replace('DIRECT_ANSWER:', '', 1).strip()
            console.print(Panel(answer, title="Answer", border_style="blue"))
            
            if save:
                save_path = Path(save)
                save_path.write_text(answer)
                console.print(f"[green]Answer saved to {save_path}[/green]")
                
        elif response.startswith('CODE_EXECUTION:'):
            # Handle code execution
            code = response.replace('CODE_EXECUTION:', '', 1).strip()
            
            if show_code:
                syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
                console.print(Panel(syntax, title="Generated Code", border_style="green"))
            
            if save:
                save_path = Path(save)
                save_path.write_text(code)
                console.print(f"[green]Code saved to {save_path}[/green]")
            
            if execute:
                console.print("[yellow]Executing code...[/yellow]")
                await execute_code(code)
        else:
            # Fallback: treat as code if no prefix
            if show_code:
                syntax = Syntax(response, "python", theme="monokai", line_numbers=True)
                console.print(Panel(syntax, title="Generated Code", border_style="green"))
            
            if save:
                save_path = Path(save)
                save_path.write_text(response)
                console.print(f"[green]Content saved to {save_path}[/green]")
            
            if execute:
                console.print("[yellow]Executing...[/yellow]")
                await execute_code(response)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

async def execute_code(code: str):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        console.print("[green]--- Output ---[/green]")
        if result.stdout:
            console.print(result.stdout)
        
        if result.stderr:
            console.print(f"[red]Errors:[/red]\n{result.stderr}")
        
        if result.returncode != 0:
            console.print(f"[red]Process exited with code {result.returncode}[/red]")
    
    except subprocess.TimeoutExpired:
        console.print("[red]Code execution timed out (30s limit)[/red]")
    except Exception as e:
        console.print(f"[red]Execution error: {e}[/red]")
    finally:
        os.unlink(temp_file)

if __name__ == "__main__":
    main()