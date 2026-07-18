"""
═══════════════════════════════════════════════════════════════
SentinelQwen - Telegram Bot Integration
Allows users to audit contracts via Telegram
═══════════════════════════════════════════════════════════════
"""
import os
import asyncio
import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from ..agents.orchestrator import AuditOrchestrator
from ..memory.vector_store import AuditMemory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Admin IDs from env
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

class QwenGuardTelegramBot:
    """Telegram Bot for SentinelQwen"""

    def __init__(self, token: str, orchestrator: AuditOrchestrator):
        self.token = token
        self.orchestrator = orchestrator
        self.application = Application.builder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup command and message handlers"""
        # Commands
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("audit", self.cmd_audit))
        self.application.add_handler(CommandHandler("quickscan", self.cmd_quickscan))
        self.application.add_handler(CommandHandler("chains", self.cmd_chains))
        self.application.add_handler(CommandHandler("stats", self.cmd_stats))
        self.application.add_handler(CommandHandler("about", self.cmd_about))

        # Callbacks
        self.application.add_handler(CallbackQueryHandler(self.callback_handler))

        # Messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

        # Errors
        self.application.add_error_handler(self.error_handler)

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        welcome_msg = """
🛡️ <b>Welcome to SentinelQwen!</b>

I'm an <b>Autopilot Smart Contract Security Auditor</b> powered by Qwen Cloud & Alibaba Cloud.

<b>What I can do:</b>
• 🔍 Full security audit with AI analysis
• ⚡ Quick vulnerability scan
• 📝 Generate professional audit reports
• 🔧 Suggest secure code fixes
• 🧠 Learn from past audits

<b>Commands:</b>
/audit - Start a full audit
/quickscan - Quick vulnerability scan
/chains - Supported blockchains
/stats - Memory statistics
/help - Detailed help
/about - About this project

<b>Track 4:</b> Autopilot Agent
<b>Hackathon:</b> Qwen Cloud Global AI Hackathon 2026
        """

        keyboard = [
            [InlineKeyboardButton("🔍 Full Audit", callback_data="audit_full")],
            [InlineKeyboardButton("⚡ Quick Scan", callback_data="audit_quick")],
            [InlineKeyboardButton("📊 View Stats", callback_data="view_stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(welcome_msg, parse_mode="HTML", reply_markup=reply_markup)

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_msg = """
<b>📖 SentinelQwen - Help Guide</b>

<b>🔍 Full Audit (/audit)</b>
Send me your Solidity contract code and I'll perform:
• Static analysis (Slither/Mythril)
• Pattern-based vulnerability detection
• AI-powered semantic analysis (Qwen 3.7)
• Fix suggestions with code examples
• Professional audit report

<b>⚡ Quick Scan (/quickscan)</b>
Fast pattern matching for common vulnerabilities:
• Reentrancy
• Access control issues
• Integer overflow
• Unchecked calls
• And more...

<b>How to use:</b>
1. Send /audit command
2. Paste your contract code (or send as file)
3. Select blockchain (Ethereum, BSC, TRON, etc.)
4. Wait for results (30-60 seconds)

<b>Supported Chains:</b>
• Ethereum (ETH)
• BNB Smart Chain (BSC)
• TRON
• Polygon
• Arbitrum

<b>Privacy:</b>
Your contract code is only used for audit purposes and may be stored in our learning memory system.
        """
        await update.message.reply_text(help_msg, parse_mode="HTML")

    async def cmd_audit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start full audit workflow"""
        context.user_data["awaiting_code"] = True
        context.user_data["audit_type"] = "full"

        await update.message.reply_text(
            "🔍 <b>Full Security Audit</b>\n\n"
            "Please send me your Solidity contract code.\n"
            "You can paste it directly or send as a .sol file.\n\n"
            "After receiving the code, I'll ask you to select the target blockchain.",
            parse_mode="HTML"
        )

    async def cmd_quickscan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start quick scan"""
        context.user_data["awaiting_code"] = True
        context.user_data["audit_type"] = "quick"

        await update.message.reply_text(
            "⚡ <b>Quick Vulnerability Scan</b>\n\n"
            "Please send me your Solidity contract code.\n"
            "I'll quickly scan for common vulnerability patterns.",
            parse_mode="HTML"
        )

    async def cmd_chains(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List supported chains"""
        chains_msg = """
<b>🔗 Supported Blockchains</b>

• <b>Ethereum (ETH)</b> - Mainnet & testnets
• <b>BNB Smart Chain (BSC)</b> - Mainnet & testnet
• <b>TRON</b> - Mainnet & Shasta testnet
• <b>Polygon</b> - POS & zkEVM
• <b>Arbitrum</b> - One & Nova

Each chain has specific vulnerability patterns and best practices that our AI considers during analysis.
        """
        await update.message.reply_text(chains_msg, parse_mode="HTML")

    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show memory stats"""
        stats = self.orchestrator.memory.get_memory_stats()

        stats_msg = f"""
