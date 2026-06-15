"""bootstrap.py — project-protocol 自举引擎
当项目缺少 CLAUDE.md / PROGRESS.md / GATES.md 时，自动从模板生成。
"""
import os
import json
import sys
from datetime import datetime, timezone


SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(SKILL_DIR, "templates")
WORKSPACE_ROOT = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

def detect_project_info(project_dir: str, project_name: str) -> dict:
    """从项目目录已有文件探测技术栈和入口命令"""
    info = {
        "project_name": project_name,
        "project_dir": project_dir,
        "tech_stack": "<!-- TODO -->",
        "entry_cmd": "<!-- TODO -->",
    }

    files = os.listdir(project_dir)

    # 探测 package.json
    if "package.json" in files:
        try:
            with open(os.path.join(project_dir, "package.json"), "r", encoding="utf-8") as f:
                pkg = json.load(f)
            scripts = pkg.get("scripts", {})
            deps = list(pkg.get("dependencies", {}).keys()) + list(pkg.get("devDependencies", {}).keys())
            deps_lower = [d.lower() for d in deps]

            tech = []
            if any("react" in d for d in deps_lower): tech.append("React")
            if any("vue" in d for d in deps_lower): tech.append("Vue")
            if any("next" in d for d in deps_lower): tech.append("Next.js")
            if any("express" in d for d in deps_lower): tech.append("Express")
            if any("vite" in d for d in deps_lower): tech.append("Vite")
            if any("typescript" in d for d in deps_lower): tech.append("TypeScript")
            if any("electron" in d for d in deps_lower): tech.append("Electron")
            if not tech: tech.append("Node.js")

            info["tech_stack"] = " + ".join(tech[:3])

            if "dev" in scripts:
                info["entry_cmd"] = "npm run dev"
            elif "start" in scripts:
                info["entry_cmd"] = "npm start"
            elif "build" in scripts:
                info["entry_cmd"] = "npm run build"
        except Exception:
            pass

    # 探测 requirements.txt / setup.py
    elif "requirements.txt" in files or "setup.py" in files:
        info["tech_stack"] = "Python"
        if "docker-compose.yml" in files or "Dockerfile" in files:
            info["tech_stack"] += " + Docker"
        info["entry_cmd"] = "python main.py" if os.path.exists(os.path.join(project_dir, "main.py")) else "<!-- TODO -->"

    # 探测 go.mod
    if "go.mod" in files:
        info["tech_stack"] = "Go"
        info["entry_cmd"] = "go run ."

    # 探测 Docker
    if "docker-compose.yml" in files:
        info["entry_cmd"] = "docker compose up -d"
    elif "Dockerfile" in files:
        info["entry_cmd"] = "docker build -t " + project_name + " . && docker run " + project_name

    # 探测 Cargo.toml
    if "Cargo.toml" in files:
        info["tech_stack"] = "Rust"
        info["entry_cmd"] = "cargo run"

    return info


def render_template(template_name: str, variables: dict) -> str:
    """渲染模板，替换 {{VAR}} 占位符"""
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.isfile(template_path):
        return ""

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    for key, value in variables.items():
        content = content.replace("{{" + key + "}}", value)

    return content


def bootstrap_project(project_dir: str) -> dict:
    """为项目目录自举生成三件套"""
    project_name = os.path.basename(project_dir.rstrip("/\\"))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    info = detect_project_info(project_dir, project_name)
    variables = {
        "PROJECT_NAME": project_name,
        "PROJECT_DIR": project_dir,
        "TECH_STACK": info["tech_stack"],
        "ENTRY_CMD": info["entry_cmd"],
        "TIMESTAMP": now,
    }

    results = {}
    file_map = {
        "CLAUDE.md": "CLAUDE.md.template",
        "PROGRESS.md": "PROGRESS.md.template",
        "GATES.md": "GATES.md.template",
    }

    for target, template_name in file_map.items():
        target_path = os.path.join(project_dir, target)
        if not os.path.isfile(target_path):
            content = render_template(template_name, variables)
            if content:
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(content)
                results[target] = "created"
            else:
                results[target] = "template_missing"
        else:
            results[target] = "exists"

    return results


def main():
    """从 stdin 读取 hook 输入或命令行参数"""
    try:
        input_data = json.loads(sys.stdin.read())
        file_path = input_data.get("tool_input", {}).get("file_path", "")
    except Exception:
        file_path = sys.argv[1] if len(sys.argv) > 1 else ""

    if not file_path:
        print(json.dumps({"bootstrapped": False, "reason": "no file_path"}))
        return

    # 确定项目目录
    rel = os.path.relpath(file_path, WORKSPACE_ROOT)
    parts = rel.replace("\\", "/").split("/")
    project_name = parts[0] if parts[0] not in (".", "..") else None

    if project_name is None:
        print(json.dumps({"bootstrapped": False, "reason": "not in a project"}))
        return

    project_dir = os.path.join(WORKSPACE_ROOT, project_name)
    if not os.path.isdir(project_dir):
        print(json.dumps({"bootstrapped": False, "reason": "project_dir missing"}))
        return

    results = bootstrap_project(project_dir)
    created = [k for k, v in results.items() if v == "created"]

    if created:
        msg = f"[PROTOCOL] 🚀 项目 '{project_name}' 自举完成：已生成 {', '.join(created)}"
        print(json.dumps({"bootstrapped": True, "project": project_name,
                          "created": created, "results": results, "message": msg}))
        sys.stderr.write(msg + "\n")
    else:
        print(json.dumps({"bootstrapped": False, "project": project_name,
                          "reason": "all files exist"}))


if __name__ == "__main__":
    main()
