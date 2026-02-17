import os
import zipfile
import json
import datetime

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.getcwd(), 'generate_index_config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def should_include_file(filepath, config):
    """判断文件是否应该包含在打包中"""
    # 获取文件名
    filename = os.path.basename(filepath)
    
    # 排除自己（防止套娃压缩）
    if filename == 'package_files.py':
        return False
    
    # 排除resume.zip（防止套娃压缩）
    if filename == 'resume.zip':
        return False
    
    # 排除resume_temp.zip（临时文件）
    if filename == 'resume_temp.zip':
        return False
    
    # 排除check_zip_content.py（工具文件）
    if filename == 'check_zip_content.py':
        return False
    
    # 排除以点开头的文件和目录（隐藏文件），但不排除.workers目录
    if filename.startswith('.') and filename != '.workers':
        return False
    
    # 排除css、img、ttf目录
    if filename in ['css', 'ttf'] and os.path.isdir(filepath):
        return False
    
    # 特定包含的文件和目录
    include_patterns = ['.workers', 'workers', 'robots.txt', 'readme.md', 'readme.html', 'README.md', 'README.html', 'index.html', 'list.html']
    
    # 包含特定文件和目录
    if filename in include_patterns:
        return True
    
    # 其他文件都包含
    return True

def create_zip_archive():
    """创建zip归档文件"""
    # 加载配置
    config = load_config()
    
    # 根目录路径（当前目录）
    root_dir = os.path.abspath(os.getcwd())
    
    # 生成zip文件名（放在根目录，使用固定名称）
    zip_filename = os.path.join(root_dir, 'resume.zip')
    temp_zip_filename = os.path.join(root_dir, 'resume_temp.zip')
    
    # 如果临时文件已存在，先删除
    if os.path.exists(temp_zip_filename):
        try:
            os.remove(temp_zip_filename)
            print(f"已删除旧的临时归档文件: {temp_zip_filename}")
        except Exception as e:
            print(f"删除临时文件时出错: {e}")
    
    # 创建zip文件（使用临时文件名）
    with zipfile.ZipFile(temp_zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历目录结构
        for root, dirs, files in os.walk(root_dir):
            # 过滤目录，避免进入不需要的目录
            dirs[:] = [d for d in dirs if should_include_file(os.path.join(root, d), config)]
            
            # 处理文件
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if should_include_file(file_path, config):
                    # 获取相对路径
                    rel_path = os.path.relpath(file_path, root_dir)
                    # 添加文件到zip
                    zipf.write(file_path, rel_path)
    
    # 重命名临时文件为最终文件名
    try:
        # 如果目标文件存在，先删除
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        # 重命名临时文件
        os.rename(temp_zip_filename, zip_filename)
        print(f"归档文件已创建: {zip_filename}")
        return zip_filename
    except Exception as e:
        print(f"重命名文件时出错: {e}")
        # 使用带时间戳的文件名作为替代
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_zip_filename = os.path.join(root_dir, f'resume_{timestamp}.zip')
        os.rename(temp_zip_filename, backup_zip_filename)
        print(f"归档文件已创建（使用备用文件名）: {backup_zip_filename}")
        return backup_zip_filename

if __name__ == "__main__":
    create_zip_archive()
