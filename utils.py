import numpy as np


def text_to_binary(text):
    binary_result = ' '.join(format(ord(char), '08b') for char in text)
    return binary_result


def int_to_bit(num):
    seq = []
    for i in range(8):
        seq.append((num >> (7 - i)) & 1)
    return seq


def bit_to_int(seq):
    if len(seq) > 8:
        seq = seq[: 8]
    elif len(seq) < 8:
        for i in range(8 - len(seq)):
            seq.append(0)
    num = 0
    for i in range(8):
        num += (seq[7 - i] << i)
    return num

def closest_letter(chunk):
    # 大写字母的Unicode范围
    uppercase_range = range(65, 91)
    # 小写字母的Unicode范围
    lowercase_range = range(97, 123)

    def count_matching_bits(char_code, chunk):
        # 将字符的Unicode编码转换为8位二进制字符串
        char_binary = int_to_bit(char_code)
        # 按位比较并计算相同的个数
        return sum(c1 == c2 for c1, c2 in zip(char_binary, chunk))

    # 初始化最大匹配位数和最相近的字母
    max_matching_bits = 0
    closest_letter = None

    # 遍历大写字母
    for code in uppercase_range:
        matching_bits = count_matching_bits(code, chunk)
        if matching_bits > max_matching_bits:
            max_matching_bits = matching_bits
            closest_letter = chr(code)

    # 遍历小写字母
    for code in lowercase_range:
        matching_bits = count_matching_bits(code, chunk)
        if matching_bits > max_matching_bits:
            max_matching_bits = matching_bits
            closest_letter = chr(code)

    # 返回最相近的字母
    return closest_letter
    

def binary_list_to_unicode(binary_list):
    unicode_string = ''
    # 将二进制列表分割为每 8 位一组
    for i in range(0, len(binary_list), 8):
        chunk = binary_list[i:i+8]
        unicode_string += closest_letter(chunk)

    return unicode_string