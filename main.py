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
    3. NEED_CONTEXT: When you need more information from the user to proceed

    FORMAT YOUR RESPONSE:
    Start with either "DIRECT_ANSWER:", "CODE_EXECUTION:", or "NEED_CONTEXT:" followed by your response.

    DIRECT_ANSWER:
    Use this mode for questions that need direct responses, explanations, facts, or analysis. Provide clear, informative answers without code execution.

    CODE_EXECUTION:
    Use this mode for tasks that require code execution, calculations, file processing, or data analysis. Generate clean, executable Python code that accomplishes the requested task.

    NEED_CONTEXT:
    Use this mode when you need more information from the user to proceed. Ask specific, actionable questions to gather required information.

    GRAPH HANDLING:
    For any query related to graphs, charts, plots, or visualizations:
    - ALWAYS save the graph to a file
    - Use descriptive filenames with timestamps
    - Show the file path in the output
    - Use matplotlib, seaborn, or plotly as appropriate
    - Include proper styling and labels

    RULES:
    - For CODE_EXECUTION: Generate clean, executable Python code
    - DO NOT include markdown formatting (```python or ```) in CODE_EXECUTION responses
    - Include proper error handling for file operations
    - Use pandas for CSV/Excel files, json for JSON files
    - For file analysis, check if file exists first
    - Always use print() to show results
    - Keep code focused and minimal
    - For GRAPHS: Always save to file and show the absolute path
    - Use descriptive filenames with timestamps for graphs
    - Include proper styling, labels, and legends for visualizations
    - For NEED_CONTEXT: Ask specific, actionable questions to gather required information
    - Be concise but thorough in context requests
    """,
    end_strategy='loop'  # Enable loop support for multi-turn conversations
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
    
    # Initialize conversation history for loop support
    conversation_history = []
    current_query = query_text
    
    try:
        while True:
            # Add current query to history
            conversation_history.append({"role": "user", "content": current_query})
            
            # Run agent with conversation history
            result = await agent.run(current_query, history=conversation_history)
            response = result.output.strip()
            
            # Clean up markdown formatting if present
            if response.startswith('```python'):
                response = response.replace('```python', '', 1)
            if response.startswith('```'):
                response = response.replace('```', '', 1)
            if response.endswith('```'):
                response = response.rsplit('```', 1)[0]
            
            response = response.strip()
            
            # Add agent response to history
            conversation_history.append({"role": "assistant", "content": response})
            
            # Check if it's a direct answer or code execution
            if response.startswith('DIRECT_ANSWER:'):
                # Handle direct answer
                answer = response.replace('DIRECT_ANSWER:', '', 1).strip()
                console.print(Panel(answer, title="Answer", border_style="blue"))
                
                if save:
                    save_path = Path(save)
                    save_path.write_text(answer)
                    console.print(f"[green]Answer saved to {save_path}[/green]")
                
                # Exit loop for direct answers
                break
                    
            elif response.startswith('CODE_EXECUTION:'):
                # Handle code execution
                code = response.replace('CODE_EXECUTION:', '', 1).strip()
                
                # Additional cleanup for code blocks
                if code.startswith('```python'):
                    code = code.replace('```python', '', 1)
                if code.startswith('```'):
                    code = code.replace('```', '', 1)
                if code.endswith('```'):
                    code = code.rsplit('```', 1)[0]
                code = code.strip()
                
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
                
                # Exit loop for code execution
                break
                
            elif response.startswith('NEED_CONTEXT:'):
                # Handle need for context
                context_request = response.replace('NEED_CONTEXT:', '', 1).strip()
                console.print(Panel(context_request, title="Context Request", border_style="yellow"))
                
                if save:
                    save_path = Path(save)
                    save_path.write_text(context_request)
                    console.print(f"[green]Context request saved to {save_path}[/green]")
                
                # Get user input for context
                console.print("\n[cyan]Please provide the requested information:[/cyan]")
                user_context = input("> ").strip()
                
                if not user_context:
                    console.print("[red]No context provided. Exiting.[/red]")
                    break
                
                # Continue loop with user's context
                current_query = f"Context provided: {user_context}. Original query: {query_text}"
                console.print(f"[blue]Continuing with context: {user_context}[/blue]")
                continue
                
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
                
                # Exit loop for fallback responses
                break
    
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