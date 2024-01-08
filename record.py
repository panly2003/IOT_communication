import pyaudio
import wave

SAMPLING_RATE = 44100  # 采样率
SAVE_PATH = './audio/receiver_audio.wav'  # 保存路径


def record(time=10):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=SAMPLING_RATE,
                    input=True,
                    frames_per_buffer=1024)

    print("开始录音...")
    frames = []
    for _ in range(0, int(SAMPLING_RATE / 1024 * time)):
        data = stream.read(1024)
        frames.append(data)
    print("录音结束.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # 将录制的音频保存到文件
    wf = wave.open(SAVE_PATH, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLING_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

if __name__ == "__main__":
    record(time=53)