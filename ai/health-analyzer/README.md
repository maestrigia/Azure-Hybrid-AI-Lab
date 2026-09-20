# Azure Local AI Health Analyzer

A lightweight AI-assisted analyzer for structured Azure Local health reports.

The project combines deterministic health-data collection with evidence-grounded AI analysis using Microsoft Foundry.

The analyzer does not connect directly to an Azure Local cluster. It consumes a structured JSON health report generated separately by the Azure Local health-check collector.

## Architecture

```text
Azure Local
    |
    v
PowerShell Health Collector
    |
    v
AzureLocalHealthSummary.json
    |
    v
Python Health Analyzer
    |
    v
Microsoft Foundry
    |
    v
Structured HealthAnalysis JSON
```

The design intentionally separates data collection from AI interpretation.

The PowerShell collector gathers deterministic evidence from the environment. The Python analyzer validates the report and sends the structured evidence to a Microsoft Foundry model for interpretation.

## Current Capabilities

The analyzer currently:

- Loads Azure Local health reports in JSON format.

- Validates the expected top-level report structure.

- Uses Microsoft Entra ID authentication.

- Connects to a Microsoft Foundry model deployment.

- Uses Pydantic structured output.

- Produces findings with controlled severity values.

- Separates evidence from recommendations.

- Writes the AI analysis to a standalone JSON file.

Supported severity values are:

```text
Informational
Advisory
Warning
Critical
```

## AI Analysis Principles

The model is instructed to:

- Use only evidence explicitly present in the supplied report.

- Avoid inventing missing configuration, events, errors, causes, or remediation.

- Avoid treating a SingleNode topology as unhealthy by itself.

- Avoid assuming that an Offline resource represents a problem without sufficient context.

- Avoid declaring the entire environment healthy based only on successful supplied checks.

- Treat status values as observed evidence unless their meaning is supported by the supplied data.

- Separate observations from conclusions.

- Avoid root-cause claims unless supported by evidence.

- State when the available evidence is insufficient.

AI output should be treated as an analysis aid rather than a replacement for engineering validation.

## Requirements

- Python 3

- Azure CLI

- Access to a Microsoft Foundry project and model deployment

- Microsoft Entra ID permissions required to access the Foundry resource

Install the Python dependencies:

```powershell
pip install -r requirements.txt
```

The current dependencies are:

```text
openai
azure-identity
pydantic
```

## Microsoft Entra ID Authentication

The analyzer does not require an API key in the source code.

For local development, authenticate with Azure CLI:

```powershell
az login
```

Verify the active Azure account:

```powershell
az account show
```

If required, verify that an access token can be obtained for the Azure AI scope:

```powershell
az account get-access-token --scope https://ai.azure.com/.default
```

Do not publish or store the returned access token.

The Python application uses:

```python
DefaultAzureCredential()
```

together with a bearer token provider for:

```text
https://ai.azure.com/.default
```

During local development, `DefaultAzureCredential` can use the authenticated Azure CLI session.

If authentication fails with an Azure CLI credential message asking you to sign in, refresh the session with:

```powershell
az login
```

## Microsoft Foundry Setup

Before running the analyzer, create or use an existing Microsoft Foundry project in your Azure subscription.

### 1. Create a Foundry resource and project

Create a Microsoft Foundry resource and a project that will host the model deployment used by the analyzer.

The analyzer does not require direct access from Foundry to the Azure Local environment. Only the structured health report is sent to the configured model endpoint.

### 2. Deploy a compatible model

From the Foundry model catalog, deploy a model that supports the OpenAI Responses API and structured outputs.

Note the deployment name. This value will later be configured as:

`FOUNDRY_DEPLOYMENT`

The analyzer is intentionally not tied to a hard-coded model deployment.

### 3. Configure Microsoft Entra ID access

Ensure that the identity running the analyzer has the `Foundry User` role on the Foundry resource.

For local development, authenticate the Azure CLI with:

```powershell
az login
az account show
```

The analyzer uses `DefaultAzureCredential` and Microsoft Entra ID authentication rather than storing an API key in the source code.

### 4. Retrieve the Foundry endpoint

Retrieve the OpenAI-compatible endpoint associated with your Foundry resource.

The endpoint follows this general format:

```text
https://<your-resource>.services.ai.azure.com/openai/v1
```

This value will later be configured as:

`FOUNDRY_ENDPOINT`

Do not commit resource-specific endpoints, credentials, access tokens, subscription IDs, or tenant IDs to the repository.


### Official Microsoft documentation

- [Create Microsoft Foundry resources and a project](https://learn.microsoft.com/en-us/azure/foundry/tutorials/quickstart-create-foundry-resources)
- [Microsoft Foundry RBAC and roles](https://learn.microsoft.com/en-us/azure/foundry/concepts/rbac-foundry)

## Foundry Configuration

The analyzer reads the Foundry configuration from environment variables.

Set them in the current PowerShell session:

```powershell
$env:FOUNDRY_ENDPOINT="https://<your-resource>.services.ai.azure.com/openai/v1"
$env:FOUNDRY_DEPLOYMENT="<your-model-deployment>"
```

No endpoint or deployment name needs to be hard-coded into the Python source.

## Running the Analyzer

From the repository root, run:

```powershell
python .\ai\health-analyzer\analyze_health.py .\azure-local\health-checks\examples\sample-health-report.json
```

The analyzer:

1. Loads and validates the health report.

2. Displays a basic deterministic summary.

3. Authenticates to Microsoft Foundry using Microsoft Entra ID.

4. Sends the structured report to the configured model.

5. Validates the model response against the Pydantic schema.

6. Displays the structured analysis.

7. Writes the analysis to a separate JSON file.

For:

```text
sample-health-report.json
```

the generated output is written next to the input health report as:

```text
sample-health-report-analysis.json
```

## Structured Output

The current analysis schema contains:

```text
HealthAnalysis
|
+-- overall_assessment
|
+-- findings[]
|   +-- category
|   +-- severity
|   +-- title
|   +-- evidence[]
|   +-- recommendation
|
+-- recommended_next_checks[]
|
+-- additional_data_required[]
```

Using structured output makes the result suitable for future API, automation, dashboard, or web-application integration without parsing free-form AI text.

## Example Files

`sample-health-report.json` contains anonymized example health data.

`sample-health-report-analysis.json` demonstrates the structured AI output generated from the sample report.

The example data is intended only to demonstrate the analyzer workflow.

## Security and Privacy

Do not submit or publish health reports containing sensitive customer or production information without appropriate review and sanitization.

Before using this approach with real environments, consider removing or anonymizing information such as:

- Host names

- Cluster names

- Domain names

- Resource names

- Infrastructure identifiers

- Other environment-specific information

Never commit credentials, access tokens, API keys, customer data, or confidential information to the repository.

## Future Direction

Potential next steps include:

- A sanitization layer before AI processing.

- Additional deterministic health rules.

- FastAPI integration.

- Azure App Service deployment.

- Managed Identity authentication for the hosted application.

- Optional grounding with authoritative public Microsoft documentation.

- Historical report comparison and trend analysis.

For an Azure-hosted implementation, Managed Identity is the preferred direction so that application credentials do not need to be stored in source code or configuration files.

## Disclaimer

This project is intended for learning, experimentation, and technical demonstration.

It is not an official Microsoft support tool and does not replace official product documentation, support processes, or engineering investigation.

Public examples must not contain customer data, confidential Microsoft information, proprietary code, internal tools, or non-public troubleshooting procedures.
