import copy

from sanitizer import sanitize_report


def build_test_report():
    return {
        "Metadata": {
            "SchemaVersion": "2.0",
            "Generated": "2026-09-21T10:00:00Z",
            "Computer": "AZL-PROD-NODE01",
            "PowerShellVersion": "5.1",
        },
        "Cluster": {
            "Information": {
                "Name": "CONTOSO-PROD-CLUSTER",
                "Domain": "corp.contoso.local",
                "QuorumType": "Majority",
                "NodeCount": 2,
                "Topology": "MultiNode",
            },
            "Nodes": [
                {
                    "Name": "AZL-PROD-NODE01",
                    "State": "Up",
                },
                {
                    "Name": "AZL-PROD-NODE02",
                    "State": "Up",
                },
            ],
            "Groups": [
                {
                    "Name": "Customer-Production-Group",
                    "State": "Online",
                    "OwnerNode": "AZL-PROD-NODE01",
                },
                {
                    "Name": "SDDC Group",
                    "State": "Online",
                    "OwnerNode": "AZL-PROD-NODE02",
                },
            ],
            "Resources": [
                {
                    "Name": "Customer-SQL-Resource",
                    "State": "Online",
                    "OwnerGroup": "Customer-Production-Group",
                    "ResourceType": "Generic Service",
                },
                {
                    "Name": "Azure Stack HCI Health Service",
                    "State": "Online",
                    "OwnerGroup": (
                        "Azure Stack HCI Health Service Cluster Group"
                    ),
                    "ResourceType": "Generic Service",
                },
            ],
            "SharedVolumes": [
                {
                    "Name": "Customer-Finance-Production",
                    "State": "Online",
                    "OwnerNode": "AZL-PROD-NODE01",
                },
            ],
        },
        "AzureLocal": {
            "SolutionUpdates": [
                {
                    "DisplayName": "Example Feature Update",
                    "Version": "12.x.x.x",
                    "State": "Ready",
                },
            ],
            "EnvironmentHealth": [
                {
                    "State": "UpdateAvailable",
                    "HealthState": "Success",
                    "HealthCheckDate": "2026-09-21T09:00:00Z",
                },
            ],
        },
    }


def test_identifiers_are_pseudonymized():
    report = build_test_report()

    sanitized = sanitize_report(report)

    assert sanitized["Metadata"]["Computer"] == "HOST-001"
    assert sanitized["Cluster"]["Information"]["Name"] == "CLUSTER-001"
    assert sanitized["Cluster"]["Information"]["Domain"] == "DOMAIN-001"
    assert sanitized["Cluster"]["Nodes"][0]["Name"] == "HOST-001"
    assert sanitized["Cluster"]["Nodes"][1]["Name"] == "HOST-002"


def test_identifier_references_remain_consistent():
    report = build_test_report()

    sanitized = sanitize_report(report)

    groups = sanitized["Cluster"]["Groups"]
    resources = sanitized["Cluster"]["Resources"]

    assert groups[0]["Name"] == "GROUP-001"
    assert resources[0]["OwnerGroup"] == "GROUP-001"
    assert groups[0]["OwnerNode"] == "HOST-001"
    assert groups[1]["OwnerNode"] == "HOST-002"


def test_unlisted_owner_group_is_replaced_as_complete_identity():
    report = build_test_report()

    sanitized = sanitize_report(report)

    resources = sanitized["Cluster"]["Resources"]

    assert resources[1]["OwnerGroup"] == "GROUP-003"
    assert resources[1]["OwnerGroup"] != "RESOURCE-002 GROUP-001"


def test_resource_and_volume_names_are_pseudonymized():
    report = build_test_report()

    sanitized = sanitize_report(report)

    resources = sanitized["Cluster"]["Resources"]
    volumes = sanitized["Cluster"]["SharedVolumes"]

    assert resources[0]["Name"] == "RESOURCE-001"
    assert resources[1]["Name"] == "RESOURCE-002"
    assert volumes[0]["Name"] == "VOLUME-001"


def test_technical_evidence_is_preserved():
    report = build_test_report()

    sanitized = sanitize_report(report)

    information = sanitized["Cluster"]["Information"]

    assert information["QuorumType"] == "Majority"
    assert information["NodeCount"] == 2
    assert information["Topology"] == "MultiNode"

    assert sanitized["Cluster"]["Nodes"][0]["State"] == "Up"

    assert (
        sanitized["Cluster"]["Resources"][0]["State"]
        == "Online"
    )

    assert (
        sanitized["Cluster"]["Resources"][0]["ResourceType"]
        == "Generic Service"
    )

    update = sanitized["AzureLocal"]["SolutionUpdates"][0]

    assert update["DisplayName"] == "Example Feature Update"
    assert update["Version"] == "12.x.x.x"
    assert update["State"] == "Ready"

    health = sanitized["AzureLocal"]["EnvironmentHealth"][0]

    assert health["State"] == "UpdateAvailable"
    assert health["HealthState"] == "Success"


def test_original_report_is_not_modified():
    report = build_test_report()

    original = copy.deepcopy(report)

    sanitize_report(report)

    assert report == original


