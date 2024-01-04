import numpy as np
import scipy.io.wavfile as wav
from utils import bit_to_int


def generate_pulse(sampling_rate, frequency, amplitude, start_phase, duration):
    num_frames = int(duration * sampling_rate)
    time_values = np.linspace(0, duration, num=num_frames)
    pulse = np.sin(2 * np.pi * frequency * time_values + start_phase) * amplitude
    return pulse


def modulate_signal(sampling_rate, frequency_0, frequency_1, amplitude, start_phase, duration, bits):
    pulse_0 = generate_pulse(sampling_rate, frequency_0, amplitude, start_phase, duration)
    pulse_1 = generate_pulse(sampling_rate, frequency_1, amplitude, start_phase, duration)
    blank_pulse = generate_pulse(sampling_rate, 1, 0, start_phase, duration)
    pulse_len = len(pulse_0)
    
    result_wave = np.zeros(shape=(pulse_len * len(bits)))
    start_index = 0
    
    for bit in bits:
        if bit == 2:  # for blank
            result_wave[start_index: start_index + pulse_len] = blank_pulse
        else:
            if bit == 0:
                result_wave[start_index: start_index + pulse_len] = pulse_0
            else:
                result_wave[start_index: start_index + pulse_len] = pulse_1
        start_index += pulse_len
    
    return result_wave


# def calculate_correlates(sampling_rate, frequency_0, frequency_1, amplitude, start_phase, duration, preamble, wave):
#     preamble_sequence = modulate_signal(sampling_rate, frequency_0, frequency_1, amplitude, start_phase, duration, bits=preamble)
#     wave_length = len(wave)
#     preamble_length = len(preamble_sequence)
#     start = 0
#     correlates = []
    
#     while start + preamble_length <= wave_length:
#         current_wave_segment = wave[start: start + preamble_length]
#         correlate = np.dot(current_wave_segment, preamble_sequence)
#         correlates.append(correlate)
#         start += 1
    
#     return correlates

# def find_start_position(sampling_rate, duration, preamble, threshold, start, correlates):
#     real_wave_start_position = -1
#     one_bit_length = sampling_rate * duration
#     length_preamble = int(len(preamble) * one_bit_length)
    
#     for i in range(len(correlates) - start):
#         if abs(correlates[i + start]) >= threshold and real_wave_start_position == -1:
#             real_wave_start_position = i + start
#             break
    
#     if real_wave_start_position == -1:
#         return -1
    
#     position = real_wave_start_position + np.argmax(correlates[real_wave_start_position:real_wave_start_position + length_preamble])
#     return position


def demodulate_one(sampling_rate, frequency_0, frequency_1, wave):
    fourier_result = np.abs(np.fft.fft(wave))
    length = len(fourier_result)
    fourier_result = fourier_result[0: length // 2]
    max_place = np.argmax(fourier_result)
    max_freq = round(max_place / length * sampling_rate)
    dist_0 = abs(max_freq - frequency_0)
    dist_1 = abs(max_freq - frequency_1)
    if dist_0 < dist_1:
        return 0
    else:
        return 1
    

def demodulate_packet(sampling_rate, frequency_0, frequency_1, duration, wave):
    one_bit_length = int(sampling_rate * duration)
    length = len(wave)
    start = 0
    result = []
    while start + one_bit_length <= length:
        sub_wave = wave[start: start + one_bit_length]
        the_bit = demodulate_one(sampling_rate, frequency_0, frequency_1, sub_wave)
        result.append(the_bit)
        start += one_bit_length
    return result


def corr_num(list1, list2):
    corr_num = 0
    for i in range(len(list1)):
        if list1[i] == list2[i]:
            corr_num += 1
    return corr_num / len(list1)


def demodulate_signal(sampling_rate, frequency_0, frequency_1, amplitude, start_phase, duration, preamble, threshold, wave):
    packet_results = []
    whole_result = demodulate_packet(sampling_rate, frequency_0, frequency_1, duration, wave)
    print(whole_result)
    # 找前导码位置
    i = 0
    while i <= len(whole_result) - len(preamble):
        if corr_num(whole_result[i:i+len(preamble)],preamble) >= 0.7:
            start_place = i
            # print(start_place)
            corr_fragments = [corr_num(whole_result[start_place + j: start_place + j + len(preamble)], preamble) for j in range(len(preamble))]     
            real_start_place = start_place + np.argmax(corr_fragments)
            print(real_start_place)
            # 计算payload长度
            payload_length = bit_to_int(whole_result[real_start_place+len(preamble):real_start_place+len(preamble)+8])
            # 计算payload
            payload = whole_result[real_start_place+len(preamble)+8:real_start_place+len(preamble)+8+payload_length]
            print(payload)
            packet_results.append((payload, real_start_place))
            i = real_start_place + len(preamble) + 8 + payload_length
            # print(i)
        else:
            i += 1
    
    return packet_results


if __name__ == '__main__':
    # Test FSK
    payload_bits = [0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 
                    0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 
                    1, 1, 0, 1, 1, 0, 0, 1, 0, 0]
    bits_for_modulation = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
                           2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
                           2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
                           2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
                           2, 2, 2, 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 
                           0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 
                           0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 
                           1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 
                           0, 1, 1, 0, 0, 1, 0, 0, 2, 2, 2, 2, 2, 2, 
                           2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
                           2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
                           2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
                           2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    # Modulation
    encoded_wave = modulate_signal(sampling_rate=48000, frequency_0=4000, frequency_1=6000, amplitude=20000.0, start_phase=0, duration=2.5e-2, bits=bits_for_modulation)
    # Save
    wav.write('./fsk_test/res.wav', 48000, encoded_wave.astype(np.int16))
    # Load
    fs, decoded_wave = wav.read('./fsk_test/res.wav')
    # Demodulation
    decoded_result = demodulate_signal(sampling_rate=48000, frequency_0=4000, frequency_1=6000, amplitude=20000.0, start_phase=0, duration=2.5e-2, preamble=[0,1]*10, threshold=2e11, wave=decoded_wave)
    print(f'decoded_result: {decoded_result}')
    
    # Concatenate decoded results
    decoded_payload_bits = []
    for item in decoded_result:
        payload, start = item[0], item[1]
        decoded_payload_bits += payload

    # Calculate bit accuracy
    corr_bit_num = 0
    for i in range(len(payload_bits)):
        if payload_bits[i] == decoded_payload_bits[i]:
            corr_bit_num += 1
    bit_accuracy = corr_bit_num / len(payload_bits)
    print(f'bit accuracy: {bit_accuracy * 100}%')
    
