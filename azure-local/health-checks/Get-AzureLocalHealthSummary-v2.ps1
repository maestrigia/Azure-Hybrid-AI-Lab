<#
.SYNOPSIS
    Collects a structured health summary from an Azure Local cluster.

.DESCRIPTION
    Performs read-only checks against Failover Clustering and Azure Local
    and produces both console output and a structured JSON report.

    The JSON output is normalized to use simple, human-readable values
    instead of serialized PowerShell/.NET objects.

    The report can be used for documentation, automation, reporting,
    or future AI-assisted infrastructure analysis.

    This script does not perform remediation or configuration changes.

.PARAMETER OutputPath
    Path of the JSON report.

.NOTES
    Supports both single-node and multi-node Azure Local environments.

    A single-node topology is recorded as environment information and is
    not automatically considered a degraded condition.

    Intended for lab, learning, and troubleshooting-assessment scenarios.
#>

param (
    [string]$OutputPath = (Join-Path $PSScriptRoot "AzureLocalHealthSummary.json")
)

$ErrorActionPreference = "Continue"

# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------

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

    try {
        return & $Command
    }
    catch {
        Write-Warning "$Name failed: $($_.Exception.Message)"
        return $null
    }
}

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------

Write-Host ""
Write-Host "Azure Local Health Summary v2"
Write-Host "Generated : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "Computer  : $env:COMPUTERNAME"
Write-Host "PowerShell: $($PSVersionTable.PSVersion)"
Write-Host ""

# ----------------------------------------------------------------------
# Load Failover Clustering
# ----------------------------------------------------------------------

try {
    Import-Module FailoverClusters -ErrorAction Stop
}
catch {
    Write-Error "Unable to load FailoverClusters module: $($_.Exception.Message)"
    return
}

# ----------------------------------------------------------------------
# Metadata
# ----------------------------------------------------------------------

$Metadata = [PSCustomObject]@{
    SchemaVersion     = "2.0"
    Generated         = (Get-Date).ToString("o")
    Computer          = [string]$env:COMPUTERNAME
    PowerShellVersion = [string]$PSVersionTable.PSVersion
}

# ----------------------------------------------------------------------
# Cluster Nodes
# ----------------------------------------------------------------------

$ClusterNodes = @(
    Invoke-HealthCheck `
        -Name "Cluster Nodes" `
        -Command {

            Get-ClusterNode |
                Select-Object `
                    @{Name='Name';Expression={[string]$_.Name}},
                    @{Name='State';Expression={[string]$_.State}}
        }
)

$NodeCount = $ClusterNodes.Count

if ($NodeCount -eq 1) {
    $Topology = "SingleNode"
}
elseif ($NodeCount -gt 1) {
    $Topology = "MultiNode"
}
else {
    $Topology = "Unknown"
}

# ----------------------------------------------------------------------
# Cluster Information
# ----------------------------------------------------------------------

$ClusterInformation = Invoke-HealthCheck `
    -Name "Cluster Information" `
    -Command {

        $Cluster = Get-Cluster
        $Quorum  = Get-ClusterQuorum

        [PSCustomObject]@{
            Name       = [string]$Cluster.Name
            Domain     = [string]$Cluster.Domain
            QuorumType = [string]$Quorum.QuorumType
            NodeCount  = $NodeCount
            Topology   = $Topology
        }
    }

# ----------------------------------------------------------------------
# Cluster Groups
# ----------------------------------------------------------------------

$ClusterGroups = @(
    Invoke-HealthCheck `
        -Name "Cluster Groups" `
        -Command {

            Get-ClusterGroup |
                Select-Object `
                    @{Name='Name';Expression={[string]$_.Name}},
                    @{Name='State';Expression={[string]$_.State}},
                    @{Name='OwnerNode';Expression={
                        if ($null -ne $_.OwnerNode) {
                            [string]$_.OwnerNode.Name
                        }
                        else {
                            $null
                        }
                    }}
        }
)

# ----------------------------------------------------------------------
# Cluster Resources
# ----------------------------------------------------------------------