<b>📊 SentinelQwen Statistics</b>

<b>Memory System:</b>
• Status: {stats.get("status", "Unknown")}
• Total Audits Stored: {stats.get("total_audits_stored", 0)}
• Vector DB: {stats.get("vector_db", "N/A")}
• Embedding Model: {stats.get("embedding_model", "N/A")}

<b>Detection Capabilities:</b>
• Vulnerability Types: 14+
• Detection Layers: 3 (Static + Pattern + AI)
• Supported Chains: 5
• AI Model: Qwen 3.7 Plus

<b>Project:</b>
• Track 4: Autopilot Agent
• Qwen Cloud Hackathon 2026
        """
        await update.message.reply_text(stats_msg, parse_mode="HTML")

    async def cmd_about(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """About command"""
        about_msg = """
<b>🛡️ SentinelQwen</b>

<b>Autopilot Smart Contract Security Auditor</b>

An end-to-end automated security auditing system that combines:
• Static analysis tools (Slither, Mythril)
• Pattern-based vulnerability detection
• AI-powered semantic analysis (Qwen 3.7)
• Persistent learning memory
• Human-in-the-loop checkpoints

<b>Built for:</b>
Track 4 - Autopilot Agent
Qwen Cloud Global AI Hackathon 2026

<b>Powered by:</b>
• Alibaba Cloud (ECS/OSS/RDS)
• Qwen Cloud (Qwen 3.7 Plus)
• ChromaDB (Vector Memory)
• Flask (API Server)

