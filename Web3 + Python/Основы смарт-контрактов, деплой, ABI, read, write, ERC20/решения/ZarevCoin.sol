// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title IERC20
 * Интерфейс стандарта ERC20
 */
interface IERC20 {
    // описание того что обязана реализовать каждая реализация интерфейса
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) external returns (bool);
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}

/**
 * @title ERC20
 * Базовая реализация стандарта ERC20
 */
contract ERC20 is IERC20 {
    string private _name;
    string private _symbol;
    uint8 private _decimals;
    uint256 private _totalSupply;
    address private _owner;

    // Хранение балансов и разрешений
    mapping(address => uint256) private _balances; // {адрес: баланс}
    mapping(address => mapping(address => uint256)) private _allowances; // {адрес: {адрес: разрешение}}

    /**
     * @dev Инициализирует параметры токена: имя, символ и количество знаков после запятой (обычно 18).
     */
    constructor(string memory name, string memory symbol, uint8 decimals, uint256 totalSupply) { // init
        _owner = msg.sender;
        _name = name;
        _symbol = symbol;
        _decimals = decimals;
        _totalSupply = totalSupply;
        _balances[msg.sender] = totalSupply;
    }

    /// Возвращает общее количество выпущенных токенов
    function totalSupply() public view override returns (uint256) {
        return _totalSupply;
    }

    function name() public view returns (string memory) {
        return _name;
    }

    function symbol() public view returns (string memory) {
        return _symbol;
    }

    function decimals() public view returns (uint8) {
        return _decimals;
    }

    /// Возвращает баланс аккаунта
    function balanceOf(address account) public view override returns (uint256) {
        return _balances[account];
    }

    /// Перевод токенов с msg.sender на recipient
    function transfer(address recipient, uint256 amount) public override returns (bool) {
        _transfer(msg.sender, recipient, amount);
        return true;
    }

    /// Возвращает оставшееся количество токенов, которое spender может потратить от имени owner
    function allowance(address owner, address spender) public view override returns (uint256) {
        return _allowances[owner][spender];
    }

    /// Устанавливает разрешение для spender тратить от имени msg.sender заданное количество токенов
    function approve(address spender, uint256 amount) public override returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }

    /// Перевод токенов от sender к recipient с использованием разрешения
    function transferFrom(address sender, address recipient, uint256 amount) public override returns (bool) {
        uint256 currentAllowance = _allowances[sender][msg.sender];
        require(currentAllowance >= amount, "ERC20: amount exceeds allowance");
        _transfer(sender, recipient, amount);
        _approve(sender, msg.sender, currentAllowance - amount);
        return true;
    }

    /**
     * @dev Внутренняя функция перевода токенов
     */
    function _transfer(address sender, address recipient, uint256 amount) internal {
        require(sender != address(0), "ERC20: transfer from the zero address");
        require(recipient != address(0), "ERC20: transfer to the zero address");
        uint256 senderBalance = _balances[sender];
        require(senderBalance >= amount, "ERC20: transfer amount exceeds balance");

        _balances[sender] = senderBalance - amount;
        _balances[recipient] += amount;

        emit Transfer(sender, recipient, amount);
    }


    /**
     * @dev Внутренняя функция установки разрешения
     */
    function _approve(address owner, address spender, uint256 amount) internal {
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");

        _allowances[owner][spender] = amount;

        emit Approval(owner, spender, amount);
    }

    function mint(uint256 amount) public {
        if (msg.sender != _owner) {
            revert("Only owner can mint");
        }
        _totalSupply += amount;
        _balances[_owner] += amount;
    }
}
