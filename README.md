# Mobile Control Skill

🎮 高性能手机自动化操控技能 - 基于 Airtest + OpenCV + OpenClaw

## ✨ 特性

- 🚀 **高性能**：多线程流水线架构，支持 15+ FPS 实时决策
- 🎯 **精准识别**：图像预处理 + 置信度过滤
- 🔧 **易扩展**：模块化设计，轻松集成自定义 OpenClaw 算法
- 📱 **广泛兼容**：支持 Android 5.0+, USB/WiFi 连接

## 📦 安装

```bash
# 下载技能包
wget https://github.com/okyody/mobile_control_skill/releases/download/v1.0.0/mobile_control_skill-1.0.0.zip

# 解压到 OpenClaw skills 目录
unzip mobile_control_skill-1.0.0.zip -d /path/to/openclaw/skills/

🚀 使用
from mobile_control_skill.skill_main import MobileControlSkill

skill = MobileControlSkill()
skill.on_init({"device": {"device_uri": "Android:///"}})
skill.on_start()

##⚙️ 配置
performance:
  target_fps: 15
  screen_width: 720
  action_cooldown: 0.1
  confidence_threshold: 0.85

##📊 性能指标
指标	             数值
决策延迟	   <       100ms
截图       FPS	   15-30
识别准确率	 >       95%

##📝 许可证
MIT License


