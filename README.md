# Azure Hybrid AI Lab

Hands-on engineering projects exploring Azure Hybrid Cloud, Azure Local, automation, and AI-assisted infrastructure operations.

## Overview

This repository documents practical engineering experiments that combine traditional infrastructure operations with modern AI services.

The current implementation focuses on collecting Azure Local health information deterministically, normalizing it into structured JSON, applying a privacy sanitization layer, and using Microsoft Foundry to produce an evidence-based AI-assisted assessment.

The goal is not to replace infrastructure troubleshooting or engineering judgment with AI.

The goal is to explore how structured infrastructure evidence can be collected, validated, sanitized, and safely used by AI-assisted operational workflows.

## Deployment

For a complete step-by-step guide to reproducing the hosted Azure reference deployment, including Microsoft Foundry, Azure App Service, Managed Identity, Microsoft Entra ID authentication, GitHub Actions, and OIDC:

**[Azure Deployment Guide](./ai/health-analyzer/DEPLOYMENT.md)**

## Featured Project - Azure Local AI Health Analyzer

The Azure Local AI Health Analyzer is an end-to-end lab that combines PowerShell-based infrastructure data collection with a Python analysis service and Microsoft Foundry.

```text
Azure Local
    |
    v
Read-Only PowerShell Collector
    |
    v
Normalized JSON Health Report
    |
    v
Schema Validation
    |
    v
Privacy Sanitization
    |
    v
Microsoft Foundry
    |
    v
Structured AI Findings
    |
    v
Human Review
```

The design deliberately separates deterministic infrastructure evidence from AI interpretation.

The Azure Local collector does not depend on AI and remains read-only.

The AI layer receives only the structured report after validation and privacy sanitization.

## Current Capabilities

- Read-only Azure Local health collection with PowerShell
- Single-node and multi-node topology detection
- Cluster, node, group, resource, shared-volume, update, and environment health collection
- Normalized JSON health-report generation
- Python-based report validation
- Schema-aware and pattern-based privacy sanitization before AI analysis
- Consistent pseudonymization of infrastructure identities
- IPv4 address pseudonymization
- GUID pseudonymization
- Email and UPN-style identity pseudonymization
- Azure Resource ID pseudonymization
- Microsoft Entra ID authentication
- Microsoft Foundry model integration
- Structured AI output using Pydantic models
- Evidence-oriented findings and recommended validation steps
- FastAPI web interface
- Azure App Service deployment
- Managed Identity authentication for the hosted workload
- Microsoft Entra ID authentication for the web application
- Automated regression testing with pytest
- GitHub Actions build, test, and deployment pipeline
- Sample anonymized health and AI analysis reports

## Privacy Boundary

Infrastructure health reports can contain identifiers that are useful for troubleshooting but should not automatically be forwarded to an external AI service.

The analyzer therefore introduces a sanitization boundary between report validation and AI processing.

Examples of values covered by the current sanitizer include:

```text
Host name                -> HOST-001
Cluster name             -> CLUSTER-001
Domain                   -> DOMAIN-001
Cluster group            -> GROUP-001
Cluster resource         -> RESOURCE-001
Shared volume            -> VOLUME-001
IPv4 address             -> IP-001
GUID                     -> GUID-001
Email / UPN identity     -> IDENTITY-001
Azure Resource ID        -> AZURE-RESOURCE-ID-001
```

Pseudonyms remain consistent within a report so that relationships and diagnostic correlation can still be analyzed.

The implementation is intentionally described as privacy sanitization and pseudonymization, not as universal anonymization.

Reports should still be reviewed before using them with real production or customer data.

## AI Analysis Principles

The AI layer is designed around evidence rather than autonomous diagnosis.

The model is instructed to use only the supplied report, avoid inventing missing configuration or events, distinguish observations from interpretation, and avoid unsupported root-cause conclusions.

A single-node topology is not treated as unhealthy simply because it contains one node.

Likewise, an Offline resource is not automatically interpreted as a failure without sufficient supporting context.

The resulting AI output remains an analysis aid and requires engineering judgment.

## Application Architecture

The hosted implementation separates deployment identity from runtime identity:

```text
GitHub Repository
       |
       v
GitHub Actions
       |
       | OIDC
       v
Azure Deployment Identity
       |
       v
Azure App Service
       |
       | Managed Identity
       v
Microsoft Foundry
```

GitHub Actions uses federated identity for deployment.

The running application uses its own Azure Managed Identity to access Microsoft Foundry.

No Foundry API key is required in the application source code.

The web application itself can be protected using Microsoft Entra ID authentication.

## Testing and CI/CD

Privacy behavior is protected by automated regression tests.

The current test suite validates:

- Infrastructure identifier pseudonymization
- Cross-reference consistency
- Complete owner-group replacement
- Resource and volume pseudonymization
- Preservation of technical evidence
- Immutability of the original report
- Removal of known sensitive identifiers
- IPv4 pseudonymization and correlation
- GUID pseudonymization and correlation
- Email and UPN-style identity pseudonymization
- Complete Azure Resource ID pseudonymization
- Rejection of invalid IPv4 candidates

The current suite contains 12 regression tests.

GitHub Actions runs the test suite before deployment. A failed regression test prevents the deployment job from proceeding.

This creates a quality gate between source changes and the hosted application.

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
    app.py
    sanitizer.py
    test_sanitizer.py
    requirements.txt
    requirements-dev.txt
    README.md
    examples/

.github/
  workflows/
    main_azure-local-health-analyzer.yml
```

## Explore the Project

### Azure Local Health Collector

Start with the PowerShell collector and normalized health-report format:

[Azure Local Health Checks](./azure-local/health-checks/README.md)

### Azure Local AI Health Analyzer

Continue with the Python analyzer, privacy layer, Microsoft Foundry integration, structured output, FastAPI application, and hosted architecture:

[Azure Local AI Health Analyzer](./ai/health-analyzer/README.md)

## Engineering Principles

This lab follows a few core principles:

- Collect consistent evidence first, interpret it second.
- Keep infrastructure collection separate from AI reasoning.
- Prefer structured evidence over unrestricted diagnostic input.
- Apply privacy controls before external AI processing.
- Preserve technical relationships when pseudonymizing identifiers.
- Do not infer root cause when the available evidence does not support it.
- Treat AI output as an analysis layer, not authoritative infrastructure state.
- Prefer identity-based authentication over embedded secrets.
- Validate privacy behavior with automated regression tests.
- Require successful tests before automated deployment.

## Future Direction

Possible future experiments include:

- Additional Azure Local health signals
- Additional privacy edge-case handling
- Deterministic health rules before AI interpretation
- Retrieval-Augmented Generation using authoritative public Microsoft documentation
- Historical report comparison and trend analysis
- Controlled agentic workflows for infrastructure investigation
- Additional observability and application monitoring

These are areas of exploration and are not presented as implemented functionality.

## Security and Privacy

All public examples are designed for personal lab, learning, and technical demonstration scenarios.

Public samples must not contain customer data, credentials, access tokens, tenant or subscription identifiers, confidential Microsoft information, internal tools, proprietary code, or non-public troubleshooting procedures.

The sanitization layer reduces exposure of known infrastructure identifiers but should not be considered a guarantee that arbitrary input is fully anonymized.

Human review remains required before processing sensitive real-world data.

## Disclaimer

This is a personal technical project based on lab environments and publicly available documentation.

It is not an official Microsoft support tool and does not replace official product documentation, support processes, security review, or engineering investigation.

## Author

**Gianluca Maestri**

Azure Hybrid Cloud | Azure Local | Cloud Architecture | AI & Automation
