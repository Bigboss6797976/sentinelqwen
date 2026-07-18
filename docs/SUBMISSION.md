# 📋 Submission Documentation

## Track 4: Autopilot Agent

### Project Name
**SentinelQwen** — Autopilot Smart Contract Security Auditor

### Project Description

SentinelQwen is an end-to-end autonomous agent that automates the entire smart contract security auditing workflow. From receiving raw Solidity code to generating professional audit reports with fix suggestions, the system operates with minimal human intervention while incorporating human approval at critical security checkpoints.

### Key Features

1. **Multi-Layer Detection**
   - Static analysis (Slither, Mythril integration)
   - Pattern-based vulnerability matching (14+ types)
   - AI-powered semantic analysis via Qwen 3.7 Plus

2. **Persistent Learning Memory**
   - ChromaDB vector store for cross-session learning
   - Similar audit retrieval for improved accuracy
   - Timely forgetting of outdated patterns (90-day cleanup)

3. **Human-in-the-Loop**
   - Critical findings trigger human approval
   - Fix suggestions require confirmation before application
   - Final report review checkpoint

4. **Multi-Platform Access**
   - RESTful API for integrations
   - Web dashboard for manual auditing
   - Telegram Bot for mobile access

5. **Multi-Chain Support**
   - Ethereum, BSC, TRON, Polygon, Arbitrum
   - Chain-specific vulnerability patterns
   - Live blockchain data integration

### Technology Stack

| Component | Technology |
|-----------|-----------|
| AI Model | Qwen 3.7 Plus (DashScope API) |
| Cloud Platform | Alibaba Cloud ECS / Function Compute |
| Storage | Alibaba Cloud OSS |
| Database | Alibaba Cloud RDS (MySQL) |
| Cache | Redis (Alibaba Cloud) |
| Vector DB | ChromaDB |
| API Framework | Flask |
| Bot Framework | python-telegram-bot |
| Container | Docker |

### Architecture Diagram

See `docs/architecture.png` or the ASCII diagram in README.md.

### Deployment Proof

- **Video**: [Alibaba Cloud Deployment Proof](https://youtube.com/your-deployment-video)
- **ECS Instance**: Running at `http://your-ecs-ip:5000`
- **Function Compute**: Deployed via `fc-deploy.yaml`
- **OSS Bucket**: `sentinelqwen-reports` storing audit reports

### Code Repository

- **URL**: https://github.com/yourusername/sentinelqwen
- **License**: MIT (visible in repository "About" section)
- **Open Source**: All source code included

### Demo Video

- **URL**: https://youtube.com/your-demo-video
- **Duration**: ~3 minutes
- **Platform**: YouTube (Public)

### Blog Post (Optional)

- **URL**: https://your-blog-link
- **Platform**: Medium / Dev.to / Personal Blog

### How to Test

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/sentinelqwen.git
cd sentinelqwen
pip install -r requirements.txt
cp .env.example .env
# Add your DASHSCOPE_API_KEY to .env

# 2. Run demo
python app.py demo

# 3. Or start API server
python app.py server
# Visit http://localhost:5000/dashboard

# 4. Or test API directly
curl -X POST http://localhost:5000/api/v1/audit \
  -H "Content-Type: application/json" \
  -d '{
    "contract_code": "pragma solidity ^0.8.0; contract Test { ... }",
    "chain": "ethereum"
  }'
```

### Contact

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com
