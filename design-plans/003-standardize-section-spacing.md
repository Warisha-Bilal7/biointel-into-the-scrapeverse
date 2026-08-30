# Plan 003 — Standardize Dashboard section spacing to match the rest of the surface

## Problem
The Dashboard route (`/`) spaces its top-level sections with `mb-12` / `mt-12`. Every other route on the same surface — sharing the same `app/layout.tsx`, `Sidebar`, and `Header` — spaces its top-level sections with `mb-8`. This creates a visible, provable rhythm inconsistency: navigating from the Dashboard to any other page (System Status, Ingestion, Explorer, Settings) noticeably tightens the vertical spacing between panels, and navigating back loosens it again.

The `mb-8` convention is established by a 4:1 majority across the surface's routes (all routes except the Dashboard), so it is the correction target rather than an arbitrary choice.

## Evidence
- **File:** `frontend/app/page.tsx` — 4 instances of `mb-12`/`mt-12` between top-level `<section>` elements:
  1. Hero section: `className="mb-12 rounded-2xl p-8 md:p-12 bg-card border border-border/30"`
  2. Overall Health section: `className="mb-12 rounded-2xl p-6 md:p-8 border-t"`
  3. Timeline section: `className="mt-12 rounded-2xl p-6 md:p-8 bg-card border border-border/30"`
  4. Footer pitch section: `className="mt-12 rounded-2xl p-6 bg-card border border-border/30 text-center"`

- **Established convention, same surface:**
  - `frontend/app/system-status/page.tsx`: hero section `className="mb-8 rounded-2xl p-8 md:p-12 bg-card border border-border/30"`, health metrics section `className="mb-8 grid gap-4 md:grid-cols-4"`
  - `frontend/app/ingestion/page.tsx`: hero `className="mb-8 rounded-2xl p-8 md:p-12 bg-card border border-border/30"`, test-payload section `className="mb-8 rounded-2xl p-6 md:p-8 bg-card border border-border/30"`
  - `frontend/app/explorer/page.tsx`: hero `className="mb-8 rounded-2xl p-8 md:p-12 bg-card border border-border/30"`, search section `className="mb-6"`

## Correction
In `frontend/app/page.tsx`, change all 4 instances of `mb-12`/`mt-12` on top-level sections to `mb-8`/`mt-8` respectively:

```diff
- <section className="mb-12 rounded-2xl p-8 md:p-12 bg-card border border-border/30">
+ <section className="mb-8 rounded-2xl p-8 md:p-12 bg-card border border-border/30">
  (hero section)

- <section className="mb-12 rounded-2xl p-6 md:p-8 border-t" style={{ borderColor: 'rgba(15, 107, 94, 0.3)' }}>
+ <section className="mb-8 rounded-2xl p-6 md:p-8 border-t" style={{ borderColor: 'rgba(15, 107, 94, 0.3)' }}>
  (Overall Health section)

- <section className="mt-12 rounded-2xl p-6 md:p-8 bg-card border border-border/30">
+ <section className="mt-8 rounded-2xl p-6 md:p-8 bg-card border border-border/30">
  (Timeline section)

- <section className="mt-12 rounded-2xl p-6 bg-card border border-border/30 text-center">
+ <section className="mt-8 rounded-2xl p-6 bg-card border border-border/30 text-center">
  (Footer pitch section)
```

Do not change the `<div className="grid gap-6 lg:grid-cols-3">` wrapper between the Sources/Alert columns — its `gap-6` is a different spacing role (inter-column, not inter-section) and is out of scope for this finding.

## Verification
1. Run the frontend locally (`npm run dev`).
2. Compare vertical spacing between panels on `/` against `/system-status` — they should now feel consistent when navigating between them.
3. No change to padding *within* any section (e.g. `p-6 md:p-8`), only the margin *between* sections.
