<#
.SYNOPSIS
    Collects a basic health summary from an Azure Local cluster.

.DESCRIPTION
    Performs read-only checks against Failover Clustering and Azure Local
    to provide a consistent starting point for health assessment and
    troubleshooting.

    This script does not perform remediation or configuration changes.

.NOTES
    Intended for lab, learning, and troubleshooting-assessment scenarios.
    Validate commands against the documentation applicable to your
    Azure Local version before using the script in production.
#>

$ErrorActionPreference = "Continue"

function Write-Section {
    param (
        [Parameter(Mandatory)]
        [string]$Title
    )

    Write-Host ""
    Write-Host "============================================================"
    Write-Host $Title
    Write-Host "============================================================"
}

function Invoke-HealthCheck {
    param (
        [Parameter(Mandatory)]
        [string]$Name,

        [Parameter(Mandatory)]
        [scriptblock]$Command
    )

    Write-Section $Name

    try {
        & $Command
    }
    catch {
        Write-Warning "Unable to complete check: $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "Azure Local Health Summary"
Write-Host "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "Computer : $env:COMPUTERNAME"
Write-Host "PowerShell: $($PSVersionTable.PSVersion)"
Write-Host ""

# ----------------------------------------------------------------------
# Failover Clustering
# ----------------------------------------------------------------------

Invoke-HealthCheck -Name "Cluster Information" -Command {

    Import-Module FailoverClusters -ErrorAction Stop

    Get-Cluster |
        Select-Object Name, Domain, QuorumType
}

Invoke-HealthCheck -Name "Cluster Nodes" -Command {

    Get-ClusterNode |
        Select-Object Name, State
}

Invoke-HealthCheck -Name "Cluster Groups" -Command {

    Get-ClusterGroup |
        Select-Object Name, State, OwnerNode
}

Invoke-HealthCheck -Name "Cluster Resources" -Command {

    Get-ClusterResource |
        Select-Object Name, State, OwnerGroup, ResourceType
}

Invoke-HealthCheck -Name "Cluster Shared Volumes" -Command {

    Get-ClusterSharedVolume |
        Select-Object Name, State, OwnerNode
}

# ----------------------------------------------------------------------
# Azure Local
# ----------------------------------------------------------------------

Invoke-HealthCheck -Name "Azure Local Solution Updates" -Command {

    if (Get-Command Get-SolutionUpdate -ErrorAction SilentlyContinue) {

        Get-SolutionUpdate |
            Select-Object DisplayName, Version, State
    }
    else {
        Write-Warning "Get-SolutionUpdate is not available on this system."
    }
}

Invoke-HealthCheck -Name "Azure Local Environment Health" -Command {

    if (Get-Command Get-SolutionUpdateEnvironment -ErrorAction SilentlyContinue) {

        Get-SolutionUpdateEnvironment |
            Select-Object State, HealthState, HealthCheckDate
    }
    else {
        Write-Warning "Get-SolutionUpdateEnvironment is not available on this system."
    }
}

Write-Section "Health Check Completed"

Write-Host "Review failed, offline, or degraded components before proceeding"
Write-Host "with deeper troubleshooting."
Write-Host ""
