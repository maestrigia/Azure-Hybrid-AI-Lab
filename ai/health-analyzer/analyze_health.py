import json
import sys
from pathlib import Path


def load_health_report(file_path):
    """Load and validate an Azure Local health report."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Health report not found: {path}")

    with path.open("r", encoding="utf-8-sig") as file:
        report = json.load(file)

    required_sections = ["Metadata", "Cluster", "AzureLocal"]

    missing_sections = [
        section for section in required_sections
        if section not in report
    ]

    if missing_sections:
        raise ValueError(
            "Invalid health report. Missing section(s): "
            + ", ".join(missing_sections)
        )

    return report


def display_summary(report):
    """Display a basic summary of the health report."""

    metadata = report.get("Metadata", {})
    cluster = report.get("Cluster", {})
    cluster_info = cluster.get("Information", {})
    azure_local = report.get("AzureLocal", {})

    nodes = cluster.get("Nodes", [])
    updates = azure_local.get("SolutionUpdates", [])
    environment_health = azure_local.get("EnvironmentHealth", [])

    print()
    print("Azure Local Health Analyzer")
    print("---------------------------")
    print(f"Schema Version : {metadata.get('SchemaVersion', 'Unknown')}")
    print(f"Cluster        : {cluster_info.get('Name', 'Unknown')}")
    print(f"Topology       : {cluster_info.get('Topology', 'Unknown')}")
    print(f"Node Count     : {cluster_info.get('NodeCount', 'Unknown')}")
    print(f"Nodes Found    : {len(nodes)}")
    print(f"Updates Found  : {len(updates)}")

    if environment_health:
        health = environment_health[0]
        print(f"Health State   : {health.get('HealthState', 'Unknown')}")

    print()
    print("Health report loaded successfully.")
    print("Ready for analysis.")


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python analyze_health.py <health-report.json>")
        sys.exit(1)

    try:
        report = load_health_report(sys.argv[1])
        display_summary(report)

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
