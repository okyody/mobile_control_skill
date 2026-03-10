cat > skill_main.py << 'EOF'
import cv2
import numpy as np
import threading
import queue
import time
import logging
from typing import Optional, Dict, Any

from airtest.core.api import connect_device, device, touch, swipe, sleep

logger = logging.getLogger(__name__)

class Config:
    SCREEN_CAPTURE_WIDTH = 720
    TARGET_FPS = 15
    ACTION_COOLDOWN = 0.1
    CONFIDENCE_THRESHOLD = 0.85
    ENABLE_PREPROCESS = True

class OpenClawEngine:
    def decide(self, frame, resolution):
        return None

class MobileControlSkill:
    def __init__(self):
        self.config = {}
        self.air_device = None
        self.openclaw = OpenClawEngine()
        self.is_running = False
        self.threads = []
        self.frame_queue = queue.Queue(maxsize=1)
        self.action_queue = queue.Queue(maxsize=5)
        self.scale_ratio = 1.0
        self.original_resolution = (1080, 2400)
        self.last_action_time = 0
        self.last_action_hash = ""

    def on_init(self, config):
        self.config = config
        logger.info(f"技能初始化：{self.config}")
        if "performance" in config:
            Config.TARGET_FPS = config["performance"].get("target_fps", 15)
            Config.SCREEN_CAPTURE_WIDTH = config["performance"].get("screen_width", 720)

    def on_start(self):
        logger.info("技能启动中...")
        try:
            uri = self.config.get("device", {}).get("device_uri", "Android:///")
            connect_device(uri)
            self.air_device = device
            self.air_device.settings["use_minicap"] = True
            self.original_resolution = self.air_device.get_resolution()
            w, h = self.original_resolution
            self.scale_ratio = w / Config.SCREEN_CAPTURE_WIDTH
            logger.info(f"设备连接成功：{self.original_resolution}")
            self.is_running = True
            self._start_threads()
        except Exception as e:
            logger.error(f"启动失败：{e}")
            raise

    def on_stop(self):
        logger.info("技能停止中...")
        self.is_running = False
        for t in self.threads:
            t.join()
        logger.info("技能已停止")

    def on_run(self):
        pass

    def _start_threads(self):
        self.threads = [
            threading.Thread(target=self._capture_loop, name="Capture"),
            threading.Thread(target=self._decision_loop, name="Decision"),
            threading.Thread(target=self._execute_loop, name="Executor")
        ]
        for t in self.threads:
            t.daemon = True
            t.start()

    def _preprocess_image(self, img):
        if not Config.ENABLE_PREPROCESS:
            return img
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        enhanced = cv2.equalizeHist(gray)
        return cv2.GaussianBlur(enhanced, (3, 3), 0)

    def _capture_loop(self):
        while self.is_running:
            try:
                start = time.perf_counter()
                pil_img = self.air_device.snapshot(max_size=Config.SCREEN_CAPTURE_WIDTH)
                if pil_img:
                    img_np = np.array(pil_img)
                    processed_img = self._preprocess_image(img_np)
                    if self.frame_queue.full():
                        try:
                            self.frame_queue.get_nowait()
                        except queue.Empty:
                            pass
                    self.frame_queue.put((processed_img, time.time()))
                elapsed = time.perf_counter() - start
                sleep_time = (1.0 / Config.TARGET_FPS) - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
            except Exception as e:
                logger.error(f"捕捉错误：{e}")
                time.sleep(1)

    def _decision_loop(self):
        while self.is_running:
            try:
                frame, capture_time = self.frame_queue.get()
                if time.time() - capture_time > 0.5:
                    continue
                action = self.openclaw.decide(frame, self.original_resolution)
                if action:
                    if "x" in action and "y" in action:
                        action["x"] = int(action["x"] * self.scale_ratio)
                        action["y"] = int(action["y"] * self.scale_ratio)
                    if not self.action_queue.full():
                        self.action_queue.put(action)
            except Exception as e:
                logger.error(f"决策错误：{e}")

    def _execute_loop(self):
        while self.is_running:
            try:
                if not self.action_queue.empty():
                    action = self.action_queue.get()
                    current_time = time.time()
                    action_hash = str(action)
                    if current_time - self.last_action_time < Config.ACTION_COOLDOWN:
                        if action_hash == self.last_action_hash:
                            continue
                    self._perform_action(action)
                    self.last_action_time = current_time
                    self.last_action_hash = action_hash
            except Exception as e:
                logger.error(f"执行错误：{e}")

    def _perform_action(self, action):
        act_type = action.get("action")
        try:
            if act_type == "click":
                touch((action["x"], action["y"]))
            elif act_type == "swipe":
                swipe((action["x1"], action["y1"]), (action["x2"], action["y2"]), duration=action.get("duration", 0.2))
            elif act_type == "keyevent":
                self.air_device.keyevent(action["key"])
        except Exception as e:
            logger.error(f"动作失败：{e}")
EOF
