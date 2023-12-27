from tkinter import scrolledtext
import tkinter as tk
from utils import int_to_bit, text_to_binary
import numpy as np
import scipy.io.wavfile as wav
from fsk import demodulate_signal, modulate_signal

entry = None  # UI entry
input_text = None  # User-input text (English string)
input_text_binary_code = None  # Binary code of the English string

def convert_text_to_binary():
    global entry, result_text
    input_text = entry.get(1.0, tk.END).strip()  # Get the entire content of the text box
    input_text_binary_code = text_to_binary(input_text)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f'{input_text_binary_code}')

def encode_bluetooth_packet(args, binary_data):
    packet_payload_len = args.packet_payload_length  # Packet payload length for segmentation
    blank_len = args.blank_length  # Length of blank space between packets
    bluetooth_packets_seq = []
    packet_payload = []

    for i in range(len(binary_data)):
        packet_payload.append(int(binary_data[i]))
        if len(packet_payload) >= packet_payload_len or i == len(binary_data) - 1:
            bluetooth_packets_seq += ([2] * blank_len)  # Add blank space
            bluetooth_packets_seq += args.preamble  # Add preamble
            bluetooth_packets_seq += (int_to_bit(len(packet_payload)))  # Add 8-bit header, encoding data packet length information
            bluetooth_packets_seq += packet_payload  # Add data content segment
            packet_payload = []
    bluetooth_packets_seq += ([2] * blank_len)
    return bluetooth_packets_seq

def send_binary_data(args):
    global result_text
    # Get binary_data directly from the text box, removing spaces
    input_text_binary_code = result_text.get(1.0, tk.END).replace(" ", "").strip()
    print(f'binary data: {input_text_binary_code}')
    # Add Bluetooth packet to form complete binary_data
    blue_tooth_binary_data = encode_bluetooth_packet(args, input_text_binary_code)
    print(f'bluetooth binary data: {blue_tooth_binary_data}')
    # FSK modulation
    fsk_data = modulate_signal(args.sampling_rate, args.frequency_0, args.frequency_1, args.amplitude, args.start_phase, args.duration, blue_tooth_binary_data)
    print(f'fsk data: {fsk_data}')
    # Save
    wav.write(args.save_path, args.sampling_rate, fsk_data.astype(np.int16))

    # Test
    # Load
    fs, decoded_wave = wav.read('./audio/res.wav')
    # Demodulation
    decoded_result = demodulate_signal(sampling_rate=args.sampling_rate, frequency_0=args.frequency_0, frequency_1=args.frequency_1, amplitude=args.amplitude, start_phase=args.start_phase, duration=args.duration, preamble=args.preamble, threshold=args.threshold, wave=decoded_wave)
    print(f'decoded result: {decoded_result}')

    # Concatenate decoded results
    decoded_payload_bits = []
    for item in decoded_result:
        payload, start = item[0], item[1]
        decoded_payload_bits += payload

    # Calculate bit accuracy
    corr_bit_num = 0
    for i in range(len(input_text_binary_code)):
        if eval(input_text_binary_code[i]) == decoded_payload_bits[i]:
            corr_bit_num += 1
    bit_accuracy = corr_bit_num / len(input_text_binary_code)
    print(f'bit accuracy: {bit_accuracy * 100}%')

    # Play (Send)

def init_ui(args):
    # Create the main window
    window = tk.Tk()
    window.title('Text to Binary Converter')

    # Set window size and position
    window.geometry('800x600')
    window.resizable(True, True)  # Allow window resizing

    global entry, result_text

    # Create labels, text boxes, and buttons
    label = tk.Label(window, text='Enter text:', font=('Arial', 14))
    label.pack(pady=10)

    entry = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=40, height=3, font=('Arial', 12))
    entry.pack(pady=10)

    convert_button = tk.Button(window, text='Convert', command=convert_text_to_binary, font=('Arial', 12))
    convert_button.pack(pady=10)

    result_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=40, height=5, font=('Arial', 12))
    result_text.pack(pady=10)

    send_button = tk.Button(window, text='Send', command=lambda: send_binary_data(args), font=('Arial', 12))
    send_button.pack(pady=10)

    # Start the main loop
    window.mainloop()

def init_args():
    import argparse
    parser = argparse.ArgumentParser(description="Choose the parameters")

    # Parameters needed for forming complete binary string with Bluetooth packet added to the original binary string
    parser.add_argument("--packet_payload_length", type=int, default=96)  # Maximum length of a packet payload, used for segmentation
    parser.add_argument("--blank_length", type=int, default=60)  # Length of blank space between packets and at the beginning and end
    parser.add_argument("--preamble", type=list, default=[0, 1] * 10)  # Preamble

    # Parameters needed for FSK modulation
    # FSK frequencies corresponding to bit 0 and bit 1
    parser.add_argument("--frequency_0", type=int, default=4000)
    parser.add_argument("--frequency_1", type=int, default=6000)
    # Sampling rate, amplitude, start phase, and duration of each wave segment corresponding to a bit
    parser.add_argument("--sampling_rate", type=int, default=48000)
    parser.add_argument("--amplitude", type=float, default=20000.0)
    parser.add_argument("--start_phase", type=int, default=0)
    parser.add_argument("--duration", type=float, default=2.5e-2)

    # Parameters needed for saving audio files: save path
    parser.add_argument("--save_path", type=str, default="audio/res.wav")

    # Parameters needed for FSK demodulation
    parser.add_argument("--threshold", type=int, default=2e11)  # Correlation threshold for preamble

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = init_args()
    print(f'args: {args}')
    init_ui(args)
