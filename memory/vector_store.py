"""
═══════════════════════════════════════════════════════════════
Audit Memory System - Persistent memory for cross-session learning
Uses ChromaDB for vector storage of audit patterns
═══════════════════════════════════════════════════════════════
"""
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class AuditMemory:
    """
    Persistent memory system for storing and retrieving audit patterns.
    Enables the agent to learn from past audits and improve over time.
    """

    def __init__(self, persist_dir: str = "./memory_db"):
        self.persist_dir = persist_dir
        self.collection = None
        self.embedding_model = None

        if CHROMADB_AVAILABLE:
            self._init_chroma()

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._init_embeddings()

    def _init_chroma(self):
        """Initialize ChromaDB vector store"""
        try:
            self.client = chromadb.Client(Settings(
                persist_directory=self.persist_dir,
                anonymized_telemetry=False
            ))

            self.collection = self.client.get_or_create_collection(
                name="audit_patterns",
                metadata={"description": "Smart contract audit patterns and findings"}
            )
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")

    def _init_embeddings(self):
        """Initialize sentence transformer for embeddings"""
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded")
        except Exception as e:
            logger.error(f"Embedding model loading failed: {e}")

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        if self.embedding_model:
            return self.embedding_model.encode(text).tolist()

        # Fallback: simple hash-based embedding
        hash_val = hashlib.md5(text.encode()).hexdigest()
        return [int(hash_val[i:i+2], 16) / 255.0 for i in range(0, 64, 2)]

    def _generate_id(self, audit_id: str) -> str:
        """Generate unique document ID"""
        return f"audit_{audit_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    async def store_audit(self, context) -> bool:
        """Store audit results in memory for future reference"""
        if not self.collection:
            logger.warning("Memory store not available")
            return False

        try:
            # Create searchable text from findings
            findings_text = "\n".join([
                f"{f.get('severity')} {f.get('type')}: {f.get('description', '')}"
                for f in context.findings
            ])

            # Create embedding
            embedding = self._generate_embedding(findings_text)

            # Store document
            doc_id = self._generate_id(context.audit_id)
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[findings_text],
                metadatas=[{
                    "audit_id": context.audit_id,
                    "chain": context.chain,
                    "risk_score": context.metadata.get("risk_score", 0),
                    "contract_type": context.metadata.get("code_analysis", {}).get("contract_type", "unknown"),
                    "timestamp": datetime.now().isoformat(),
                    "finding_count": len(context.findings),
                    "critical_count": sum(1 for f in context.findings if f.get("severity") == "Critical")
                }]
            )

            logger.info(f"Audit {context.audit_id} stored in memory")
            return True

        except Exception as e:
            logger.error(f"Failed to store audit: {e}")
            return False

    async def get_similar_audits(self, contract_code: str, n_results: int = 5) -> List[Dict]:
        """Retrieve similar past audits based on code patterns"""
        if not self.collection:
            return []

        try:
            # Generate embedding for query code
            query_embedding = self._generate_embedding(contract_code[:2000])

            # Search similar audits
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["metadatas", "documents", "distances"]
            )

            similar_audits = []
            for i in range(len(results["ids"][0])):
                similar_audits.append({
                    "audit_id": results["metadatas"][0][i].get("audit_id"),
                    "chain": results["metadatas"][0][i].get("chain"),
                    "risk_score": results["metadatas"][0][i].get("risk_score"),
                    "contract_type": results["metadatas"][0][i].get("contract_type"),
                    "similarity": 1 - results["distances"][0][i],
                    "pattern": results["documents"][0][i][:200]
                })

            return similar_audits

        except Exception as e:
            logger.error(f"Similar audit retrieval failed: {e}")
            return []

    async def get_audit_history(self, chain: Optional[str] = None,
                                 min_risk: int = 0) -> List[Dict]:
        """Get audit history with optional filters"""
        if not self.collection:
            return []

        try:
            where_filter = {"risk_score": {"$gte": min_risk}}
            if chain:
                where_filter["chain"] = chain

            results = self.collection.get(
                where=where_filter,
                include=["metadatas"]
            )

            return [
                {
                    "audit_id": meta.get("audit_id"),
                    "chain": meta.get("chain"),
                    "risk_score": meta.get("risk_score"),
                    "timestamp": meta.get("timestamp"),
                    "finding_count": meta.get("finding_count")
                }
                for meta in results["metadatas"]
            ]

        except Exception as e:
            logger.error(f"Audit history retrieval failed: {e}")
            return []

    async def forget_outdated(self, days: int = 90) -> int:
        """Remove audits older than specified days (timely forgetting)"""
        if not self.collection:
            return 0

        try:
            from datetime import timedelta
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()

            results = self.collection.get(
                where={"timestamp": {"$lt": cutoff}}
            )

            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info(f"Forgot {len(results['ids'])} outdated audits")
                return len(results["ids"])

            return 0

        except Exception as e:
            logger.error(f"Forget operation failed: {e}")
            return 0

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        if not self.collection:
            return {"status": "unavailable"}

        try:
            count = self.collection.count()
            return {
                "status": "active",
                "total_audits_stored": count,
                "persist_dir": self.persist_dir,
                "embedding_model": "sentence-transformers" if self.embedding_model else "hash-based",
                "vector_db": "chroma"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
