---
type: component
generated: true
language: typescript
layer: frontend
qualified_name: frontend.src.features.overview.OverviewPage.OverviewPage
source: frontend/src/features/overview/OverviewPage.tsx
status: active
tags: [component, frontend]
---

# OverviewPage

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

React component declared in `frontend/src/features/overview/OverviewPage.tsx`.

## Location

`frontend/src/features/overview/OverviewPage.tsx`

## Signature

```ts
export function OverviewPage(
```

## React Query usage

- `{ queryKey: ['briefing'], queryFn: fetchBriefing }`
- `{
    queryKey: ['emails', { scope: 'overview' }],
    queryFn: () => fetchEmails({ limit: 200 }),
  }`
- `{ queryKey: ['emailCounts'], queryFn: emailCounts }`
- `mutate: regenerateBriefing`

## Related

- [[frontend.src.features.overview.OverviewPage|OverviewPage]] (module)
