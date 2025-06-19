# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pydantic-ai",
#     "click",
#     "rich",
#     "pandas",
#     "matplotlib",
#     "numpy",
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
from datetime import datetime
import re

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

    GRAPH HANDLING:
    For any query related to graphs, charts, plots, or visualizations:
    - ALWAYS save the graph to a file
    - Use descriptive filenames with timestamps
    - Show the file path in the output
    - Use matplotlib, seaborn, or plotly as appropriate
    - Include proper styling and labels

    Graph Examples:
    Query: "create a bar chart of sales data"
    Response: CODE_EXECUTION:
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    from datetime import datetime
    import os
    
    # Generate sample sales data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    sales = [1200, 1500, 1800, 1600, 2000, 2200]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(months, sales, color='skyblue', edgecolor='navy')
    plt.title('Monthly Sales Data', fontsize=16, fontweight='bold')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Sales ($)', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for i, v in enumerate(sales):
        plt.text(i, v + 50, str(v), ha='center', va='bottom', fontweight='bold')
    
    # Save the graph
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sales_chart_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Graph saved as: {os.path.abspath(filename)}")
    print(f"File size: {os.path.getsize(filename)} bytes")

    Query: "plot a line graph of temperature over time"
    Response: CODE_EXECUTION:
    import matplotlib.pyplot as plt
    import numpy as np
    from datetime import datetime, timedelta
    import os
    
    # Generate sample temperature data
    dates = [datetime.now() - timedelta(days=i) for i in range(7, 0, -1)]
    temperatures = [22, 24, 26, 23, 25, 27, 28]
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(dates, temperatures, marker='o', linewidth=2, markersize=8, color='red')
    plt.title('Temperature Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Temperature (°C)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # Add temperature labels
    for i, temp in enumerate(temperatures):
        plt.annotate(f'{temp}°C', (dates[i], temp), textcoords="offset points", 
                    xytext=(0,10), ha='center')
    
    plt.tight_layout()
    
    # Save the graph
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"temperature_graph_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Graph saved as: {os.path.abspath(filename)}")
    print(f"File size: {os.path.getsize(filename)} bytes")

    RULES:
    - For CODE_EXECUTION: Generate clean, executable Python code
    - Include proper error handling for file operations
    - Use pandas for CSV/Excel files, json for JSON files
    - For file analysis, check if file exists first
    - Always use print() to show results
    - Keep code focused and minimal
    - For GRAPHS: Always save to file and show the absolute path
    - Use descriptive filenames with timestamps for graphs
    - Include proper styling, labels, and legends for visualizations
    """
)

def is_graph_query(query: str) -> bool:
    """Detect if the query is related to graphs, charts, or visualizations."""
    graph_keywords = [
        'graph', 'chart', 'plot', 'visualization', 'visualize', 'visualise',
        'bar chart', 'line graph', 'scatter plot', 'histogram', 'pie chart',
        'heatmap', 'box plot', 'violin plot', 'area chart', 'bubble chart',
        'create graph', 'make chart', 'draw plot', 'generate visualization',
        'plot data', 'chart data', 'graph data'
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in graph_keywords)

def generate_graph_filename(query: str) -> str:
    """Generate a descriptive filename for graph files."""
    # Extract meaningful words from query
    words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
    # Filter out common words
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now', 'create', 'make', 'draw', 'generate', 'show', 'display', 'data'}
    meaningful_words = [word for word in words if word not in common_words]
    
    # Take first 3 meaningful words or use 'graph' as fallback
    if meaningful_words:
        base_name = '_'.join(meaningful_words[:3])
    else:
        base_name = 'graph'
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.py"

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
    smart-cli "create a bar chart of sales data"  # Automatically saves graph
    """
    query_text = ' '.join(query)
    
    if not query_text.strip():
        console.print("[red]Error: Please provide a query[/red]")
        sys.exit(1)
    
    # Auto-detect graph queries and set save path if not provided
    if is_graph_query(query_text) and not save:
        save = generate_graph_filename(query_text)
        console.print(f"[blue]Graph query detected! Will save to: {save}[/blue]")
    
    asyncio.run(process_query(query_text, execute, save, show_code))

async def process_query(query_text: str, execute: bool, save: str, show_code: bool):
    console.print(f"[blue]Query:[/blue] {query_text}")
    
    # Special handling for graph queries
    is_graph = is_graph_query(query_text)
    if is_graph:
        console.print("[cyan]📊 Graph/Visualization query detected[/cyan]")
    
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
                
                if is_graph:
                    console.print(f"[cyan]📁 Graph code saved to: {save_path.absolute()}[/cyan]")
            
            if execute:
                if is_graph:
                    console.print("[yellow]🎨 Generating graph...[/yellow]")
                else:
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
                
                if is_graph:
                    console.print(f"[cyan]📁 Graph code saved to: {save_path.absolute()}[/cyan]")
            
            if execute:
                if is_graph:
                    console.print("[yellow]🎨 Generating graph...[/yellow]")
                else:
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
            
            # Check if graph was saved and show path
            if "Graph saved as:" in result.stdout:
                console.print("[cyan]🎉 Graph generated successfully![/cyan]")
            elif "saved as:" in result.stdout.lower() or "saved to:" in result.stdout.lower():
                console.print("[cyan]💾 File saved successfully![/cyan]")
        
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