def test_sensitive_identifiers_are_not_present_in_output():
    report = build_test_report()

    sanitized = sanitize_report(report)

    serialized = str(sanitized)

    sensitive_values = [
        "AZL-PROD-NODE01",
        "AZL-PROD-NODE02",
        "CONTOSO-PROD-CLUSTER",
        "corp.contoso.local",
        "Customer-Production-Group",
        "Customer-SQL-Resource",
        "Customer-Finance-Production",
        "Azure Stack HCI Health Service",
        "Azure Stack HCI Health Service Cluster Group",
    ]

    for value in sensitive_values:
        assert value.lower() not in serialized.lower()


def test_ipv4_addresses_are_pseudonymized_consistently():
    report = build_test_report()

    report["Cluster"]["Nodes"][0]["ManagementAddress"] = "10.20.30.40"
    report["Cluster"]["Nodes"][1]["ManagementAddress"] = "10.20.30.41"

    report["Cluster"]["Resources"][0]["DiagnosticMessage"] = (
        "Connection from 10.20.30.40 to 10.20.30.41 succeeded"
    )

    sanitized = sanitize_report(report)

    nodes = sanitized["Cluster"]["Nodes"]

    diagnostic_message = sanitized["Cluster"]["Resources"][0][
        "DiagnosticMessage"
    ]

    assert nodes[0]["ManagementAddress"] == "IP-001"
    assert nodes[1]["ManagementAddress"] == "IP-002"

    assert "IP-001" in diagnostic_message
    assert "IP-002" in diagnostic_message

    serialized = str(sanitized)

    assert "10.20.30.40" not in serialized
    assert "10.20.30.41" not in serialized


def test_guids_are_pseudonymized_consistently():
    report = build_test_report()

    first_guid = "550e8400-e29b-41d4-a716-446655440000"
    second_guid = "123e4567-e89b-12d3-a456-426614174000"

    report["Metadata"]["CorrelationId"] = first_guid
    report["Cluster"]["Resources"][0]["ActivityId"] = second_guid

    report["Cluster"]["Resources"][0]["DiagnosticMessage"] = (
        f"Correlation {first_guid} references activity {second_guid}"
    )

    sanitized = sanitize_report(report)

    assert sanitized["Metadata"]["CorrelationId"] == "GUID-001"

    assert (
        sanitized["Cluster"]["Resources"][0]["ActivityId"]
        == "GUID-002"
    )

    diagnostic_message = sanitized["Cluster"]["Resources"][0][
        "DiagnosticMessage"
    ]

    assert "GUID-001" in diagnostic_message
    assert "GUID-002" in diagnostic_message

    serialized = str(sanitized)

    assert first_guid not in serialized
    assert second_guid not in serialized


def test_email_identities_are_pseudonymized_consistently():
    report = build_test_report()

    first_identity = "admin@contoso.com"
    second_identity = "operator@fabrikam.com"

    report["Metadata"]["RequestedBy"] = first_identity
    report["Cluster"]["Resources"][0]["Operator"] = second_identity

    report["Cluster"]["Resources"][0]["DiagnosticMessage"] = (
        f"Operation requested by {first_identity} "
        f"and reviewed by {second_identity}"
    )

    sanitized = sanitize_report(report)

    assert sanitized["Metadata"]["RequestedBy"] == "IDENTITY-001"

    assert (
        sanitized["Cluster"]["Resources"][0]["Operator"]
        == "IDENTITY-002"
    )

    diagnostic_message = sanitized["Cluster"]["Resources"][0][
        "DiagnosticMessage"
    ]

    assert "IDENTITY-001" in diagnostic_message
    assert "IDENTITY-002" in diagnostic_message

    serialized = str(sanitized)

    assert first_identity not in serialized
    assert second_identity not in serialized


def test_azure_resource_ids_are_pseudonymized_as_complete_identifiers():
    report = build_test_report()

    subscription_id = "11111111-2222-3333-4444-555555555555"

    resource_id = (
        f"/subscriptions/{subscription_id}"
        "/resourceGroups/rg-customer-production"
        "/providers/Microsoft.Compute"
        "/virtualMachines/customer-vm-01"
    )

    report["AzureLocal"]["AzureResourceId"] = resource_id

    report["Cluster"]["Resources"][0]["DiagnosticMessage"] = (
        f"Related Azure resource: {resource_id}"
    )

    sanitized = sanitize_report(report)

    assert (
        sanitized["AzureLocal"]["AzureResourceId"]
        == "AZURE-RESOURCE-ID-001"
    )

    diagnostic_message = sanitized["Cluster"]["Resources"][0][
        "DiagnosticMessage"
    ]

    assert "AZURE-RESOURCE-ID-001" in diagnostic_message

    serialized = str(sanitized)

    assert resource_id not in serialized
    assert subscription_id not in serialized
    assert "rg-customer-production" not in serialized
    assert "customer-vm-01" not in serialized


def test_invalid_ipv4_candidate_is_not_treated_as_ip_address():
    report = build_test_report()

    invalid_address = "999.999.999.999"

    report["Metadata"]["DiagnosticValue"] = invalid_address

    sanitized = sanitize_report(report)

    assert sanitized["Metadata"]["DiagnosticValue"] == invalid_address