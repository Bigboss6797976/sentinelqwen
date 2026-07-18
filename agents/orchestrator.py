"""
═══════════════════════════════════════════════════════════════
Audit Orchestrator - Central workflow controller
Manages the end-to-end audit pipeline with human-in-the-loop
═══════════════════════════════════════════════════════════════
"""
import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

from .code_analyzer import CodeAnalyzerAgent
from .vulnerability_detector import VulnerabilityDetectorAgent
from .report_generator import ReportGeneratorAgent
from .fix_suggester import FixSuggesterAgent
from ..memory.vector_store import AuditMemory
from ..tools.qwen_client import QwenClient, get_qwen_client
from ..core.vulnerability_db import VulnerabilityDatabase, Severity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditStage(Enum):
    INIT = "initialization"
    CODE_ANALYSIS = "code_analysis"
    VULNERABILITY_SCAN = "vulnerability_scan"
    AI_REVIEW = "ai_review"
    FIX_SUGGESTION = "fix_suggestion"
    REPORT_GENERATION = "report_generation"
    HUMAN_REVIEW = "human_review"
    COMPLETE = "complete"

class AuditStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_HUMAN = "waiting_human"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AuditContext:
    """Context maintained across the audit workflow"""
    contract_code: str
    contract_address: Optional[str] = None
    chain: str = "ethereum"
    compiler_version: Optional[str] = None
    audit_id: str = ""
    stage: AuditStage = AuditStage.INIT
    status: AuditStatus = AuditStatus.PENDING
    findings: List[Dict] = field(default_factory=list)
    ai_analysis: Dict = field(default_factory=dict)
    fix_suggestions: List[Dict] = field(default_factory=list)
    report: Optional[str] = None
    human_approvals: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)

