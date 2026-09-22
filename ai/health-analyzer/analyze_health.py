import json
import os
import sys
from pathlib import Path
from typing import Literal

from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from pydantic import BaseModel
from sanitizer import sanitize_report


FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT")
FOUNDRY_DEPLOYMENT = os.getenv("FOUNDRY_DEPLOYMENT")


class Finding(BaseModel):
    category: str
    severity: Literal["Informational", "Advisory", "Warning", "Critical"]
    title: str
    evidence: list[str]
    recommendation: str


class HealthAnalysis(BaseModel):
    overall_assessment: str
    findings: list[Finding]
    recommended_next_checks: list[str]
    additional_data_required: list[str]


def load_health_report(file_path):
    """Load and validate an Azure Local health report."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Health report not found: {path}")

    with path.open("r", encoding="utf-8-sig") as file:
        report = json.load(file)

    required_sections = ["Metadata", "Cluster", "AzureLocal"]

    missing_sections = [
        section
        for section in required_sections
        if section not in report
    ]

    if missing_sections:
        raise ValueError(
            "Invalid health report. Missing section(s): "
            + ", ".join(missing_sections)
        )

    return report


def analyze_with_foundry(report):
    """Analyze the validated health report with Microsoft Foundry."""

    if not FOUNDRY_ENDPOINT:
        raise ValueError(
            "FOUNDRY_ENDPOINT environment variable is not configured."
        )

    if not FOUNDRY_DEPLOYMENT:
        raise ValueError(
            "FOUNDRY_DEPLOYMENT environment variable is not configured."
        )

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://ai.azure.com/.default"
    )

    client = OpenAI(
        base_url=FOUNDRY_ENDPOINT,
        api_key=token_provider
    )

    instructions = """
You are an Azure Local Health Analysis assistant.

Analyze only the health-report evidence provided by the user.

Rules:
- Use only information explicitly present in the supplied health report.
- Do not invent missing configuration, events, errors, causes, or remediation steps.
- Do not treat a SingleNode topology as unhealthy by itself.
- Do not assume that an Offline resource is a problem without sufficient context.
- Do not describe the entire Azure Local environment as healthy solely because
  the supplied checks show successful states.
- Prefer wording such as "no degraded conditions are evident in the supplied report."
- Treat status values such as Ready, Offline, UpdateAvailable, Success, and Installed
  as observed evidence.
- Do not infer their operational meaning unless supported by the supplied data.
- Separate observations from conclusions.
- Do not claim root cause unless the supplied evidence supports it.
- If evidence is insufficient, state that clearly.
- Keep the analysis concise and technical.

For each finding:
- Use category to identify the technical area.
- Use severity to describe the significance of the observed evidence.
- Keep evidence directly traceable to the supplied health report.
- Keep recommendations limited to reasonable next validation steps.
"""

    report_json = json.dumps(report, indent=2)

    response = client.responses.parse(
        model=FOUNDRY_DEPLOYMENT,
        instructions=instructions,
        input=(
            "Analyze the following Azure Local health report:\n\n"
            + report_json
        ),
        text_format=HealthAnalysis
    )

    return response.output_parsed


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

        print()
        print("Applying privacy sanitization...")
        sanitized_report = sanitize_report(report)
        print("Privacy sanitization completed.")

        print()
        print("Running structured AI analysis with Microsoft Foundry...")
        print()

        analysis = analyze_with_foundry(sanitized_report)

        print("Structured AI Health Analysis")
        print("-----------------------------")

        analysis_json = analysis.model_dump_json(indent=2)
        print(analysis_json)

        input_path = Path(sys.argv[1])
        output_path = input_path.with_name(
            input_path.stem + "-analysis.json"
        )

        output_path.write_text(
            analysis_json,
            encoding="utf-8"
        )

        print()
        print(f"Analysis saved to: {output_path}")

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()