from tkinter import scrolledtext
import tkinter as tk
from utils import int_to_bit, text_to_code
import numpy as np
import wave
from fsk import modulate

# 定义一些常量
PAYLOAD_LENGTH = 192  # 数据包负载长度
BLANK_LENGTH = 30  # 空白区长度
PREAMBLE_CODE = [3]*10  # 前导码
LOW_FREQUENCY = 1000  # 低频信号频率
HIGH_FREQUENCY = 6000  # 高频信号频率
SAMPLING_RATE = 44100  # 采样率
A = 20000.0  # 振幅
START_PHASE = 0.0  # 初始相位
DURATION = 5e-2  # 信号持续时间
SAVE_PATH = './audio/sender_audio.wav'  # 保存路径

entry = None
input_text = None
original_code = None

def add_bluetooth_code(binary_data):
    bluetooth_code = []
    packet_payload = []
    for i in range(len(binary_data)):
        packet_payload.append(int(binary_data[i]))
        if len(packet_payload) >= PAYLOAD_LENGTH or i == len(binary_data) - 1:
            bluetooth_code += ([2] * BLANK_LENGTH)  # 添加空白区
            bluetooth_code += PREAMBLE_CODE  # 添加前导码
            bluetooth_code += (int_to_bit(len(packet_payload)))  # 添加8位头部，编码数据包长度信息
            bluetooth_code += packet_payload  # 添加数据内容段
            packet_payload = []
    bluetooth_code += ([2] * BLANK_LENGTH)
    return bluetooth_code

def send_binary_data():
    global entry
    # 直接从文本框获取二进制数据，去除空格
    input_text = entry.get(1.0, tk.END).strip()  # 获取文本框的全部内容
    original_code = text_to_code(input_text)
    original_code = original_code.replace(' ','')
    bluetooth_code = add_bluetooth_code(original_code)

    # FSK调制
    fsk_data = modulate(SAMPLING_RATE, LOW_FREQUENCY, HIGH_FREQUENCY, A, START_PHASE, DURATION, bluetooth_code)

    # 保存
    wf = wave.open(SAVE_PATH, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLING_RATE)
    wf.writeframes(fsk_data.astype(np.int16).tobytes())
    wf.close()

    # 完成
    print('完成')

def init_ui():
    # 创建主窗口
    window = tk.Tk()
    window.title('UI')

    # 设置窗口大小和位置
    window.geometry('800x600')
    window.resizable(True, True)  # 允许窗口调整大小

    global entry, result_text

    # 创建标签、文本框和按钮
    label = tk.Label(window, text='输入文本:', font=('Arial', 14))
    label.pack(pady=10)

    entry = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=40, height=3, font=('Arial', 12))
    entry.pack(pady=10)

    send_button = tk.Button(window, text='转换成音频', command=lambda: send_binary_data(), font=('Arial', 12))
    send_button.pack(pady=10)

    # 启动主循环
    window.mainloop()

if __name__ == '__main__':
    init_ui()
