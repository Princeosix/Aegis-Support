# AEGIS Support (SOC Command Center)

> An enterprise-grade, hybrid AI threat-hunting platform and automated IT Helpdesk. AEGIS triages network anomalies, detects data leaks, and generates technical mitigation strategies locally without relying on external cloud APIs.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

Modern Security Operations Centers (SOCs) are overwhelmed by user complaints, making it difficult to separate routine IT bugs from critical security breaches. **AEGIS Support** bridges this gap by acting as an autonomous Level 3 SOC Analyst. 

It features a three-portal UI (Public Helpdesk, Staff Auth, and SOC Dashboard) and utilizes a multi-layered local AI pipeline to instantly analyze, score, and summarize incident payloads.

## Key Features

- **📡 Multi-Portal Interface:** Includes a public-facing ticket submission portal, a secure IT login gate, and a deep-inspection SOC dashboard.
- **🛡️ Layer 1 - Heuristics (DLP):** Lightning-fast Regex engine that instantly flags exposed Data Loss Prevention (DLP) triggers, including IPv4 addresses, MAC addresses, and AWS API Keys.
- **🧠 Layer 2 - Discriminative AI:** Utilizes `BART-Large-MNLI` for zero-shot text classification to mathematically score the threat level, separating critical breaches from standard software bugs or adversarial spam.
- **✍️ Layer 3 - Generative AI:** Deploys `Qwen2.5-1.5B-Instruct` to act as a senior engineer, extracting technical threat vectors and generating actionable isolation protocols.
- **🔒 100% Data Privacy (Air-Gapped):** All AI inference is done locally on-device. Zero sensitive corporate data or PII is ever sent to OpenAI, Google, or external cloud APIs.
- **💾 State Persistence:** Analysts can run the AI pipeline, navigate away, and return to see their forensic analysis safely saved in the session state.

## Architecture & Tech Stack

- **Frontend / Framework:** Streamlit (Python)
- **Data Handling:** Pandas, RegEx
- **Machine Learning Backend:** PyTorch
- **AI / LLM Library:** Hugging Face `transformers`
- **Models:**
  - `facebook/bart-large-mnli` (~400M Parameters)
  - `Qwen/Qwen2.5-1.5B-Instruct` (1.5B Parameters)
- **Hardware Optimization:** Models are quantized to `FP16` (Half-Precision), allowing the entire dual-model pipeline to run comfortably on a consumer laptop with a 6GB Nvidia GPU (~2.5GB VRAM allocation).

## Prerequisites

Before you begin, ensure you have the following:
* **Python:** Version 3.9 or higher.
* **Hardware:** An Nvidia GPU with at least 4GB of VRAM is highly recommended. The app will fall back to the CPU if no GPU is detected, but inference will be significantly slower.
* **Storage:** At least 5GB of free hard drive space to cache the initial Hugging Face model downloads.

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/aegis-support.git](https://github.com/your-username/aegis-support.git)
   cd aegis-support
