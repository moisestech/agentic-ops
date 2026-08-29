# The agent is expensive and hallucinating

**Prompt:** Quality dropped and the bill rose after a live-model swap.

**First moves**

1. Replay the golden set offline (`make eval-offline`). If fake still passes, the regression is the provider, not retrieval.
2. Fail closed on missing citations. Do not "repair" with a second, more expensive call.
3. Cache identical brief + corpus hash. Most Saturday cycles are repeats.
4. Route: tools and retrieval first; model only to draft from passages.

**Eval design:** groundedness, tool-choice, approval compliance, refusal. Not BLEU. Not "sounds institutional."

**This repo's answer:** CI never calls a paid model. Unsupported ids cannot execute.
