# Azure Hybrid AI Lab

Hands-on engineering projects exploring Azure Hybrid Cloud, Azure Local, automation, and AI-assisted infrastructure operations.

## Overview

This repository documents practical experiments that combine traditional infrastructure engineering with modern AI services.

The current implementation focuses on collecting Azure Local health information deterministically, normalizing it into structured JSON, and using Microsoft Foundry to produce an evidence-based AI-assisted assessment.

The goal is not to replace infrastructure troubleshooting or engineering judgment with AI. The goal is to explore how structured infrastructure evidence can be safely and consistently used by AI-assisted operational workflows.

## Featured Project - Azure Local AI Health Analyzer

The Azure Local AI Health Analyzer is an end-to-end lab that combines PowerShell-based infrastructure data collection with structured AI analysis.

```text
Azure Local
    |
    v
PowerShell Health Collector
    |
    v
Normalized JSON Health Report
    |
    v
Python Health Analyzer
    |
    v
Microsoft Foundry
    |
    v
Structured AI Assessment
```

The collector remains deterministic and read-only, while the AI layer operates only on the structured evidence supplied in the health report.

The analyzer is designed to avoid unsupported conclusions by separating observed infrastructure state from AI interpretation.

### Current capabilities

- Read-only Azure Local health collection with PowerShell
- Single-node and multi-node topology detection
- Cluster, node, group, resource, CSV, update, and environment health collection
- Normalized JSON health-report generation
- Python-based report validation and processing
- Microsoft Entra ID authentication
- Microsoft Foundry model integration
- Structured AI output using Pydantic models
- Evidence-oriented findings and recommended validation steps
- Sample anonymized health and AI analysis reports

## Repository Structure

```text
azure-local/
  health-checks/
    Get-AzureLocalHealthSummary.ps1
    Get-AzureLocalHealthSummary-v2.ps1
    README.md
    examples/

ai/
  health-analyzer/
    analyze_health.py
    README.md
    requirements.txt
    examples/
```

## Explore the Project

### Azure Local Health Collector

Start with the PowerShell collector and the normalized health-report format:

[Azure Local Health Checks](./azure-local/health-checks/README.md)

### AI Health Analyzer

Continue with the Python analyzer, Microsoft Foundry integration, authentication, configuration, and structured AI output:

[Azure Local AI Health Analyzer](./ai/health-analyzer/README.md)

## Engineering Principles

This lab follows a few core principles:

- Collect evidence deterministically before interpreting it.
- Keep infrastructure collection separate from AI reasoning.
- Prefer structured data over free-form diagnostic input.
- Do not infer root cause when the available evidence does not support it.
- Treat AI output as an additional analysis layer, not as authoritative infrastructure state.
- Keep authentication and environment-specific configuration outside the source code.

## Future Direction

Possible future experiments include:

- Additional Azure Local health signals
- Sanitization and privacy controls before external analysis
- API-based execution with FastAPI and Azure App Service
- Managed Identity authentication for hosted workloads
- Retrieval-Augmented Generation using public Microsoft documentation
- Agentic workflows for controlled infrastructure investigation

These are future areas of exploration and are not presented as implemented functionality.

## Security and Privacy

All examples are designed for personal lab and learning scenarios.

Public samples are anonymized and must not contain customer data, credentials, access tokens, tenant or subscription identifiers, confidential Microsoft information, internal tools, proprietary code, or non-public troubleshooting procedures.

## Disclaimer

This is a personal technical project based on lab environments and publicly available documentation.

It is not an official Microsoft support tool and does not replace official product documentation, support processes, or engineering investigation.

## Author

**Gianluca Maestri**

Azure Hybrid Cloud | Azure Local | Cloud Architecture | AI & Automation

[LinkedIn profile](https://www.linkedin.com/in/gianlucamaestri)
