# Smart CLI

Smart CLI is a powerful command-line tool that bridges the gap between human language and computational tasks. Ask questions, analyze data, or request code generation—all through simple natural language queries powered by Claude AI.

## Features

- **Dual Intelligence**: Provides direct answers OR generates executable code based on query context
- **Smart File Analysis**: Automatically handles CSV, JSON, Excel files with statistical insights
- **Instant Execution**: Runs generated code safely with built-in timeouts and sandboxing
- **Rich Terminal UI**: Beautiful syntax highlighting and formatted output panels
- **Save & Export**: Save responses, code, or analysis results to files
- **Safety First**: Secure execution environment with error handling
- **🆕 Loop Support**: Multi-turn conversations with context gathering
- **🆕 User Interaction**: LLM can ask for additional context when needed

## Quick Start

### Prerequisites
- Python 3.12+
- Anthropic API key

### Installation

```bash
# Clone the repository
git clone https://github.com/prudhvi1709/smart-cli.git
cd smart-cli

# Install the package
pip install -e .

# Set your API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Run the CLI
smart-cli "your query here"
```

## Usage

QueryFlow automatically detects the type of query and responds appropriately:

### Command Syntax
```bash
smart-cli "your natural language query" [OPTIONS]
```

### Options
- `--execute/--no-execute` (`-e/-n`): Execute generated code (default: true)
- `--save FILENAME` (`-s`): Save output to file
- `--show-code/--no-show-code`: Display code before execution (default: true)
- `--help`: Show help message

## Examples

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

### 🆕 Interactive Context Gathering
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

## How It Works

QueryFlow uses intelligent prompt engineering to determine the best response type:

1. **Query Analysis**: Examines your natural language input
2. **Response Mode Selection**:
   - **Direct Answer**: For explanations, definitions, and conceptual questions
   - **Code Execution**: For computations, data analysis, and file operations
   - **🆕 Need Context**: When more information is required from the user
3. **🆕 Loop Support**: Multi-turn conversations with conversation history tracking
4. **🆕 User Interaction**: Prompts for additional context when needed
5. **Safe Execution**: Runs code in isolated temporary files with timeouts
6. **Rich Output**: Displays results with syntax highlighting and formatted panels

## Configuration

### Environment Variables
```bash
# Required: Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Optional: Custom model (default: claude-sonnet-4-0)
export ANTHROPIC_MODEL="claude-3-haiku-20240307"
```

### Supported File Formats
- **CSV**: Full pandas integration for data analysis
- **JSON**: Structure analysis and data extraction  
- **Excel**: Spreadsheet processing and statistics
- **Text files**: Content analysis and processing

## Safety & Limitations

### Built-in Safety Features
- 30-second execution timeout
- Sandboxed temporary file execution
- No persistent system modifications without explicit save
- Comprehensive error handling and logging

### Current Limitations
- Code execution limited to Python
- File operations restricted to current directory context
- Internet requests require appropriate libraries to be available

## Contributing

We welcome contributions! Please fork our repository and send a pull request.

### Development Setup
```bash
git clone https://github.com/prudhvi1709/smart-cli.git
cd smart-cli
pip install -e .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Documentation](https://github.com/prudhvi1709/smart-cli/wiki)
- [Report Issues](https://github.com/prudhvi1709/smart-cli/issues)
- [Discussions](https://github.com/prudhvi1709/smart-cli/discussions)

## Acknowledgments

- Built with [PydanticAI](https://github.com/pydantic/pydantic-ai)
- Powered by [Anthropic Claude](https://www.anthropic.com/)
- UI components by [Rich](https://github.com/Textualize/rich)