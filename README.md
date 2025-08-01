# Smart CLI

Smart CLI is a powerful command-line tool that bridges the gap between human language and computational tasks. Ask questions, analyze data, browse the web, automate tasks, or request code generation—all through simple natural language queries powered by Claude AI or OpenAI GPT with Model Context Protocol (MCP) support.

## Features

- **Dual Intelligence**: Provides direct answers OR generates executable code based on query context
- **Multi-Provider Support**: Works with both Anthropic Claude and OpenAI GPT models
- **🆕 MCP Integration**: Seamlessly connect to external tools and services via Model Context Protocol
- **🆕 Web Automation**: Browser control, screenshots, and web scraping with Playwright MCP
- **🆕 Interactive Mode**: Continuous conversations with context retention
- **Smart File Analysis**: Automatically handles CSV, JSON, Excel files with statistical insights
- **Instant Execution**: Runs generated code safely with built-in timeouts and sandboxing
- **Rich Terminal UI**: Beautiful syntax highlighting and formatted output panels
- **Save & Export**: Save responses, code, or analysis results to files
- **Safety First**: Secure execution environment with error handling
- **Loop Support**: Multi-turn conversations with context gathering
- **User Interaction**: LLM can ask for additional context when needed
- **Clean Architecture**: Professionally designed codebase with robust error handling

## Quick Start

### Prerequisites
- Python 3.12+
- Anthropic API key OR OpenAI API key
- Node.js 18+ (for MCP servers)

### Installation

**Option 1: Using uvx (Recommended - No installation required)**
```bash
# Set your API key first (choose one)
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
# OR
export OPENAI_API_KEY="your-openai-api-key-here"

# Run directly with uvx - no installation needed!
uvx git+https://github.com/prudhvi1709/smart-cli "What is machine learning?"

# Interactive mode with web automation
uvx git+https://github.com/prudhvi1709/smart-cli --interactive --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"

# Data analysis example
uvx git+https://github.com/prudhvi1709/smart-cli "analyze my sales_data.csv and create visualizations"
```

**Option 2: Traditional Installation**
```bash
# Clone the repository
git clone https://github.com/prudhvi1709/smart-cli.git
cd smart-cli

# Install the package with MCP support
pip install -e .

# Set your API key (choose one)
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
# OR
export OPENAI_API_KEY="your-openai-api-key-here"

# Basic usage
smart-cli "your query here"

# Interactive mode with web automation
smart-cli --interactive --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"
```

## Usage

### Command Syntax
```bash
smart-cli "your natural language query" [OPTIONS]
smart-cli [OPTIONS]  # Starts interactive mode if no query provided

# Or using uvx (no installation required)
uvx git+https://github.com/prudhvi1709/smart-cli "your natural language query" [OPTIONS]
```

### 🚀 Quick Start with uvx (No Installation Required)

**Try these examples immediately without installing anything:**

```bash
# Set your API key first (choose one)
export OPENAI_API_KEY="your-openai-api-key-here"
# OR
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# 1. Ask questions and get instant answers
uvx git+https://github.com/prudhvi1709/smart-cli "What is the difference between Python and JavaScript?"

# 2. Generate and run code
uvx git+https://github.com/prudhvi1709/smart-cli "create a password generator with 16 characters"

# 3. Data analysis (place your CSV file in current directory first)
uvx git+https://github.com/prudhvi1709/smart-cli "analyze my data.csv and show me statistical summary"

# 4. Mathematical computations
uvx git+https://github.com/prudhvi1709/smart-cli "calculate compound interest for $5000 at 7% for 10 years"

# 5. Interactive mode for conversations
uvx git+https://github.com/prudhvi1709/smart-cli --interactive

# 6. Web automation (requires Node.js)
uvx git+https://github.com/prudhvi1709/smart-cli --interactive --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"

# 7. File operations
uvx git+https://github.com/prudhvi1709/smart-cli --interactive --mcp-server "stdio:npx,-y,@modelcontextprotocol/server-filesystem,."

# 8. Save generated code to file
uvx git+https://github.com/prudhvi1709/smart-cli "create a QR code generator" --save qr_generator.py

# 9. Code without execution (just show the code)
uvx git+https://github.com/prudhvi1709/smart-cli "create a web scraper for news headlines" --no-execute

# 10. Use specific AI model
uvx git+https://github.com/prudhvi1709/smart-cli "explain quantum computing" --model openai:gpt-4o
```

