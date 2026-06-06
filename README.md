# GPA & Athletic Eligibility Calculator

A single-file web app that converts high-school grades between a **7-point** and **10-point**
grading scale and computes:

- **Overall GPA** — 7-pt vs 10-pt, unweighted and weighted (Honors/AP bonus)
- **NCAA core-course GPA** — core academics only, unweighted, with live **Division I (≥2.3)** and **Division II (≥2.2)** PASS/FAIL checks
- **NAIA eligibility** — evaluates the **"2 of 3"** rule using overall GPA, **ACT/SAT test scores**, and (informationally) class rank
- **ACT / SAT input** — feeds NAIA's test leg (ACT ≥ 18 / SAT ≥ 970). *The NCAA dropped test scores from DI/DII initial eligibility in 2023, so they don't affect the NCAA result — the app notes this.*
- **College search & match** — live search of U.S. colleges (federal **College Scorecard**) by name / state / major, with **NCAA/NAIA division** labels and **division + men's/women's sport filters** (federal **EADA** data), showing **cost, admission rate, SAT/ACT ranges**, plus an **academic match** (Likely / Target / Reach) based on the ACT/SAT entered
- **Senior-year projection** — flag planned courses and toggle between *Completed only* and *Projected at graduation*

Everything runs **client-side** — no server, no data leaves the browser. Suitable for student
records (FERPA-friendly).

**▶ Live app:** https://wacit.github.io/gpa-eligibility-calculator/

> In the app, click **❓ How to use** (top-right of the header) for the same guide below. It
> also opens automatically on your first visit.

## Screenshots

| Enter courses | Results & eligibility |
|:---:|:---:|
| ![Course entry with sample data](docs/screenshot-overview.png) | ![GPA results with NCAA DI/DII and NAIA checks](docs/screenshot-results.png) |

**College search & match** — live cost, admission rate, SAT/ACT ranges, and a Likely/Target/Reach estimate:

![College search and academic match](docs/screenshot-colleges.png)

Built-in **How to use** guide (opens automatically on first visit):

![How-to-use help guide](docs/screenshot-help.png)

*(Screenshots use fictional sample data.)*

## How to use

### 1. Enter the student's courses
List **one row per semester grade** (the grades that earn credit). Three ways to add them:

- **Type them in** — click **+ Add course** and fill each row.
- **Import a spreadsheet** — click **Download CSV template**, fill it in Excel/Google Sheets, then **Import CSV…**.
- **Try it first** — click **Load sample data** to see a worked example, then **Clear all** when ready.

