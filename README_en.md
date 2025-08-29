# Mailo - AI Assistant

Mailo is a Python project built on Large Language Models (LLMs) to provide a suite of automated and intelligent functionalities, including document processing, email management, and web search.

## Features

- **Markdown Formatting**:
  - **Single File Processing**: The `agents/markdown.py` script can be used to format a specified Markdown file into a clean, well-structured version using an LLM.
  - **Batch Processing**: The `agents/batch_md.py` script automatically processes all Markdown files in the `processed_data` directory, skipping already processed files and saving the results to the `format_data` directory. The script includes error handling and a retry mechanism.

- **Intelligent Email Assistant**:
  - **Send Emails**: The agent can send emails through natural language commands (e.g., "Send an email to a@b.com with the subject... and body...").
  - **Read Emails**: Supports fetching summaries of recent emails with commands like "Read my last 5 emails".
  - **Multi-Platform Support**: Can be configured to use various email providers like QQ, 163, and Aliyun in the `.env` file.

- **Web Search**:
  - Integrated with the Baidu Search API, allowing the agent to perform web searches for information on demand.

## Installation and Setup

1.  **Clone the Project**
    ```bash
    git clone [<your-repository-url>](https://github.com/clg3227783168/Mailo.git)
    cd Mailo
    ```

2.  **Create and Activate a Python Virtual Environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    *Note: To exit the virtual environment, simply run the `deactivate` command.*

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    - Copy an `.env.example` file (if provided) to `.env`, or create a new `.env` file.
    - Fill in your API keys and email configurations in the `.env` file.

    ```dotenv
    # API Key for ZhipuAI
    ZHIPUAI_API_KEY="your_zhipu_api_key"

    # API Key for Baidu Search
    SEARCH_API_KEY="your_search_api_key"

    # The email service to use (QQ, 163, or aliyun)
    EMAIL_USE="QQ"

    # Detailed configurations for email services
    EMAIL_CONFIGS='{"QQ":{"username":"your_qq_email","password":"your_qq_password","smtp_host":"smtp.qq.com","smtp_port":465,"imap_host":"imap.qq.com"},"163":{"username":"your_163_email","password":"your_163_password","smtp_host":"smtp.163.com","smtp_port":465,"imap_host":"imap.163.com"},"aliyun":{"username":"your_aliyun_email","password":"your_aliyun_password","smtp_host":"smtp.qiye.aliyun.com","smtp_port":465,"imap_host":"imap.qiye.aliyun.com"}}'
    ```
    *Please make sure to replace `your_...` with your actual credentials. For QQ Mail, the `password` is typically the authorization code, not the login password.*

## Usage

### Batch Formatting Markdown Files

This script will process all files in the `processed_data` directory and save the results to `format_data`.

```bash
python3 agents/batch_md.py
```

### Running the Email Assistant

Edit the `agents/mail.py` file to modify the input (recipient, subject, body, etc.) according to your needs, and then run:

```bash
python3 agents/mail.py
```

### Running the Search Tool

`tools/search.py` contains an example of how to invoke the Baidu search tool.

```bash
python3 tools/search.py
```
