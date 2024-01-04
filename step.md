1. P的电脑运行`python sender.py`，获得`audio/res.wav`
2. X的电脑运行`python record.py`(根据res.wav修改录音时长)，同时P的电脑播放`res.wav`，在X的电脑上得到`recorded_audio.wav`
3. 将`recorded_audio.wav`微信发回给P电脑，运行`python receiver.py`