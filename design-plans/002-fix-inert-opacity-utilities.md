# Plan 002 — Replace inert opacity utilities on the Dashboard route

## Problem
Several elements on the Dashboard route use Tailwind's `text-opacity-N` / `bg-opacity-N` utilities **without a paired `text-{color}` / `bg-{color}` utility**. These legacy opacity utilities only take effect by modifying a CSS variable (`--tw-text-opacity` / `--tw-bg-opacity`) that a color utility must reference via `rgb(r g b / var(--tw-text-opacity))`. Used alone, with no color utility present to consume that variable, they have **no visual effect at all** — the element renders at its inherited color and full opacity, not the intended muted/translucent treatment.

The rest of the same surface (this page and all other routes) establishes a working alternative: Tailwind's `{color}/{opacity}` slash syntax (e.g. `text-slate-400/60`), which applies color and opacity together in one utility and does not have this failure mode.

## Evidence
- **File:** `frontend/app/page.tsx`
- **Broken instances (5):**
  1. Timeline row timestamp: `className="w-10 font-mono text-opacity-60 text-sm"`
  2. Timeline row description: `className="text-opacity-70 text-sm"`
  3. Footer paragraph: `className="text-opacity-60 leading-relaxed"`
  4. Footer emphasized brand name: `className="font-semibold text-opacity-80"`
  5. "3 Sources" count badge background: `className="rounded-full bg-opacity-20 px-3 py-1 text-xs text-slate-400/60"`
  6. Data Confidence box background: `className="rounded-2xl bg-opacity-70 p-6 md:p-8 text-center"` (background is actually set via inline `style`, so this instance is dead code rather than a visible defect — include for consistency, but lowest priority of the six)

- **Established working pattern, same page** (e.g. directly above the Timeline section):
  ```tsx
  <p className="mt-1 text-sm text-slate-400/50">
    Real-time monitoring events from the scraper integrity layer.
  </p>
  ```
  and used consistently across `system-status/page.tsx`, `ingestion/page.tsx`, `explorer/page.tsx` (e.g. `text-slate-400/60`, `text-slate-400/70`).

## Correction
Replace each bare opacity utility with the surface's established `{color}/{N}` slash syntax, using `slate-400` as the color (matching every other muted-text instance on this surface) and preserving the same `N` already specified in each instance:

```diff
- <span className="w-10 font-mono text-opacity-60 text-sm">
+ <span className="w-10 font-mono text-slate-400/60 text-sm">

- <span className="text-opacity-70 text-sm">{event.text}</span>
+ <span className="text-slate-400/70 text-sm">{event.text}</span>

- <p className="text-opacity-60 leading-relaxed">
+ <p className="text-slate-400/60 leading-relaxed">

- <span className="font-semibold text-opacity-80">
+ <span className="font-semibold text-slate-400/80">

- <span className="rounded-full bg-opacity-20 px-3 py-1 text-xs text-slate-400/60">
+ <span className="rounded-full bg-slate-400/20 px-3 py-1 text-xs text-slate-400/60">

- <div className="rounded-2xl bg-opacity-70 p-6 md:p-8 text-center" style={{ background: 'rgba(15, 107, 94, 0.15)' }}>
+ <div className="rounded-2xl p-6 md:p-8 text-center" style={{ background: 'rgba(15, 107, 94, 0.15)' }}>
```
(Last instance: the inline `style` already sets the real background, so the correction there is simply removing the dead `bg-opacity-70` class rather than replacing it with a color pairing — adding a `bg-{color}` class would fight the inline style.)

## Verification
1. Run the frontend locally (`npm run dev`) and navigate to `/`.
2. Confirm the Timeline row timestamps and descriptions render visibly muted/gray (not full white/foreground).
3. Confirm the footer paragraph text is muted gray, with "BioIntel Guardian" slightly more prominent than the surrounding sentence.
4. Confirm the "3 Sources" badge now has a faint visible background pill instead of no background.
5. No functional/behavioral change — this is a pure visual correction.
