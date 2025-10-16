"""
配置测试脚本 - 检查系统配置是否正确
"""
import os
import sys

def check_env_file():
    """检查.env文件"""
    print("1. 检查环境变量文件...")
    if not os.path.exists('.env'):
        print("   ❌ .env 文件不存在")
        print("   💡 请复制 env_template.txt 为 .env 并填入配置")
        return False
    print("   ✅ .env 文件存在")
    return True

def check_api_key():
    """检查API Key"""
    print("\n2. 检查 API Key...")
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key or api_key == 'your_dashscope_api_key_here':
        print("   ❌ DASHSCOPE_API_KEY 未配置")
        print("   💡 请在 .env 文件中设置有效的 API Key")
        return False
    
    print(f"   ✅ API Key 已配置 (长度: {len(api_key)})")
    return True

def check_directories():
    """检查必要的目录"""
    print("\n3. 检查目录结构...")
    required_dirs = [
        'agents', 'tasks', 'tools', 'crew', 
        'static', 'static/css', 'static/js', 'uploads'
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"   ❌ 目录不存在: {dir_name}")
            all_exist = False
        else:
            print(f"   ✅ {dir_name}/")
    
    return all_exist

def check_dependencies():
    """检查依赖包"""
    print("\n4. 检查依赖包...")
    required_packages = [
        'fastapi', 'uvicorn', 'crewai', 'langchain',
        'langchain_openai', 'pydantic', 'dotenv'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} 未安装")
            all_installed = False
    
    if not all_installed:
        print("\n   💡 运行: pip install -r requirements.txt")
    
    return all_installed

def check_config_module():
    """检查配置模块"""
    print("\n5. 检查配置模块...")
    try:
        from config import Config
        Config.validate()
        print("   ✅ 配置模块加载成功")
        print(f"   ✅ 模型: {Config.LLM_MODEL}")
        print(f"   ✅ 端口: {Config.PORT}")
        return True
    except Exception as e:
        print(f"   ❌ 配置验证失败: {e}")
        return False

def check_static_files():
    """检查静态文件"""
    print("\n6. 检查静态文件...")
    required_files = [
        'static/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]
    
    all_exist = True
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"   ❌ 文件不存在: {file_path}")
            all_exist = False
        else:
            print(f"   ✅ {file_path}")
    
    return all_exist

def main():
    """运行所有检查"""
    print("="*60)
    print("  🔍 情绪识别系统 - 配置检查")
    print("="*60 + "\n")
    
    checks = [
        check_env_file,
        check_api_key,
        check_directories,
        check_dependencies,
        check_config_module,
        check_static_files
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"   ❌ 检查出错: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"  ✅ 所有检查通过！({passed}/{total})")
        print("  🚀 系统已准备就绪，可以启动服务器")
        print("\n  启动命令:")
        print("    python server.py")
        print("    或")
        print("    ./start.sh")
    else:
        print(f"  ⚠️  部分检查未通过 ({passed}/{total})")
        print("  请根据上述提示修复问题后重试")
    
    print("="*60 + "\n")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

