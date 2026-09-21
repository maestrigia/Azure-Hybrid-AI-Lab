import copy
import ipaddress
import re
import uuid
from typing import Any


class ReportSanitizer:
    """
    Sanitizes infrastructure identity information before a health report
    is sent to an external AI service.

    Operational evidence such as states, resource types, versions,
    timestamps, topology, and update information is preserved.
    """

    _IPV4_CANDIDATE_PATTERN = re.compile(
        r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])"
    )

    _GUID_CANDIDATE_PATTERN = re.compile(
        r"(?<![0-9A-Fa-f])"
        r"[0-9A-Fa-f]{8}-"
        r"[0-9A-Fa-f]{4}-"
        r"[0-9A-Fa-f]{4}-"
        r"[0-9A-Fa-f]{4}-"
        r"[0-9A-Fa-f]{12}"
        r"(?![0-9A-Fa-f])"
    )

    def __init__(self) -> None:
        self._replacements: dict[str, str] = {}

        self._host_counter = 0
        self._cluster_counter = 0
        self._domain_counter = 0
        self._group_counter = 0
        self._resource_counter = 0
        self._volume_counter = 0
        self._ip_counter = 0
        self._guid_counter = 0

    def sanitize(self, report: dict[str, Any]) -> dict[str, Any]:
        """
        Return a sanitized deep copy of the supplied report.
        The original report is never modified.
        """
        sanitized = copy.deepcopy(report)

        self._discover_identifiers(sanitized)
        self._discover_ipv4_addresses(sanitized)
        self._discover_guids(sanitized)

        return self._replace_recursive(sanitized)

    def _add_replacement(
        self,
        original: Any,
        replacement: str,
    ) -> None:
        """
        Register an identifier replacement if the original value is a
        non-empty string and has not already been registered.
        """
        if not isinstance(original, str):
            return

        original = original.strip()

        if not original:
            return

        if original not in self._replacements:
            self._replacements[original] = replacement

    def _discover_identifiers(
        self,
        report: dict[str, Any],
    ) -> None:
        """
        Discover infrastructure identifiers that may contain environment,
        organization, workload, or customer-specific information.
        """

        # --------------------------------------------------------------
        # Metadata / host identity
        # --------------------------------------------------------------
        metadata = report.get("Metadata", {})

        if isinstance(metadata, dict):
            computer = metadata.get("Computer")

            if computer:
                self._host_counter += 1
                self._add_replacement(
                    computer,
                    f"HOST-{self._host_counter:03d}",
                )

        # --------------------------------------------------------------
        # Cluster
        # --------------------------------------------------------------
        cluster = report.get("Cluster", {})

        if not isinstance(cluster, dict):
            return

        # --------------------------------------------------------------
        # Cluster identity
        # --------------------------------------------------------------
        information = cluster.get("Information", {})

        if isinstance(information, dict):
            cluster_name = information.get("Name")

            if cluster_name:
                self._cluster_counter += 1
                self._add_replacement(
                    cluster_name,
                    f"CLUSTER-{self._cluster_counter:03d}",
                )

            domain = information.get("Domain")

            if domain:
                self._domain_counter += 1
                self._add_replacement(
                    domain,
                    f"DOMAIN-{self._domain_counter:03d}",
                )

        # --------------------------------------------------------------
        # Cluster nodes
        # --------------------------------------------------------------
        nodes = cluster.get("Nodes", [])

        if isinstance(nodes, list):
            for node in nodes:
                if not isinstance(node, dict):
                    continue

                node_name = node.get("Name")

                if not node_name:
                    continue

                if node_name in self._replacements:
                    continue

                self._host_counter += 1

                self._add_replacement(
                    node_name,
                    f"HOST-{self._host_counter:03d}",
                )

        # --------------------------------------------------------------
        # Cluster groups
        # --------------------------------------------------------------
        groups = cluster.get("Groups", [])

        if isinstance(groups, list):
            for group in groups:
                if not isinstance(group, dict):
                    continue

                group_name = group.get("Name")

                if not group_name:
                    continue

                if group_name in self._replacements:
                    continue

                self._group_counter += 1

                self._add_replacement(
                    group_name,
                    f"GROUP-{self._group_counter:03d}",
                )

        # --------------------------------------------------------------
        # Cluster resources and their owner-group references
        # --------------------------------------------------------------
        resources = cluster.get("Resources", [])

        if isinstance(resources, list):
            for resource in resources:
                if not isinstance(resource, dict):
                    continue

                # OwnerGroup may reference a cluster group that is not
                # included in Cluster.Groups. Discover the complete
                # OwnerGroup value before resource names are registered.
                #
                # This prevents partial replacements such as:
                #
                # "Azure Stack HCI Health Service Cluster Group"
                #
                # becoming:
                #
                # "RESOURCE-002 GROUP-001"
                #
                # instead of a single pseudonymous group identifier.
                owner_group = resource.get("OwnerGroup")

                if (
                    owner_group
                    and owner_group not in self._replacements
                ):
                    self._group_counter += 1

                    self._add_replacement(
                        owner_group,
                        f"GROUP-{self._group_counter:03d}",
                    )

                resource_name = resource.get("Name")

                if (
                    resource_name
                    and resource_name not in self._replacements
                ):
                    self._resource_counter += 1

                    self._add_replacement(
                        resource_name,
                        f"RESOURCE-{self._resource_counter:03d}",
                    )

        # --------------------------------------------------------------
        # Cluster Shared Volumes
        # --------------------------------------------------------------
        shared_volumes = cluster.get("SharedVolumes", [])

        if isinstance(shared_volumes, list):
            for volume in shared_volumes:
                if not isinstance(volume, dict):
                    continue

                volume_name = volume.get("Name")

                if not volume_name:
                    continue

                if volume_name in self._replacements:
                    continue

                self._volume_counter += 1

                self._add_replacement(
                    volume_name,
                    f"VOLUME-{self._volume_counter:03d}",
                )

    def _discover_ipv4_addresses(
        self,
        value: Any,
    ) -> None:
        """
        Recursively discover valid IPv4 addresses in string values.
        """

        if isinstance(value, dict):
            for item in value.values():
                self._discover_ipv4_addresses(item)
            return

        if isinstance(value, list):
            for item in value:
                self._discover_ipv4_addresses(item)
            return

        if not isinstance(value, str):
            return

        for match in self._IPV4_CANDIDATE_PATTERN.finditer(value):
            candidate = match.group(0)

            try:
                address = ipaddress.ip_address(candidate)
            except ValueError:
                continue

            if not isinstance(address, ipaddress.IPv4Address):
                continue

            if candidate in self._replacements:
                continue

            self._ip_counter += 1

            self._add_replacement(
                candidate,
                f"IP-{self._ip_counter:03d}",
            )

    def _discover_guids(
        self,
        value: Any,
    ) -> None:
        """
        Recursively discover GUIDs in string values.
        """

        if isinstance(value, dict):
            for item in value.values():
                self._discover_guids(item)
            return

        if isinstance(value, list):
            for item in value:
                self._discover_guids(item)
            return

        if not isinstance(value, str):
            return

        for match in self._GUID_CANDIDATE_PATTERN.finditer(value):
            candidate = match.group(0)

            try:
                uuid.UUID(candidate)
            except ValueError:
                continue

            if candidate in self._replacements:
                continue

            self._guid_counter += 1

            self._add_replacement(
                candidate,
                f"GUID-{self._guid_counter:03d}",
            )

    def _replace_string(
        self,
        value: str,
    ) -> str:
        """
        Replace discovered identifiers inside a string.

        Longer identifiers are replaced first so that a complete identity
        takes precedence over a shorter identity contained within it.
        """
        sanitized = value

        replacements = sorted(
            self._replacements.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        for original, replacement in replacements:
            sanitized = re.sub(
                re.escape(original),
                replacement,
                sanitized,
                flags=re.IGNORECASE,
            )

        return sanitized

    def _replace_recursive(
        self,
        value: Any,
    ) -> Any:
        """
        Recursively apply identifier replacements throughout the report.
        """
        if isinstance(value, dict):
            return {
                key: self._replace_recursive(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                self._replace_recursive(item)
                for item in value
            ]

        if isinstance(value, str):
            return self._replace_string(value)

        return value


def sanitize_report(
    report: dict[str, Any],
) -> dict[str, Any]:
    """
    Return a sanitized copy of an Azure Local health report.

    The original report is not modified.
    """
    sanitizer = ReportSanitizer()

    return sanitizer.sanitize(report)