### Options
- `--execute/--no-execute` (`-e/-n`): Execute generated code (default: true)
- `--save FILENAME` (`-s`): Save output to file
- `--show-code/--no-show-code`: Display code before execution (default: true)
- `--model MODEL` (`-m`): Specify AI model to use
- `--mcp-server TEXT`: Add MCP server (format: type:config, can be used multiple times)
- `--interactive` (`-i`): Interactive mode - continue conversation after each response
- `--help`: Show help message

### Core Functionalities

**1. Direct Question Answering**
- Get explanations, definitions, and conceptual answers
- Mathematical computations and problem solving
- General knowledge queries and research assistance

**2. Code Generation & Execution**
- Automatic Python code generation from natural language
- Safe code execution with built-in timeouts
- Real-time syntax highlighting and formatted output

**3. Data Analysis & File Operations**
- CSV, JSON, and Excel file analysis
- Statistical insights and data visualization
- File management and processing tasks

**4. Interactive Conversations**
- Multi-turn conversations with context retention
- Dynamic context gathering when more information is needed
- Seamless switching between different query types

**5. MCP Server Integration**
- Web automation with Playwright (screenshots, form filling, navigation)
- File system operations and directory management
- External API integrations and tool connectivity
- Custom server support for specialized tasks

### 🆕 Interactive Mode

Start continuous conversations with your AI assistant:

```bash
# Start interactive mode
smart-cli --interactive

# Interactive mode with web automation
smart-cli --interactive --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"

# Interactive mode with file system access
smart-cli --interactive --mcp-server "stdio:npx,-y,@modelcontextprotocol/server-filesystem,."

# Interactive mode with multiple MCP servers
smart-cli --interactive \
  --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server" \
  --mcp-server "stdio:npx,-y,@modelcontextprotocol/server-filesystem,."

# Exit interactive mode
> exit  # or 'quit' or 'q'
```

### 🆕 MCP Server Integration

Connect to external tools and services:

```bash
# Web automation with Playwright
smart-cli "take a screenshot of google.com" \
  --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"

# File system operations
smart-cli "list all Python files in current directory" \
  --mcp-server "stdio:npx,-y,@modelcontextprotocol/server-filesystem,."

# Web search capabilities
smart-cli "search for latest Python news" \
  --mcp-server "stdio:npx,-y,@modelcontextprotocol/server-brave-search"

# Multiple servers at once
smart-cli --interactive \
  --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server" \
  --mcp-server "stdio:npx,-y,@modelcontextprotocol/server-filesystem,."
```

### How to Use Each Functionality

**Direct Question Answering**
```bash
# Get explanations and definitions
smart-cli "What is machine learning and how does it work?"
smart-cli "Explain the difference between Python lists and tuples"
smart-cli "What are the benefits of using Docker containers?"

# Mathematical computations
smart-cli "Calculate the compound interest for $1000 at 5% for 3 years"
smart-cli "Solve the quadratic equation x^2 + 5x + 6 = 0"
smart-cli "Find the area of a circle with radius 7"
```

**Code Generation & Execution**
```bash
# Generate utility scripts
smart-cli "create a password generator with 12 characters"
smart-cli "generate a QR code for https://github.com"
smart-cli "create a file organizer that sorts files by extension"

# Data processing
smart-cli "read sales.csv and calculate total revenue"
smart-cli "create a bar chart from data.json"
smart-cli "convert excel file to csv format"
```

**File Operations with MCP**
```bash
# File system operations
smart-cli --interactive --mcp-server "stdio:npx,-y,@modelcontextprotocol/server-filesystem,."
# Then: > "create a backup of all .py files in current directory"
# Then: > "find all files modified in the last 7 days"
# Then: > "analyze disk usage by file type"
```

