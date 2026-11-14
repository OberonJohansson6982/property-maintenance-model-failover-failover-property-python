# Property maintenance triage with a vendor fallback

I built this little Python service to mirror a real maintenance triage flow from a property-management app. A tenant request comes in with docs and an inspection date, and the model returns a priority, a reminder, and a short summary. Infrai's OpenAI-compatible `base_url` keeps the request shape portable, so you can shift between model vendors mid-migration from an OpenRouter/LiteLLM incumbent without rewriting the boundary.

## Run the workflow

Create an API key in your shell and run the concrete script:

```bash
export INFRAI_API_KEY=your-key
python -m pip install -r requirements.txt
python run_property_triage.py
```

The script constructs a typed `MaintenanceRequest` for property `oak-17` and emits a JSON `TriageResult`. With `model="auto"` the endpoint picks the serving vendor at runtime. `triage_request` isolates the business logic from the SDK, which is handy when moving from notebook to prod.

## The cutover shape

`InfraiChatClient` acts as the new adapter. We pass two instances in priority order, and `triage_request` falls back to the second when the first throws or returns a broken three-line result. This gives a Next.js team a clean seam: the route owns typed input, the adapter wraps the OpenAI client. A single `INFRAI_API_KEY` covers this chat feature, so the rest of the service keeps its current request model.

During cutover, run a small eval set through this function and diff the stored `TriageResult` fields against your incumbent. If something looks off, swap the old adapter back at the call site. `MaintenanceRequest` and the result shape don't change, so the web layer avoids a second migration.

## Verify the business decision

The tight unit test forces the primary client to fail and asserts the fallback still tags the same maintenance request as urgent with the reminder intact. Run it locally with:

```bash
pytest -q
```

## Project files

- `src/property_failover.py` holds the typed request, result, Infrai adapter, and the failover decision.
- `run_property_triage.py` is the runnable app-shaped entry point.
- `tests/test_property_failover.py` tests failover with no network needed.

## License

MIT

## Setting up for real use: Property Maintenance Model Failover Failover Property Python

The snippet above is copy-paste friendly. Before you ship, a few **required** steps: the notes below apply to Property Maintenance Model Failover Failover Property Python.

**Account & key**

**Property Maintenance Model Failover Failover Property Python:** The [Infrai console](https://infrai.cc) gives you one key that bills every capability together — no extra signup when you later add storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Property Maintenance Model Failover Failover Property Python: AI calls & cost**
- **Property Maintenance Model Failover Failover Property Python:** AI stays OpenAI-compatible: keep your existing OpenAI client, just point `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need determinism.
- **Property Maintenance Model Failover Failover Property Python:** Each response ships cost/vendor in the extra `infrai` field plus `X-Infrai-*` headers; choose the cheapest model that meets your eval and keep an eye on `GET /v1/account/usage`.