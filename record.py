import pyaudio
import wave
import numpy as np


def record_audio(args, duration=10):
    CHUNK = 1024  # 每次读取的帧数
    FORMAT = pyaudio.paInt16  # 采样格式
    RATE = args.sampling_rate  # 采样率
    RECORD_SECONDS = duration  # 录制时长

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始录音...")
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("录音结束.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # 将录制的音频保存到文件
    wf = wave.open(args.save_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

if __name__ == "__main__":
    # init args
    import argparse
    parser = argparse.ArgumentParser(description="Choose the parameters")
    parser.add_argument("--sampling_rate", type=int, default=44100)
    parser.add_argument("--save_path", type=str, default="audio/recorded_audio.wav")
    args = parser.parse_args()

    # Record
    record_audio(args, 29) ####### change