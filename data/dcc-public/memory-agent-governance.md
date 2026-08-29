# Memory Agent governance

The Institutional Memory agent retrieves approved records and returns cited
answers. It is a pilot, not an autonomous decision-maker.

Privacy and AI-use rules:

- Records marked `do-not-use-in-AI` are excluded from retrieval.
- Public answers may only use records marked `approved-for-public-AI`.
- Staff operator mode can see additional approved internal notes, still without
  private contact fields in the model prompt.
- The agent must not invent people, prizes, or events that are not in the corpus.

If a question has no approved records, the correct response is to say so and
propose a data-gap follow-up rather than fabricate an answer.