$ClusterResources = @(
    Invoke-HealthCheck `
        -Name "Cluster Resources" `
        -Command {

            Get-ClusterResource |
                Select-Object `
                    @{Name='Name';Expression={[string]$_.Name}},
                    @{Name='State';Expression={[string]$_.State}},
                    @{Name='OwnerGroup';Expression={
                        if ($null -ne $_.OwnerGroup) {
                            [string]$_.OwnerGroup.Name
                        }
                        else {
                            $null
                        }
                    }},
                    @{Name='ResourceType';Expression={
                        if ($null -ne $_.ResourceType) {
                            [string]$_.ResourceType
                        }
                        else {
                            $null
                        }
                    }}
        }
)

# ----------------------------------------------------------------------
# Cluster Shared Volumes
# ----------------------------------------------------------------------

$ClusterSharedVolumes = @(
    Invoke-HealthCheck `
        -Name "Cluster Shared Volumes" `
        -Command {

            Get-ClusterSharedVolume |
                Select-Object `
                    @{Name='Name';Expression={[string]$_.Name}},
                    @{Name='State';Expression={[string]$_.State}},
                    @{Name='OwnerNode';Expression={
                        if ($null -ne $_.OwnerNode) {
                            [string]$_.OwnerNode.Name
                        }
                        else {
                            $null
                        }
                    }}
        }
)

# ----------------------------------------------------------------------
# Azure Local Solution Updates
# ----------------------------------------------------------------------

$SolutionUpdates = @(
    Invoke-HealthCheck `
        -Name "Azure Local Solution Updates" `
        -Command {

            if (Get-Command Get-SolutionUpdate -ErrorAction SilentlyContinue) {

                Get-SolutionUpdate |
                    Select-Object `
                        @{Name='DisplayName';Expression={[string]$_.DisplayName}},
                        @{Name='Version';Expression={[string]$_.Version}},
                        @{Name='State';Expression={[string]$_.State}}
            }
            else {
                Write-Warning "Get-SolutionUpdate is not available on this system."
            }
        }
)

# ----------------------------------------------------------------------
# Azure Local Environment Health
# ----------------------------------------------------------------------

$EnvironmentHealth = @(
    Invoke-HealthCheck `
        -Name "Azure Local Environment Health" `
        -Command {

            if (Get-Command Get-SolutionUpdateEnvironment -ErrorAction SilentlyContinue) {

                Get-SolutionUpdateEnvironment |
                    Select-Object `
                        @{Name='State';Expression={[string]$_.State}},
                        @{Name='HealthState';Expression={[string]$_.HealthState}},
                        @{Name='HealthCheckDate';Expression={
                            if ($null -ne $_.HealthCheckDate) {
                                $_.HealthCheckDate.ToString("o")
                            }
                            else {
                                $null
                            }
                        }}
            }
            else {
                Write-Warning "Get-SolutionUpdateEnvironment is not available on this system."
            }
        }
)

# ----------------------------------------------------------------------
# Console Output
# ----------------------------------------------------------------------

Write-Section "Cluster Information"
$ClusterInformation | Format-Table -AutoSize

Write-Section "Cluster Nodes"
$ClusterNodes | Format-Table -AutoSize

Write-Section "Cluster Groups"
$ClusterGroups | Format-Table -AutoSize

Write-Section "Cluster Resources"
$ClusterResources | Format-Table -AutoSize

Write-Section "Cluster Shared Volumes"
$ClusterSharedVolumes | Format-Table -AutoSize

Write-Section "Azure Local Solution Updates"
$SolutionUpdates | Format-Table -AutoSize

Write-Section "Azure Local Environment Health"
$EnvironmentHealth | Format-Table -AutoSize

# ----------------------------------------------------------------------
# Structured Health Report
# ----------------------------------------------------------------------

$HealthReport = [PSCustomObject]@{

    Metadata = $Metadata

    Cluster = [PSCustomObject]@{
        Information   = $ClusterInformation
        Nodes         = $ClusterNodes
        Groups        = $ClusterGroups
        Resources     = $ClusterResources
        SharedVolumes = $ClusterSharedVolumes
    }

    AzureLocal = [PSCustomObject]@{
        SolutionUpdates   = $SolutionUpdates
        EnvironmentHealth = $EnvironmentHealth
    }
}

# ----------------------------------------------------------------------
# Export JSON
# ----------------------------------------------------------------------

try {

    $HealthReport |
        ConvertTo-Json -Depth 6 |
        Set-Content -Path $OutputPath -Encoding UTF8 -ErrorAction Stop

    Write-Section "Health Check Completed"

    Write-Host "JSON report created:"
    Write-Host $OutputPath
    Write-Host ""

    Write-Host "Topology detected: $Topology ($NodeCount node(s))"
    Write-Host ""

    Write-Host "Review the collected information and investigate unexpected"
    Write-Host "or degraded states before proceeding with deeper troubleshooting."
    Write-Host ""
}
catch {

    Write-Warning "Unable to create JSON report: $($_.Exception.Message)"
}
