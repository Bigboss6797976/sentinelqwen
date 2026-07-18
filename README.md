# 🛡️ SentinelQwen

> **Autopilot Smart Contract Security Auditor**  
> Track 4: Autopilot Agent — Qwen Cloud Global AI Hackathon 2026

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Qwen 3.7](https://img.shields.io/badge/Qwen-3.7%20Plus-orange.svg)](https://qwen.aliyun.com)
[![Alibaba Cloud](https://img.shields.io/badge/Alibaba%20Cloud-ECS-red.svg)](https://www.alibabacloud.com)

---

## 🎯 Project Overview

**SentinelQwen** is an end-to-end autonomous smart contract security auditing system that combines:

- 🔍 **Static Analysis** (Slither, Mythril)
- 🧠 **AI-Powered Semantic Analysis** (Qwen 3.7 Plus)
- 📊 **Pattern-Based Detection** (14+ vulnerability types)
- 🧬 **Persistent Learning Memory** (ChromaDB vector store)
- 👤 **Human-in-the-Loop** (Critical decision checkpoints)
- 🔧 **Auto-Fix Generation** (Secure code suggestions)

### Why Track 4: Autopilot Agent?

SentinelQwen fully embodies the **Autopilot Agent** philosophy:

| Requirement | Implementation |
|------------|----------------|
| **End-to-end automation** | Contract submission → Analysis → Reporting → Fix suggestions, fully automated |
| **Real business workflow** | Smart contract security auditing is a critical $2B+ industry workflow |
| **Ambiguous input handling** | Accepts raw Solidity code, deployed addresses, or file uploads; auto-detects format |
| **External tool invocation** | Calls Slither, Mythril, blockchain RPCs, and Qwen Cloud API |
| **Human intervention** | Critical findings trigger human approval before proceeding |
| **Production-ready** | Deployed on Alibaba Cloud ECS with Docker, health checks, monitoring |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Web Dashboard │  │ Telegram Bot │  │  REST API (JSON)       │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
└─────────┼────────────────┼─────────────────────┼────────────────┘
          │                │                     │
          └────────────────┴──────────┬──────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Audit Orchestrator                            │
│         (Central workflow controller with human checkpoints)     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ Code Analyzer │   │ Vulnerability   │   │ Fix Suggester   │
│   Agent       │   │ Detector Agent  │   │    Agent        │
│               │   │                 │   │                 │
│ • Complexity  │   │ • Static (Slither)│  │ • AI-generated  │
│ • AI semantic │   │ • Pattern match  │   │   secure code   │
│ • Architecture│   │ • AI analysis    │   │ • Gas impact    │
└───────┬───────┘   └────────┬────────┘   └─────────────────┘
        │                    │
        └────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Report Generator                            │
│         (Professional markdown/HTML reports with charts)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Persistent Memory                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ChromaDB Vector Store                                   │   │
│  │  • Similar audit retrieval                               │   │
│  │  • Cross-session learning                                │   │
│  │  • Timely forgetting (90-day cleanup)                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Alibaba Cloud Infrastructure                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ ECS/FC   │  │   OSS    │  │   RDS    │  │    Redis     │   │
│  │ (Compute)│  │ (Storage)│  │ (MySQL)  │  │  (Cache)     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Qwen Cloud API (Qwen 3.7 Plus)              │   │
│  │         • Semantic code analysis                         │   │
│  │         • Vulnerability detection                        │   │
│  │         • Fix generation                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional, for deployment)
- Alibaba Cloud account (for deployment)
- Qwen Cloud API key ([Get free trial](https://www.aliyun.com/product/bailian))

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/sentinelqwen.git
cd sentinelqwen

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Run API Server

```bash
python app.py server
```

Access:
- API: http://localhost:5000
- Dashboard: http://localhost:5000/dashboard
- Health: http://localhost:5000/health

### Run Telegram Bot

```bash
python app.py bot
```

### Run Demo

```bash
python app.py demo
```

---

## 📡 API Documentation

### Submit Audit

```bash
POST /api/v1/audit
Content-Type: application/json

{
  "contract_code": "pragma solidity ^0.8.0; contract Test { ... }",
  "chain": "ethereum",
  "contract_address": "0x..."  // optional
}
```

Response:
```json
{
  "audit_id": "AUD-A1B2C3D4",
  "status": "completed",
  "risk_score": 75,
  "critical_count": 2,
  "total_findings": 8,
  "findings": [
    {
      "type": "Reentrancy",
      "severity": "Critical",
      "line": 42,
      "description": "External call before state update",
      "confidence": "high"
    }
  ]
}
```

### Quick Scan

```bash
POST /api/v1/quick-scan
Content-Type: application/json

{
  "contract_code": "pragma solidity ^0.8.0; ..."
}
```

### List Vulnerabilities

```bash
GET /api/v1/vulnerabilities
```

---

## 🔍 Detection Capabilities

| Severity | Vulnerability | SWC ID | CVSS |
|----------|--------------|--------|------|
| 🔴 Critical | Reentrancy | SWC-107 | 9.8 |
| 🔴 Critical | Access Control | SWC-106 | 9.1 |
| 🔴 Critical | Flash Loan | — | 9.3 |
| 🔴 Critical | Oracle Manipulation | — | 9.0 |
| 🟠 High | Integer Overflow | SWC-101 | 8.2 |
| 🟠 High | Unchecked External Call | SWC-104 | 7.5 |
| 🟠 High | Signature Replay | SWC-121 | 8.1 |
| 🟠 High | Delegatecall Injection | SWC-112 | 8.8 |
| 🟡 Medium | Timestamp Dependence | SWC-116 | 5.3 |
| 🟡 Medium | tx.origin Usage | SWC-115 | 6.5 |
| 🟡 Medium | Front-Running | — | 5.9 |
| 🟡 Medium | Storage Collision | — | 6.8 |
| 🟢 Low | Denial of Service | SWC-113 | 4.3 |
| 🟢 Low | Uninitialized Proxy | — | 5.0 |
| 🟢 Low | Floating Pragma | SWC-103 | 3.1 |
| ⚪ Info | Unused Variables | — | 2.0 |

---

## 🏗️ Supported Blockchains

| Chain | Type | Status |
|-------|------|--------|
| Ethereum | EVM | ✅ Full support |
| BNB Smart Chain | EVM | ✅ Full support |
| TRON | TVM | ✅ Full support |
| Polygon | EVM | ✅ Full support |
| Arbitrum | EVM L2 | ✅ Full support |

---

## 🚢 Deployment

### Deploy to Alibaba Cloud ECS

```bash
# Build and push Docker image
docker build -t sentinelqwen .
docker tag sentinelqwen registry.ap-southeast-1.aliyuncs.com/your-namespace/sentinelqwen
docker push registry.ap-southeast-1.aliyuncs.com/your-namespace/sentinelqwen

# Deploy using script
chmod +x deployment/aliyun/deploy.sh
./deployment/aliyun/deploy.sh
```

### Deploy to Function Compute (Serverless)

```bash
cd deployment/aliyun
fun deploy
```

---

## 📹 Demo Video

[Watch Demo on YouTube](https://youtube.com/your-video-link)

---

## 📝 Blog Post

[Read about our journey building SentinelQwen](https://your-blog-link)

---

## 👥 Team

Solo developer passionate about blockchain security and AI automation.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- [Qwen Cloud](https://qwen.aliyun.com) for providing the AI model
- [Alibaba Cloud](https://www.alibabacloud.com) for infrastructure
- [OpenZeppelin](https://openzeppelin.com) for security patterns
- [SWC Registry](https://swcregistry.io) for vulnerability standards

---

> Built with ❤️ for Qwen Cloud Global AI Hackathon 2026
