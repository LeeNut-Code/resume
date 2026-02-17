# .workers 目录说明

## 目录简介

`.workers` 目录包含了一系列用于管理和维护简历网站的工具脚本。这些脚本用于生成文件索引、更新简历内容、打包文件和启动本地服务器等操作。

## 目录结构

```
├── background/             # 背景图片目录
│   ├── 0.jpg              # 背景图片1
│   ├── 1.png              # 背景图片2
│   ├── 2.webp             # 背景图片3
│   ├── ...                 # 更多背景图片
├── static/                 # 静态资源目录
│   ├── script.js          # JavaScript 脚本
│   ├── style.css           # CSS 样式文件
├── generate_list_config.json  # 配置文件
├── list.py                 # 生成索引文件脚本
├── package_files.py        # 打包文件脚本
├── start_local_server.py   # 启动本地服务器脚本
├── update_resume.py        # 更新简历脚本
├── readme.md               # 本说明文件
```

## 脚本说明

### 1. list.py

**功能**：生成文件索引页面，方便浏览和下载项目中的所有文件。

**特点**：
- 在根目录生成 `list.html` 文件
- 在子目录生成 `index.html` 文件
- 支持随机背景图片
- 支持响应式设计
- 自动读取目录下的 readme 文件内容

**使用方法**：
```bash
python .workers/list.py
```

### 2. update_resume.py

**功能**：根据 `resume/简历.md` 文件更新 `index.html` 中的简历内容。

**特点**：
- 自动解析 Markdown 格式的简历内容
- 生成美观的 HTML 页面
- 支持更新个人信息、教育背景、实习经历、工作经验、校园经历、个人项目、专业技能和自我评价等部分
- 自动更新最后更新时间

**使用方法**：
```bash
python .workers/update_resume.py
```

### 3. package_files.py

**功能**：将项目文件打包为 zip 格式，方便传输和部署。

**特点**：
- 自动排除不需要打包的文件和目录
- 确保包含所有必要的文件
- 支持处理文件重命名冲突

**使用方法**：
```bash
python .workers/package_files.py
```

### 4. start_local_server.py

**功能**：启动本地服务器，方便在本地预览网站效果。

**特点**：
- 启动一个简单的 HTTP 服务器
- 支持指定端口号
- 提供访问 URL 提示

**使用方法**：
```bash
python .workers/start_local_server.py
```

## 配置文件

### generate_list_config.json

**功能**：配置 `list.py` 脚本的行为。

**主要配置项**：
- `api_address`：API 地址
- `enable_online_wallpaper`：是否启用在线壁纸
- `hidden_patterns`：需要隐藏的文件和目录模式
- `default_expanded`：默认展开的目录
- `default_collapsed`：默认折叠的目录

## 静态资源

### static/script.js

**功能**：提供网站的交互功能。

**主要功能**：
- 处理导航菜单的交互
- 处理标签页的切换
- 处理内容的展开和折叠

### static/style.css

**功能**：提供网站的样式定义。

**主要样式**：
- 全局样式重置
- 响应式布局
- 组件样式
- 动画效果

## 背景图片

`background/` 目录包含了一系列用于网站背景的图片。`list.py` 脚本会随机选择一张图片作为网站背景。

## 使用流程

1. **更新简历内容**：修改 `resume/简历.md` 文件，然后运行 `update_resume.py` 脚本更新 `index.html`。

2. **生成文件索引**：运行 `list.py` 脚本生成 `list.html` 和各个子目录的 `index.html` 文件。

3. **本地预览**：运行 `start_local_server.py` 脚本启动本地服务器，在浏览器中预览网站效果。

4. **打包部署**：运行 `package_files.py` 脚本打包所有文件，然后将打包文件部署到服务器。

## 注意事项

- 确保 Python 版本为 3.6 或更高
- 确保所有依赖库已安装
- 运行脚本时，确保当前工作目录为项目根目录
- 定期备份重要文件，以防意外丢失
