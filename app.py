#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
SentinelQwen - Main Entry Point
Autopilot Smart Contract Security Auditor
Track 4: Autopilot Agent - Qwen Cloud Hackathon 2026

Usage:
    python app.py server          # Start Flask API server
    python app.py bot             # Start Telegram Bot
    python app.py audit <file>    # Audit a contract file
    python app.py demo            # Run demo with sample contract
    python app.py test-api        # Test Qwen API connection
═══════════════════════════════════════════════════════════════
"""
import sys
import os
import argparse
import asyncio
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def print_banner():
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ██████╗ ██╗    ██╗███████╗███╗   ██╗ ██████╗ ██╗   ██╗    ║
    ║  ██╔═══██╗██║    ██║██╔════╝████╗  ██║██╔════╝ ██║   ██║    ║
    ║  ██║   ██║██║ █╗ ██║█████╗  ██╔██╗ ██║██║  ███╗██║   ██║    ║
    ║  ██║▄▄ ██║██║███╗██║██╔══╝  ██║╚██╗██║██║   ██║██║   ██║    ║
    ║  ╚██████╔╝╚███╔███╔╝███████╗██║ ╚████║╚██████╔╝╚██████╔╝    ║
    ║   ╚══▀▀═╝  ╚══╝╚══╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝     ║
    ║                                                               ║
    ║   SentinelQwen - AI-Powered Smart Contract Security Auditor                 ║
    ║   Track 4: Autopilot Agent                                   ║
    ║   Qwen Cloud Global AI Hackathon 2026                        ║
    ║   SentinelQwen | Powered by Qwen3.7-Plus                                    ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

def test_api():
    """Test Qwen API connection"""
    from tools.qwen_client import get_qwen_client

    print("🔌 Testing Qwen API connection...")

    client = get_qwen_client()
    stats = client.get_usage_stats()

    print(f"   Model: {stats.get('model', 'N/A')}")
    print(f"   API Key: {'✅ Set' if stats.get('api_key_set') else '❌ Not set'}")
    print(f"   DashScope: {'✅ Available' if stats.get('dashscope_available') else '❌ Not installed'}")

    if stats.get('api_key_set') and stats.get('dashscope_available'):
        print("\n🚀 Testing API call...")
        try:
            result = asyncio.run(client.analyze_contract(
                "pragma solidity ^0.8.0; contract Test { uint x; }",
                "ethereum"
            ))
            print(f"   ✅ API call successful!")
            print(f"   Risk Score: {result.get('risk_score', 'N/A')}")
            print(f"   Vulnerabilities found: {len(result.get('vulnerabilities', []))}")
        except Exception as e:
            print(f"   ❌ API call failed: {e}")
    else:
        print("\n⚠️  Set DASHSCOPE_API_KEY in .env and run: pip install dashscope")

def run_server():
    """Start Flask API server"""
    from api.server import app
    import os

    port = int(os.getenv("FLASK_PORT", 5000))
    host = os.getenv("FLASK_HOST", "0.0.0.0")

    print(f"🚀 Starting API server on {host}:{port}...")
    print(f"   Dashboard: http://{host}:{port}/dashboard")
    print(f"   Health: http://{host}:{port}/health")
    print(f"   API Docs: http://{host}:{port}/api/v1/")
    app.run(host=host, port=port, debug=False)

def run_bot():
    """Start Telegram Bot"""
    from bot.telegram_bot import QwenGuardTelegramBot
    from agents.orchestrator import AuditOrchestrator
    from memory.vector_store import AuditMemory
    from tools.qwen_client import get_qwen_client
    import os

    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN not set in environment")
        print("   Get one from @BotFather on Telegram")
        sys.exit(1)

    memory = AuditMemory()
    qwen_client = get_qwen_client()
    orchestrator = AuditOrchestrator(qwen_client, memory)

    bot = QwenGuardTelegramBot(token, orchestrator)
    bot.run()

async def audit_file(filepath: str, chain: str = "ethereum"):
    """Audit a contract file"""
    from agents.orchestrator import AuditOrchestrator
    from memory.vector_store import AuditMemory
    from tools.qwen_client import get_qwen_client

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, "r") as f:
        contract_code = f.read()

    print(f"🔍 Auditing {filepath} on {chain}...")
    print(f"   Contract size: {len(contract_code)} characters")

    memory = AuditMemory()
    qwen_client = get_qwen_client()
    orchestrator = AuditOrchestrator(qwen_client, memory)

    context = await orchestrator.run_audit(
        contract_code=contract_code,
        chain=chain
    )

    print(f"\n{'='*60}")
    print(f"✅ AUDIT COMPLETE: {context.audit_id}")
    print(f"{'='*60}")
    print(f"   Status: {context.status.value}")
    print(f"   Risk Score: {context.metadata.get('risk_score', 0)}/100")
    print(f"   Total Findings: {len(context.findings)}")
    print(f"   🔴 Critical: {sum(1 for f in context.findings if f.get('severity') == 'Critical')}")
    print(f"   🟠 High: {sum(1 for f in context.findings if f.get('severity') == 'High')}")
    print(f"   🟡 Medium: {sum(1 for f in context.findings if f.get('severity') == 'Medium')}")
    print(f"   🟢 Low: {sum(1 for f in context.findings if f.get('severity') == 'Low')}")

    if context.findings:
        print(f"\n--- TOP FINDINGS ---")
        for i, f in enumerate(context.findings[:10], 1):
            print(f"   {i}. [{f.get('severity')}] {f.get('type')} (line {f.get('line', 'N/A')})")
            print(f"      {f.get('description', 'No description')}")

    if context.report:
        report_path = f"audit_report_{context.audit_id}.md"
        with open(report_path, "w") as f:
            f.write(context.report)
        print(f"\n📝 Report saved to: {report_path}")

    if context.fix_suggestions:
        print(f"\n🔧 Fix suggestions: {len(context.fix_suggestions)}")

def run_demo():
    """Run demo with sample vulnerable contract"""
    sample_contract = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableToken {
    mapping(address => uint256) public balances;
    address public owner;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // VULNERABLE: Reentrancy
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
        balances[msg.sender] = 0;
    }

    // VULNERABLE: tx.origin
    function transferOwnership(address newOwner) public {
        require(tx.origin == owner);
        owner = newOwner;
    }

    // VULNERABLE: Unchecked call
    function sendReward(address user, uint256 amount) public {
        user.call{value: amount}("");
    }

    // VULNERABLE: Anyone can mint
    function mint(address to, uint256 amount) public {
        balances[to] += amount;
    }

    // VULNERABLE: Self-destruct
    function destroy() public {
        selfdestruct(payable(msg.sender));
    }
}
"""

    print("🧪 Running demo with sample vulnerable contract...")
    print("   This contract contains intentional vulnerabilities for testing.\n")

    with open("/tmp/demo_contract.sol", "w") as f:
        f.write(sample_contract)

    asyncio.run(audit_file("/tmp/demo_contract.sol"))

def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="SentinelQwen - Smart Contract Security Auditor"
    )
    parser.add_argument(
        "command",
        choices=["server", "bot", "audit", "quick", "demo", "test-api"],
        help="Command to run"
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Contract file path (for audit command)"
    )
    parser.add_argument(
        "--chain",
        default="ethereum",
        choices=["ethereum", "bsc", "tron", "polygon", "arbitrum"],
        help="Target blockchain"
    )

    args = parser.parse_args()

    if args.command == "server":
        run_server()
    elif args.command == "bot":
        run_bot()
    elif args.command == "audit":
        if not args.file:
            print("❌ Please provide a contract file path")
            print("   Usage: python app.py audit contract.sol --chain ethereum")
            sys.exit(1)
        asyncio.run(audit_file(args.file, args.chain))
    elif args.command == "quick":
        if not args.file:
            print("❌ Please provide a contract file path")
            sys.exit(1)
        print("⚡ Quick scan uses pattern matching only")
        print("   Use 'audit' for full AI-powered analysis")
    elif args.command == "demo":
        run_demo()
    elif args.command == "test-api":
        test_api()

if __name__ == "__main__":
    main()
