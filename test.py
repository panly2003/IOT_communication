import random
import string

# 设置字符串长度
string_length = 100

# 生成随机字符串
random_string = ''.join(random.choices(string.ascii_letters, k=string_length))

# 打印结果
print(random_string)