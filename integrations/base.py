"""
Base chain interface for multi-chain support
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

class BaseChain(ABC):
    """Abstract base class for blockchain integrations"""

    def __init__(self, rpc_url: str, chain_id: int):
        self.rpc_url = rpc_url
        self.chain_id = chain_id

    @abstractmethod
    async def get_contract_code(self, address: str) -> str:
        """Fetch contract source code from blockchain explorer"""
        pass

    @abstractmethod
    async def get_contract_abi(self, address: str) -> Optional[Dict]:
        """Fetch contract ABI"""
        pass

    @abstractmethod
    async def get_balance(self, address: str) -> float:
        """Get address balance"""
        pass

    @abstractmethod
    def get_explorer_url(self, address: str) -> str:
        """Get blockchain explorer URL for address"""
        pass
