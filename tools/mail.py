import os
from typing import Optional, Type
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from langchain.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import imaplib
import email
from email.header import decode_header
import html2text

load_dotenv(override=True)

import json

# 从环境变量加载邮件配置
EMAIL_CONFIGS = json.loads(os.getenv("EMAIL_CONFIGS"))


class EmailInput(BaseModel):
    """通用邮件工具的输入"""
    to: str = Field(..., description="收件人邮箱地址")
    subject: str = Field(..., description="邮件主题")
    body: str = Field(..., description="邮件内容")
    cc: Optional[str] = Field(None, description="可选的抄送邮箱地址")
    is_html: Optional[bool] = Field(False, description="邮件内容是否为HTML格式")
    attachment_path: Optional[str] = Field(None, description="附件文件的可选路径")


class UniversalEmailTool(BaseTool):
    """通过多种邮件服务发送邮件的工具"""
    name: str = "universal_email_sender"
    description: str = """通过多种邮件服务（QQ、163、阿里云）发送邮件，支持HTML内容、抄送收件人和附件。
    输入应为描述邮件详情的自然语言请求。

    示例:
    1. "发送邮件给user@example.com，主题为'Hello'，内容为'Test email'"
    2. "发送HTML邮件给user@example.com，抄送给cc@example.com，主题为'Test'，内容为'<h1>Hello</h1>'"
    3. "发送邮件给user@example.com，主题为'Files'，内容为'See attachment'，附加文件file.txt"
    4. "发送HTML邮件给user@example.com，抄送给cc@example.com，主题为'Test'，内容为'hi'"

    工具会将请求格式化为正确的邮件参数。"""
    args_schema: Type[BaseModel] = EmailInput

    def __init__(self, **data):
        super().__init__(**data)
        self._email_service = os.getenv("EMAIL_USE", "QQ").upper()
        if self._email_service not in EMAIL_CONFIGS:
            raise ValueError(f"不支持的邮件服务: {self._email_service}")

        config = EMAIL_CONFIGS[self._email_service]
        self._sender_email = config["username"]
        self._auth_code = config["password"]
        self._smtp_host = config["smtp_host"]
        self._smtp_port = config["smtp_port"]

        if not self._sender_email or not self._auth_code:
            raise ValueError(f"缺少 {self._email_service} 的邮箱地址或密码")

    def _prepare_message(
            self,
            to_email: str,
            subject: str,
            body: str,
            cc_email: Optional[str] = None,
            is_html: bool = False,
            attachment_path: Optional[str] = None
    ) -> MIMEMultipart:
        """准备包含所有组件的邮件消息"""
        message = MIMEMultipart()
        message["From"] = self._sender_email
        message["To"] = to_email
        if cc_email:
            message["Cc"] = cc_email
        message["Subject"] = subject

        # 添加正文
        body_part = MIMEText(body, 'html' if is_html else 'plain', 'utf-8')
        message.attach(body_part)

        # 添加附件（如果提供）
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                attachment = MIMEApplication(f.read())
                attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=os.path.basename(attachment_path)
                )
                message.attach(attachment)

        return message

    def _run(
            self,
            to: str,
            subject: str,
            body: str,
            cc: Optional[str] = None,
            is_html: bool = False,
            attachment_path: Optional[str] = None
    ) -> str:
        """运行工具发送邮件"""
        try:
            # 创建消息
            msg = self._prepare_message(
                to_email=to,
                subject=subject,
                body=body,
                cc_email=cc,
                is_html=is_html,
                attachment_path=attachment_path
            )

            # 创建收件人列表
            recipients = [to]
            if cc:
                recipients.append(cc)

            try:
                # 连接到SMTP服务器
                server = smtplib.SMTP_SSL(self._smtp_host, self._smtp_port)
                server.login(self._sender_email, self._auth_code)

                # 发送邮件
                server.sendmail(self._sender_email, recipients, msg.as_string())
                server.quit()

                return f"邮件已通过 {self._email_service} 成功发送给 {to}" + (
                    f"，抄送给 {cc}" if cc else "")

            except smtplib.SMTPException as e:
                return f"SMTP错误: {str(e)}"

        except Exception as e:
            return f"发送邮件失败: {str(e)}"


class EmailReadInput(BaseModel):
    """阅读邮件的输入"""
    num_emails: int = Field(..., description="要阅读的最近邮件数量（最多30封）")


