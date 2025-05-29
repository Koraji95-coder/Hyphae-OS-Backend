import os
import subprocess
from datetime import datetime
from pathlib import Path
import json

ROOTS = {
    "os": Path("shared/meta/version.py"),
    "ui": Path("hyphaeos-ui/src/version.js"),
    "npm": Path("hyphaeos-ui/package.json")
}
CHANGELOG = Path("CHANGELOG.md")
TASKS_FILE = Path(".vscode/tasks.json")

def prompt_project():
    print("🔧 Which project are you bumping?")
    print("1 = HyphaeOS")
    print("2 = HyphaeOS-UI")
    print("3 = Both")
    choice = input("Choice (1, 2, or 3): ").strip()
    if choice == "1":
        return ["os"]
    elif choice == "2":
        return ["ui"]
    elif choice == "3":
        return ["os", "ui"]
    else:
        raise ValueError("❌ Invalid project choice.")

def get_current_version(file: Path) -> str:
    if not file.exists():
        if file.name.endswith(".js"):
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text('export const version = "0.0.0";\n', encoding="utf-8")
            return "0.0.0"
        else:
            raise FileNotFoundError(f"Missing version file: {file}")
    text = file.read_text(encoding="utf-8")
    if file.name.endswith(".py"):
        return next(line.split("=")[1].strip().strip('"') for line in text.splitlines() if "__version__" in line)
    elif file.name.endswith(".js"):
        return text.split('"')[1]
    raise ValueError("Unknown version format")

def bump_version(ver: str, level: str) -> str:
    major, minor, patch = map(int, ver.split("."))
    if level == "patch":
        patch += 1
    elif level == "minor":
        minor += 1
        patch = 0
    elif level == "major":
        major += 1
        minor = patch = 0
    return f"{major}.{minor}.{patch}"

def update_version_file(file: Path, version: str):
    if file.name.endswith(".py"):
        file.write_text(f'__version__ = "{version}"\n', encoding="utf-8")
    elif file.name.endswith(".js"):
        file.write_text(f'export const version = "{version}";\n', encoding="utf-8")

def get_git_changes():
    untracked = subprocess.getoutput("git ls-files --others --exclude-standard").splitlines()
    modified = subprocess.getoutput("git diff --name-only").splitlines()
    return untracked, modified

def update_changelog(version: str, title: str, untracked, modified):
    now = datetime.now().strftime("%Y-%m-%d")
    header = f"## 🚀 v{version} – {title} ({now})\n\n"
    body = "### 🆕 New Files\n" + "\n".join(f"- {f}" for f in untracked or ["(None)"])
    body += "\n\n### 🔧 Modified Files\n" + "\n".join(f"- {f}" for f in modified or ["(None)"])
    body += "\n\n---\n"

    existing = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else ""
    CHANGELOG.write_text(header + body + existing, encoding="utf-8")

def update_tasks_version(new_ver: str):
    if not TASKS_FILE.exists():
        return
    content = TASKS_FILE.read_text(encoding="utf-8").splitlines()
    updated = []
    for line in content:
        if '"hyphaeos_version":' in line:
            updated.append(f'  "hyphaeos_version": "v{new_ver}",  // 🔄 DO NOT REMOVE – gets auto-updated by version_bump.py')
        else:
            updated.append(line)
    TASKS_FILE.write_text("\n".join(updated), encoding="utf-8")

def update_tasks_json(version: str):
    if not TASKS_FILE.exists():
        print("⚠️ tasks.json not found — skipping update.")
        return
    try:
        tasks = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
        for task in tasks.get("tasks", []):
            detail = task.get("detail", "")
            base = detail.split(" [v")[0]
            task["detail"] = f"{base} [v{version}]"
        TASKS_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
        print("✅ tasks.json updated with new version tag.")
    except Exception as e:
        print(f"❌ Failed to update tasks.json: {e}")

def run_git(version: str, title: str):
    subprocess.run("git add .", shell=True)
    subprocess.run(f'git commit -m "🚀 v{version} – {title}"', shell=True)
    subprocess.run(f"git tag v{version}", shell=True)
    subprocess.run("git push origin main", shell=True)
    subprocess.run(f"git push origin v{version}", shell=True)

def run():
    print("🛠️  Version Bumper")
    targets = prompt_project()

    # Use first target as the source of truth for current version
    base_version = get_current_version(ROOTS[targets[0]])
    print(f"📦 Current version: {base_version}")

    level = input("Bump level (patch / minor / major)? ").strip().lower()
    title = input("📋 What's the changelog title?: ").strip()
    new_ver = bump_version(base_version, level)

    # Update all version files
    for target in targets:
        update_version_file(ROOTS[target], new_ver)

    update_tasks_version(new_ver)
    update_tasks_json(new_ver)

    untracked, modified = get_git_changes()
    update_changelog(new_ver, title, untracked, modified)
    run_git(new_ver, title)

    print(f"\n✅ Project bumped to v{new_ver} and pushed to GitHub.")
    
def update_package_json_version(version: str, file: Path):
    content = json.loads(file.read_text(encoding="utf-8"))
    content['version'] = version
    file.write_text(json.dumps(content, indent=2), encoding="utf-8")

if __name__ == "__main__":
    run()