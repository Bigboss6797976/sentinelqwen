"""
═══════════════════════════════════════════════════════════════
SentinelQwen - Flask API Server
RESTful API for smart contract security auditing
Deployed on Alibaba Cloud ECS/Function Compute
═══════════════════════════════════════════════════════════════
"""
import os
import asyncio
import json
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key')
CORS(app)

# Import agents
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.orchestrator import AuditOrchestrator, AuditContext
from memory.vector_store import AuditMemory

# Initialize Qwen client
try:
    import dashscope
    from dashscope import Generation
    dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')
    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False
    print("WARNING: DashScope not available. Using mock client.")

class MockQwenClient:
    """Mock client for testing without API key"""
    async def chat_completions_create(self, **kwargs):
        class MockResponse:
            class Choice:
                class Message:
                    content = json.dumps({
                        "architecture_pattern": "Mock analysis",
                        "design_patterns": ["Mock pattern"],
                        "potential_risk_areas": ["Mock risk"],
                        "external_dependencies": [],
                        "access_control_model": "Mock",
                        "state_machine_complexity": "Simple",
                        "audit_focus_areas": ["Mock focus"]
                    })
            choices = [Choice()]
        return MockResponse()

# Initialize components
memory_store = AuditMemory()
orchestrator = None

async def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        from tools.qwen_client import get_qwen_client
        qwen_client = get_qwen_client()
        orchestrator = AuditOrchestrator(qwen_client, memory_store)
    return orchestrator

