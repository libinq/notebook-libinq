import sys
import os
import subprocess
import webbrowser
from pathlib import Path

def main():
    base_dir = Path(__file__).resolve().parent
    requirements_file = base_dir / "backend" / "requirements.txt"

    print("=" * 60)
    print(" 📓 Open Notebook Bilingual · 对标 Google NotebookLM")
    print("=" * 60)
    print(f"工作目录: {base_dir}")

    # Check and run with uvicorn
    try:
        import uvicorn
    except ImportError:
        print("正在自动安装核心依赖包 (FastAPI, Uvicorn, Edge-TTS 等)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])

    port = int(os.getenv("PORT", "8502"))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"\n🚀 服务启动中: http://localhost:{port}")
    print(f"👉 局域网访问: http://<本机IP>:{port}\n")

    # Run Uvicorn
    import uvicorn
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()
