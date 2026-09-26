---
type: component
generated: true
language: typescript
layer: frontend
qualified_name: frontend.src.App.App
source: frontend/src/App.tsx
status: active
tags: [component, frontend]
---

# App

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

React component declared in `frontend/src/App.tsx`.

## Location

`frontend/src/App.tsx`

## Signature

```ts
export default function App()
```

## React Query usage

- `{ queryKey: ['accounts'], queryFn: fetchAccounts }`
- `{
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30_000,
    retry: 0,
  }`
- `{
    queryKey: ['emailCounts', 'all'],
    queryFn: () => fetchEmailCounts(),
    staleTime: 30_000,
    retry: 0,
  }`
- `mutate: async (ids: string[]): Promise<SyncOutcome[]> => {
      const settled = await Promise.allSettled(ids.map(id => syncAccount(id, false)));
      return ids.map((id, i) => {
        const result = settled[i];
        if (result.status === 'fulfilled') return { id, ok: true };
        const reason = result.reason;
        return {
          id,
          ok: false,
          error: reason instanceof Error ? reason.message : 'Sync failed',
        };
      });
    }`

## Related

- [[frontend.src.App|App]] (module)
