import tkinter as tk
from tkinter import scrolledtext

def text_to_binary(text):
    binary_result = ' '.join(format(ord(char), '08b') for char in text)
    return binary_result

def convert_text_to_binary():
    input_text = entry.get(1.0, tk.END).strip()  # 获取整个文本框的内容
    binary_result = text_to_binary(input_text)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f'Binary: {binary_result}')

# 创建主窗口
window = tk.Tk()
window.title('Text to Binary Converter')

# 设置窗口大小和位置
window.geometry('800x600')
window.resizable(True, True)  # 允许调整窗口大小

# 创建标签、文本框和按钮
label = tk.Label(window, text='Enter text:', font=('Arial', 14))
label.pack(pady=10)

entry = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=40, height=3, font=('Arial', 12))
entry.pack(pady=10)

convert_button = tk.Button(window, text='Convert', command=convert_text_to_binary, font=('Arial', 12))
convert_button.pack(pady=10)

result_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=40, height=5, font=('Arial', 12))
result_text.pack(pady=10)

# 启动主循环
window.mainloop()
