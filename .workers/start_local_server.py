import os
import http.server
import socketserver
import webbrowser
import threading
import time

def start_local_server():
    """启动本地HTTP服务器"""
    # 获取项目根目录
    project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
    
    # 切换到项目根目录
    os.chdir(project_root)
    
    # 定义服务器端口
    PORT = 5123
    
    # 创建请求处理器
    Handler = http.server.SimpleHTTPRequestHandler
    
    # 创建服务器
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"本地服务器已启动，运行在 http://localhost:{PORT}")
        print(f"项目根目录: {project_root}")
        print("按 Ctrl+C 停止服务器")
        
        # 尝试在浏览器中打开
        try:
            webbrowser.open(f'http://localhost:{PORT}')
            print("已尝试在默认浏览器中打开页面")
        except:
            print("无法自动打开浏览器，请手动访问 http://localhost:{PORT}")
        
        # 启动服务器
        httpd.serve_forever()

def main():
    """主函数"""
    print("正在启动本地部署服务...")
    print("此服务将允许您在本地访问生成的索引页面")
    print("所有文件（包括隐藏文件）都可以通过浏览器或命令行工具访问")
    print()
    
    try:
        start_local_server()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动服务器时出错: {e}")

if __name__ == "__main__":
    main()