from src.property_failover import MaintenanceRequest, configured_clients, triage_request


request = MaintenanceRequest(
    property_id="oak-17",
    tenant_name="Mina Chen",
    description="Water is dripping under the kitchen sink.",
    document_text="Lease requires access notice before non-emergency entry.",
    inspection_due="2026-10-15",
)
result = triage_request(request, configured_clients())
print(result.model_dump_json(indent=2))
