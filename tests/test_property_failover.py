from src.property_failover import MaintenanceRequest, triage_request


class DownClient:
    def complete(self, prompt: str) -> str:
        raise ConnectionError("primary unavailable")


class WorkingClient:
    def complete(self, prompt: str) -> str:
        assert "oak-17" in prompt
        return "urgent\nNotify the tenant before entry\nSink leak needs same-day maintenance"


def test_maintenance_request_fails_over_to_next_client():
    request = MaintenanceRequest(
        property_id="oak-17",
        tenant_name="Mina Chen",
        description="Water leak",
        document_text="Access notice required",
        inspection_due="2026-10-15",
    )
    result = triage_request(request, [DownClient(), WorkingClient()])
    assert result.priority == "urgent"
    assert result.reminder.startswith("Notify")
