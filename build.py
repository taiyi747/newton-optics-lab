#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物理光学综合实验平台 - Python 后端打包脚本 (Nuitka)

使用方法:
    python build.py
    python build.py --force

输出:
    src-tauri/binaries/backend-x86_64-pc-windows-msvc.exe
"""

import os
import sys
import shutil
import subprocess
import argparse

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BINARIES_DIR = os.path.join(PROJECT_ROOT, "src-tauri", "binaries")
TARGET_TRIPLE = "x86_64-pc-windows-msvc"


def generate_builtin_config():
    """从 .env 生成内置配置文件，打包时嵌入到代码中。"""
    print("\n=== 生成内置配置 ===")

    env_path = os.path.join(PROJECT_ROOT, ".env")
    config_path = os.path.join(PROJECT_ROOT, "lib", "_config_built.py")

    if not os.path.exists(env_path):
        print("警告: .env 文件不存在，跳过内置配置生成")
        return

    config_content = ["# 构建时自动生成的内置配置", "# 不要手动修改此文件", ""]
    config_keys = ["AI_API_KEY", "AI_API_BASE_URL", "AI_MODEL", "AI_REASONING_EFFORT"]

    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("AI_") and "=" in line:
                key, value = line.split("=", 1)
                value = value.strip().strip('"').strip("'")
                if key in config_keys and value:
                    config_content.append(f'{key} = "{value}"')
                    print(f"  嵌入配置: {key}")

    if len(config_content) > 2:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("\n".join(config_content))
        print(f"已生成: {config_path}")
    else:
        print("  .env 中无有效配置，跳过生成")


def build_backend():
    """使用 Nuitka 打包后端"""
    print("\n=== 打包 Python 后端 (Nuitka) ===")

    cmd = [
        sys.executable, "-m", "nuitka",

        # 输出模式
        "--onefile",
        "--output-filename=backend.exe",

        # 依赖管理
        "--assume-yes-for-downloads",
        "--follow-imports",

        # 插件
        "--enable-plugin=numpy",
        "--enable-plugin=matplotlib",

        # 包含项目模块
        "--include-package=lib",

        # onefile 解压缓存 — 避免每次启动重新解压
        "--onefile-tempdir-spec={TEMP}/newton-backend",

        # 排除不需要的标准库模块
        "--nofollow-import-to=tkinter",
        "--nofollow-import-to=unittest",
        "--nofollow-import-to=pydoc",
        "--nofollow-import-to=doctest",
        "--nofollow-import-to=curses",
        "--nofollow-import-to=msvcrt",
        "--nofollow-import-to=audiodev",
        "--nofollow-import-to=audioop",
        "--nofollow-import-to=ossaudiodev",
        "--nofollow-import-to=sunau",
        "--nofollow-import-to=wave",
        "--nofollow-import-to=chunk",
        "--nofollow-import-to=imghdr",
        "--nofollow-import-to=nntplib",
        "--nofollow-import-to=telnetlib",
        "--nofollow-import-to=uu",
        "--nofollow-import-to=xdrlib",

        # 排除不需要的第三方包
        "--nofollow-import-to=scipy",
        "--nofollow-import-to=scipy.linalg",
        "--nofollow-import-to=scipy.sparse",
        "--nofollow-import-to=scipy.optimize",
        "--nofollow-import-to=scipy.integrate",
        "--nofollow-import-to=scipy.fft",
        "--nofollow-import-to=scipy.signal",
        "--nofollow-import-to=scipy.ndimage",
        "--nofollow-import-to=scipy.stats",
        "--nofollow-import-to=scipy.io",
        "--nofollow-import-to=scipy.special",
        "--nofollow-import-to=pandas",

        # matplotlib 只保留 agg 后端和中文字体
        "--nofollow-import-to=matplotlib.tests",
        "--nofollow-import-to=matplotlib.backends.backend_qt",
        "--nofollow-import-to=matplotlib.backends.backend_qt5",
        "--nofollow-import-to=matplotlib.backends.backend_qt6",
        "--nofollow-import-to=matplotlib.backends.backend_tk",
        "--nofollow-import-to=matplotlib.backends.backend_gtk",
        "--nofollow-import-to=matplotlib.backends.backend_wx",
        "--nofollow-import-to=matplotlib.backends.backend_macosx",
        "--nofollow-import-to=matplotlib.backends.backend_pdf",
        "--nofollow-import-to=matplotlib.backends.backend_svg",
        "--nofollow-import-to=matplotlib.backends.backend_pgf",

        # Windows 设置
        "--windows-console-mode=force",

        # 入口文件
        "server.py"
    ]

    print(f"\n>>> 执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        print(f"错误: 命令执行失败 (返回码 {result.returncode})")
        sys.exit(1)

    # 清理旧的 standalone 产物
    internal_dir = os.path.join(BINARIES_DIR, "_internal")
    if os.path.exists(internal_dir):
        print(f"清理旧 standalone 产物: {internal_dir}")
        shutil.rmtree(internal_dir)

    # 创建 binaries 目录
    os.makedirs(BINARIES_DIR, exist_ok=True)

    # 复制 exe 到 binaries 目录
    src_exe = os.path.join(PROJECT_ROOT, "backend.exe")
    dst_exe = os.path.join(BINARIES_DIR, f"backend-{TARGET_TRIPLE}.exe")

    if os.path.exists(src_exe):
        print(f"复制: {src_exe} -> {dst_exe}")
        shutil.copy2(src_exe, dst_exe)
        os.remove(src_exe)
    else:
        print("错误: backend.exe 未找到")
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="构建 Newton Rings Python sidecar")
    parser.add_argument(
        "--force",
        action="store_true",
        help="即使已存在 sidecar 也重新构建",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("牛顿环综合实验平台 - 后端打包脚本 (Nuitka)")
    print("=" * 60)

    # 生成内置配置
    generate_builtin_config()

    # 检查 Nuitka
    try:
        import nuitka
        print("Nuitka: 已安装")
    except ImportError:
        print("错误: Nuitka 未安装")
        print("请运行: pip install nuitka ordered-set zstandard")
        sys.exit(1)

    # 检查是否已有构建产物
    sidecar_exe = os.path.join(BINARIES_DIR, f"backend-{TARGET_TRIPLE}.exe")
    if os.path.exists(sidecar_exe):
        size_mb = os.path.getsize(sidecar_exe) / (1024 * 1024)
        print(f"\n检测到已存在: {sidecar_exe} ({size_mb:.1f} MB)")
        if not args.force:
            answer = input("是否重新构建? (y/N): ").strip().lower()
            if answer != "y":
                print("使用现有文件")
                return
            print("重新构建")
        else:
            print("已指定 --force，重新构建")

    build_backend()

    sidecar_exe = os.path.join(BINARIES_DIR, f"backend-{TARGET_TRIPLE}.exe")
    size_mb = os.path.getsize(sidecar_exe) / (1024 * 1024)

    print("\n" + "=" * 60)
    print("后端打包完成!")
    print(f"输出: {sidecar_exe} ({size_mb:.1f} MB)")
    print("=" * 60)
    print("\n下一步: npm run tauri build")


if __name__ == "__main__":
    main()