> **Where do I get my grades?** Click **📥 Where's my data?** in the app for step-by-step guidance — see [Getting your grades out of your school's system](#getting-your-grades-out-of-your-schools-system) below.

What each column means:

| Column | What to enter |
|--------|---------------|
| **Term** | A label, e.g. `Freshman S1`. |
| **Course** | The class name. |
| **Category** | The subject. Only academic categories (English, Math, Science, Social Science, Foreign Language, Other Academic) count toward the **NCAA** core GPA. Use `Elective / Non-Core` for Band, PE, Health, study hall, etc. |
| **%** | The percentage grade (e.g. `88`). The letter grade is computed automatically. |
| **Credit hrs** | Used for the overall GPA. Enter `0` for a failed/no-credit class if your school awards no credit. |
| **Track** | `Regular`, `Honors`, or `AP` — affects the *weighted* overall GPA only (NCAA/NAIA ignore weighting). |
| **Plan?** | Check for **future/senior-year** courses you're projecting (see step 4). |

### 2. Match your school's grading scale
Open **Grading scale settings** and set the cutoffs to match your school exactly. Defaults are the
common 7-point (A ≥ 93) and 10-point (A ≥ 90) scales. You can also set the Honors/AP bonus and the
DI / DII / NAIA pass thresholds here.

### 3. Add test scores (optional)
In the **Test scores** card, enter the **ACT composite** and/or **SAT total**. These feed the **NAIA** check.
**Note:** the NCAA no longer uses ACT/SAT for DI/DII initial eligibility (permanent since 2023), so scores don't change the NCAA result — the app states this inline.

### 4. Read the results
- **Overall GPA** — your full GPA on both scales, unweighted and weighted (green = the 10-point result).
- **NCAA Core GPA** — core-academic courses only, no weighting; badges show pass/fail vs **DI ≥ 2.3** and **DII ≥ 2.2**, and it tracks progress toward the 16 required core units.
- **NAIA Eligibility** — the **"2 of 3"** rule: overall GPA ≥ 2.3, test leg (**ACT ≥ 18 / SAT ≥ 970**), or top-50% class rank. Two legs met → **QUALIFIES**; one leg met → still needs the top-50% rank leg.

### 5. Project the senior year (optional)
Add upcoming courses with the **Plan?** box checked (or use **+ Add planned (senior) course**). Then
use the **View** toggle above the results to switch between **Completed only** and
**Projected (incl. planned)** to see where the GPA is headed at graduation.

### 6. Explore colleges (optional)
In **College search & match**, search by school name, state, and/or major, then narrow by **NCAA/NAIA division** and a **men's or women's sport**. Each result is labeled with its **division** and shows **cost** (net price & tuition), **admission rate**, and **SAT/ACT middle-50%** ranges, with a link to the school. If you entered ACT/SAT, you also get an **academic match** badge — **Likely / Target / Reach** — comparing your scores to the school's ranges and selectivity.
- *Estimate only*, not a guarantee; recruited athletes may receive extra admissions support.
- Data: U.S. Dept. of Education **College Scorecard** (cost/admissions/majors) + **EADA 2024-25** (`athletics.json` — division & sponsored sports for ~1,300 NCAA DI/DII/DIII + NAIA schools, joined by IPEDS id).
- Only your search terms are sent — your grades/scores stay in the browser.
- Uses a free `api.data.gov` key (`SCORECARD_KEY` in `index.html`); get your own at <https://api.data.gov/signup/> if forking.
- The men's/women's sport filter currently lists the 6 most-sponsored sports per gender (editable via `SPORT_FILTER` in `index.html`).
- *Browsing tip:* pick a **state** when filtering by division/sport (the API returns a state's 4-year schools, which are then filtered locally).
- **Results count:** a **Show 25 / 50 / 100** selector controls how many results display; the search pages through the API as needed to fill it. Filters are an **AND** (a school must match every active filter) — to find one specific school, type its **name** and leave the other filters on "Any."

### 7. Save or share
- **Export results (CSV)** — the GPA/eligibility summary (includes ACT/SAT and NAIA status).
- **Export courses (CSV)** — your course list, to reopen later.
- **Print / Save as PDF** — a clean printout for a counselor or coach.

> **Privacy:** your data is remembered only in *this browser on this device*. **Planning only:**
> confirm your school's exact scale/weighting and its official NCAA-approved core-course list at the
> NCAA Eligibility Center — official eligibility is determined by the NCAA/NAIA.

## Getting your grades out of your school's system

Most parent/student portals don't have a one-click export, so the fastest reliable source is usually
your **transcript**. (The app has this same guide built in — click **📥 Where's my data?**.)

- **⭐ Best source — your transcript.** Ask your **counselor or registrar** for an **unofficial transcript**
  (almost always a free PDF, often same-day). It lists every course, final grade, and credit for all
  years — exactly what this tool needs. Many schools also post it in **Naviance** or **SCOIR**.
- **PowerSchool** (parent/student portal or app) — open **Grades and Attendance** for the current term
  and **Grade History** for past semesters; click a grade for the percentage. No CSV export in most
  parent portals, so read the grades into the template or **Ctrl/Cmd + P → Save as PDF**.
- **Infinite Campus** (Campus Parent/Student) — **Grades** (switch terms); report cards/transcripts under
  **Documents** or **Reports**.
- **Skyward** (Family/Student Access) — **Gradebook** for current grades; **Portfolio** for report cards
  and the transcript.
- **Canvas / Schoology / Google Classroom** — show **current course grades only**, not full history; use
  your transcript for past years.

Then fill the **CSV template** (one row per semester course) and **Import CSV…**, or type rows in.
**Only have letter grades?** This tool uses **percentages** — enter a value inside that letter's band
(e.g. A→95, B→85, C→75), or set your school's exact cutoffs in **Grading scale settings**.

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
