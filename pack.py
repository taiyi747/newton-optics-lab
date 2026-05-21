"""项目源码打包脚本 — 排除依赖和构建产物，输出 zip"""

import argparse
import os
import zipfile
from datetime import datetime
from pathlib import Path

# 项目根目录（脚本所在目录）
ROOT = Path(__file__).resolve().parent
PROJECT_NAME = ROOT.name
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
DEFAULT_OUTPUT = ROOT.parent / f"{PROJECT_NAME}-source-{TIMESTAMP}.zip"

# 排除规则：目录名（任意层级匹配）或文件名/后缀
SKIP_DIRS = {
    "node_modules", "__pycache__", ".claude", ".git", ".vscode", ".pua",
    "build", "dist", "target", "gen", "binaries",
    ".nuxt", ".output", ".next", ".parcel-cache", ".cache",
    ".pytest_cache", ".mypy_cache", "htmlcov", "coverage",
    "server.build", "server.dist", "server.onefile-build",
}
SKIP_FILES = {
    "package-lock.json", "Cargo.lock", "nuitka-crash-report.xml",
    "task_plan.md", "findings.md", "progress.md", "design.md",
    ".DS_Store", "Thumbs.db", "desktop.ini",
    # 商业计划书文档
    "拾光悟理-基于Python+Tauri的光学智能仿真与教学辅助平台商业计划书(1).doc",
    "拾光悟理-技术部分-商业计划书.md",
}
SKIP_SUFFIXES = {".pyc", ".log", ".tmp", ".temp", ".bak"}
# 按相对路径排除
SKIP_PATHS = {"template.zip"}


def should_skip(rel_path: str) -> bool:
    parts = Path(rel_path).parts
    # 目录名黑名单
    for d in parts[:-1]:
        if d in SKIP_DIRS:
            return True
    name = parts[-1]
    # 编辑器备份文件（~开头或~结尾）
    if name.startswith("~") or name.endswith("~"):
        return True
    # 文件名黑名单
    if name in SKIP_FILES:
        return True
    # 后缀黑名单
    suffix = Path(name).suffix
    if suffix in SKIP_SUFFIXES:
        return True
    # 相对路径黑名单
    for p in SKIP_PATHS:
        if rel_path == p or rel_path.startswith(p + "/"):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description="打包项目源码（排除依赖与构建产物）")
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"输出 zip 路径（默认: {DEFAULT_OUTPUT}）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅列出会打包的文件，不实际生成 zip",
    )
    args = parser.parse_args()

    output: Path = args.output
    if not args.dry_run:
        output.parent.mkdir(parents=True, exist_ok=True)

    print(f"=== 打包项目源码 ===")
    print(f"项目目录: {ROOT}")
    if args.dry_run:
        print("模式: 预览（dry-run）")
    else:
        print(f"输出文件: {output}")
    print()

    collected = []  # (rel_path, size)
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # 就地过滤目录，阻止 os.walk 进入
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and d != ".git"]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            rel = fpath.relative_to(ROOT).as_posix()
            if should_skip(rel):
                continue
            collected.append((rel, fpath.stat().st_size))

    # 按路径排序，让输出清晰
    collected.sort(key=lambda x: x[0])

    total_size = sum(s for _, s in collected)
    count = len(collected)

    # 列出文件（预览模式或长列表）
    if args.dry_run:
        for rel, size in collected:
            print(f"  {rel}  ({size / 1024:.1f} KB)")
        print()

    if not args.dry_run:
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
            for rel, _ in collected:
                fpath = ROOT / rel
                zf.write(fpath, rel)

    size_mb = total_size / (1024 * 1024)
    zip_mb = output.stat().st_size / (1024 * 1024) if not args.dry_run and output.exists() else 0

    print(f"=== 统计 ===")
    print(f"文件数量: {count}")
    print(f"原始大小: {size_mb:.1f} MB")
    if not args.dry_run:
        print(f"输出文件: {output}")
        print(f"Zip 大小: {zip_mb:.1f} MB")
        print(f"压缩率:   {(1 - zip_mb / size_mb) * 100:.1f}%") if size_mb > 0 else None
    print()
    print("打包完成" if not args.dry_run else "预览结束，未生成文件")


if __name__ == "__main__":
    main()
