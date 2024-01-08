import numpy as np
from utils import bit_to_int 


def generate_pulse(sampling_rate, frequency, a, start_phase, duration):
    # 计算帧数
    num_frames = int(duration * sampling_rate)
    # 生成时间值
    time_values = np.linspace(0, duration, num=num_frames)
    # 生成脉冲信号
    pulse = np.sin(2 * np.pi * frequency * time_values + start_phase) * a
    return pulse


def modulate(sampling_rate, low_frequency, high_frequency, a, start_phase, duration, bits):
    # 生成不同比特的脉冲信号
    pulse_0 = generate_pulse(sampling_rate, low_frequency, a, start_phase, duration)
    pulse_1 = generate_pulse(sampling_rate, high_frequency, a, start_phase, duration)
    pulse_3 = generate_pulse(sampling_rate, 12000, a, start_phase, duration)
    blank_pulse = generate_pulse(sampling_rate, 0, 0, start_phase, duration)
    pulse_len = len(pulse_0)
    
    result_wave = np.zeros(shape=(pulse_len * len(bits)))
    start_index = 0
    
    for bit in bits:
        if bit == 2:  # 对应空白位
            result_wave[start_index: start_index + pulse_len] = blank_pulse
        if bit == 3:  # 对应脉冲3
            result_wave[start_index: start_index + pulse_len] = pulse_3
        if bit == 0:  # 对应脉冲0
            result_wave[start_index: start_index + pulse_len] = pulse_0
        if bit == 1:  # 对应脉冲1
            result_wave[start_index: start_index + pulse_len] = pulse_1
        start_index += pulse_len
    
    return result_wave


def demodulate_one_bit(sampling_rate, low_frequency, high_frequency, wave):
    # 傅里叶变换得到频谱
    fourier_result = np.abs(np.fft.fft(wave))
    length = len(fourier_result)
    fourier_result = fourier_result[0: length // 2]
    max_place = np.argmax(fourier_result)
    max_freq = round(max_place / length * sampling_rate)
    dist_0 = abs(max_freq - low_frequency)
    dist_2 = abs(max_freq - 0)
    dist_1 = abs(max_freq - high_frequency)
    dist_3 = abs(max_freq - 12000)
    l = [dist_0, dist_1, dist_2, dist_3]
    return np.argmin(l)


def corr_num(list1, list2):
    # 计算两个列表相同元素的数量比例
    corr_num = 0
    for i in range(len(list1)):
        if list1[i] == list2[i]:
            corr_num += 1
    return corr_num / len(list1)


def demodulate(sampling_rate, low_frequency, high_frequency, duration, preamble_code, wave):
    # 解调
    one_bit_length = int(sampling_rate * duration)
    length = len(wave)
    start = 0
    whole_result = []
    while start + one_bit_length <= length:
        sub_wave = wave[start: start + one_bit_length]
        the_bit = demodulate_one_bit(sampling_rate, low_frequency, high_frequency, sub_wave)
        whole_result.append(the_bit)
        start += one_bit_length

    print(whole_result)

    packet_results = []

    # 找前导码位置 + 解调
    i = 0
    s = 0
    while i <= len(whole_result) - len(preamble_code):
        if corr_num(whole_result[i:i+len(preamble_code)], preamble_code) >= 0.7:
            s += 1
            start_place = i
            # print(start_place)
            corr_fragments = [corr_num(whole_result[start_place + j: start_place + j + len(preamble_code)], preamble_code) for j in range(len(preamble_code))]     
            real_start_place = start_place + np.argmax(corr_fragments)
            while whole_result[real_start_place+len(preamble_code)] == 3:
                real_start_place += 1
            # print(real_start_place)
                
            # 计算payload长度
            payload_length = bit_to_int(whole_result[real_start_place+len(preamble_code):real_start_place+len(preamble_code)+8])
            
            # 计算payload
            payload = whole_result[real_start_place+len(preamble_code)+8:real_start_place+len(preamble_code)+8+payload_length]
            packet_results.append((payload, real_start_place))
            i = real_start_place + len(preamble_code) + 8 + payload_length
            
        else:
            i += 1
    
    return packet_results
