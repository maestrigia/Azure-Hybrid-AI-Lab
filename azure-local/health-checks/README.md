# Azure Local Health Checks

A collection of practical health-check examples for Azure Local environments.

## Purpose

The goal of this section is to build a simple and reusable approach for assessing the health of an Azure Local environment before starting a deeper troubleshooting investigation.

The checks focus on obtaining an initial view of the environment across areas such as:

- Cluster nodes
- Cluster groups and resources
- Storage
- Azure Local solution update state
- Environment health
- Basic infrastructure status

## Health-check approach

A troubleshooting investigation can start with a simple sequence:

1. Confirm cluster node status.
2. Review cluster groups and resources.
3. Check storage and Cluster Shared Volumes.
4. Review Azure Local solution update state.
5. Review environment health checks.
6. Identify failed or degraded components requiring deeper investigation.

The objective is not to automatically diagnose every issue, but to create a consistent starting point for further analysis.

## Planned content

This folder will include:

- `Get-AzureLocalHealthSummary.ps1` — PowerShell starter script for collecting a basic health summary.
- Example output generated from a lab environment.
- Notes explaining how to interpret the collected information.

## Requirements

- Azure Local environment
- Windows PowerShell / PowerShell
- Appropriate administrative permissions
- Required Azure Local and Failover Clustering PowerShell modules

## Disclaimer

This project is intended for learning and lab purposes.

Examples are based on personal lab environments and publicly available Microsoft documentation. Always validate commands and procedures against the documentation applicable to your Azure Local version before using them in a production environment.
