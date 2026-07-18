"""
═══════════════════════════════════════════════════════════════
Fix Suggester Agent - AI-powered vulnerability remediation
Generates secure code fixes using Qwen Cloud
═══════════════════════════════════════════════════════════════
"""
import json
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class FixSuggesterAgent:
    """Agent for generating secure code fixes"""

    def __init__(self, qwen_client):
        self.qwen = qwen_client

    async def generate_fixes(self, contract_code: str, 
                            findings: List[Dict],
                            qwen_client) -> List[Dict]:
        """Generate fix suggestions for all findings"""
        fixes = []

        for finding in findings:
            fix = await self._generate_single_fix(
                contract_code, finding, qwen_client
            )
            if fix:
                fixes.append(fix)

        return fixes

    async def _generate_single_fix(self, contract_code: str,
                                    finding: Dict,
                                    qwen_client) -> Optional[Dict]:
        """Generate a fix for a single vulnerability"""

        vuln_type = finding.get("type", "")
        severity = finding.get("severity", "")
        line = finding.get("line", 0)
        description = finding.get("description", "")

        prompt = f"""You are an expert Solidity security developer. Fix the following vulnerability.

Vulnerability: {vuln_type}
Severity: {severity}
Location: Line ~{line}
Description: {description}

Original Contract Code:
```solidity
{contract_code[:8000]}
```

Provide:
1. The exact vulnerable code snippet (3-5 lines)
2. The fixed secure code snippet
3. Explanation of the fix
4. Any additional security measures needed

Format as JSON:
{{
    "vulnerability_type": "{vuln_type}",
    "severity": "{severity}",
    "original_code": "vulnerable code here",
    "fixed_code": "secure code here",
    "explanation": "Why this fixes the issue",
    "additional_measures": ["Any extra security steps"],
    "gas_impact": "Impact on gas usage",
    "confidence": "high/medium/low"
}}

Respond ONLY with JSON."""

        try:
            response = await qwen_client.chat.completions.create(
                model="qwen3.7-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=3000
            )

            content = response.choices[0].message.content
            json_match = json.loads(content[content.find("{"):content.rfind("}")+1])

            if json_match:
                return {
                    **json_match,
                    "finding_id": finding.get("type", "") + str(line)
                }

        except Exception as e:
            logger.error(f"Fix generation failed for {vuln_type}: {e}")

        return None

    async def generate_patched_contract(self, contract_code: str,
                                        fixes: List[Dict],
                                        qwen_client) -> str:
        """Generate a fully patched version of the contract"""

        fixes_summary = "\n\n".join([
            f"Fix {i+1}: {f.get('vulnerability_type')}\n"
            f"Original: {f.get('original_code', 'N/A')}\n"
            f"Fixed: {f.get('fixed_code', 'N/A')}"
            for i, f in enumerate(fixes)
        ])

        prompt = f"""Apply the following security fixes to the contract and return the complete patched code.

Original Contract:
```solidity
{contract_code}
```

Fixes to apply:
{fixes_summary}

Return ONLY the complete patched Solidity contract code, with all fixes applied. No explanations."""

        try:
            response = await qwen_client.chat.completions.create(
                model="qwen3.7-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=6000
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Patched contract generation failed: {e}")
            return contract_code  # Return original if patching fails
