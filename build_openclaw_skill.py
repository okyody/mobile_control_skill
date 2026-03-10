cat > build_openclaw_skill.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenClaw Skill 构建与打包脚本"""

import os
import sys
import zipfile
import tarfile
import json
import shutil

SKILL_ID = "mobile_control_skill"
VERSION = "1.0.0"

MANIFEST = {
    "id": SKILL_ID,
    "name": "Mobile Control Skill",
    "version": VERSION,
    "description": "高性能手机自动化操控技能",
    "author": "Your Name",
    "type": "automation",
    "platform": "openclaw",
    "entry_point": "skill_main:MobileControlSkill",
    "requirements": ["airtest-python>=1.1.30", "opencv-python>=4.8.0", "numpy>=1.24.0"],
    "permissions": ["device_control", "screen_capture", "network_access"],
    "enabled": True
}

CONFIG = """device:
  connection_type: "usb"
  device_uri: "Android:///"
  use_minicap: true

performance:
  target_fps: 15
  screen_width: 720
  action_cooldown: 0.1
  confidence_threshold: 0.85

openclaw:
  heartbeat_interval: 5
  log_level: "INFO"
"""

REQUIREMENTS = """airtest-python>=1.1.30
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
"""

README = """# Mobile Control Skill

高性能手机自动化操控技能 (Airtest + OpenCV)

## 安装
将 zip/tar.gz 包放入 OpenClaw 的 skills/ 目录

## 配置
编辑 config.yaml 调整设备连接和性能参数
"""

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(content, dict):
            json.dump(content, f, indent=2, ensure_ascii=False)
        else:
            f.write(content)
    print(f"  OK: {path}")

def build():
    print(f"Building {SKILL_ID}...")
    
    if os.path.exists("skill_main.py"):
        shutil.copy("skill_main.py", f"{SKILL_ID}/skill_main.py")
        print(f"  OK: {SKILL_ID}/skill_main.py")
    else:
        print("  ERROR: skill_main.py not found!")
        sys.exit(1)
    
    write_file(f"{SKILL_ID}/manifest.json", MANIFEST)
    write_file(f"{SKILL_ID}/config.yaml", CONFIG)
    write_file(f"{SKILL_ID}/requirements.txt", REQUIREMENTS)
    write_file(f"{SKILL_ID}/README.md", README)
    write_file(f"{SKILL_ID}/__init__.py", "")

def pack():
    zip_name = f"{SKILL_ID}-{VERSION}.zip"
    tar_name = f"{SKILL_ID}-{VERSION}.tar.gz"
    
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(SKILL_ID):
            for f in files:
                if not f.endswith((".pyc", ".log")):
                    z.write(os.path.join(root, f))
    print(f"  OK: {zip_name}")
    
    with tarfile.open(tar_name, "w:gz") as t:
        for root, dirs, files in os.walk(SKILL_ID):
            for f in files:
                if not f.endswith((".pyc", ".log")):
                    t.add(os.path.join(root, f))
    print(f"  OK: {tar_name}")

if __name__ == "__main__":
    os.makedirs(SKILL_ID, exist_ok=True)
    build()
    pack()
    print("Done!")
EOF
