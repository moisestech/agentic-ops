# Contracts

OpenAPI is generated from the FastAPI app:

```bash
make install
make openapi
```

`openapi.json` is the source of truth for the TypeScript client in `apps/web`.
Generated `types.ts` lands here once the generator is wired in CI.