**Web Automation**
```bash
# Browser automation
smart-cli --interactive --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"
# Then: > "take screenshots of google.com, github.com, and stackoverflow.com"
# Then: > "navigate to amazon.com and search for 'python books'"
# Then: > "fill out a contact form with test data"
```

**Interactive Data Analysis**
```bash
# Start interactive session for data work
smart-cli --interactive --mcp-server "stdio:npx,-y,@modelcontextprotocol/server-filesystem,."
# Then: > "load customer_data.csv and show me the first 10 rows"
# Then: > "calculate average age by department"
# Then: > "create a visualization of sales trends"
# Then: > "save the analysis results to a report"
```

### Model Selection
You can specify which AI model to use:

```bash
# Use specific models
smart-cli "your query" --model anthropic:claude-sonnet-4-0
smart-cli "your query" --model openai:gpt-4.1-mini
smart-cli "your query" --model openai:gpt-4o-mini

# The system will automatically choose based on available API keys:
# - If OPENAI_API_KEY is set: uses openai:gpt-4.1-mini
# - If ANTHROPIC_API_KEY is set: uses anthropic:claude-sonnet-4-0
```

## Examples

### 🚀 uvx Quick Examples (Try Now!)

**No installation required - just run these commands:**

```bash
# Set your API key first
export OPENAI_API_KEY="your-key-here"  # or ANTHROPIC_API_KEY

# Quick Q&A
uvx git+https://github.com/prudhvi1709/smart-cli "What is Docker and why should I use it?"

# Code generation
uvx git+https://github.com/prudhvi1709/smart-cli "create a Python function to validate email addresses"

# Data analysis (put your CSV file in current directory first)
uvx git+https://github.com/prudhvi1709/smart-cli "do full EDA on my sales.csv and create visualizations"

# Web automation - take a screenshot
uvx git+https://github.com/prudhvi1709/smart-cli "take a screenshot of python.org" --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"

# Interactive data exploration
uvx git+https://github.com/prudhvi1709/smart-cli --interactive --mcp-server "stdio:npx,-y,@modelcontextprotocol/server-filesystem,."
# Then: > "analyze all CSV files in this directory"
# Then: > "create a summary report of the findings"
```

### 🆕 Web Automation & Browser Control
```bash
# Take screenshots
smart-cli "take a screenshot of github.com/prudhvi1709" \
  --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"

# Web interaction
smart-cli "navigate to google.com and search for Python tutorials" \
  --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"

# Form filling and automation
smart-cli "fill out the contact form on example.com with test data" \
  --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"

# Generate test code
smart-cli "create automated tests for login functionality" \
  --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"
```

### 🆕 Interactive Conversations
```bash
# Start interactive session  
smart-cli --interactive --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"

# Example conversation:
> take a screenshot of google.com
# AI takes screenshot and saves it

> now navigate to github.com and search for "python"
# AI navigates and performs search

> create a data visualization of website load times
# AI generates code to analyze and visualize data

> exit
# Goodbye!
```

### Direct Questions & Explanations
```bash
# Get detailed explanations
smart-cli "What is machine learning?"
smart-cli "Explain the difference between lists and tuples in Python"
smart-cli "How does a neural network work?"
```

### Mathematical Computations
```bash
# Calculations and algorithms
smart-cli "calculate fibonacci of 15"
smart-cli "find all prime numbers between 1 and 100"
smart-cli "solve quadratic equation x^2 + 5x + 6 = 0"
```

### Data Analysis & File Operations
```bash
# CSV file analysis
smart-cli "how many rows in sales_data.csv"
smart-cli "preview first 5 rows of employees.csv"
smart-cli "calculate average salary from payroll.csv"
smart-cli "find the highest value in revenue column"

# JSON file operations
smart-cli "preview structure of config.json"
smart-cli "count items in products.json"

# With filesystem MCP server
smart-cli "analyze all CSV files in the current directory" \
  --mcp-server "stdio:npx,-y,@modelcontextprotocol/server-filesystem,."
```

