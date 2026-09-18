# Azure Local Health Checks

This folder contains read-only PowerShell health-check examples for Azure Local.

The goal is to provide a structured starting point for infrastructure health assessment before moving into deeper troubleshooting.

The project evolves from simple console-based data collection toward structured reporting, automation, and future AI-assisted infrastructure analysis.

---

## Health Check v1

`Get-AzureLocalHealthSummary.ps1`

The first version provides a simple console-based health summary for an Azure Local environment.

It collects:

- Cluster information
- Cluster nodes
- Cluster groups
- Cluster resources
- Cluster Shared Volumes
- Azure Local solution update state
- Azure Local environment health

The purpose of v1 is deliberately simple:

> Collect consistent evidence first, then decide where deeper troubleshooting is needed.

An anonymized example of the console output is available here:

`examples/sample-output.txt`

---

## Health Check v2

`Get-AzureLocalHealthSummary-v2.ps1`

Version 2 extends the original health check by introducing structured and normalized data collection.

The script still provides human-readable console output, but it also generates a structured JSON health report that can be used by other tools and workflows.

### What's new in v2

- Structured JSON reporting
- Normalized state values
- Normalized Azure Local update versions
- Cluster topology detection
- Node count detection
- Support for single-node and multi-node environments
- ISO 8601 health-check timestamps
- Structured cluster resource information
- Data suitable for reporting and automation
- Foundation for future AI-assisted analysis

The script remains read-only and does not perform remediation or configuration changes.

---

## Usage

Run the health check from PowerShell:

```powershell
.\Get-AzureLocalHealthSummary-v2.ps1
```

By default, the JSON report is created in the same directory as the script:

```text
AzureLocalHealthSummary.json
```

A custom output path can also be specified:

```powershell
.\Get-AzureLocalHealthSummary-v2.ps1 `
    -OutputPath "C:\Temp\AzureLocalHealthSummary.json"
```

---

## JSON Report Structure

Version 2 produces a structured health report with the following logical hierarchy:

```text
Metadata
|
+-- SchemaVersion
+-- Generated
+-- Computer
+-- PowerShellVersion

Cluster
|
+-- Information
|   +-- Name
|   +-- Domain
|   +-- QuorumType
|   +-- NodeCount
|   +-- Topology
|
+-- Nodes
+-- Groups
+-- Resources
+-- SharedVolumes

AzureLocal
|
+-- SolutionUpdates
+-- EnvironmentHealth
```

Example:

```json
{
  "Metadata": {
    "SchemaVersion": "2.0",
    "Computer": "AZLOCAL-NODE01",
    "PowerShellVersion": "5.1"
  },
  "Cluster": {
    "Information": {
      "Name": "AZLOCAL-CLUSTER",
      "Domain": "lab.example",
      "QuorumType": "Majority",
      "NodeCount": 1,
      "Topology": "SingleNode"
    },
    "Nodes": [
      {
        "Name": "AZLOCAL-NODE01",
        "State": "Up"
      }
    ]
  }
}
```

A more complete anonymized JSON example is available here:

`examples/sample-health-report.json`

---

## Why Structured JSON?

Console output is useful for engineers, but structured data makes the health information reusable.

The JSON report can become an input for:

- Automated reporting
- Infrastructure health dashboards
- Historical health comparisons
- PowerShell or Python analysis
- Workflow automation
- AI-assisted diagnostics
- RAG-based troubleshooting experiments
- Agent-based infrastructure analysis

This separates **data collection** from **data interpretation**.

The PowerShell script remains responsible for deterministic collection of infrastructure state, while future components can analyze the structured output without changing the collection logic.

---

## Single-Node and Multi-Node Environments

The health check records the detected cluster topology.

For example:

```json
{
  "NodeCount": 1,
  "Topology": "SingleNode"
}
```

or:

```json
{
  "NodeCount": 3,
  "Topology": "MultiNode"
}
```

Topology information is treated as environmental context.

A single-node deployment is therefore not automatically classified as a degraded condition simply because only one cluster node is detected.

---

## Health-Check Philosophy

The health check follows a simple principle:

> **Collect consistent evidence first, interpret it second.**

Infrastructure state should be interpreted in the context of the environment and its configuration.

For this reason, the current scripts focus primarily on collecting and normalizing evidence rather than automatically classifying every non-default state as a problem.

This approach also provides a cleaner foundation for future diagnostic logic.

---

## Current Checks

The current health-check implementation collects information about:

### Failover Clustering

- Cluster identity
- Quorum type
- Node count
- Cluster topology
- Node state
- Cluster groups
- Cluster resources
- Cluster Shared Volumes

### Azure Local

- Solution update versions
- Solution update state
- Environment update state
- Environment health state
- Health-check timestamp

---

## Repository Files

```text
health-checks/
|
+-- Get-AzureLocalHealthSummary.ps1
+-- Get-AzureLocalHealthSummary-v2.ps1
+-- README.md
|
+-- examples/
    +-- sample-output.txt
    +-- sample-health-report.json
```

`Get-AzureLocalHealthSummary.ps1` represents the initial console-based implementation.

`Get-AzureLocalHealthSummary-v2.ps1` introduces normalized structured reporting and JSON output.

---

## Future Development

Possible future extensions include:

- Additional Azure Local health signals
- Storage health checks
- Network health checks
- Improved summary reporting
- Health findings and evidence correlation
- Historical comparison between reports
- Infrastructure health dashboards
- AI-assisted interpretation of health data
- RAG-based troubleshooting experiments
- Agent-based diagnostic workflows

A future AI-assisted layer should consume the structured health report rather than replace deterministic infrastructure data collection.

---

## Safety

The current scripts are designed to be read-only.

They collect infrastructure state and do not intentionally:

- Modify cluster configuration
- Restart services
- Restart nodes
- Move workloads
- Install updates
- Perform remediation
- Change Azure Local configuration

Any future remediation functionality should be clearly separated from health assessment and require explicit operator control.

---

## Disclaimer

These scripts are intended for lab, learning, community knowledge-sharing, and troubleshooting-assessment scenarios.

Always review and validate commands against the documentation applicable to your Azure Local version and environment before using them in production.

The examples in this repository are anonymized and do not contain customer data, confidential information, internal tools, proprietary code, or non-public troubleshooting procedures.
