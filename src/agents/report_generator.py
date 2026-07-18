"""
═══════════════════════════════════════════════════════════════
Report Generator Agent - Professional audit report creation
Generates HTML/PDF reports with visualizations
═══════════════════════════════════════════════════════════════
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ReportGeneratorAgent:
    """Agent for generating comprehensive audit reports"""

    def __init__(self, qwen_client):
        self.qwen = qwen_client

    async def generate(self, context, revision_notes: Optional[str] = None) -> str:
        """Generate complete audit report"""

        # Build report sections
        sections = []

        # Executive Summary
        sections.append(self._generate_executive_summary(context))

        # Risk Overview
        sections.append(self._generate_risk_overview(context))

        # Detailed Findings
        sections.append(self._generate_findings_section(context))

        # Fix Suggestions
        if context.fix_suggestions:
            sections.append(self._generate_fixes_section(context))

        # AI Analysis
        if context.ai_analysis:
            sections.append(self._generate_ai_analysis_section(context))

        # Appendices
        sections.append(self._generate_appendices(context))

        # Combine into full report
        report = self._compile_report(sections, context, revision_notes)

        return report

    def _generate_executive_summary(self, context) -> str:
        """Generate executive summary section"""
        risk_level = self._get_risk_level(context.metadata.get("risk_score", 0))
        critical_count = context.metadata.get("critical_count", 0)
        total_findings = len(context.findings)

        return f"""
# Smart Contract Security Audit Report

**Audit ID:** {context.audit_id}  
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}  
**Chain:** {context.chain.title()}  
**Contract Type:** {context.metadata.get("code_analysis", {}).get("contract_type", "Unknown")}  
**Overall Risk:** {risk_level}

## Executive Summary

This audit analyzed a smart contract deployed on {context.chain.title()}.

- **Total Findings:** {total_findings}
- **Critical:** {critical_count}
- **High:** {sum(1 for f in context.findings if f.get("severity") == "High")}
- **Medium:** {sum(1 for f in context.findings if f.get("severity") == "Medium")}
- **Low:** {sum(1 for f in context.findings if f.get("severity") == "Low")}
- **Informational:** {sum(1 for f in context.findings if f.get("severity") == "Info")}

**Risk Score:** {context.metadata.get("risk_score", 0)}/100

**Recommendation:** {"IMMEDIATE ACTION REQUIRED" if critical_count > 0 else "Address findings before deployment" if total_findings > 0 else "Contract appears secure"}
"""

    def _generate_risk_overview(self, context) -> str:
        """Generate risk overview with visual indicators"""
        score = context.metadata.get("risk_score", 0)

        risk_bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))

        return f"""
## Risk Overview

```
Risk Score: [{risk_bar}] {score}/100
```

| Severity | Count | Status |
|----------|-------|--------|
| 🔴 Critical | {sum(1 for f in context.findings if f.get("severity") == "Critical")} | {"⚠️ Requires immediate fix" if any(f.get("severity") == "Critical" for f in context.findings) else "✅ None found"} |
| 🟠 High | {sum(1 for f in context.findings if f.get("severity") == "High")} | {"⚠️ Should be fixed" if any(f.get("severity") == "High" for f in context.findings) else "✅ None found"} |
| 🟡 Medium | {sum(1 for f in context.findings if f.get("severity") == "Medium")} | {"ℹ️ Review recommended" if any(f.get("severity") == "Medium" for f in context.findings) else "✅ None found"} |
| 🟢 Low | {sum(1 for f in context.findings if f.get("severity") == "Low")} | {"ℹ️ Minor issues" if any(f.get("severity") == "Low" for f in context.findings) else "✅ None found"} |
| ⚪ Info | {sum(1 for f in context.findings if f.get("severity") == "Info")} | ℹ️ Suggestions |
"""

    def _generate_findings_section(self, context) -> str:
        """Generate detailed findings section"""
        sections = ["## Detailed Findings\n"]

        for i, finding in enumerate(context.findings, 1):
            severity_emoji = {
                "Critical": "🔴", "High": "🟠", "Medium": "🟡",
                "Low": "🟢", "Info": "⚪"
            }.get(finding.get("severity"), "⚪")

            sections.append(f"""
### {severity_emoji} Finding #{i}: {finding.get("type", "Unknown")}

**Severity:** {finding.get("severity", "Unknown")}  
**Line:** {finding.get("line", "N/A")}  
**Detection Method:** {finding.get("detection_method", "Unknown")}  
**Confidence:** {finding.get("confidence", "Unknown")}

