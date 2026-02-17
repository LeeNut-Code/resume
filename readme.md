
# 熊大简历网站

## 项目简介

这是一个基于熊出没角色熊大的简历网站项目，用于展示熊大的教育背景、实习经历、校园经历、个人项目、专业技能和自我评价等信息。网站采用现代化的设计风格，响应式布局，适配各种设备屏幕。

> 此网站通过robots.txt文件配置，禁止**搜索引擎爬虫**访问。

## 项目特点

- **现代化设计**：采用 Tailwind CSS 和 Font Awesome 构建，视觉效果美观
- **响应式布局**：适配桌面、平板和手机等各种设备屏幕
- **内容丰富**：包含个人信息、教育背景、实习经历、校园经历、个人项目、专业技能和自我评价等完整信息
- **交互友好**：提供导航菜单，支持快速跳转到不同部分
- **功能完善**：支持简历PDF下载、文件列表索引等功能
- **易于维护**：通过Markdown文件管理简历内容，支持自动更新网站

## 使用说明

### 本地运行

1. 克隆项目到本地
2. 确保安装了Python 3.6+
3. 运行 `python .workers/start_local_server.py` 启动本地服务器
4. 在浏览器中访问 `http://localhost:5123` 查看网站

### 更新简历

1. 修改 `resume/简历.md` 文件中的简历内容
2. 运行 `python .workers/update_resume.py` 更新网站内容

### 生成文件索引

运行 `python .workers/list.py` 生成文件索引页面

### 打包文件

运行 `python .workers/package_files.py` 打包所有文件为zip格式

## 文件结构

```
├── .workers/              # 工具脚本目录
│   ├── background/        # 背景图片
│   ├── static/            # 静态资源
│   ├── list.py            # 生成文件索引
│   ├── package_files.py    # 打包文件
│   ├── start_local_server.py  # 启动本地服务器
│   └── update_resume.py    # 更新简历
├── application/           # 求职申请相关文件
├── resume/                # 简历文件目录
│   ├── css/               # 样式文件
│   ├── img/               # 图片资源
│   ├── ttf/               # 字体文件
│   ├── 简历.md            # 简历内容（Markdown格式）
│   └── 简历.pdf           # 简历PDF文件
├── index.html             # 主页面
├── list.html              # 文件索引页面
├── robots.txt             # 搜索引擎爬虫配置
└── readme.md              # 项目说明文档
```

## 技术栈

- **前端**：HTML5, CSS3, JavaScript, Tailwind CSS, Font Awesome
- **后端**：Python 3.6+
- **工具**：Markdown, BeautifulSoup, YAML
- **部署**：静态网站托管

## 示例访问

- **主页面**：`http://localhost:5123`
- **文件索引**：`http://localhost:5123/list.html`
- **求职申请**：`http://localhost:5123/application/求职申请&HR须知.html`

## 致谢

感谢 [GitHub仓库](https://github.com/wxnan/resume) 提供的简历模板。

## 免责声明

此项目仅用于展示和学习目的，所有内容均为虚构，基于熊出没角色熊大创作。
