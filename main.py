# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pydantic-ai[mcp]",
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
from dataclasses import dataclass
from typing import Optional, List, Any, Tuple
import click
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio, MCPServerHTTP

console = Console()

@dataclass
class Config:
    execute: bool
    save: Optional[str]
    show_code: bool
    interactive: bool

class ResponseHandler:
    def __init__(self, config: Config):
        self.config = config
        self.handlers = {
            'DIRECT_ANSWER:': self._handle_direct_answer,
            'CODE_EXECUTION:': self._handle_code_execution,
            'NEED_CONTEXT:': self._handle_need_context,
        }
    
    async def handle_response(self, response: str) -> Tuple[bool, Optional[str]]:
        response = response.strip()
        
        if response in ['CODE_EXECUTION', 'DIRECT_ANSWER', 'NEED_CONTEXT']:
            console.print(f"[red]Error: Malformed response from AI. Got '{response}' without content.[/red]")
            return False, "Please provide a complete response. Original query: {}"
        
        for prefix, handler in self.handlers.items():
            if response.startswith(prefix):
                return await handler(response, prefix)
        
        return await self._handle_fallback(response)
    
    async def _handle_direct_answer(self, response: str, prefix: str) -> Tuple[bool, Optional[str]]:
        answer = response.replace(prefix, '', 1).strip()
        if not answer:
            console.print("[red]Error: Empty DIRECT_ANSWER response[/red]")
            return False, None
        console.print(Panel(answer, title="Answer", border_style="blue"))
        self._save_content(answer, "Answer")
        return True, None
    
    async def _handle_code_execution(self, response: str, prefix: str) -> Tuple[bool, Optional[str]]:
        code = self._clean_markdown(response.replace(prefix, '', 1))
        if not code:
            console.print("[red]Error: Empty CODE_EXECUTION response[/red]")
            return False, None
        self._display_code(code)
        self._save_content(code, "Code")
        if self.config.execute:
            console.print("[yellow]Executing code...[/yellow]")
            await execute_code(code)
        return True, None
    
    async def _handle_need_context(self, response: str, prefix: str) -> Tuple[bool, Optional[str]]:
        context_request = response.replace(prefix, '', 1).strip()
        if not context_request:
            console.print("[red]Error: Empty NEED_CONTEXT response[/red]")
            return False, None
        console.print(Panel(context_request, title="Context Request", border_style="yellow"))
        self._save_content(context_request, "Context request")
        console.print("\\n[cyan]Please provide the requested information:[/cyan]")
        user_context = input("> ").strip()
        if not user_context:
            console.print("[red]No context provided.[/red]")
            return False, None
        console.print(f"[blue]Continuing with context: {user_context}[/blue]")
        return False, f"Context provided: {user_context}. Original query: {{}}"
    
    async def _handle_fallback(self, response: str) -> Tuple[bool, Optional[str]]:
        self._display_code(response)
        self._save_content(response, "Content")
        if self.config.execute:
            console.print("[yellow]Executing...[/yellow]")
            await execute_code(response)
        return True, None
    
    def _clean_markdown(self, text: str) -> str:
        text = text.strip()
        for marker in ['```python', '```']:
            if text.startswith(marker):
                text = text.replace(marker, '', 1)
        return text.rsplit('```', 1)[0].strip() if text.endswith('```') else text
    
    def _save_content(self, content: str, content_type: str):
        if self.config.save:
            Path(self.config.save).write_text(content)
            console.print(f"[green]{content_type} saved to {self.config.save}[/green]")
    
    def _display_code(self, code: str):
        if self.config.show_code:
            console.print(Panel(Syntax(code, "python", theme="monokai", line_numbers=True), title="Generated Code", border_style="green"))

def get_agent(model: str = None, mcp_servers: list = None) -> Agent:
    model = model or ("openai:gpt-4.1-mini" if os.getenv('OPENAI_API_KEY') else 
                      os.getenv('ANTHROPIC_MODEL', 'anthropic:claude-sonnet-4-0'))
    
    if mcp_servers is None:
        mcp_servers = []
        try:
            mcp_servers.append(MCPServerStdio(command="npx", args=["-y", "@modelcontextprotocol/server-filesystem", "./"]))
        except:
            pass
    
    return Agent(model, mcp_servers=mcp_servers, end_strategy='loop',
        instructions="You are an intelligent assistant that handles queries in three modes. You MUST respond in exactly one of these formats:\\n\\nFORMAT 1 - DIRECT_ANSWER: [Your explanation or answer here]\\nFORMAT 2 - CODE_EXECUTION: [Your Python code here]\\nFORMAT 3 - NEED_CONTEXT: [Your question for more information here]\\n\\nRULES:\\n- ALWAYS start with the mode followed by a colon and space\\n- For CODE_EXECUTION: Generate clean, executable Python code\\n- For DIRECT_ANSWER: Provide explanations, facts, or analysis\\n- For NEED_CONTEXT: Ask specific questions when you need more information\\n- For graphs/charts: Always save to file with descriptive names and timestamps\\n- Use pandas for CSV/Excel, json for JSON files, matplotlib/seaborn/plotly for graphs\\n- Always use print() to show results and include proper error handling\\n- DO NOT include markdown formatting (```python or ```) in CODE_EXECUTION responses\\n- You have access to MCP tools for file operations and other capabilities when available")

