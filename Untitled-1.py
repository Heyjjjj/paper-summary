import cv2
import numpy as np
import pyautogui
import time
import threading
from collections import deque
import pytesseract
from PIL import Image

class GameAutomation:
    def __init__(self):
        self.player_name = "你的角色名"  # 设置你的角色名
        self.npc_queue = deque()  # 存储NPC顺序
        self.current_round = 0
        self.max_rounds = 15
        self.is_preview_active = False
        self.dodge_duration = 0.3
        
    def capture_screen_region(self, x, y, width, height):
        """截取屏幕指定区域"""
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def extract_npc_names(self, image):
        """从左侧区域提取NPC名称"""
        # 预处理图像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 根据你描述的颜色进行颜色过滤
        # 这里需要根据实际游戏调整HSV范围
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # 假设NPC名称是白色或特定颜色，需要根据实际调整
        mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))
        
        # OCR识别文字
        text = pytesseract.image_to_string(
            Image.fromarray(mask), 
            config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        )
        
        # 清理并返回识别到的名称
        names = [name.strip() for name in text.split('\n') if name.strip()]
        return names
    
    def detect_round_indicator(self, image):
        """检测"第n界"提示，判断预告是否结束"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(Image.fromarray(gray), lang='chi_sim')
        
        # 检测是否有"第"和"界"字样
        if "第" in text and "界" in text:
            # 提取轮数
            import re
            match = re.search(r'第(\d+)界', text)
            if match:
                return int(match.group(1))
        return None
    
    def monitor_npc_queue(self):
        """监控左侧NPC队列"""
        # 定义左侧NPC显示区域坐标（需要根据实际游戏调整）
        npc_region = (200, 400, 350, 400)  # x, y, width, height
        
        previous_names = set()
        
        while self.current_round < self.max_rounds:
            try:
                # 截取NPC区域
                npc_image = self.capture_screen_region(*npc_region)
                current_names = self.extract_npc_names(npc_image)
                
                # 检测新出现的NPC
                for name in current_names:
                    if name not in previous_names and name not in self.npc_queue:
                        self.npc_queue.append(name)
                        print(f"检测到NPC: {name}")
                
                previous_names = set(current_names)
                time.sleep(0.1)  # 每100ms检查一次
                
            except Exception as e:
                print(f"NPC监控错误: {e}")
                time.sleep(0.1)
    
    def monitor_round_status(self):
        """监控轮次状态"""
        # 定义轮次提示区域坐标（需要根据实际游戏调整）
        round_region = (400, 50, 400, 100)  # x, y, width, height
        
        while self.current_round < self.max_rounds:
            try:
                # 截取轮次区域
                round_image = self.capture_screen_region(*round_region)
                round_num = self.detect_round_indicator(round_image)
                
                if round_num and round_num != self.current_round:
                    self.current_round = round_num
                    self.is_preview_active = False
                    print(f"检测到第{round_num}轮开始")
                    
                    # 开始计算闪避时机
                    self.calculate_dodge_timing()
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"轮次监控错误: {e}")
                time.sleep(0.1)
    
    def calculate_dodge_timing(self):
        """计算闪避时机"""
        if self.player_name not in self.npc_queue:
            print("未在队列中找到玩家名称")
            return
        
        # 找到玩家在队列中的位置
        player_position = list(self.npc_queue).index(self.player_name)
        
        # 计算闪避时间：1秒预告结束延迟 + 每个角色0.2秒 * 位置
        dodge_delay = 1.0 + (player_position * 0.2)
        
        print(f"玩家位置: {player_position + 1}, 将在{dodge_delay}秒后闪避")
        
        # 设置闪避定时器
        threading.Timer(dodge_delay - 0.1, self.execute_dodge).start()  # 提前0.1秒执行
    
    def execute_dodge(self):
        """执行闪避操作"""
        print("开始闪避!")
        
        # 同时按下Q和W键
        pyautogui.keyDown('q')
        pyautogui.keyDown('w')
        
        # 持续0.3秒
        time.sleep(self.dodge_duration)
        
        # 释放按键
        pyautogui.keyUp('q')
        pyautogui.keyUp('w')
        
        print("闪避结束")
    
    def start_automation(self):
        """启动自动化脚本"""
        print("游戏自动化脚本启动...")
        
        # 启动监控线程
        npc_thread = threading.Thread(target=self.monitor_npc_queue)
        round_thread = threading.Thread(target=self.monitor_round_status)
        
        npc_thread.daemon = True
        round_thread.daemon = True
        
        npc_thread.start()
        round_thread.start()
        
        try:
            # 保持主线程运行
            while self.current_round < self.max_rounds:
                time.sleep(1)
        except KeyboardInterrupt:
            print("脚本已停止")

# 使用示例
if __name__ == "__main__":
    # 安装所需库：pip install opencv-python pyautogui pytesseract pillow
    
    automation = GameAutomation()
    automation.player_name = "输入你的角色名"  # 设置你的角色名称
    
    print("5秒后开始运行脚本...")
    time.sleep(5)
    
    automation.start_automation()