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

console = Console()

def get_agent(model: str = None):
    """Create agent with specified model or default."""
    if not model:
        # Check if OpenAI API key is set
        if os.getenv('OPENAI_API_KEY'):
            model = 'openai:gpt-4.1-mini'
        else:
            model = os.getenv('ANTHROPIC_MODEL', 'anthropic:claude-sonnet-4-0')
    
    return Agent(
        model,
        instructions="""
        You are an intelligent assistant that handles queries in three modes. You MUST respond in exactly one of these formats:

        FORMAT 1 - DIRECT_ANSWER: [Your explanation or answer here]
        FORMAT 2 - CODE_EXECUTION: [Your Python code here]
        FORMAT 3 - NEED_CONTEXT: [Your question for more information here]

        RULES:
        - ALWAYS start with the mode followed by a colon and space
        - For CODE_EXECUTION: Generate clean, executable Python code
        - For DIRECT_ANSWER: Provide explanations, facts, or analysis
        - For NEED_CONTEXT: Ask specific questions when you need more information
        - For graphs/charts: Always save to file with descriptive names and timestamps
        - Use pandas for CSV/Excel, json for JSON files, matplotlib/seaborn/plotly for graphs
        - Always use print() to show results and include proper error handling
        - DO NOT include markdown formatting (```python or ```) in CODE_EXECUTION responses
        """,
        end_strategy='loop'
    )

def clean_markdown(text: str) -> str:
    """Remove markdown formatting from text."""
    text = text.strip()
    if text.startswith('```python'):
        text = text.replace('```python', '', 1)
    if text.startswith('```'):
        text = text.replace('```', '', 1)
    if text.endswith('```'):
        text = text.rsplit('```', 1)[0]
    return text.strip()

def save_content(content: str, save_path: str, content_type: str = "Content"):
    """Save content to file and show confirmation."""
    if save_path:
        Path(save_path).write_text(content)
        console.print(f"[green]{content_type} saved to {save_path}[/green]")

def display_code(code: str, show_code: bool):
    """Display code with syntax highlighting if enabled."""
    if show_code:
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Generated Code", border_style="green"))

@click.command()
@click.argument('query', nargs=-1, required=True)
@click.option('--execute/--no-execute', '-e/-n', default=True, help='Execute the generated code')
@click.option('--save', '-s', help='Save generated code to file')
@click.option('--show-code/--no-show-code', default=True, help='Show generated code before execution')
@click.option('--model', '-m', help='AI model to use (e.g., anthropic:claude-sonnet-4-0, openai:gpt-4.1-mini)')
def main(query, execute, save, show_code, model):
    """Smart CLI: Generate and execute Python code from natural language queries."""
    query_text = ' '.join(query)
    if not query_text.strip():
        console.print("[red]Error: Please provide a query[/red]")
        sys.exit(1)
    
    # Show model being used
    if model:
        console.print(f"[cyan]Using model: {model}[/cyan]")
    elif os.getenv('OPENAI_API_KEY'):
        console.print(f"[cyan]Using model: openai:gpt-4.1-mini (OpenAI API key detected)[/cyan]")
    elif os.getenv('ANTHROPIC_MODEL'):
        console.print(f"[cyan]Using model: {os.getenv('ANTHROPIC_MODEL')}[/cyan]")
    
    asyncio.run(process_query(query_text, execute, save, show_code, model))

async def process_query(query_text: str, execute: bool, save: str, show_code: bool, model: str = None):
    console.print(f"[blue]Query:[/blue] {query_text}")
    console.print("[yellow]Processing...[/yellow]")
    
    # Create agent with specified model
    agent = get_agent(model)
    
    conversation_history = []
    current_query = query_text
    
    try:
        while True:
            conversation_history.append({"role": "user", "content": current_query})
            result = await agent.run(current_query)
            response = clean_markdown(result.output)
            conversation_history.append({"role": "assistant", "content": response})
            
            # Check for malformed responses
            if response.strip() in ['CODE_EXECUTION', 'DIRECT_ANSWER', 'NEED_CONTEXT']:
                console.print(f"[red]Error: Malformed response from AI. Got '{response}' without content.[/red]")
                console.print("[yellow]Retrying with clearer instructions...[/yellow]")
                current_query = f"Please provide a complete response. Original query: {query_text}"
                continue
            
            if response.startswith('DIRECT_ANSWER:'):
                answer = response.replace('DIRECT_ANSWER:', '', 1).strip()
                if not answer:
                    console.print("[red]Error: Empty DIRECT_ANSWER response[/red]")
                    break
                console.print(Panel(answer, title="Answer", border_style="blue"))
                save_content(answer, save, "Answer")
                break
                    
            elif response.startswith('CODE_EXECUTION:'):
                code = clean_markdown(response.replace('CODE_EXECUTION:', '', 1))
                if not code:
                    console.print("[red]Error: Empty CODE_EXECUTION response[/red]")
                    break
                display_code(code, show_code)
                save_content(code, save, "Code")
                
                if execute:
                    console.print("[yellow]Executing code...[/yellow]")
                    await execute_code(code)
                break
                
            elif response.startswith('NEED_CONTEXT:'):
                context_request = response.replace('NEED_CONTEXT:', '', 1).strip()
                if not context_request:
                    console.print("[red]Error: Empty NEED_CONTEXT response[/red]")
                    break
                console.print(Panel(context_request, title="Context Request", border_style="yellow"))
                save_content(context_request, save, "Context request")
                
                console.print("\n[cyan]Please provide the requested information:[/cyan]")
                user_context = input("> ").strip()
                
                if not user_context:
                    console.print("[red]No context provided. Exiting.[/red]")
                    break
                
                current_query = f"Context provided: {user_context}. Original query: {query_text}"
                console.print(f"[blue]Continuing with context: {user_context}[/blue]")
                continue
                
            else:
                # Fallback: treat as code
                display_code(response, show_code)
                save_content(response, save, "Content")
                
                if execute:
                    console.print("[yellow]Executing...[/yellow]")
                    await execute_code(response)
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
            if any(phrase in result.stdout.lower() for phrase in ["saved as:", "saved to:", "graph saved"]):
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