""""""

"""
Задание 1 - easy

Закодируйте input data для функции 
swap(address tokenIn, address tokenOut, uint256 amountIn, uint256 amountOutMin, address recipient, uint256 deadline)
tokenIn - USDC в сети Arbitrum
tokenOut - USDT в сети Arbitrum
amountIn - 1000
amountOutMin - 950
recipient - любой адрес
deadline - сегодняшний timestamp + 24 часа 

"""


# код пишем тут

"""
Задание 2  - medium
Закодируйте input data для функции
bridge(address[2] tokens, string operator, bytes[] extraOptions, uint256[2] amounts)
tokens - массив адресов токенов USDC и USDT в сети Arbitrum
operator - текст layerzero
bytes[] extraOptions - массив байт [0x123456, 0x654321, 0xabcdef]
amounts - массив uint256 [1000, 2000]

Будьте внимательны с типами данных, имеются данные фиксированной и переменной длины.

"""

# код пишем тут

"""
Задание 3 - hard

Закодируйте input data для функции
claim(bytes32[] merkleProof, bytes proof, address recipient)
merkleProof - массив байт [0x123456654321654321, 0x654321654321654321, 0xabcdef654321654321]
proof - '0x1234567890123456789012345673453456345678901234567890123456778901234567890123456767890123456789012345678901234567890123456789012345678901234'
recipient - адрес получателя, любой адрес

"""

# код пишем тут

