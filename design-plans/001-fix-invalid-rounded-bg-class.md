# Plan 001 — Fix invalid `rounded-bg` class on the Dashboard alert icon wrapper

## Problem
The Alert icon wrapper on the Dashboard route uses an invalid Tailwind class, `rounded-bg`, which is not a recognized utility (Tailwind's radius scale is `rounded-{none|sm|md|lg|xl|2xl|3xl|full}`). Tailwind's build silently drops unrecognized class names, so this element currently renders with **zero border-radius** — sharp square corners — regardless of what was intended.

## Evidence
- **File:** `frontend/app/page.tsx`
- **Current code** (inside the `<aside>` "Alert" section, near the "AI DRIFT ALERT" heading):
  ```tsx
  <div
    className="flex h-10 w-10 items-center justify-center rounded-bg"
    style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)' }}
  >
  ```
- **Established local pattern:** `frontend/components/sidebar.tsx` renders a square icon-badge container of the same role (fixed h/w, centered icon, colored background) using `rounded-md`:
  ```tsx
  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary text-sm font-medium text-white">
  ```
  `Sidebar` is rendered on every route (including this one, via `app/layout.tsx`), so this is a directly co-rendered, provable exemplar — not a distant or unrelated component.

## Correction
In `frontend/app/page.tsx`, change:
```diff
- className="flex h-10 w-10 items-center justify-center rounded-bg"
+ className="flex h-10 w-10 items-center justify-center rounded-md"
```
This is the only change required. Do not alter the inline `style` background/border values — those are unaffected by this finding.

## Verification
1. Run the frontend locally (`npm run dev`) and navigate to `/`.
2. Confirm the small red-tinted icon square to the left of "AI DRIFT ALERT" now has visibly rounded corners, matching the rounded square badge in the sidebar (top-left, next to the app name/logo).
3. No other visual change should occur on the page.
