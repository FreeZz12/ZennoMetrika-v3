import random

def better_hash(text: str) -> int:
    result = 0
    for i, char in enumerate(text, start=1):
        result += ord(char) * i
    return result % 1000

message = 'Выдра, курва!'
print(better_hash(message))