### Code Generation & Utilities
```bash
# Generate useful scripts
smart-cli "create a password generator" --save password_gen.py
smart-cli "generate QR code for a URL"
smart-cli "create a file organizer script"
```

### File Management
```bash
# Save outputs
smart-cli "analyze customer_data.csv" --save analysis_report.txt
smart-cli "create a backup script" --save backup.py --no-execute
```

### Interactive Context Gathering
```bash
# The LLM will ask for more information when needed
smart-cli "create a chart"
# Output: NEED_CONTEXT: I need more information to create a chart for you. Please provide:
# 1. What type of data do you want to visualize?
# 2. What type of chart would you prefer?
# 3. Do you have a data file, or should I generate sample data?

smart-cli "analyze the data"
# Output: NEED_CONTEXT: I need more information to analyze data for you. Please specify:
# 1. What data file should I analyze?
# 2. What type of analysis do you need?
# 3. Are there specific columns or aspects you want me to focus on?
```

## MCP Servers

### Available MCP Servers

| Server | Description | Command |
|--------|-------------|---------|
| **Playwright** | Web automation, screenshots, browser control | `stdio:npx,-y,@executeautomation/playwright-mcp-server` |
| **Filesystem** | Local file operations and directory access | `stdio:npx,-y,@modelcontextprotocol/server-filesystem,.` |
| **Brave Search** | Web search capabilities | `stdio:npx,-y,@modelcontextprotocol/server-brave-search` |
| **GitHub** | GitHub API operations | `stdio:npx,-y,@modelcontextprotocol/server-github` |
| **Memory** | Persistent memory for conversations | `stdio:npx,-y,@modelcontextprotocol/server-memory` |

### MCP Server Setup

Install MCP servers globally for better performance:

```bash
# Install Playwright MCP server
npm install -g @executeautomation/playwright-mcp-server

# Install official MCP servers
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-github
```

### Custom MCP Server Configuration

```bash
# Stdio transport (local processes)
--mcp-server "stdio:command,arg1,arg2,..."

# HTTP transport (remote servers)
--mcp-server "http:http://localhost:8000/mcp"
```

## How It Works

Smart CLI uses intelligent prompt engineering with MCP integration:

1. **Query Analysis**: Examines your natural language input
2. **MCP Tool Discovery**: Identifies available tools from connected servers
3. **Response Mode Selection**:
   - **Direct Answer**: For explanations, definitions, and conceptual questions
   - **Code Execution**: For computations, data analysis, and file operations
   - **Tool Usage**: For web automation, file operations, and external API calls
   - **Need Context**: When more information is required from the user
4. **Interactive Loop**: Multi-turn conversations with conversation history tracking
5. **Tool Execution**: Safely executes MCP tools and Python code
6. **Rich Output**: Displays results with syntax highlighting and formatted panels

## Configuration

### Environment Variables
```bash
# Required: Set one of these API keys
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
# OR
export OPENAI_API_KEY="your-openai-api-key-here"

# Optional: Custom model selection
export ANTHROPIC_MODEL="claude-3-haiku-20240307"

# Optional: MCP server environment variables
export BRAVE_API_KEY="your-brave-search-api-key"
export GITHUB_PERSONAL_ACCESS_TOKEN="your-github-token"
```

### Supported Models
- **Anthropic Claude**: `anthropic:claude-sonnet-4-0`, `anthropic:claude-3-haiku-20240307`, `anthropic:claude-3-opus-20240229`
- **OpenAI GPT**: `openai:gpt-4.1-mini`, `openai:gpt-4o-mini`, `openai:gpt-4o`, `openai:gpt-3.5-turbo`

### Model Selection Priority
1. Command line `--model` option (highest priority)
2. Environment variable `ANTHROPIC_MODEL` (if Anthropic API key is set)
3. Automatic detection based on available API keys:
   - `openai:gpt-4.1-mini` if `OPENAI_API_KEY` is set
   - `anthropic:claude-sonnet-4-0` if `ANTHROPIC_API_KEY` is set

