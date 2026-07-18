"""
═══════════════════════════════════════════════════════════════
SentinelQwen - Unit Tests
═══════════════════════════════════════════════════════════════
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.vulnerability_db import VulnerabilityDatabase, VulnerabilityType, Severity

class TestVulnerabilityDatabase:
    """Test vulnerability database"""

    def test_load_all_vulnerabilities(self):
        db = VulnerabilityDatabase()
        vulns = db.get_all()
        assert len(vulns) >= 14  # At least 14 vulnerability types

    def test_get_by_severity(self):
        db = VulnerabilityDatabase()
        critical = db.get_by_severity(Severity.CRITICAL)
        assert len(critical) >= 4  # At least 4 critical

        high = db.get_by_severity(Severity.HIGH)
        assert len(high) >= 4  # At least 4 high

    def test_get_by_swc(self):
        db = VulnerabilityDatabase()
        reentrancy = db.get_by_swc("SWC-107")
        assert reentrancy is not None
        assert reentrancy.type == VulnerabilityType.REENTRANCY

    def test_critical_count(self):
        db = VulnerabilityDatabase()
        assert db.get_critical_count() >= 4

    def test_high_count(self):
        db = VulnerabilityDatabase()
        assert db.get_high_count() >= 4

class TestPatternDetection:
    """Test pattern-based vulnerability detection"""

    def test_reentrancy_detection(self):
        from agents.vulnerability_detector import VulnerabilityDetectorAgent

        db = VulnerabilityDatabase()
        detector = VulnerabilityDetectorAgent(None, db)

        vulnerable_code = """
        function withdraw() public {
            uint amount = balances[msg.sender];
            (bool success, ) = msg.sender.call{value: amount}("");
            require(success);
            balances[msg.sender] = 0;
        }
        """

        findings = detector.pattern_matching(vulnerable_code)
        reentrancy = [f for f in findings if f["type"] == "Reentrancy"]
        assert len(reentrancy) > 0

    def test_tx_origin_detection(self):
        from agents.vulnerability_detector import VulnerabilityDetectorAgent

        db = VulnerabilityDatabase()
        detector = VulnerabilityDetectorAgent(None, db)

        vulnerable_code = """
        modifier onlyOwner() {
            require(tx.origin == owner);
            _;
        }
        """

        findings = detector.pattern_matching(vulnerable_code)
        tx_origin = [f for f in findings if "tx.origin" in f["type"]]
        assert len(tx_origin) > 0

    def test_protected_reentrancy_not_detected(self):
        from agents.vulnerability_detector import VulnerabilityDetectorAgent

        db = VulnerabilityDatabase()
        detector = VulnerabilityDetectorAgent(None, db)

        safe_code = """
        function withdraw() public nonReentrant {
            uint amount = balances[msg.sender];
            balances[msg.sender] = 0;
            (bool success, ) = msg.sender.call{value: amount}("");
            require(success);
        }
        """

        findings = detector.pattern_matching(safe_code)
        reentrancy = [f for f in findings if f["type"] == "Reentrancy"]
        assert len(reentrancy) == 0  # Should not detect due to nonReentrant

class TestAPI:
    """Test Flask API endpoints"""

    def test_health_endpoint(self):
        from api.server import app
        client = app.test_client()
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"

    def test_chains_endpoint(self):
        from api.server import app
        client = app.test_client()
        response = client.get('/api/v1/chains')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["chains"]) == 5

    def test_vulnerabilities_endpoint(self):
        from api.server import app
        client = app.test_client()
        response = client.get('/api/v1/vulnerabilities')
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] >= 14

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
