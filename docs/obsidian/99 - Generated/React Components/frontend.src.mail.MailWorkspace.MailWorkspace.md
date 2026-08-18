---
type: component
generated: true
language: typescript
layer: frontend
qualified_name: frontend.src.mail.MailWorkspace.MailWorkspace
source: frontend/src/mail/MailWorkspace.tsx
status: active
tags: [component, frontend]
---

# MailWorkspace

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

React component declared in `frontend/src/mail/MailWorkspace.tsx`.

## Location

`frontend/src/mail/MailWorkspace.tsx`

## Signature

```ts
export function MailWorkspace(
```

## React Query usage

- `{
    queryKey: ['emailCounts'],
    queryFn: emailCounts,
    staleTime: 15_000,
  }`
- `{
    queryKey: ['accounts'],
    queryFn: fetchAccounts,
    staleTime: 10_000,
    refetchInterval: ACCOUNTS_REFRESH_MS,
  }`
- `{
    queryKey: ['emails', { view, kind, category, filter, globalSearchActive, searchQuery, viewFilter }],
    queryFn: () => fetchEmails({
      category: globalSearchActive || view === 'all' ? null : category,
      scope,
      kind: globalSearchActive ? null : view === 'all' ? kind : null,
      priority: filter === 'important' && !globalSearchActive ? 'high' : undefined,
      needsReply: filter === 'reply' && !globalSearchActive ? true : undefined,
      query: activeQuery || undefined,
      limit: 500,
    }),
    staleTime: 15_000,
  }`
- `mutate: (id: string) => backfillAccount(id)`
- `mutate: (id: string) => pauseBackfill(id)`

## Related

- [[frontend.src.mail.MailWorkspace|MailWorkspace]] (module)