class AuditOrchestrator:
    """
    End-to-end autonomous audit orchestrator.
    Handles ambiguous inputs, invokes external tools, 
    and incorporates human-in-the-loop at critical checkpoints.
    """

    def __init__(self, qwen_client, memory_store: AuditMemory):
        self.qwen = qwen_client
        self.memory = memory_store
        self.vuln_db = VulnerabilityDatabase()

        # Initialize agents
        self.code_analyzer = CodeAnalyzerAgent(qwen_client)
        self.vuln_detector = VulnerabilityDetectorAgent(qwen_client, self.vuln_db)
        self.report_gen = ReportGeneratorAgent(qwen_client)
        self.fix_suggester = FixSuggesterAgent(qwen_client)

        # Human-in-the-loop checkpoints
        self.critical_checkpoints = {
            AuditStage.VULNERABILITY_SCAN: "Critical vulnerabilities detected - human review required",
            AuditStage.FIX_SUGGESTION: "Fix suggestions ready - approve before applying?",
            AuditStage.REPORT_GENERATION: "Final report ready - confirm before publishing?"
        }

        logger.info("AuditOrchestrator initialized with 4 agents")

    async def run_audit(self, contract_code: str, 
                       contract_address: Optional[str] = None,
                       chain: str = "ethereum",
                       human_callback: Optional[callable] = None) -> AuditContext:
        """
        Main entry point: Run complete autonomous audit workflow.

        Args:
            contract_code: Solidity source code
            contract_address: Optional deployed address for live analysis
            chain: Target blockchain (ethereum, bsc, tron, polygon, arbitrum)
            human_callback: Function to call for human approval at checkpoints

        Returns:
            AuditContext with complete audit results
        """
        context = AuditContext(
            contract_code=contract_code,
            contract_address=contract_address,
            chain=chain,
            audit_id=self._generate_audit_id()
        )

        logger.info(f"Starting audit {context.audit_id} for {chain}")

        try:
            # Stage 1: Code Analysis
            context = await self._stage_code_analysis(context)

            # Stage 2: Vulnerability Detection (Static + AI)
            context = await self._stage_vulnerability_scan(context)

            # Checkpoint: Human review if critical findings
            if self._has_critical_findings(context) and human_callback:
                context.status = AuditStatus.WAITING_HUMAN
                approved = await human_callback(context, self.critical_checkpoints[AuditStage.VULNERABILITY_SCAN])
                if not approved:
                    logger.warning("Human rejected vulnerability findings")
                    return context
                context.status = AuditStatus.RUNNING

            # Stage 3: AI Deep Review
            context = await self._stage_ai_review(context)

            # Stage 4: Fix Suggestions
            context = await self._stage_fix_suggestions(context)

            # Checkpoint: Human approval for fixes
            if human_callback and context.fix_suggestions:
                approved = await human_callback(context, self.critical_checkpoints[AuditStage.FIX_SUGGESTION])
                if not approved:
                    logger.info("Human chose to skip fix suggestions")
                    context.fix_suggestions = []

            # Stage 5: Report Generation
            context = await self._stage_report_generation(context)

            # Final Checkpoint
            if human_callback:
                approved = await human_callback(context, self.critical_checkpoints[AuditStage.REPORT_GENERATION])
                if not approved:
                    logger.info("Human requested report revision")
                    context = await self._stage_report_generation(context, revision=True)

            context.status = AuditStatus.COMPLETED
            context.stage = AuditStage.COMPLETE

            # Store in memory for future reference
            await self.memory.store_audit(context)

            logger.info(f"Audit {context.audit_id} completed successfully")

        except Exception as e:
            logger.error(f"Audit {context.audit_id} failed: {str(e)}")
            context.status = AuditStatus.FAILED
            context.metadata["error"] = str(e)

        return context

    async def _stage_code_analysis(self, context: AuditContext) -> AuditContext:
        """Stage 1: Analyze contract structure and complexity"""
        context.stage = AuditStage.CODE_ANALYSIS
        logger.info(f"[{context.audit_id}] Stage 1: Code Analysis")

        analysis = await self.code_analyzer.analyze(context.contract_code)
        context.metadata["code_analysis"] = analysis
        context.metadata["complexity_score"] = analysis.get("complexity", 0)
        context.metadata["function_count"] = analysis.get("functions", 0)

        return context

    async def _stage_vulnerability_scan(self, context: AuditContext) -> AuditContext:
        """Stage 2: Multi-layer vulnerability detection"""
        context.stage = AuditStage.VULNERABILITY_SCAN
        logger.info(f"[{context.audit_id}] Stage 2: Vulnerability Scan")

        # Layer 1: Static analysis (Slither)
        static_findings = await self.vuln_detector.static_analysis(
            context.contract_code, context.chain
        )

        # Layer 2: Pattern matching against vulnerability DB
        pattern_findings = self.vuln_detector.pattern_matching(
            context.contract_code
        )

        # Layer 3: AI-powered semantic analysis via Qwen
        ai_findings = await self.vuln_detector.ai_analysis(
            context.contract_code, context.chain, self.qwen
        )

        # Merge and deduplicate findings
        context.findings = self._merge_findings(static_findings, pattern_findings, ai_findings)

        # Risk scoring
        context.metadata["risk_score"] = self._calculate_risk_score(context.findings)
        context.metadata["critical_count"] = sum(1 for f in context.findings if f.get("severity") == "Critical")

        return context

    async def _stage_ai_review(self, context: AuditContext) -> AuditContext:
        """Stage 3: Deep AI review with Qwen for complex logic"""
        context.stage = AuditStage.AI_REVIEW
        logger.info(f"[{context.audit_id}] Stage 3: AI Deep Review")

        # Retrieve similar past audits from memory
        similar_audits = await self.memory.get_similar_audits(context.contract_code)

        context.ai_analysis = await self.code_analyzer.deep_ai_review(
            context.contract_code,
            context.findings,
            similar_audits,
            self.qwen
        )

        return context

    async def _stage_fix_suggestions(self, context: AuditContext) -> AuditContext:
        """Stage 4: Generate fix suggestions for all findings"""
        context.stage = AuditStage.FIX_SUGGESTION
        logger.info(f"[{context.audit_id}] Stage 4: Fix Suggestions")

        if not context.findings:
            return context

        context.fix_suggestions = await self.fix_suggester.generate_fixes(
            context.contract_code,
            context.findings,
            self.qwen
        )

        return context

    async def _stage_report_generation(self, context: AuditContext, revision: bool = False) -> AuditContext:
        """Stage 5: Generate comprehensive audit report"""
        context.stage = AuditStage.REPORT_GENERATION
        logger.info(f"[{context.audit_id}] Stage 5: Report Generation" + (" (Revision)" if revision else ""))

        context.report = await self.report_gen.generate(
            context,
            revision_notes=context.metadata.get("revision_notes") if revision else None
        )

        return context

    def _has_critical_findings(self, context: AuditContext) -> bool:
        """Check if any critical vulnerabilities were found"""
        return any(f.get("severity") == "Critical" for f in context.findings)

    def _merge_findings(self, *finding_lists: List[Dict]) -> List[Dict]:
        """Merge findings from multiple sources, deduplicate by location+type"""
        seen = set()
        merged = []
        for findings in finding_lists:
            for f in findings:
                key = f"{f.get('line', 0)}:{f.get('type', '')}"
                if key not in seen:
                    seen.add(key)
                    merged.append(f)
        return sorted(merged, key=lambda x: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}.get(x.get("severity", "Info"), 5))

    def _calculate_risk_score(self, findings: List[Dict]) -> float:
        """Calculate overall risk score 0-100"""
        weights = {"Critical": 25, "High": 10, "Medium": 3, "Low": 1, "Info": 0}
        score = sum(weights.get(f.get("severity", "Info"), 0) for f in findings)
        return min(score, 100)

    def _generate_audit_id(self) -> str:
        """Generate unique audit ID"""
        import uuid
        return f"AUD-{uuid.uuid4().hex[:8].upper()}"
