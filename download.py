#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量下载 Jenkins 常用插件源码

用法:
    python download_jenkins_plugin_sources.py
    python download_jenkins_plugin_sources.py --dir jenkins_plugin_sources
    python download_jenkins_plugin_sources.py --skip-pull

要求:
    1. 本机已安装 git
    2. Python 3.8+

功能:
    - 批量 clone Jenkins 插件源码
    - 目录已存在时默认执行 git pull
    - 可通过 --skip-pull 跳过更新
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# 前面那 20 个常用插件对应的常见源码仓库
PLUGINS = {
    "git": "https://github.com/jenkinsci/git-plugin.git",
    "github": "https://github.com/jenkinsci/github-plugin.git",
    "gitlab-plugin": "https://github.com/jenkinsci/gitlab-plugin.git",
    "subversion": "https://github.com/jenkinsci/subversion-plugin.git",
    "workflow-aggregator": "https://github.com/jenkinsci/workflow-aggregator-plugin.git",
    "workflow-cps": "https://github.com/jenkinsci/workflow-cps-plugin.git",
    "pipeline-model-definition": "https://github.com/jenkinsci/pipeline-model-definition-plugin.git",
    "job-dsl": "https://github.com/jenkinsci/job-dsl-plugin.git",
    "credentials": "https://github.com/jenkinsci/credentials-plugin.git",
    "credentials-binding": "https://github.com/jenkinsci/credentials-binding-plugin.git",
    "ssh-credentials": "https://github.com/jenkinsci/ssh-credentials-plugin.git",
    "role-strategy": "https://github.com/jenkinsci/role-strategy-plugin.git",
    "docker-plugin": "https://github.com/jenkinsci/docker-plugin.git",
    "docker-workflow": "https://github.com/jenkinsci/docker-workflow-plugin.git",
    "kubernetes": "https://github.com/jenkinsci/kubernetes-plugin.git",
    "maven-plugin": "https://github.com/jenkinsci/maven-plugin.git",
    "email-ext": "https://github.com/jenkinsci/email-ext-plugin.git",
    "slack": "https://github.com/jenkinsci/slack-plugin.git",
    "blueocean": "https://github.com/jenkinsci/blueocean-plugin.git",
    "ws-cleanup": "https://github.com/jenkinsci/ws-cleanup-plugin.git",
}


def run(cmd: list[str], cwd: Path | None = None) -> int:
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    return result.returncode


def ensure_git_installed() -> None:
    if shutil.which("git") is None:
        print("[ERROR] 未检测到 git，请先安装 git 再运行。", file=sys.stderr)
        sys.exit(1)


def clone_or_update(name: str, repo_url: str, base_dir: Path, skip_pull: bool) -> bool:
    repo_dir = base_dir / name

    if not repo_dir.exists():
        print(f"\n[CLONE] {name}")
        code = run(["git", "clone", repo_url, str(repo_dir)])
        return code == 0

    git_dir = repo_dir / ".git"
    if not git_dir.exists():
        print(f"\n[WARN] {repo_dir} 已存在，但不是 git 仓库，跳过。")
        return False

    if skip_pull:
        print(f"\n[SKIP] {name} 已存在，跳过更新")
        return True

    print(f"\n[UPDATE] {name}")
    code = run(["git", "pull", "--ff-only"], cwd=repo_dir)
    return code == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="批量下载 Jenkins 插件源码")
    parser.add_argument(
        "--dir",
        default="jenkins_plugin_sources",
        help="源码下载目录，默认: jenkins_plugin_sources",
    )
    parser.add_argument(
        "--skip-pull",
        action="store_true",
        help="如果目录已存在则跳过 git pull",
    )
    args = parser.parse_args()

    ensure_git_installed()

    base_dir = Path(args.dir).resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] 下载目录: {base_dir}")
    print(f"[INFO] 插件数量: {len(PLUGINS)}")

    ok_count = 0
    fail_count = 0

    for name, repo_url in PLUGINS.items():
        success = clone_or_update(name, repo_url, base_dir, args.skip_pull)
        if success:
            ok_count += 1
        else:
            fail_count += 1

    print("\n====== 完成 ======")
    print(f"成功: {ok_count}")
    print(f"失败: {fail_count}")
    print(f"目录: {base_dir}")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
