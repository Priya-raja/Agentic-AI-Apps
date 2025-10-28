import pyautogui
import time
import subprocess

subprocess.run(['open', '-a', 'Keynote'])
time.sleep(3)
pyautogui.hotkey('command', 'n')
time.sleep(2)
pyautogui.press('return')
time.sleep(2)

print("Testing Insert menu click...")
pyautogui.click(603, 355)
time.sleep(1)

print("Did the Insert menu open? (y/n)")