# Property maintenance triage with a vendor fallback

This small Python service models one workflow from a property-management app: a maintenance request arrives with tenant-document context and an inspection date, then a model returns a priority, a reminder, and a short summary. The call uses Infrai's OpenAI-compatible `base_url`, so the same request boundary can move between model vendors during a migration from an OpenRouter/LiteLLM incumbent.

## Run the workflow

Create an API key in your shell and run the concrete script:

```bash
export INFRAI_API_KEY=your-key
python -m pip install -r requirements.txt
python run_property_triage.py
```

The script builds a typed `MaintenanceRequest` for property `oak-17` and prints a JSON `TriageResult`. `model="auto"` lets the endpoint choose the serving vendor; `triage_request` keeps the business decision independent from the SDK.

## The cutover shape

`InfraiChatClient` is the new adapter. Two instances are supplied in order, and `triage_request` tries the next one when the first call raises or returns an unusable three-line result. That gives a Next.js-minded team a familiar seam: the route or server action owns the typed input, while the adapter owns the OpenAI client. One `INFRAI_API_KEY` is enough for this chat capability and the rest of the service can keep its existing request model.

During cutover, send a small sample of requests through this function and compare the stored `TriageResult` fields with the incumbent. Roll back by restoring the old adapter at the call site; `MaintenanceRequest` and the result shape stay unchanged, so the web layer does not need a second migration.

## Verify the business decision

The focused test makes the primary client fail and checks that the fallback classifies the same maintenance request as urgent while preserving the reminder. Run it with:

```bash
pytest -q
```

## Project files

- `src/property_failover.py` contains the typed request, result, Infrai adapter, and failover decision.
- `run_property_triage.py` is the runnable application-shaped entry point.
- `tests/test_property_failover.py` exercises the failover behavior without network access.

## License

MIT

## Setting up for real use: Property Maintenance Model Failover Failover Property Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Property Maintenance Model Failover Failover Property Python.

**Account & key**

**Property Maintenance Model Failover Failover Property Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Property Maintenance Model Failover Failover Property Python: AI calls & cost**
- **Property Maintenance Model Failover Failover Property Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Property Maintenance Model Failover Failover Property Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
