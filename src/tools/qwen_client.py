"""
═══════════════════════════════════════════════════════════════
SentinelQwen - Qwen Cloud API Client
Real implementation using DashScope SDK
═══════════════════════════════════════════════════════════════
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any

# Try to import dashscope
try:
    import dashscope
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    logging.warning("dashscope not installed. Run: pip install dashscope")

logger = logging.getLogger(__name__)

class QwenClient:
    """
    Real Qwen Cloud API Client
    Uses DashScope SDK to call Qwen3.7-Plus
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "qwen3.7-plus"):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.model = model or os.getenv("QWEN_MODEL", "qwen3.7-plus")

        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY not provided. Get one at https://home.qwencloud.com/api-keys")

        if DASHSCOPE_AVAILABLE:
            dashscope.api_key = self.api_key

        logger.info(f"QwenClient initialized with model: {self.model}")

    async def chat(self, messages: List[Dict[str, str]], 
                   temperature: float = 0.1,
                   max_tokens: int = 4000,
                   **kwargs) -> Dict[str, Any]:
        """
        Send chat completion request to Qwen API

        Args:
            messages: List of {"role": "user/system/assistant", "content": "..."}
            temperature: 0.0-1.0, lower = more deterministic
            max_tokens: Maximum output tokens

        Returns:
            Response dict with choices, usage, etc.
        """
        if not DASHSCOPE_AVAILABLE:
            raise RuntimeError("dashscope not installed. Run: pip install dashscope")

        try:
            response = Generation.call(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                result_format="message",
                **kwargs
            )

            if response.status_code == 200:
                return {
                    "choices": [{
                        "message": {
                            "content": response.output.choices[0].message.content,
                            "role": response.output.choices[0].message.role
                        },
                        "finish_reason": response.output.choices[0].finish_reason
                    }],
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "model": self.model
                }
            else:
                logger.error(f"Qwen API error: {response.status_code} - {response.message}")
                raise RuntimeError(f"Qwen API error: {response.message}")

        except Exception as e:
            logger.error(f"Qwen API call failed: {e}")
            raise

    async def analyze_contract(self, contract_code: str, chain: str = "ethereum") -> Dict[str, Any]:
        """
        Specialized method for smart contract analysis

        Args:
            contract_code: Solidity source code
            chain: Target blockchain

        Returns:
            Analysis results as dict
        """
        system_prompt = """You are an expert smart contract security auditor with 10+ years of experience.
Analyze the provided Solidity code for vulnerabilities, gas inefficiencies, and best practice violations.
Provide structured output in JSON format."""

        user_prompt = f"""Analyze the following {chain} smart contract for security vulnerabilities:

```solidity
{contract_code[:80000]}  # Qwen3.7-Plus supports up to 991K input
```

Provide your analysis in this JSON format:
{{
    "vulnerabilities": [
        {{
            "type": "Vulnerability Name",
            "severity": "Critical|High|Medium|Low|Info",
            "line": 42,
            "description": "Detailed description",
            "impact": "What could happen",
            "recommendation": "How to fix",
            "code_example": "Secure code example"
        }}
    ],
    "gas_issues": [
        {{
            "location": "function name or line",
            "issue": "Description",
            "savings": "Estimated gas savings"
        }}
    ],
    "architecture_review": "Overall architecture assessment",
    "risk_score": 0-100,
    "confidence": "high|medium|low"
}}

Respond ONLY with valid JSON."""

        response = await self.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=6000
        )

        content = response["choices"][0]["message"]["content"]

        # Extract JSON from response
        try:
            # Find JSON block
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            else:
                return {"error": "No JSON found", "raw_response": content}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {"error": "Invalid JSON", "raw_response": content}

    async def generate_fix(self, vulnerable_code: str, vulnerability_type: str, 
                          description: str) -> str:
        """Generate secure fix for a vulnerability"""

        prompt = f"""Fix the following {vulnerability_type} vulnerability in Solidity:

Vulnerability: {description}

Code:
```solidity
{vulnerable_code}
```

Provide ONLY the fixed code block, no explanations."""

        response = await self.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=3000
        )

        return response["choices"][0]["message"]["content"]

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            "model": self.model,
            "api_key_set": bool(self.api_key),
            "dashscope_available": DASHSCOPE_AVAILABLE
        }


# Backward compatibility wrapper
class MockQwenClient:
    """Mock client for testing without API calls"""

    async def chat(self, **kwargs):
        class MockResponse:
            class Choice:
                class Message:
                    content = json.dumps({
                        "vulnerabilities": [],
                        "gas_issues": [],
                        "architecture_review": "Mock analysis - no API key",
                        "risk_score": 0,
                        "confidence": "low"
                    })
                    role = "assistant"
            choices = [Choice()]
            usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        return MockResponse()

    async def analyze_contract(self, contract_code: str, chain: str = "ethereum"):
        return {
            "vulnerabilities": [],
            "gas_issues": [],
            "architecture_review": "Mock analysis - install dashscope and set DASHSCOPE_API_KEY",
            "risk_score": 0,
            "confidence": "low"
        }


def get_qwen_client() -> QwenClient:
    """Factory function to get configured Qwen client"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    model = os.getenv("QWEN_MODEL", "qwen3.7-plus")

    if api_key and DASHSCOPE_AVAILABLE:
        return QwenClient(api_key=api_key, model=model)
    else:
        logger.warning("Using mock Qwen client. Set DASHSCOPE_API_KEY for real API.")
        return MockQwenClient()
