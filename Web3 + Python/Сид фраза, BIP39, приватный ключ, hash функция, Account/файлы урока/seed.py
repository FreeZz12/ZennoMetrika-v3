import hashlib
import os
import random
from mnemonic import Mnemonic

# генерация 8 * 16 = 128 битов нулей и единиц
entropy = os.urandom(16)

# преобразование энтропии в бинарное представление
entropy_bits = bin(int.from_bytes(entropy, "big"))[2:].zfill(128)  # Бинарное представление энтропии

print(entropy_bits)

# получение хэша от энтропии
checksum = hashlib.sha256(entropy).digest()
# Бинарное представление хэша
checksum_bits = bin(int.from_bytes(checksum, "big"))[2:].zfill(256)

print()
print(checksum_bits)

result = entropy_bits + checksum_bits[:4]

print()
seed = ''

for i in range(0, len(result), 11):
    index_bin = result[i:i + 11]
    index = int(index_bin, 2)
    print(index_bin, index, Mnemonic().wordlist[index])
    seed += Mnemonic().wordlist[index] + ' '

print(seed)