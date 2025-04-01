from eth_abi import decode


def decoder():
    data = '0x000000000000000000000000af88d065e77c8cc2239327c5edb3a432268e5831000000000000000000000000ffffffffffffffffffffffffffffffffffffffff000000000000000000000000000000000000000000000000000000006809cce70000000000000000000000000000000000000000000000000000000000000003000000000000000000000000a51afafe0263b40edaef0df8781ea9aa03e381a30000000000000000000000000000000000000000000000000000000067e246ef00000000000000000000000000000000000000000000000000000000000000e00000000000000000000000000000000000000000000000000000000000000041fac56dfc4fd26b0650a55f6ecc8db299994cc20f0887633845c44baba3afdcaf6aea23dfadac64a04e4a5e8c589b7176936667277c174a81ac665eecb8fb98541c00000000000000000000000000000000000000000000000000000000000000'
    data_bytes = bytes.fromhex(data[2:])
    permit_details = '(address,uint160,uint48,uint48)'
    permit_single = f'({permit_details},address,uint256)'
    permit_single, data  = decode([permit_single, 'bytes'], data_bytes)
    permit_details, spender, sig_deadline = permit_single
    token, amount, expiration, nonce = permit_details
    print(f'Token: {token}')
    print(f'Amount: {amount}')
    print(f'Expiration: {expiration}') # 30 дней
    print(f'Nonce: {nonce}') # из контракта permit2
    print(f'Spender: {spender}') # юнисвап роутер
    print(f'Sig Deadline: {sig_deadline}') # 30 минут
    print(f'Data: {data.hex()}')


    """
    struct PermitDetails {
        // ERC20 token address
        address token;
        // the maximum amount allowed to spend
        uint160 amount;
        // timestamp at which a spender's token allowances become invalid
        uint48 expiration;
        // an incrementing value indexed per owner,token,and spender for each signature
        uint48 nonce;
    }

    /// @notice The permit message signed for a single token allownce
    struct PermitSingle {
        // the permit data for a single token alownce
        PermitDetails details;
        // address permissioned on the allowed tokens
        address spender;
        // deadline on the permit signature
        uint256 sigDeadline;
    }
    
    """





if __name__ == '__main__':
    decoder()
