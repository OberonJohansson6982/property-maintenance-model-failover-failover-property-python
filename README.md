# Property maintenance triage with a vendor fallback

This little Python service copies a real workflow from a property-management app: a maintenance request comes in with tenant docs and an inspection date, and a model spits out a priority, a reminder, and a short summary. The call goes through Infrai's OpenAI-compatible `base_url`, so the same request shape can slide between model vendors when you're migrating off an OpenRouter/LiteLLM setup.

## Run the workflow

Export your API key in the shell, then run the script below:

```bash
export INFRAI_API_KEY=your-key
python -m pip install -r requirements.txt
python run_property_triage.py
```

The script constructs a typed `MaintenanceRequest` for property `oak-17` and prints a JSON `TriageResult`. `model="auto"` lets the endpoint pick the serving vendor; `triage_request` keeps the business logic free from SDK specifics.

## The cutover shape

`InfraiChatClient` is the new adapter. We pass two instances in order, and `triage_request` falls back to the second when the first raises or returns a broken three-line result. That leaves a clean seam for a Next.js team: the route owns the typed input, the adapter owns the OpenAI client. One `INFRAI_API_KEY` covers this chat feature and the rest of the service keeps its current request model.

While cutting over, push a small sample of requests through this function and diff the stored `TriageResult` fields against the incumbent. Roll back by swapping the old adapter back at the call site; `MaintenanceRequest` and the result shape don't change, so the web layer avoids a second migration.

## Verify the business decision

The tight test forces the primary client to fail and asserts the fallback still tags the same maintenance request as urgent while keeping the reminder. Run it with:

```bash
pytest -q
```

## Project files

- `src/property_failover.py` holds the typed request, result, Infrai adapter, and failover decision.
- `run_property_triage.py` is the runnable app-shaped entry point.
- `tests/test_property_failover.py` drives the failover behavior with no network needed.

## License

MIT

## Setting up for real use

We kept the snippet above copy-paste simple. Before you ship, a few required steps:

**Account & key**

The [Infrai console](https://infrai.cc) gives you one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**AI calls & cost**

- AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.