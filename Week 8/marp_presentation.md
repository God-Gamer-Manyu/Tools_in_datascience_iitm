---
marp: true
title: Tools in Data Science — Marp Presentation
author: Rtamanhu N J
theme: default
paginate: true
class: lead
---

<style>
/* Custom theme/style for this presentation */
:root {
  --bg: #0b1220;
  --fg: #e6eef8;
  --accent: #38bdf8;
  --muted: rgba(230,238,248,0.6);
}
section {
  background-color: var(--bg);
  color: var(--fg);
  font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
}
h1, h2, h3 { font-weight: 700; }
h1 { color: var(--accent); font-size: 2.4rem; }
.lead p { font-size: 1.05rem; }
.footer-email { position: absolute; right: 1rem; bottom: 1rem; font-size: 12px; color: var(--muted); }
.page-number { position: absolute; left: 1rem; bottom: 1rem; font-size: 12px; color: var(--muted); }
.math { font-family: Georgia, 'Times New Roman', serif; }
/* Small media tweak for better printing */
@media print { section { font-size: 12pt } }
</style>

---

# Tools in Data Science

_A concise Marp demo with custom theme, math, and background image._

---

## Agenda

- Motivation
- Example algorithmic complexities
- Background-image slide
- Contact

---



![bg](Background.jpg)

## Example: Algorithm Complexity

This slide uses a large, full-bleed background image.

- Sorting typical complexity: $O(n\log n)$
- Linear pass: $O(n)$

Block equation:

$$
T(n) = a\,T\left(\frac{n}{b}\right) + f(n)
$$

Use the Master Theorem to reason about recurrences. For example, if $f(n)=\Theta(n^{\log_b a})$, then

$$
T(n)=\Theta\left(n^{\log_b a}\log n\right).
$$

---

## Sample Pseudocode and Complexity

```
function sortAndCount(A):
  if |A| <= 1: return A
  mid = |A|/2
  L = sortAndCount(A[0:mid])
  R = sortAndCount(A[mid:])
  return merge(L,R)
```

The runtime satisfies the recurrence $T(n)=2T(n/2)+\Theta(n)$, so $T(n)=\Theta(n\log n)$.

---

## Styling Notes (Marp directives)

- Front-matter: `marp: true`, `paginate: true`
- Custom CSS added via `<style>` block
- Background image applied with slide-level HTML comments
- Math uses KaTeX delimiters `$...$` and `$$...$$`

---

## Contact

If you have questions, reach me at:

**Email:** `24f3001383@ds.study.iitm.ac.in`

<div class="footer-email">24f3001383@ds.study.iitm.ac.in</div>

---

## Appendix — More Math

A common summation:

$$
\sum_{i=1}^n i = \frac{n(n+1)}{2} = \Theta(n^2)
$$

And asymptotic hierarchy example:

$$
1 \prec \log n \prec n^{\alpha} \prec n \log n \prec n^2 \prec 2^n
$$

---

<footer class="page-number">Page</footer>
