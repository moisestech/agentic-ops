from agentic_ops.config import settings
from agentic_ops.providers.fake import FakeProvider


def get_provider():
    name = settings.agent_provider.lower().strip()
    if name in {"fake", "offline", "test"}:
        return FakeProvider()
    if name == "openai":
        raise RuntimeError("OpenAI adapter is scaffolded but not enabled until parity tests land.")
    if name in {"anthropic", "claude"}:
        raise RuntimeError("Claude adapter is scaffolded but not enabled until parity tests land.")
    if name == "bedrock":
        raise RuntimeError("Bedrock adapter is reserved for the AWS evaluation path.")
    raise RuntimeError(f"Unknown AGENT_PROVIDER={name!r}")
