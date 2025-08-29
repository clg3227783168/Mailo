# Mailo - AI 智能助理

Mailo 是一个基于大语言模型（LLM）的 Python 项目，旨在提供一系列自动化和智能化功能，包括文档处理、邮件管理和网络搜索。

## 功能特性

- **Markdown 格式化**:
  - **单个文件处理**: 使用 `agents/markdown.py` 脚本，可以调用 LLM 将指定的 Markdown 文件转换为格式规范、干净的版本。
  - **批量处理**: `agents/batch_md.py` 脚本可以自动处理 `processed_data` 目录下的所有 Markdown 文件，跳过已处理过的文件，并将结果保存到 `format_data` 目录。该脚本还包含了错误处理和重试机制。

- **邮件智能助手**:
  - **发送邮件**: 通过自然语言指令（例如“给 a@b.com 发邮件，主题是... 内容是...”），代理可以调用邮件工具发送邮件。
  - **读取邮件**: 支持通过指令（例如“读我最近的5封邮件”）来获取邮件摘要。
  - **多平台支持**: 在 `.env` 文件中可以配置 QQ、163、阿里云等多种邮件服务商。

- **网络搜索**:
  - 集成了百度搜索 API，允许代理根据需要进行网络搜索以获取信息。

## 安装与设置

1.  **克隆项目**
    ```bash
    git clone [<your-repository-url>](https://github.com/clg3227783168/Mailo.git)
    cd Mailo
    ```

2.  **创建并激活 Python 虚拟环境**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    *注意：退出虚拟环境请使用 `deactivate` 命令。*

3.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置环境变量**
    - 将 `.env.example` 文件（如果提供）复制为 `.env`，或者直接创建 `.env` 文件。
    - 在 `.env` 文件中填入您的 API 密钥和邮箱配置。

    ```dotenv
    # 智谱AI的API Key
    ZHIPUAI_API_KEY="your_zhipu_api_key"

    # 百度搜索的API Key
    SEARCH_API_KEY="your_search_api_key"

    # 当前使用的邮件服务 (QQ, 163, or aliyun)
    EMAIL_USE="QQ"

    # 邮件服务商的详细配置
    EMAIL_CONFIGS='{"QQ":{"username":"your_qq_email","password":"your_qq_password","smtp_host":"smtp.qq.com","smtp_port":465,"imap_host":"imap.qq.com"},"163":{"username":"your_163_email","password":"your_163_password","smtp_host":"smtp.163.com","smtp_port":465,"imap_host":"imap.163.com"},"aliyun":{"username":"your_aliyun_email","password":"your_aliyun_password","smtp_host":"smtp.qiye.aliyun.com","smtp_port":465,"imap_host":"imap.qiye.aliyun.com"}}'
    ```
    *请确保将 `your_...` 替换为您的真实凭据。对于QQ邮箱，`password` 通常指的是授权码，而不是登录密码。*

## 使用方法

### 批量格式化 Markdown 文件

该脚本会处理 `processed_data` 目录下的所有文件，并将结果保存到 `format_data`。

```bash
python3 agents/batch_md.py
```

### 运行邮件助手

编辑 `agents/mail.py` 文件，根据您的需求修改输入（收件人、主题、内容等），然后运行：

```bash
python3 agents/mail.py
```

### 运行搜索工具

`tools/search.py` 中包含了一个调用百度搜索工具的示例。

```bash
python3 tools/search.py
```