class UniversalEmailToolReading(BaseTool):
    """阅读和总结邮件的工具"""
    name: str = "universal_email_reader"
    description: str = """从您的邮箱收件箱中阅读和总结最近的邮件。
    输入应为1到30之间的数字，表示要阅读多少封最近的邮件。

    示例:
    1. "阅读我最后的10封邮件"
    2. "显示我最近的20封邮件"
    3. "总结我最新的30封邮件"
    4. "获取我最近15封邮件的摘要"
    """
    args_schema: Type[BaseModel] = EmailReadInput

    def __init__(self, **data):
        super().__init__(**data)
        self._email_service = os.getenv("EMAIL_USE", "QQ").upper()
        if self._email_service not in EMAIL_CONFIGS:
            raise ValueError(f"不支持的邮件服务: {self._email_service}")

        config = EMAIL_CONFIGS[self._email_service]
        self._email = config["username"]
        self._auth_code = config["password"]
        self._imap_host = config["imap_host"]

        if not self._email or not self._auth_code:
            raise ValueError(f"缺少 {self._email_service} 的邮箱地址或密码")
        self._h2t = html2text.HTML2Text()
        self._h2t.ignore_links = True

    def _decode_email_subject(self, subject):
        """解码邮件主题"""
        if not subject:
            return "无主题"
        decoded_list = decode_header(subject)
        subject = ""
        for decoded_str, charset in decoded_list:
            if isinstance(decoded_str, bytes):
                if charset:
                    try:
                        subject += decoded_str.decode(charset)
                    except:
                        subject += decoded_str.decode('utf-8', errors='ignore')
                else:
                    subject += decoded_str.decode('utf-8', errors='ignore')
            else:
                subject += str(decoded_str)
        return subject

    def _get_email_content(self, msg):
        """从消息中提取邮件内容"""
        try:
            content = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            content = part.get_payload(decode=True).decode()
                            break
                        except:
                            content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                    elif part.get_content_type() == "text/html":
                        try:
                            html_content = part.get_payload(decode=True).decode()
                            content = self._h2t.handle(html_content)
                            break
                        except:
                            html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            content = self._h2t.handle(html_content)
                            break
            else:
                try:
                    content = msg.get_payload(decode=True).decode()
                except:
                    content = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

            # 清理内容
            content = content.strip()
            content = ' '.join(content.split())  # 移除多余空白
            return content
        except Exception as e:
            return f"[提取内容时出错: {str(e)}]"

    def _run(
            self,
            num_emails: int
    ) -> str:
        """运行工具阅读最近的邮件"""
        try:
            # 限制邮件数量在1-30之间
            num_emails = min(max(1, num_emails), 30)

            # 连接到IMAP服务器
            mail = imaplib.IMAP4_SSL(self._imap_host)
            mail.login(self._email, self._auth_code)

            # 选择收件箱
            mail.select("INBOX")

            # 搜索所有邮件并获取最新的邮件
            _, messages = mail.search(None, "ALL")
            email_ids = messages[0].split()
            latest_emails = email_ids[-num_emails:]

            # 处理每封邮件
            summaries = []
            separator = "-" * 50

            for email_id in reversed(latest_emails):
                try:
                    _, msg_data = mail.fetch(email_id, "(RFC822)")
                    email_body = msg_data[0][1]
                    msg = email.message_from_bytes(email_body)

                    # 获取主题
                    subject = self._decode_email_subject(msg["subject"])

                    # 获取发件人
                    sender = msg["from"] if msg["from"] else "未知发件人"

                    # 获取内容
                    content = self._get_email_content(msg)

                    # 创建摘要
                    summary = f"\n发件人: {sender}\n主题: {subject}\n内容摘要: {content[:200]}...\n{separator}"
                    summaries.append(summary)
                except Exception as e:
                    summaries.append(f"\n处理邮件时出错: {str(e)}\n{separator}")

            mail.close()
            mail.logout()

            if not summaries:
                return "收件箱中未找到邮件。"

            header = f"来自 {self._email_service} 账户的最新 {num_emails} 封邮件:"
            top_separator = "=" * 50
            bottom_separator = "=" * 50

            return f"{header}\n{top_separator}\n{''.join(summaries)}\n{bottom_separator}\n邮件摘要结束。"

        except Exception as e:
            return f"阅读邮件失败: {str(e)}"