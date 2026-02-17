import os
import datetime
import markdown
import json
import random

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.getcwd(), '.workers', 'generate_list_config.json')
    default_config = {
        "api_address": "https://t.alcy.cc/ycy",
        "enable_online_wallpaper": False,
        "hidden_patterns": [
            ".*",  # 隐藏以点开头的文件和目录
            "list.html",  # 隐藏根目录生成的索引文件
            "index.html"  # 隐藏子目录生成的索引文件
        ],
        "default_expanded": [
            ""  # 根目录默认展开
        ],
        "default_collapsed": []  # 默认折叠的目录
    }
    
    # 如果配置文件不存在，创建默认配置
    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        return default_config
    
    # 读取配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # 添加缺失的配置项
        if "default_expanded" not in config:
            config["default_expanded"] = [""]
        if "default_collapsed" not in config:
            config["default_collapsed"] = []
        return config
    except:
        return default_config

def is_hidden(filepath, hidden_patterns):
    """检查文件或目录是否为隐藏"""
    # 获取文件名
    filename = os.path.basename(filepath)
    
    # 检查是否匹配隐藏模式
    for pattern in hidden_patterns:
        if pattern == filename:
            return True
        elif pattern == ".*" and filename.startswith('.'):
            return True
        elif pattern.startswith('*') and filename.endswith(pattern[1:]):
            return True
        elif pattern.endswith('*') and filename.startswith(pattern[:-1]):
            return True
    
    return False

