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