def parse_mcp_servers(server_configs: List[str]) -> List[Any]:
    mcp_servers = []
    for config in server_configs:
        try:
            if config.startswith('stdio:'):
                parts = config[6:].split(',')
                mcp_servers.append(MCPServerStdio(command=parts[0], args=parts[1:]))
            elif config.startswith('http:'):
                mcp_servers.append(MCPServerHTTP(url=config[5:]))
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to configure MCP server {config}: {e}[/yellow]")
    return mcp_servers

def show_config_info(model: str, mcp_servers: List[Any], interactive: bool):
    if model:
        console.print(f"[cyan]Using model: {model}[/cyan]")
    elif os.getenv('OPENAI_API_KEY'):
        console.print(f"[cyan]Using model: openai:gpt-4.1-mini (OpenAI API key detected)[/cyan]")
    elif os.getenv('ANTHROPIC_MODEL'):
        console.print(f"[cyan]Using model: {os.getenv('ANTHROPIC_MODEL')}[/cyan]")
    if mcp_servers:
        console.print(f"[cyan]MCP servers configured: {len(mcp_servers)}[/cyan]")
    if interactive:
        console.print(f"[green]Interactive mode enabled. Type 'exit' or 'quit' to stop.[/green]")

def get_user_input(prompt: str) -> Optional[str]:
    console.print(f"\\n[cyan]{prompt}[/cyan]")
    user_input = input("> ").strip()
    if user_input.lower() in ['exit', 'quit', 'q']:
        console.print("[green]Goodbye![/green]")
        return None
    if not user_input:
        console.print("[yellow]Please enter a query[/yellow]")
        return ""
    return user_input

async def execute_code(code: str):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = subprocess.run([sys.executable, temp_file], capture_output=True, text=True, timeout=30)
        console.print("[green]--- Output ---[/green]")
        if result.stdout:
            console.print(result.stdout)
            if any(phrase in result.stdout.lower() for phrase in ["saved as:", "saved to:", "graph saved"]):
                console.print("[cyan]💾 File saved successfully![/cyan]")
        if result.stderr:
            console.print(f"[red]Errors:[/red]\\n{result.stderr}")
        if result.returncode != 0:
            console.print(f"[red]Process exited with code {result.returncode}[/red]")
    except subprocess.TimeoutExpired:
        console.print("[red]Code execution timed out (30s limit)[/red]")
    except Exception as e:
        console.print(f"[red]Execution error: {e}[/red]")
    finally:
        os.unlink(temp_file)

async def process_query(query_text: str, config: Config, model: str = None, mcp_servers: list = None):
    agent = get_agent(model, mcp_servers)
    handler = ResponseHandler(config)
    current_query = query_text
    first_run = True
    
    try:
        async with agent.run_mcp_servers():
            while True:
                if config.interactive and not first_run:
                    current_query = get_user_input("Enter your next query (or 'exit'/'quit' to stop):")
                    if current_query is None:
                        break
                    if current_query == "":
                        continue
                
                if config.interactive and first_run and not current_query:
                    current_query = get_user_input("Enter your query:")
                    if current_query is None:
                        break
                    if current_query == "":
                        continue
                
                first_run = False
                console.print(f"[blue]Query:[/blue] {current_query}")
                console.print("[yellow]Processing...[/yellow]")
                
                result = await agent.run(current_query)
                response = handler._clean_markdown(result.output)
                
                task_completed, next_query = await handler.handle_response(response)
                
                if next_query:
                    current_query = next_query.format(current_query)
                    continue
                
                if not task_completed and not config.interactive:
                    break
                
                if not config.interactive and task_completed:
                    break
    
    except KeyboardInterrupt:
        console.print("\\n[yellow]Operation cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if not config.interactive:
            sys.exit(1)

@click.command()
@click.argument('query', nargs=-1, required=False)
@click.option('--execute/--no-execute', '-e/-n', default=True, help='Execute the generated code')
@click.option('--save', '-s', help='Save generated code to file')
@click.option('--show-code/--no-show-code', default=True, help='Show generated code before execution')
@click.option('--model', '-m', help='AI model to use (e.g., anthropic:claude-sonnet-4-0, openai:gpt-4.1-mini)')
@click.option('--mcp-server', multiple=True, help='MCP server to add (format: type:config)')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode - continue conversation after each response')
def main(query, execute, save, show_code, model, mcp_server, interactive):
    """Smart CLI: Generate and execute Python code from natural language queries with MCP support."""
    interactive = interactive or not query
    query_text = ' '.join(query) if query else ""
    
    if query and not query_text.strip():
        console.print("[red]Error: Please provide a query[/red]")
        sys.exit(1)
    
    mcp_servers = parse_mcp_servers(mcp_server)
    show_config_info(model, mcp_servers, interactive)
    
    config = Config(execute=execute, save=save, show_code=show_code, interactive=interactive)
    asyncio.run(process_query(query_text, config, model, mcp_servers))

if __name__ == "__main__":
    main()