def read_readme(directory):
    """读取目录下的readme文件内容"""
    # 优先检查HTML文件，然后是MD文件，最后是TXT文件
    readme_files = [
        'README.html', 'readme.html',  # HTML文件优先
    ]
    
    # 尝试每个文件，直到找到一个可以正确读取的
    for filename in readme_files:
        readme_path = os.path.join(directory, filename)
        if os.path.exists(readme_path):
            try:
                # 尝试读取文件大小
                file_size = os.path.getsize(readme_path)
                if file_size < 5:  # 太小的文件可能是空的
                    print(f"{filename} is too small ({file_size} bytes), skipping")
                    continue
                
                # 尝试使用不同编码读取文件，包括utf-16
                encodings = ['utf-8', 'utf-16', 'gbk', 'latin-1']
                content = None
                
                for encoding in encodings:
                    try:
                        with open(readme_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    # 如果所有编码都失败，尝试二进制模式读取
                    with open(readme_path, 'rb') as f:
                        raw_content = f.read()
                    
                    # 尝试使用utf-8解码，忽略错误
                    try:
                        content = raw_content.decode('utf-8', errors='replace')
                    except:
                        content = str(raw_content)
                
                # 清理内容
                content = content.replace('\ufeff', '').replace('\x00', '').strip()
                
                # 移除BOM标记
                if content.startswith('\ufeff'):
                    content = content[1:]
                
                if not content:
                    print(f"{filename} has no valid content, skipping")
                    continue
                
                # 根据文件类型处理
                if filename.endswith('.html'):
                    # HTML文件直接返回
                    return content
                elif filename.endswith('.md'):
                    # Markdown文件
                    lines = content.split('\n')
                    html_lines = []
                    for line in lines:
                        line = line.strip()
                        if not line:
                            html_lines.append('<br>')
                        elif line.startswith('# '):
                            html_lines.append(f'<h1>{line[2:]}</h1>')
                        elif line.startswith('## '):
                            html_lines.append(f'<h2>{line[3:]}</h2>')
                        elif line.startswith('### '):
                            html_lines.append(f'<h3>{line[4:]}</h3>')
                        else:
                            html_lines.append(f'<p>{line}</p>')
                    return '\n'.join(html_lines)
                else:
                    # 文本文件
                    return f'<pre>{content}</pre>'
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                # 继续尝试下一个文件
                continue
    
    # 没有找到可以读取的readme文件
    return "<p>------</p>"

def get_random_wallpaper():
    """从background目录中随机选择一张壁纸"""
    background_dir = os.path.join(os.getcwd(), 'background')
    if not os.path.exists(background_dir):
        return None
    
    # 获取目录中的所有图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    image_files = []
    
    for file in os.listdir(background_dir):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    
    if not image_files:
        return None
    
    # 随机选择一张图片
    return random.choice(image_files)

def generate_index_for_directory(target_dir, root_dir):
    """为指定目录生成索引HTML文件"""
    # 加载配置
    config = load_config()
    hidden_patterns = config.get('hidden_patterns', ['.*', 'index.html', 'list.html'])
    default_expanded = config.get('default_expanded', [""])
    default_collapsed = config.get('default_collapsed', [])
    enable_online_wallpaper = config.get('enable_online_wallpaper', False)
    
    # 定义输出文件路径
    if os.path.normpath(target_dir) == os.path.normpath(root_dir):
        output_file = os.path.join(target_dir, 'list.html')
        print(f"在根目录生成list.html: {output_file}")
    else:
        output_file = os.path.join(target_dir, 'index.html')
        print(f"在子目录生成index.html: {output_file}")
    
    # 读取readme文件内容
    readme_content = read_readme(target_dir)
    
    # 计算相对路径到root_dir
    rel_path_to_root = os.path.relpath(root_dir, target_dir).replace('\\', '/')
    if rel_path_to_root == '.':
        rel_path_to_root = ''
    else:
        rel_path_to_root += '/'
    
    # 获取背景目录中的所有图片文件名
    def get_all_wallpapers():
        """获取背景目录中的所有图片文件名"""
        # 检查.workers/background目录
        background_dir = os.path.join(os.getcwd(), '.workers', 'background')
        if not os.path.exists(background_dir):
            # 如果不存在，检查当前目录下的background目录
            background_dir = os.path.join(os.getcwd(), 'background')
            if not os.path.exists(background_dir):
                print(f"背景目录不存在: {background_dir}")
                return []
        
        # 获取目录中的所有图片文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        image_files = []
        
        try:
            for file in os.listdir(background_dir):
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(file)
            print(f"找到 {len(image_files)} 张背景图片")
        except Exception as e:
            print(f"读取背景目录时出错: {e}")
            return []
        
        return image_files
    
    # 获取所有壁纸文件名
    all_wallpapers = get_all_wallpapers()
    
    # 开始构建HTML内容
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的简历</title>
    <link rel="stylesheet" href="''' + rel_path_to_root + '''.workers/static/style.css">
    <script src="''' + rel_path_to_root + '''.workers/static/script.js"></script>
    <style>
    </style>
'''
    
    # 添加内联JavaScript，实现随机背景图片
    if all_wallpapers:
        # 构建壁纸文件名数组的JavaScript代码
        wallpapers_array = '[' + ','.join(['"' + w + '"' for w in all_wallpapers]) + ']'
        wallpaper_base_path = rel_path_to_root + '.workers/background/'
        
        if not enable_online_wallpaper:
            html_content += '''    <script>
        // 随机背景图片设置
        document.addEventListener('DOMContentLoaded', function() {
            // 所有背景图片文件名
            var wallpapers = ''' + wallpapers_array + ''';
            // 背景图片基础路径
            var basePath = "''' + wallpaper_base_path + '''";
            // 随机选择一张图片
            var randomIndex = Math.floor(Math.random() * wallpapers.length);
            var randomWallpaper = wallpapers[randomIndex];
            // 完整背景图片路径
            var wallpaperPath = basePath + randomWallpaper;
            // 设置背景图片
            document.body.style.backgroundImage = "url('" + wallpaperPath + "')";
            // 确保背景图片正确显示
            document.body.style.backgroundSize = "cover";
            document.body.style.backgroundPosition = "center";
            document.body.style.backgroundRepeat = "no-repeat";
            document.body.style.backgroundAttachment = "fixed";
        });
    </script>
'''
        else:
            html_content += '''    <script>
        // 随机背景图片设置
        document.addEventListener('DOMContentLoaded', function() {
            // 所有背景图片文件名
            var wallpapers = ''' + wallpapers_array + ''';
            // 背景图片基础路径
            var basePath = "''' + wallpaper_base_path + '''";
            // 随机选择一张图片
            var randomIndex = Math.floor(Math.random() * wallpapers.length);
            var randomWallpaper = wallpapers[randomIndex];
            // 完整背景图片路径
            var localWallpaper = basePath + randomWallpaper;
            var onlineWallpaper = "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=modern%20abstract%20tech%20background%20with%20blue%20and%20purple%20gradients&image_size=landscape_16_9";
            // 设置背景图片
            document.body.style.backgroundImage = "url('" + onlineWallpaper + "'), url('" + localWallpaper + "')";
            // 确保背景图片正确显示
            document.body.style.backgroundSize = "cover";
            document.body.style.backgroundPosition = "center";
            document.body.style.backgroundRepeat = "no-repeat";
            document.body.style.backgroundAttachment = "fixed";
        });
    </script>
'''
    
    html_content += '''</head>
<body>
    <div class="container">
        <header>
            <h3>📁我的简历</h3>
            <div class="header-info">
                <p>生成时间: ''' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '''</p>
                <p> 我的简历——索引目录</p>
            </div>
        </header>

        <div class="file-list">
            <div class="file-list-header">
                <div>名称</div>
                <div>大小</div>
                <div>修改时间</div>
            </div>
            <div class="file-list-content">
                <details open class="directory-details root-directory">
                    <summary class="directory-summary">
                        <div class="file-item">
                            <div class="file-name">
                                <span class="directory-icon">📁</span>
                                <a href="''' + ('../list.html' if target_dir != root_dir else './') + '''">/</a>
                            </div>
                            <div class="file-size">-</div>
                            <div class="file-date">-</div>
                        </div>
                    </summary>
                    <div class="subdirectory">
'''
    
    # 检查是否需要添加上级目录链接
    if target_dir != root_dir:
        # 添加上级目录链接，指向list.html
        html_content += '''                <div class="file-item">
                    <div class="file-name">
                        <span class="directory-icon">📁</span>
                        <a href="../list.html">.. /</a>
                    </div>
                    <div class="file-size">-</div>
                    <div class="file-date">-</div>
                </div>
'''
    
    # 遍历目录结构
    def traverse_directory(current_path, level=0, current_rel_path=""):
        """递归遍历目录并生成HTML"""
        nonlocal html_content
        # 获取当前目录下的所有文件和子目录
        try:
            items = os.listdir(current_path)
        except PermissionError:
            return
        
        # 按名称排序
        items.sort()
        
        for item in items:
            item_path = os.path.join(current_path, item)
            
            # 跳过隐藏文件和目录
            if is_hidden(item_path, hidden_patterns):
                continue
            
            # 计算相对路径（相对于target_dir）
            relative_path = os.path.relpath(item_path, target_dir).replace('\\', '/')
            
            if os.path.isdir(item_path):
                # 处理目录
                # 计算从根目录开始的路径
                path_from_root = os.path.relpath(item_path, root_dir).replace('\\', '/')
                display_path = '/' + path_from_root
                # 检查是否应该默认折叠
                is_collapsed = False
                if relative_path in default_collapsed:
                    is_collapsed = True
                elif relative_path not in default_expanded and current_rel_path not in default_expanded:
                    # 如果当前目录和父目录都不在默认展开列表中，则折叠
                    is_collapsed = True
                
                # 创建目录项容器
                indent = '                ' * (level + 1)
                html_content += indent + '<details' + (' open' if not is_collapsed else '') + ' class="directory-details">\n'
                html_content += indent + '    <summary class="directory-summary">\n'
                html_content += indent + '        <div class="file-item">\n'
                html_content += indent + '            <div class="file-name">\n'
                html_content += indent + '                <span class="directory-icon">' + ('📂' if not is_collapsed else '📁') + '</span>\n'
                html_content += indent + '                <a href="' + relative_path + '/">' + display_path + '</a>\n'
                html_content += indent + '            </div>\n'
                html_content += indent + '            <div class="file-size">-</div>\n'
                html_content += indent + '            <div class="file-date">-</div>\n'
                html_content += indent + '        </div>\n'
                html_content += indent + '    </summary>\n'
                html_content += indent + '    <div class="subdirectory">\n'
                
                # 递归处理子目录
                traverse_directory(item_path, level + 1, relative_path)
                
                # 关闭子目录容器
                html_content += indent + '    </div>\n'
                html_content += indent + '</details>\n'
            else:
                # 处理文件
                # 获取文件大小
                try:
                    file_size = os.path.getsize(item_path)
                    # 格式化文件大小
                    if file_size < 1024:
                        size_str = str(file_size) + " B"
                    elif file_size < 1024 * 1024:
                        size_str = "{:.2f}".format(file_size / 1024) + " KB"
                    else:
                        size_str = "{:.2f}".format(file_size / (1024 * 1024)) + " MB"
                except:
                    size_str = "N/A"
                
                # 获取文件修改时间
                try:
                    mod_time = os.path.getmtime(item_path)
                    mod_str = datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M")
                except:
                    mod_str = "N/A"
                
                # 根据文件类型选择图标
                file_ext = os.path.splitext(item)[1].lower()
                if file_ext in ['.pdf']:
                    icon = '📄'
                elif file_ext in ['.doc', '.docx']:
                    icon = '📃'
                elif file_ext in ['.md']:
                    icon = '📝'
                elif file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    icon = '🖼️'
                elif file_ext in ['.zip', '.rar', '.7z']:
                    icon = '📦'
                else:
                    icon = '📄'
                
                indent = '                ' * (level + 1)
                html_content += indent + '<div class="file-item">\n'
                html_content += indent + '    <div class="file-name">\n'
                html_content += indent + '        <span class="file-icon">' + icon + '</span>\n'
                html_content += indent + '        <a href="' + relative_path + '">' + item + '</a>\n'
                html_content += indent + '    </div>\n'
                html_content += indent + '    <div class="file-size">' + size_str + '</div>\n'
                html_content += indent + '    <div class="file-date">' + mod_str + '</div>\n'
                html_content += indent + '</div>\n'
    
    # 开始遍历
    traverse_directory(target_dir)
    
    # 结束HTML内容，移除JavaScript引用
    html_content += '''                    </div>
                </details>
            </div>
        </div>
        <br>
        <!-- 添加readme部分 -->
        ''' + ('<div class="readme-section">' +
               readme_content +
               '</div>' if readme_content else '') + '''
        
        <div class="footer">
            <p>索引由自动生成工具创建 | 生成时间: ''' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '''</p>
        </div>
    </div>
</body>
</html>
'''
    
    # 写入HTML文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"索引文件已生成: {output_file}")

def generate_index():
    """生成所有目录的索引HTML文件"""
    # 加载配置
    config = load_config()
    hidden_patterns = config.get('hidden_patterns', ['.*', 'index.html'])
    
    # 获取当前目录路径作为根目录
    root_dir = os.path.abspath(os.getcwd())
    
    # 为根目录生成索引
    generate_index_for_directory(root_dir, root_dir)
    
    # 递归为所有子目录生成索引
    def traverse_directories(current_path):
        """递归遍历所有目录并生成索引"""
        # 获取当前目录下的所有子目录
        try:
            items = os.listdir(current_path)
        except PermissionError:
            return
        
        for item in items:
            item_path = os.path.join(current_path, item)
            
            # 跳过隐藏文件和目录
            if is_hidden(item_path, hidden_patterns):
                continue
            
            if os.path.isdir(item_path):
                # 为子目录生成索引
                generate_index_for_directory(item_path, root_dir)
                # 递归处理更深层的目录
                traverse_directories(item_path)
    
    # 开始遍历所有目录
    traverse_directories(root_dir)

if __name__ == "__main__":
    generate_index()