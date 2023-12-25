import tkinter as tk
from tkinter import scrolledtext

import numpy as np

entry = None
result_text = None

def text_to_binary(text):
    binary_result = ' '.join(format(ord(char), '08b') for char in text)
    return binary_result

def convert_text_to_binary():
    global entry, result_text
    input_text = entry.get(1.0, tk.END).strip()  # 获取整个文本框的内容
    binary_result = text_to_binary(input_text)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f'{binary_result}')

def int_to_bit(num):
    '''
    描述：把数字转化成八bit二进制
    参数：数字
    返回：二进制
    '''
    seq = []
    for i in range(8):
        seq.append((num >> (7 - i)) & 1)
    return seq

def encode_bluetooth_packet(args, binary_data):
    """
    描述：生成蓝牙包
    参数：全局参数，0-1序列
    返回：完整的蓝牙包(0-1序列)(包括分包)
    """
    packet_payload_len = 96 # 一个数据包payload长度（用于分包）
    packets_cnt = 0
    blank_len = 60 # 包和包之间的blank长度
    bluetooth_packets_seq = []
    encoded_seq = []

    for i in range(len(binary_data)):
        encoded_seq.append(int(binary_data[i]))
        if len(encoded_seq) >= packet_payload_len or i == len(binary_data) - 1:
            bluetooth_packets_seq += ([2] * blank_len)
            bluetooth_packets_seq += args.preamble # 加前导码
            bluetooth_packets_seq += (int_to_bit(len(encoded_seq))) # 加包头，编码数据包长度信息
            bluetooth_packets_seq += encoded_seq #                                      
            encoded_seq = []
            packets_cnt += 1
    bluetooth_packets_seq += ([2] * blank_len)
    return bluetooth_packets_seq


def generate_pulse(framerate, frequency, volume, start_place, duration):
    """
    描述：生成脉冲信号
    参数：帧率，频率，振幅，相位，时长
    返回：波形
    """
    n_frames = round(duration * framerate)
    x = np.linspace(0, duration, num=n_frames)
    y = np.sin(2 * np.pi * frequency * x + start_place) * volume
    return y


def modulation(args, bits):
    """
    描述：FSK调制算法
    参数：全局参数, 0-1比特信号（规定比特信号长度小于等于一个包的限制）
    返回：得到的波---numpy格式的一维数组
    """
    code0 = generate_pulse(args.framerate, args.frequency_0, args.volume, args.start_place, args.window_length)
    code1 = generate_pulse(args.framerate, args.frequency_1, args.volume, args.start_place, args.window_length)
    code2 = generate_pulse(args.framerate, 1, 0, args.start_place, args.window_length)
    code_len = len(code0)
    result_wave = np.zeros(shape=(code_len * len(bits)))
    start_index = 0
    for bit in bits:
        if bit == 2:  # for blank
            result_wave[start_index: start_index + code_len] = code2
        else:
            if bit == 0:
                result_wave[start_index: start_index + code_len] = code0
            else:
                result_wave[start_index: start_index + code_len] = code1
        start_index += code_len
    return result_wave


def send_binary_data(args):
    global result_text
    # 直接从文本框里获取的binary_data,去除空格
    binary_data = result_text.get(1.0, tk.END).replace(" ", "").strip()
    print(f'binary data: {binary_data}')
    # 加上蓝牙包，变成完整的binary_data
    blue_tooth_binary_data = encode_bluetooth_packet(args, binary_data)
    print(f'blue tooth binary data: {blue_tooth_binary_data}')
    # FSK
    fsk_data = modulation(args, blue_tooth_binary_data)
    print(f'fsk data: {fsk_data}')


def init_ui(args):
    # 创建主窗口
    window = tk.Tk()
    window.title('Text to Binary Converter')

    # 设置窗口大小和位置
    window.geometry('800x600')
    window.resizable(True, True)  # 允许调整窗口大小

    global entry, result_text

    # 创建标签、文本框和按钮
    label = tk.Label(window, text='Enter text:', font=('Arial', 14))
    label.pack(pady=10)

    entry = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=40, height=3, font=('Arial', 12))
    entry.pack(pady=10)

    convert_button = tk.Button(window, text='Convert', command=convert_text_to_binary, font=('Arial', 12))
    convert_button.pack(pady=10)

    result_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=40, height=5, font=('Arial', 12))
    result_text.pack(pady=10)

    send_button = tk.Button(window, text='Send', command=lambda:send_binary_data(args), font=('Arial', 12))
    send_button.pack(pady=10)

    # 启动主循环
    window.mainloop()


def init_args():
    """
    描述：加载全局设置---窗口长度，0和1对应的频率，采样频率振幅等其他参数
    参数：无
    返回：args变量，对应全局设置
    """
    import argparse
    parser = argparse.ArgumentParser(description="Choose the parameters")

    # 0和1的频率
    parser.add_argument("--frequency_0", type=int, default=4000)
    parser.add_argument("--frequency_1", type=int, default=6000)

    # 采样频率，振幅，宽度等通用设置
    parser.add_argument("--framerate", type=int, default=48000)
    parser.add_argument("--sample_width", type=int, default=2)
    parser.add_argument("--nchannels", type=int, default=1)
    parser.add_argument("--volume", type=float, default=20000.0)
    parser.add_argument("--start_place", type=int, default=0)

    # 单个窗口的长度(单位秒)
    parser.add_argument("--window_length", type=float, default=2.5e-2)

    # 一个包最长长度(多少个比特)
    parser.add_argument("--packet_length", type=int, default=1000)

    # # 保存和接收的文件夹名称
    # parser.add_argument("--save_base_send", type=str, default='send')
    # parser.add_argument("--save_base_receive", type=str, default='receive')
    # parser.add_argument("--original_place", type=str, default='content.csv')
    # parser.add_argument("--result_place", type=str, default='result.csv')

    # 包长度是几个bit
    parser.add_argument("--packet_head_length", type=int, default=8)

    # #beep-beep
    # parser.add_argument("--sound_velocity", type=int, default=343)
    # parser.add_argument("--server_url", type=str, default="http://localhost:5000/distance/<side>")
    # parser.add_argument("--side", type=str, default="a")
    # parser.add_argument("--delay_a", type=int, default=1)
    # parser.add_argument("--delay_b", type=int, default=3)
    # parser.add_argument("--record_len", type=int, default=5)
    # parser.add_argument("--beep_wave", type=str, default="distance/beep.wav")
    # parser.add_argument("--beep_beep", type=bool, default=False)

    # #测不测试（是否显示图啥的）
    # parser.add_argument("--test", type = int, default = 0)
    
    args = parser.parse_args()

    # 前导码
    args.preamble = [0, 1] * 10

    # # 解码用
    # args.threshold = 2e11
    return args

if __name__ == '__main__':
    args = init_args()
    print(f'args:{args}')
    init_ui(args)

