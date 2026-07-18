// SPDX-License-Identifier: MIT
// ═══════════════════════════════════════════════════════════════
// Sample Vulnerable Contract - For Testing SentinelQwen
// Contains intentional vulnerabilities for demonstration
// DO NOT USE IN PRODUCTION
// ═══════════════════════════════════════════════════════════════

pragma solidity ^0.8.0;

contract VulnerableToken {
    string public name = "Vulnerable Token";
    string public symbol = "VULN";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balances;
    mapping(address => mapping(address => uint256)) public allowance;

    address public owner;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    // ❌ VULNERABILITY 1: No access control on constructor
    constructor(uint256 initialSupply) {
        totalSupply = initialSupply;
        balances[msg.sender] = initialSupply;
        owner = msg.sender;
    }

    // ❌ VULNERABILITY 2: Reentrancy (CEI violation)
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance");

        // External call BEFORE state update!
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        balances[msg.sender] = 0;  // State update too late
        emit Transfer(address(this), msg.sender, amount);
    }

    // ❌ VULNERABILITY 3: tx.origin authentication
    function transferOwnership(address newOwner) public {
        require(tx.origin == owner, "Not owner");  // Phishable!
        owner = newOwner;
    }

    // ❌ VULNERABILITY 4: Unchecked external call
    function sendReward(address user, uint256 amount) public {
        // Return value not checked!
        user.call{value: amount}("");
        emit Transfer(address(this), user, amount);
    }

    // ❌ VULNERABILITY 5: Integer overflow (if < Solidity 0.8)
    function mint(address to, uint256 amount) public {
        // No access control - anyone can mint!
        totalSupply += amount;
        balances[to] += amount;
        emit Transfer(address(0), to, amount);
    }

    // ❌ VULNERABILITY 6: Self-destruct without access control
    function destroy() public {
        selfdestruct(payable(msg.sender));  // Anyone can destroy!
    }

    // ❌ VULNERABILITY 7: Timestamp dependence for randomness
    function lottery() public view returns (bool) {
        return uint256(keccak256(abi.encodePacked(block.timestamp))) % 2 == 0;
    }

    // ❌ VULNERABILITY 8: Unchecked math with assembly
    function unsafeAdd(uint256 a, uint256 b) public pure returns (uint256) {
        uint256 c;
        assembly {
            c := add(a, b)  // No overflow check!
        }
        return c;
    }

    // Standard functions (no vulnerabilities)
    function transfer(address to, uint256 amount) public returns (bool) {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        balances[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }

    function approve(address spender, uint256 amount) public returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    receive() external payable {
        balances[msg.sender] += msg.value;
    }
}