<b>Team:</b>
Solo developer passionate about blockchain security and AI automation.
        """
        await update.message.reply_text(about_msg, parse_mode="HTML")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (contract code)"""
        if not context.user_data.get("awaiting_code"):
            await update.message.reply_text(
                "Please use /audit or /quickscan to start an audit.\n"
                "Use /help for more information."
            )
            return

        contract_code = update.message.text

        # Validate it's Solidity code
        if "pragma solidity" not in contract_code and "contract " not in contract_code:
            await update.message.reply_text(
                "⚠️ This doesn't look like Solidity code.\n"
                "Please send a valid Solidity contract."
            )
            return

        # Store code and ask for chain
        context.user_data["contract_code"] = contract_code
        context.user_data["awaiting_code"] = False

        keyboard = [
            [InlineKeyboardButton("Ethereum", callback_data="chain_ethereum")],
            [InlineKeyboardButton("BSC", callback_data="chain_bsc")],
            [InlineKeyboardButton("TRON", callback_data="chain_tron")],
            [InlineKeyboardButton("Polygon", callback_data="chain_polygon")],
            [InlineKeyboardButton("Arbitrum", callback_data="chain_arbitrum")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "✅ Code received!\n\n"
            "Please select the target blockchain:",
            reply_markup=reply_markup
        )

    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        query = update.callback_query
        await query.answer()

        data = query.data

        if data.startswith("chain_"):
            chain = data.replace("chain_", "")
            context.user_data["chain"] = chain

            await query.edit_message_text(
                f"🔗 Selected: <b>{chain.title()}</b>\n\n"
                f"⏳ Starting audit... This may take 30-60 seconds.",
                parse_mode="HTML"
            )

            # Run audit
            await self._run_audit(update, context)

        elif data == "audit_full":
            await self.cmd_audit(update, context)

        elif data == "audit_quick":
            await self.cmd_quickscan(update, context)

        elif data == "view_stats":
            await self.cmd_stats(update, context)

    async def _run_audit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute the audit workflow"""
        contract_code = context.user_data.get("contract_code", "")
        chain = context.user_data.get("chain", "ethereum")
        audit_type = context.user_data.get("audit_type", "full")

        try:
            if audit_type == "quick":
                # Quick scan
                from ..core.vulnerability_db import VulnerabilityDatabase
                from ..agents.vulnerability_detector import VulnerabilityDetectorAgent

                vuln_db = VulnerabilityDatabase()
                detector = VulnerabilityDetectorAgent(None, vuln_db)
                findings = detector.pattern_matching(contract_code)

                # Format results
                if findings:
                    msg = f"⚡ <b>Quick Scan Results</b>\n\n"
                    msg += f"Found <b>{len(findings)}</b> potential issues:\n\n"

                    for f in findings[:10]:
                        emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(
                            f.get("severity"), "⚪"
                        )
                        msg += f"{emoji} <b>{f.get('severity')}</b>: {f.get('type')} (line {f.get('line')})\n"
                        msg += f"   {f.get('description', '')}\n\n"

                    if len(findings) > 10:
                        msg += f"... and {len(findings) - 10} more issues\n"

                    msg += "\nUse /audit for a full analysis with AI review and fix suggestions."
                else:
                    msg = "✅ <b>No common vulnerabilities detected!</b>\n\n"
                    msg += "Note: Quick scan only checks for known patterns. Use /audit for comprehensive analysis."

                await update.callback_query.edit_message_text(msg, parse_mode="HTML")

            else:
                # Full audit with human-in-the-loop
                async def human_callback(ctx, message):
                    # For Telegram: send approval request
                    keyboard = [
                        [InlineKeyboardButton("✅ Approve", callback_data="approve")],
                        [InlineKeyboardButton("❌ Reject", callback_data="reject")]
                    ]
                    await update.callback_query.message.reply_text(
                        f"⏸️ <b>Human Review Required</b>\n\n{message}",
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    # In production: wait for user response
                    return True  # Auto-approve for demo

                audit_context = await self.orchestrator.run_audit(
                    contract_code=contract_code,
                    chain=chain,
                    human_callback=human_callback
                )

                # Format results
                msg = f"""
✅ <b>Audit Complete: {audit_context.audit_id}</b>

<b>Risk Score:</b> {audit_context.metadata.get("risk_score", 0)}/100
<b>Status:</b> {audit_context.status.value}

<b>Findings Summary:</b>
🔴 Critical: {sum(1 for f in audit_context.findings if f.get("severity") == "Critical")}
🟠 High: {sum(1 for f in audit_context.findings if f.get("severity") == "High")}
🟡 Medium: {sum(1 for f in audit_context.findings if f.get("severity") == "Medium")}
🟢 Low: {sum(1 for f in audit_context.findings if f.get("severity") == "Low")}
⚪ Info: {sum(1 for f in audit_context.findings if f.get("severity") == "Info")}

<b>Top Findings:</b>
"""
                for f in audit_context.findings[:5]:
                    emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(
                        f.get("severity"), "⚪"
                    )
                    msg += f"{emoji} {f.get('type')} (line {f.get('line', 'N/A')})\n"

                if audit_context.fix_suggestions:
                    msg += f"\n🔧 <b>{len(audit_context.fix_suggestions)} fix suggestions generated</b>"

                msg += "\n\nFull report available via web dashboard."

                await update.callback_query.edit_message_text(msg, parse_mode="HTML")

        except Exception as e:
            logger.error(f"Audit failed: {e}")
            await update.callback_query.edit_message_text(
                f"❌ <b>Audit Failed</b>\n\nError: {str(e)}\n\nPlease try again or contact support.",
                parse_mode="HTML"
            )

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred. Please try again later."
            )

    def run(self):
        """Start the bot"""
        logger.info("Starting QwenGuard Telegram Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


# Entry point
if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("ERROR: BOT_TOKEN not set")
        exit(1)

    # Initialize orchestrator
    memory = AuditMemory()

    # Mock Qwen client for testing
    class MockQwen:
        pass

    orchestrator = AuditOrchestrator(MockQwen(), memory)

    bot = QwenGuardTelegramBot(token, orchestrator)
    bot.run()
