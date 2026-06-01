# GPA & Athletic Eligibility Calculator

A single-file web app that converts high-school grades between a **7-point** and **10-point**
grading scale and computes:

- **Overall GPA** — 7-pt vs 10-pt, unweighted and weighted (Honors/AP bonus)
- **NCAA core-course GPA** — core academics only, unweighted, with live **Division I (≥2.3)** and **Division II (≥2.2)** PASS/FAIL checks
- **NAIA GPA** — overall GPA vs the **2.3** benchmark (one leg of NAIA's "2 of 3" rule)
- **Senior-year projection** — flag planned courses and toggle between *Completed only* and *Projected at graduation*

Everything runs **client-side** — no server, no data leaves the browser. Suitable for student
records (FERPA-friendly).

## Files

| File | Purpose |
|------|---------|
| `index.html` | The entire app (HTML + CSS + JS, no dependencies). Open it directly or host it. |
| `gpa_template.csv` | Starter import file showing the expected columns. |

## Input format (CSV)

Use a UTF-8 CSV with this header row:

```
Term,Course,Category,Percent,CreditHours,Track,Planned
```

| Column | Notes |
|--------|-------|
| **Term** | Free text, e.g. `Freshman S1`. One row per **semester** grade. |
| **Course** | Free text. |
| **Category** | `English`, `Math`, `Science`, `Social Science`, `Foreign Language`, `Other Academic`, or `Elective / Non-Core`. Only the academic categories count toward the NCAA core GPA. |
| **Percent** | Numeric grade percentage (e.g. `88`). |
| **CreditHours** | Used for the overall GPA. Enter `0` for a failed/no-credit course if your school awards no credit. |
| **Track** | `Regular`, `Honors`, or `AP` (drives the weighted-GPA bonus only). |
| **Planned** | `Yes` for future/senior-year courses, `No` (or blank) for completed. |

The importer is case-insensitive and tolerant of abbreviations. You can also enter courses
manually and **Download CSV template** / **Export courses** from inside the app.

## Adjustable settings (in the app)

- 7-point and 10-point cutoffs (min % for A/B/C/D) — set these to match your school exactly
- Honors / AP weighting bonus
- NCAA unit per semester course (default 0.5) and the DI / DII / NAIA thresholds

## Run locally

Just open `index.html` in any modern browser. (For development with live reload you can serve
the folder with `py -m http.server` and visit `http://localhost:8000/`.)

## Deploy

### GitHub Pages
1. Create a repo and add these files at the root (or in a `/docs` folder).
2. **Settings → Pages → Build and deployment → Source: Deploy from a branch**, pick `main` and `/ (root)` (or `/docs`).
3. Your app is live at `https://<user>.github.io/<repo>/`. `index.html` is served automatically.

### Cloudflare Pages / Netlify
Drag-and-drop the folder into the dashboard, or connect the repo. No build command needed —
it's a static site. Output/publish directory = the folder containing `index.html`.

### SharePoint / Microsoft 365 (internal)
- Upload `index.html` to a document library and use **... → Open** or host via an internal site.
- Note: some tenants render uploaded HTML as download-only for security. For an embeddable
  experience, host on Pages/Netlify and surface it in SharePoint via an **Embed** web part /
  iframe, or publish through a controlled internal static-hosting path.

## Methodology & disclaimer

- **NCAA core GPA**: core-academic courses only; no Honors/AP weighting; no +/-; each core
  semester = 0.5 unit; failing grades earn 0 units (consistent with the "best 16 core courses"
  rule). 16 core units are required by graduation (10, including 7 in English/Math/Science,
  before the 7th semester).
- **NAIA**: uses the overall (cumulative) GPA on a 4.0 scale; GPA ≥ 2.3 is one of three
  requirements, of which a student must meet at least two (GPA, test score, or top-50% rank).

This tool is for **planning only** and does not determine eligibility. Always confirm your
school's exact grading scale/weighting and its official **NCAA-approved core-course list** at
the NCAA Eligibility Center.
