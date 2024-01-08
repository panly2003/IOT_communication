import scipy.io.wavfile as wav
from fsk import demodulate
from utils import binary_list_to_unicode
from tkinter import messagebox

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
SAVE_PATH = './audio/receiver_audio.wav'  # 保存路径

if __name__ == "__main__":
    fs, wave = wav.read(SAVE_PATH)
    decoded_result = demodulate(SAMPLING_RATE, LOW_FREQUENCY, HIGH_FREQUENCY, DURATION, PREAMBLE_CODE, wave)

    # 连接解码结果
    decoded_payload_bits = []
    for item in decoded_result:
        payload, start = item[0], item[1]
        decoded_payload_bits.extend(payload)
    
    decoded_str = binary_list_to_unicode(decoded_payload_bits)
    print(f'解码字符串: {decoded_str}')

    # 弹出框显示文本
    messagebox.showinfo("解码文本", decoded_str)