**Description:**
{finding.get("description", "No description available")}

**Code Snippet:**
```solidity
{finding.get("code_snippet", "N/A")}
```

**Context:**
```solidity
{finding.get("context", "N/A")}
```
""")

        return "\n".join(sections)

    def _generate_fixes_section(self, context) -> str:
        """Generate fix suggestions section"""
        sections = ["## Fix Suggestions\n"]

        for i, fix in enumerate(context.fix_suggestions, 1):
            sections.append(f"""
### Fix #{i}: {fix.get("vulnerability_type", "Unknown")}

**Severity:** {fix.get("severity", "Unknown")}  
**Confidence:** {fix.get("confidence", "Unknown")}  
**Gas Impact:** {fix.get("gas_impact", "Unknown")}

**Vulnerable Code:**
```solidity
{fix.get("original_code", "N/A")}
```

**Fixed Code:**
```solidity
{fix.get("fixed_code", "N/A")}
```

**Explanation:**
{fix.get("explanation", "No explanation available")}

**Additional Measures:**
{"\n".join(f"- {m}" for m in fix.get("additional_measures", []))}
""")

        return "\n".join(sections)

    def _generate_ai_analysis_section(self, context) -> str:
        """Generate AI deep analysis section"""
        ai = context.ai_analysis

        return f"""
## AI Deep Analysis (Qwen 3.7)

**Confidence Score:** {ai.get("confidence_score", 0)}/100

### Advanced Attack Vectors
{"\n".join(f"- {v}" for v in ai.get("advanced_attack_vectors", []))}

### Business Logic Flaws
{"\n".join(f"- {f}" for f in ai.get("business_logic_flaws", []))}

### Economic Security
{ai.get("economic_security", "N/A")}

### Cross-Contract Risks
{"\n".join(f"- {r}" for r in ai.get("cross_contract_risks", []))}

### Gas Optimization Opportunities
{"\n".join(f"- {o}" for o in ai.get("gas_optimization_opportunities", []))}

### Overall Security Posture
{ai.get("overall_security_posture", "N/A")}
"""

    def _generate_appendices(self, context) -> str:
        """Generate appendices with technical details"""
        analysis = context.metadata.get("code_analysis", {})

        return f"""
## Appendices

### A. Contract Metrics
| Metric | Value |
|--------|-------|
| Lines of Code | {analysis.get("lines_of_code", "N/A")} |
| Functions | {analysis.get("functions", "N/A")} |
| Modifiers | {analysis.get("modifiers", "N/A")} |
| Events | {analysis.get("events", "N/A")} |
| Mappings | {analysis.get("mappings", "N/A")} |
| External Calls | {analysis.get("external_calls", "N/A")} |
| Complexity Score | {analysis.get("complexity", "N/A")} |
| Solidity Version | {analysis.get("pragma_version", "N/A")} |

### B. Audit Methodology
1. **Static Analysis** - Automated tool scanning (Slither, Mythril)
2. **Pattern Matching** - Rule-based vulnerability detection
3. **AI Semantic Analysis** - Qwen 3.7 deep code understanding
4. **Cross-Reference** - Historical audit pattern matching
5. **Manual Review** - Human expert validation

### C. Disclaimer
This audit report is provided for informational purposes only. It does not constitute financial or legal advice. The findings represent the best effort of automated tools and AI analysis but may not identify all vulnerabilities. A manual security review by experienced auditors is always recommended before deployment.

---
*Report generated by SentinelQwen - Autopilot Security Auditor*  
*Powered by Qwen Cloud & Alibaba Cloud*
"""

    def _compile_report(self, sections: List[str], context, revision_notes: Optional[str]) -> str:
        """Compile all sections into final report"""
        header = f"""<!--
SentinelQwen Security Audit Report
Audit ID: {context.audit_id}
Generated: {datetime.now().isoformat()}
-->
"""

        if revision_notes:
            header += f"""
> **Revision Notes:** {revision_notes}

"""

        return header + "\n\n---\n\n".join(sections)

    def _get_risk_level(self, score: int) -> str:
        """Convert numeric score to risk level"""
        if score >= 75:
            return "🔴 CRITICAL"
        elif score >= 50:
            return "🟠 HIGH"
        elif score >= 25:
            return "🟡 MEDIUM"
        elif score > 0:
            return "🟢 LOW"
        return "✅ SAFE"
