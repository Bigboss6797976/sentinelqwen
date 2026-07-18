"""
═══════════════════════════════════════════════════════════════
Code Analyzer Agent - AI-powered contract analysis
Uses Qwen Cloud for semantic code understanding
═══════════════════════════════════════════════════════════════
"""
import re
import json
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class CodeAnalyzerAgent:
    """Agent for analyzing smart contract code structure and complexity"""

    def __init__(self, qwen_client):
        self.qwen = qwen_client

    async def analyze(self, contract_code: str) -> Dict[str, Any]:
        """Analyze contract structure, complexity, and key metrics"""

        # Static metrics
        metrics = self._calculate_metrics(contract_code)

        # AI-powered semantic analysis via Qwen
        ai_insights = await self._ai_semantic_analysis(contract_code)

        return {
            **metrics,
            **ai_insights
        }

    def _calculate_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate static code metrics"""
        lines = code.split("\n")

        # Count key elements
        functions = len(re.findall(r'\bfunction\b', code))
        modifiers = len(re.findall(r'\bmodifier\b', code))
        events = len(re.findall(r'\bevent\b', code))
        mappings = len(re.findall(r'\bmapping\b', code))
        requires = len(re.findall(r'\brequire\b', code))
        external_calls = len(re.findall(r'\.call\b|\.delegatecall\b|\.staticcall\b', code))

        # Complexity estimation
        complexity = (
            functions * 2 +
            modifiers * 3 +
            mappings * 1 +
            external_calls * 5
        )

        # Detect contract type
        contract_type = self._detect_contract_type(code)

        return {
            "lines_of_code": len(lines),
            "functions": functions,
            "modifiers": modifiers,
            "events": events,
            "mappings": mappings,
            "requires": requires,
            "external_calls": external_calls,
            "complexity": complexity,
            "contract_type": contract_type,
            "pragma_version": self._extract_pragma(code)
        }

    def _detect_contract_type(self, code: str) -> str:
        """Detect the type of smart contract"""
        code_lower = code.lower()

        if "erc20" in code_lower or "transfer" in code_lower and "balance" in code_lower:
            return "ERC20 Token"
        elif "erc721" in code_lower or "nft" in code_lower or "tokenuri" in code_lower:
            return "ERC721 NFT"
        elif "proxy" in code_lower or "upgradeable" in code_lower:
            return "Upgradeable Proxy"
        elif "stake" in code_lower or "reward" in code_lower:
            return "Staking/Yield"
        elif "swap" in code_lower or "amm" in code_lower or "dex" in code_lower:
            return "DEX/AMM"
        elif "lending" in code_lower or "borrow" in code_lower:
            return "Lending Protocol"
        elif "governance" in code_lower or "vote" in code_lower:
            return "Governance"
        else:
            return "General Contract"

    def _extract_pragma(self, code: str) -> Optional[str]:
        """Extract Solidity pragma version"""
        match = re.search(r'pragma\s+solidity\s+([^;]+);', code)
        return match.group(1).strip() if match else None

    async def _ai_semantic_analysis(self, code: str) -> Dict[str, Any]:
        """Use Qwen for deep semantic understanding of the contract"""

        prompt = f"""You are an expert smart contract auditor. Analyze the following Solidity contract and provide a structured analysis.

Contract Code:
```solidity
{code[:8000]}  # Truncate if too long
```

Provide your analysis in this exact JSON format:
{{
    "architecture_pattern": "Description of the contract architecture",
    "design_patterns": ["List of design patterns used"],
    "potential_risk_areas": ["High-level risk areas to investigate"],
    "external_dependencies": ["External contracts/libraries used"],
    "access_control_model": "How access control is implemented",
    "state_machine_complexity": "Simple/Moderate/Complex",
    "audit_focus_areas": ["Specific areas that need deep audit"]
}}

Respond ONLY with the JSON, no other text."""

        try:
            response = await self.qwen.chat.completions.create(
                model="qwen3.7-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )

            content = response.choices[0].message.content
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")

        return {
            "architecture_pattern": "Unknown",
            "design_patterns": [],
            "potential_risk_areas": ["Manual review required"],
            "external_dependencies": [],
            "access_control_model": "Unknown",
            "state_machine_complexity": "Unknown",
            "audit_focus_areas": ["Full manual audit recommended"]
        }

    async def deep_ai_review(self, contract_code: str, 
                            findings: List[Dict],
                            similar_audits: List[Dict],
                            qwen_client) -> Dict[str, Any]:
        """Deep AI review combining current findings with historical knowledge"""

        # Build context from similar audits
        historical_context = ""
        if similar_audits:
            historical_context = "\n\nHistorical similar audit patterns:\n"
            for audit in similar_audits[:3]:
                historical_context += f"- {audit.get('pattern', 'N/A')}: {audit.get('finding', 'N/A')}\n"

        findings_summary = "\n".join([
            f"- [{f.get('severity')}] {f.get('type')} at line {f.get('line', 'N/A')}: {f.get('description', 'N/A')}"
            for f in findings[:10]
        ])

        prompt = f"""You are an elite smart contract security researcher. Perform a deep security review.

Current Findings:
{findings_summary}

{historical_context}

Contract Code (truncated):
```solidity
{contract_code[:6000]}
```

Provide deep analysis in JSON format:
{{
    "advanced_attack_vectors": ["Sophisticated attack scenarios"],
    "business_logic_flaws": ["Logic errors that could be exploited"],
    "economic_security": "Tokenomics and economic attack analysis",
    "cross_contract_risks": ["Risks from external interactions"],
    "gas_optimization_opportunities": ["Specific gas savings"],
    "overall_security_posture": "Summary security assessment",
    "confidence_score": 0-100
}}

Respond ONLY with JSON."""

        try:
            response = await qwen_client.chat.completions.create(
                model="qwen3.7-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2500
            )

            content = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            logger.error(f"Deep AI review failed: {e}")

        return {
            "advanced_attack_vectors": ["Analysis failed - manual review required"],
            "business_logic_flaws": [],
            "economic_security": "Unknown",
            "cross_contract_risks": [],
            "gas_optimization_opportunities": [],
            "overall_security_posture": "Review incomplete",
            "confidence_score": 0
        }