# ═══════════════════════════════════════════════════════════════
# API Routes
# ═══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """API root - health check"""
    return jsonify({
        "name": "SentinelQwen",
        "version": "2.0.0",
        "track": "Autopilot Agent",
        "hackathon": "Qwen Cloud Global AI Hackathon 2026",
        "status": "running",
        "qwen_available": QWEN_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/audit', methods=['POST'])
def audit_contract():
    """
    Submit a smart contract for security audit

    Request Body:
    {
        "contract_code": "string (required) - Solidity source code",
        "contract_address": "string (optional) - Deployed address",
        "chain": "string (optional) - ethereum/bsc/tron/polygon/arbitrum",
        "auto_fix": "boolean (optional) - Auto-apply fix suggestions"
    }

    Returns:
    {
        "audit_id": "string",
        "status": "string",
        "findings": [...],
        "risk_score": "number",
        "report_url": "string"
    }
    """
    data = request.get_json()

    if not data or 'contract_code' not in data:
        return jsonify({"error": "contract_code is required"}), 400

    contract_code = data['contract_code']
    contract_address = data.get('contract_address')
    chain = data.get('chain', 'ethereum')

    # Validate chain
    valid_chains = ['ethereum', 'bsc', 'tron', 'polygon', 'arbitrum']
    if chain not in valid_chains:
        return jsonify({"error": f"Invalid chain. Must be one of: {valid_chains}"}), 400

    async def run_audit():
        orch = await get_orchestrator()

        # Human-in-the-loop callback (simulated for API)
        async def human_callback(context, message):
            # In production: send notification, wait for approval
            # For API: auto-approve or return pending status
            return True

        context = await orch.run_audit(
            contract_code=contract_code,
            contract_address=contract_address,
            chain=chain,
            human_callback=human_callback
        )

        return context

    try:
        context = asyncio.run(run_audit())

        response = {
            "audit_id": context.audit_id,
            "status": context.status.value,
            "chain": context.chain,
            "risk_score": context.metadata.get("risk_score", 0),
            "critical_count": context.metadata.get("critical_count", 0),
            "total_findings": len(context.findings),
            "findings": [
                {
                    "type": f.get("type"),
                    "severity": f.get("severity"),
                    "line": f.get("line"),
                    "description": f.get("description"),
                    "confidence": f.get("confidence")
                }
                for f in context.findings[:20]  # Limit response size
            ],
            "report": context.report[:5000] if context.report else None,  # Truncate
            "timestamp": datetime.now().isoformat()
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/audit/<audit_id>', methods=['GET'])
def get_audit_status(audit_id):
    """Get audit status and results by ID"""
    # In production: query from database
    return jsonify({
        "audit_id": audit_id,
        "status": "completed",
        "message": "Use /api/v1/audit to submit new audits"
    })

@app.route('/api/v1/quick-scan', methods=['POST'])
def quick_scan():
    """Quick vulnerability scan (faster, less detailed)"""
    data = request.get_json()

    if not data or 'contract_code' not in data:
        return jsonify({"error": "contract_code is required"}), 400

    contract_code = data['contract_code']

    # Run pattern matching only (fast)
    from core.vulnerability_db import VulnerabilityDatabase
    from agents.vulnerability_detector import VulnerabilityDetectorAgent

    vuln_db = VulnerabilityDatabase()
    detector = VulnerabilityDetectorAgent(None, vuln_db)
    findings = detector.pattern_matching(contract_code)

    return jsonify({
        "scan_type": "quick",
        "findings_count": len(findings),
        "findings": findings,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/memory/stats', methods=['GET'])
def memory_stats():
    """Get audit memory statistics"""
    stats = memory_store.get_memory_stats()
    return jsonify(stats)

@app.route('/api/v1/memory/similar', methods=['POST'])
def find_similar():
    """Find similar past audits"""
    data = request.get_json()
    contract_code = data.get('contract_code', '')

    async def search():
        return await memory_store.get_similar_audits(contract_code)

    similar = asyncio.run(search())
    return jsonify({"similar_audits": similar})

@app.route('/api/v1/chains', methods=['GET'])
def list_chains():
    """List supported blockchains"""
    return jsonify({
        "chains": [
            {"id": "ethereum", "name": "Ethereum", "type": "EVM"},
            {"id": "bsc", "name": "BNB Smart Chain", "type": "EVM"},
            {"id": "tron", "name": "TRON", "type": "TVMP"},
            {"id": "polygon", "name": "Polygon", "type": "EVM"},
            {"id": "arbitrum", "name": "Arbitrum", "type": "EVM L2"}
        ]
    })

@app.route('/api/v1/vulnerabilities', methods=['GET'])
def list_vulnerabilities():
    """List all known vulnerability types"""
    from core.vulnerability_db import VulnerabilityDatabase, Severity

    db = VulnerabilityDatabase()
    vulns = db.get_all()

    return jsonify({
        "total": len(vulns),
        "by_severity": {
            "Critical": db.get_critical_count(),
            "High": db.get_high_count(),
            "Medium": len(db.get_by_severity(Severity.MEDIUM)),
            "Low": len(db.get_by_severity(Severity.LOW)),
            "Info": len(db.get_by_severity(Severity.INFO))
        },
        "vulnerabilities": [
            {
                "type": v.type.value,
                "severity": v.severity.value,
                "title": v.title,
                "swc_id": v.swc_id,
                "cvss_score": v.cvss_score
            }
            for v in vulns
        ]
    })

# ═══════════════════════════════════════════════════════════════
# Health & Monitoring (Alibaba Cloud required)
# ═══════════════════════════════════════════════════════════════

@app.route('/health')
def health_check():
    """Health check endpoint for Alibaba Cloud load balancer"""
    return jsonify({
        "status": "healthy",
        "qwen_api": "connected" if QWEN_AVAILABLE else "mock",
        "memory_db": memory_store.get_memory_stats().get("status", "unknown"),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/metrics')
def metrics():
    """Basic metrics for monitoring"""
    return jsonify({
        "total_audits": memory_store.get_memory_stats().get("total_audits_stored", 0),
        "qwen_api_calls": 0,  # Track in production
        "uptime": "running"
    })

# ═══════════════════════════════════════════════════════════════
# Web Dashboard (Simple HTML)
# ═══════════════════════════════════════════════════════════════

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SentinelQwen - Smart Contract Security Auditor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0e27; color: #fff; }
        .header { background: linear-gradient(135deg, #ff6b35, #f7931e); padding: 40px; text-align: center; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .card { background: #1a1f3a; border-radius: 12px; padding: 30px; margin-bottom: 20px; }
        .card h2 { color: #f7931e; margin-bottom: 15px; }
        textarea { width: 100%; height: 300px; background: #0a0e27; border: 1px solid #2a2f4a; 
                   color: #fff; padding: 15px; border-radius: 8px; font-family: monospace; }
        button { background: linear-gradient(135deg, #ff6b35, #f7931e); color: #fff; border: none;
                 padding: 15px 40px; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 15px; }
        button:hover { opacity: 0.9; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .stat-box { background: #1a1f3a; padding: 20px; border-radius: 12px; text-align: center; }
        .stat-box .number { font-size: 2em; color: #f7931e; font-weight: bold; }
        .badge { display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 12px; margin: 5px; }
        .badge-critical { background: #ff4444; }
        .badge-high { background: #ff8844; }
        .badge-medium { background: #ffcc44; color: #000; }
        .badge-low { background: #44ff88; color: #000; }
        .footer { text-align: center; padding: 40px; opacity: 0.6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ SentinelQwen</h1>
        <p>Autopilot Smart Contract Security Auditor | Powered by Qwen Cloud & Alibaba Cloud</p>
        <p>Track 4: Autopilot Agent | Qwen Cloud Hackathon 2026</p>
    </div>

    <div class="container">
        <div class="card">
            <h2>🔍 Submit Contract for Audit</h2>
            <textarea id="contractCode" placeholder="Paste your Solidity contract code here..."></textarea>
            <br>
            <select id="chain" style="padding: 10px; margin-top: 10px; background: #0a0e27; color: #fff; border: 1px solid #2a2f4a; border-radius: 5px;">
                <option value="ethereum">Ethereum</option>
                <option value="bsc">BNB Smart Chain</option>
                <option value="tron">TRON</option>
                <option value="polygon">Polygon</option>
                <option value="arbitrum">Arbitrum</option>
            </select>
            <button onclick="submitAudit()">🔍 Start Audit</button>
            <div id="result" style="margin-top: 20px;"></div>
        </div>

        <div class="stats">
            <div class="stat-box">
                <div class="number">14+</div>
                <div>Vulnerability Types</div>
            </div>
            <div class="stat-box">
                <div class="number">5</div>
                <div>Blockchains</div>
            </div>
            <div class="stat-box">
                <div class="number">3</div>
                <div>Detection Layers</div>
            </div>
            <div class="stat-box">
                <div class="number">AI</div>
                <div>Powered by Qwen 3.7</div>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>Built with ❤️ for Qwen Cloud Global AI Hackathon 2026</p>
        <p>Powered by Alibaba Cloud | Qwen 3.7 Plus | ChromaDB | Flask</p>
    </div>

    <script>
        async function submitAudit() {
            const code = document.getElementById('contractCode').value;
            const chain = document.getElementById('chain').value;
            const result = document.getElementById('result');

            if (!code.trim()) {
                result.innerHTML = '<p style="color: #ff4444;">Please enter contract code</p>';
                return;
            }

            result.innerHTML = '<p>⏳ Running security audit... This may take 30-60 seconds</p>';

            try {
                const response = await fetch('/api/v1/audit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({contract_code: code, chain: chain})
                });

                const data = await response.json();

                if (data.error) {
                    result.innerHTML = `<p style="color: #ff4444;">Error: ${data.error}</p>`;
                    return;
                }

                let findingsHtml = data.findings.map(f => {
                    const badgeClass = f.severity === 'Critical' ? 'badge-critical' :
                                      f.severity === 'High' ? 'badge-high' :
                                      f.severity === 'Medium' ? 'badge-medium' : 'badge-low';
                    return `<span class="badge ${badgeClass}">${f.severity}: ${f.type}</span>`;
                }).join('');

                result.innerHTML = `
                    <h3>✅ Audit Complete: ${data.audit_id}</h3>
                    <p>Risk Score: <strong>${data.risk_score}/100</strong></p>
                    <p>Findings: ${data.total_findings} (Critical: ${data.critical_count})</p>
                    <div style="margin-top: 10px;">${findingsHtml}</div>
                    <details style="margin-top: 15px;">
                        <summary>View Full Report</summary>
                        <pre style="background: #0a0e27; padding: 15px; border-radius: 8px; overflow-x: auto;">${data.report || 'Report generation in progress...'}</pre>
                    </details>
                `;
            } catch (e) {
                result.innerHTML = `<p style="color: #ff4444;">Error: ${e.message}</p>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/dashboard')
def dashboard():
    """Web dashboard for manual auditing"""
    return render_template_string(DASHBOARD_HTML)

# ═══════════════════════════════════════════════════════════════
# Error Handlers
# ═══════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found", "available": ["/", "/api/v1/audit", "/dashboard", "/health"]}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  SentinelQwen - Autopilot Smart Contract Security Auditor    ║
    ║  Track 4: Autopilot Agent | Qwen Cloud Hackathon 2026        ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  API Server running on http://{host}:{port}                      ║
    ║  Dashboard: http://{host}:{port}/dashboard                       ║
    ║  Health: http://{host}:{port}/health                             ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    app.run(host=host, port=port, debug=debug)
