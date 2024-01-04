import scipy.io.wavfile as wav
from fsk import demodulate_signal
from utils import binary_list_to_unicode
from tkinter import messagebox

if __name__ == "__main__":
    # init args
    import argparse
    parser = argparse.ArgumentParser(description="Choose the parameters")
    # Parameters needed for forming complete binary string with Bluetooth packet added to the original binary string
    parser.add_argument("--packet_payload_length", type=int, default=192)  # Maximum length of a packet payload, used for segmentation
    parser.add_argument("--blank_length", type=int, default=20)  # Length of blank space between packets and at the beginning and end
    parser.add_argument("--preamble", type=list, default=[1, 1, 1, 1, 0, 0, 0, 0]*3)  # Preamble

    # Parameters needed for FSK modulation
    # FSK frequencies corresponding to bit 0 and bit 1
    parser.add_argument("--frequency_0", type=int, default=4000)
    parser.add_argument("--frequency_1", type=int, default=6000)
    # Sampling rate, amplitude, start phase, and duration of each wave segment corresponding to a bit
    parser.add_argument("--sampling_rate", type=int, default=44100)
    parser.add_argument("--amplitude", type=float, default=20000.0)
    parser.add_argument("--start_phase", type=int, default=0)
    parser.add_argument("--duration", type=float, default=2.5e-2)

    # Parameters needed for saving audio files: save path
    parser.add_argument("--save_path", type=str, default="audio/recorded_audio.wav")

    # Parameters needed for FSK demodulation
    parser.add_argument("--threshold", type=int, default=2e11)  # Correlation threshold for preamble

    args = parser.parse_args()

    # Load
    test_path = './audio/recorded_audio.wav'
    fs, decoded_wave = wav.read(test_path)

    # Demodulation
    decoded_result = demodulate_signal(sampling_rate=args.sampling_rate, frequency_0=args.frequency_0, frequency_1=args.frequency_1, amplitude=args.amplitude, start_phase=args.start_phase, duration=args.duration, preamble=args.preamble, threshold=args.threshold, wave=decoded_wave)
    # print(f'decoded result: {decoded_result}')
    # Concatenate decoded results
    decoded_payload_bits = []
    for item in decoded_result:
        payload, start = item[0], item[1]
        decoded_payload_bits.extend(payload)
        # print(binary_list_to_unicode(payload))
    
    # print(f'decoded payload bits: {decoded_payload_bits}')
    str = binary_list_to_unicode(decoded_payload_bits)
    print(f'decoded string: {str}')

    # 弹出框显示文本
    messagebox.showinfo("Decoded String", str)
