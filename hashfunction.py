import sys
import re
from collections import defaultdict
import hashlib

if __name__ == "__main__":
    number = 100000000
    stringtest = "This is an example sentence."
    stringtest2 = "why are animals so fucking stubborn sometimes? like just let me kill you"

    tokenlist = re.findall(r"[\x30-\x39\x41-\x5A\x61-\x7A]+", stringtest)
    count_dict = defaultdict(int)
    hash_dict = {}

    num_bits = 32
    hash_list = [0] * num_bits

    for i in tokenlist:
        count_dict[i] += 1
    
    for i in tokenlist:
        number = (int.from_bytes(hashlib.sha256(i.encode()).digest()[:4], 'little')) # 32-bit int
        
        bits = [(number >> bit) & 1 for bit in range(num_bits - 1, -1, -1)]
        print(f'i: {i:<10} bits: {bits}')
        for index, bit in enumerate(bits):
            hash_list[index] += count_dict[i] if bit == 1 else (-1 * count_dict[i])
            # if bit == 1:
            #     hash_list[index] += count_dict[i]
            # elif bit == 0:
            #     hash_list[index] -= count_dict[i]
    
    finalhash = sum(c << i for i, c in enumerate(hash_list))
    print(finalhash)