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
- `mutate: (id: string) => syncAccount(id, false)`

## Related

- [[frontend.src.App|App]] (module)
