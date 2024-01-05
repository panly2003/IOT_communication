import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wav


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


def calculate_correlates(sampling_rate, frequency_0, frequency_1, amplitude, start_phase, duration, preamble, wave):
    preamble_sequence = modulate_signal(sampling_rate, frequency_0, frequency_1, amplitude, start_phase, duration, bits=preamble)
    correlation = signal.correlate(wave, preamble_sequence, mode='full')
    
    return correlation


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


def demodulate_signal(sampling_rate, frequency_0, frequency_1, amplitude, start_phase, duration, preamble, threshold, wave):
    one_bit_length = int(sampling_rate * duration)
    correlates = calculate_correlates(sampling_rate, frequency_0, frequency_1, amplitude, start_phase, duration, preamble, wave)
    packet_results = []

    max_indices = []
    
    l = len(correlates)

    for i in range(5):
        p = np.argmax(correlates)
        print(p)
        max_indices.append(p)
        st = max(p - 192*one_bit_length, 0)
        en = min(p + 192*one_bit_length, l)
        correlates[st:en] = float('-inf')
    
    max_indices.sort()

    print(max_indices)

    for i in range(len(max_indices)):
        if i != len(max_indices) - 1:
            packet_length = 192
        else:
            packet_length = 32
        start_position = max_indices[i]

        packet_payload = wave[start_position + one_bit_length * 8: start_position + one_bit_length * len(preamble) + one_bit_length * 8 + packet_length * one_bit_length]
        decoded_payload = demodulate_packet(sampling_rate, frequency_0, frequency_1, duration, packet_payload)
        packet_results.append((decoded_payload, start_position))
    
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
    
