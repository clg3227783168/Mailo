import os
import sys
import time

# 将父目录添加到系统路径中，以便可以从`agents`模块导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 尝试从markdown.py导入核心处理函数
    from markdown import format_and_save_markdown
except ImportError:
    print("错误: 无法从 'markdown.py' 导入 'format_and_save_markdown' 函数。")
    print("请确保 'agents/markdown.py' 文件存在且路径正确。")
    sys.exit(1)

def batch_format_markdown():
    """
    批量处理 `processed_data` 目录下的所有文件，进行格式化，
    并保存到 `format_data` 目录。
    如果目标目录中已存在同名文件，则会跳过。
    对于处理失败的文件，会进行自动重试。
    """
    # 使用相对路径定位目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_data_dir = os.path.join(base_dir, 'processed_data')
    format_data_dir = os.path.join(base_dir, 'format_data')

    # 如果输出目录不存在，则创建它
    if not os.path.exists(format_data_dir):
        os.makedirs(format_data_dir)
        print(f"已创建目录: {format_data_dir}")

    try:
        # 获取待处理文件列表
        files_to_process = [f for f in os.listdir(processed_data_dir) if os.path.isfile(os.path.join(processed_data_dir, f))]
        
        # 获取目标目录中已存在的文件集合，用于快速查找
        existing_files = set(os.listdir(format_data_dir))

        if not files_to_process:
            print(f"在 '{processed_data_dir}' 目录下未找到任何文件。")
            return

        print(f"开始批量处理 {len(files_to_process)} 个文件...")
        processed_count = 0
        skipped_count = 0
        failed_files = []

        # 设置重试参数
        max_retries = 3
        retry_delay = 1  # 秒

        for filename in files_to_process:
            if filename in existing_files:
                skipped_count += 1
                continue

            input_path = os.path.join(processed_data_dir, filename)
            output_path = os.path.join(format_data_dir, filename)

            print(f"正在处理: {input_path}")
            
            for attempt in range(max_retries):
                try:
                    format_and_save_markdown(input_path, output_path)
                    processed_count += 1
                    break  # 成功，跳出重试循环
                except Exception as e:
                    print(f"  处理 '{filename}' 时出错 (尝试 {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        print(f"  将在 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                    else:
                        print(f"  文件 '{filename}' 重试失败。")
                        failed_files.append(filename)
        
        print("\n批量处理完成。")
        print(f"成功处理: {processed_count} 个文件")
        print(f"跳过 (已存在): {skipped_count} 个文件")
        if failed_files:
            print(f"处理失败的文件 ({len(failed_files)} 个):")
            for f in failed_files:
                print(f"  - {f}")

    except FileNotFoundError:
        print(f"错误: 找不到目录 '{processed_data_dir}'。")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == '__main__':
    batch_format_markdown()