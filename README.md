# IOT_communication
2023清华大学《物联网导论》课程大作业：声波信号通信

## 运行方法
### 创建环境
```
conda create -n IOT python=3.9
pip install -r requirements.txt
```
### 运行
- 输入字符，生成音频，结果在`./audio/sender_audio.wav`中
  ```
  python sender.py
  ```
- 录音，结果在`./audio/receiver_audio.wav`中
  ```
  python record.py
  ```
- 解码，展示结果
  ```
  python receiver.py
  ```