### Supported File Formats
- **CSV**: Full pandas integration for data analysis
- **JSON**: Structure analysis and data extraction  
- **Excel**: Spreadsheet processing and statistics
- **Text files**: Content analysis and processing

## Advanced Usage

### Batch Operations with Interactive Mode
```bash
# Start interactive session for multiple tasks
smart-cli --interactive --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server"

# Then perform multiple operations:
> take screenshots of google.com, github.com, and stackoverflow.com
> create a comparison chart of the three websites
> generate a report summarizing the visual differences
> save the report as website_comparison.md
> exit
```

### Combining Code Generation with Web Automation
```bash
smart-cli --interactive \
  --mcp-server "stdio:npx,-y,@executeautomation/playwright-mcp-server" \
  --mcp-server "stdio:npx,-y,@modelcontextprotocol/server-filesystem,."

# Example workflow:
> scrape product data from example-store.com
> clean and analyze the scraped data
> create visualizations of pricing trends
> save everything to a comprehensive report
```

## Safety & Limitations

### Built-in Safety Features
- 30-second execution timeout for code
- Sandboxed temporary file execution
- MCP server process isolation
- No persistent system modifications without explicit save
- Comprehensive error handling and logging
- Graceful MCP server connection handling

### Current Limitations
- Code execution limited to Python
- File operations restricted to current directory context  
- MCP servers require Node.js runtime
- Internet requests require appropriate libraries or MCP servers
- Browser automation requires headless browser support

### Security Considerations
- MCP servers run as separate processes
- Network access is controlled by individual MCP servers
- File access is limited to specified directories
- Always review generated code before execution

## Troubleshooting

### Common Issues

**MCP Server Connection Errors:**
```bash
# Check if Node.js is installed
node --version

# Install MCP server globally
npm install -g @executeautomation/playwright-mcp-server

# Test MCP server manually
npx -y @executeautomation/playwright-mcp-server
```

**API Key Issues:**
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Load environment (if using custom script)
loadenv  # or your custom environment loading command
```

**Interactive Mode Not Working:**
```bash
# With uvx (always gets latest version)
uvx git+https://github.com/prudhvi1709/smart-cli --interactive

# With traditional installation - make sure you have the latest version
pip install -e .

# Start with explicit interactive flag
smart-cli --interactive
```

**Testing uvx Installation:**
```bash
# Test basic functionality
uvx git+https://github.com/prudhvi1709/smart-cli "What is 2+2?"

# Test with your API key
export OPENAI_API_KEY="your-key-here"
uvx git+https://github.com/prudhvi1709/smart-cli "create a simple hello world program"

# Test interactive mode
uvx git+https://github.com/prudhvi1709/smart-cli --interactive
```

## Contributing

We welcome contributions! Please fork our repository and send a pull request.

### Development Setup
```bash
git clone https://github.com/prudhvi1709/smart-cli.git
cd smart-cli
pip install -e .

# Install development dependencies
npm install -g @executeautomation/playwright-mcp-server
npm install -g @modelcontextprotocol/server-filesystem
```

### Adding New MCP Servers
1. Find or create an MCP server
2. Test it with the `--mcp-server` option
3. Add documentation and examples
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Documentation](https://github.com/prudhvi1709/smart-cli/wiki)
- [Report Issues](https://github.com/prudhvi1709/smart-cli/issues)
- [Discussions](https://github.com/prudhvi1709/smart-cli/discussions)

## Acknowledgments

- Built with [PydanticAI](https://github.com/pydantic/pydantic-ai) and [Model Context Protocol](https://modelcontextprotocol.io/)
- Powered by [Anthropic Claude](https://www.anthropic.com/) and [OpenAI GPT](https://openai.com/)
- Web automation by [Playwright MCP Server](https://github.com/executeautomation/mcp-playwright)
- UI components by [Rich](https://github.com/Textualize/rich)
- MCP ecosystem by [Model Context Protocol](https://modelcontextprotocol.io/)