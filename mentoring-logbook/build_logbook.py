#!/usr/bin/env python3
"""Generate a print-ready Phase I MBBS mentor–mentee logbook (HTML)."""

from pathlib import Path

OUT = Path(__file__).parent / "mentoring-logbook.html"

CSS = r"""
@page { size: A4; margin: 14mm 14mm 16mm 14mm; }
* { box-sizing: border-box; }
html, body {
  font-family: "Source Sans 3", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  font-size: 11pt;
  color: #1a2332;
  line-height: 1.35;
  margin: 0;
}
h1,h2,h3 { margin: 0 0 .4em; font-weight: 700; color: #0b3d5c; }
.page { page-break-after: always; position: relative; min-height: 250mm; }
.page:last-child { page-break-after: auto; }
.footer {
  position: running(footer);
  font-size: 8.5pt; color: #5a6a7a;
}
.small { font-size: 9pt; color: #4a5a6a; }
.tiny { font-size: 8.5pt; color: #5a6a7a; }
.rule { border: none; border-top: 2px solid #0b3d5c; margin: 8px 0 12px; }
.rule-thin { border: none; border-top: 1px solid #c5d0da; margin: 8px 0; }
.line { border-bottom: 1px dotted #7a8a9a; min-height: 1.55em; margin: 2px 0 6px; }
.line.tall { min-height: 2.4em; }
.row { display: flex; gap: 12px; }
.col { flex: 1; }
.col-2 { flex: 2; }
label { font-size: 9pt; color: #3a4a5a; font-weight: 600; }
.box {
  border: 1px solid #c5d0da;
  border-radius: 4px;
  padding: 8px 10px;
  margin: 6px 0;
}
.tick {
  display: inline-block;
  width: 11px; height: 11px;
  border: 1.2px solid #0b3d5c;
  margin-right: 4px;
  vertical-align: -1px;
  border-radius: 2px;
}
.item { display: inline-block; width: 48%; margin: 3px 0; font-size: 10pt; }
.item-3 { display: inline-block; width: 32%; margin: 3px 0; font-size: 10pt; }
.banner {
  background: #0b3d5c;
  color: #fff;
  padding: 8px 12px;
  font-weight: 700;
  letter-spacing: .04em;
  font-size: 12pt;
  margin: 0 0 10px;
}
.banner.a { background: #0b3d5c; }
.banner.b { background: #1e6b4f; }
.banner.c { background: #8a4b12; }
.subbanner {
  background: #e8eef3;
  color: #0b3d5c;
  padding: 5px 10px;
  font-weight: 700;
  font-size: 10.5pt;
  margin-bottom: 8px;
}
.logo-box {
  width: 32mm; height: 32mm;
  border: 2px dashed #8aa0b4;
  display: flex; align-items: center; justify-content: center;
  text-align: center;
  color: #6a7a8a;
  font-size: 8pt;
  margin: 0 auto 14px;
  background: #f7fafc;
}
.cover-logo {
  width: 38mm; height: 38mm;
  object-fit: contain;
  display: block;
  margin: 0 auto 10px;
  background: #0b3d5c;
  border-radius: 6px;
}
.inst-name {
  font-size: 13.5pt;
  font-weight: 700;
  color: #0b3d5c;
  line-height: 1.3;
  margin: 0 16mm 4px;
}
.inst-meta { font-size: 9.5pt; color: #3a4a5a; margin: 2px 20mm; }
.filled {
  font-size: 11.5pt;
  font-weight: 700;
  color: #0b3d5c;
  border-bottom: 1px solid #c5d0da;
  min-height: 1.55em;
  padding: 2px 0 4px;
  margin: 0 0 8px;
  text-align: left;
}
.cover {
  text-align: center;
  padding-top: 18mm;
}
.cover h1 { font-size: 22pt; letter-spacing: .08em; margin: 8px 0; }
.cover .inst { font-size: 16pt; min-height: 1.6em; border-bottom: 1px solid #0b3d5c; margin: 6px 40px; }
.sig-row { display: flex; justify-content: space-between; margin-top: 18px; gap: 24px; }
.sig { flex: 1; text-align: center; }
.sig .line { margin-top: 28px; }
.table { width: 100%; border-collapse: collapse; font-size: 9.5pt; }
.table th, .table td {
  border: 1px solid #b8c4d0;
  padding: 5px 6px;
  vertical-align: top;
}
.table th { background: #0b3d5c; color: #fff; font-weight: 600; text-align: left; }
.table td { height: 22px; }
.note {
  background: #fff8e8;
  border-left: 4px solid #c48a1a;
  padding: 8px 10px;
  font-size: 9.5pt;
  margin: 8px 0;
}
.red {
  background: #fdeeee;
  border-left: 4px solid #a33;
  padding: 8px 10px;
  font-size: 9.5pt;
  margin: 8px 0;
}
.ok {
  background: #eef7f1;
  border-left: 4px solid #1e6b4f;
  padding: 8px 10px;
  font-size: 9.5pt;
  margin: 8px 0;
}
.month-chip {
  display: inline-block;
  border: 1px solid #0b3d5c;
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 9pt;
  margin-right: 6px;
}
"""

MENTEE_META = [
    ("A", "a", "#0b3d5c", "Mentee A"),
    ("B", "b", "#1e6b4f", "Mentee B"),
    ("C", "c", "#8a4b12", "Mentee C"),
]

MONTHS = [
    "Meeting 1 · Foundation / Month 1",
    "Meeting 2 · Month 2",
    "Meeting 3 · Month 3 (end of 1st quarter)",
    "Meeting 4 · Month 4",
    "Meeting 5 · Month 5",
    "Meeting 6 · Month 6 (mid-year / 2nd quarter)",
    "Meeting 7 · Month 7",
    "Meeting 8 · Month 8",
    "Meeting 9 · Month 9 (3rd quarter / pre-university)",
    "Meeting 10 · Month 10",
    "Meeting 11 · Month 11",
    "Meeting 12 · Month 12 (year-end / university exam)",
]


def lines(n=1, cls="line"):
    return "".join(f'<div class="{cls}"></div>' for _ in range(n))


def cover():
    return f"""
<section class="page cover">
  <img class="cover-logo" src="assets/gvp-logo.jpg" alt="GVPIHCMT emblem">
  <p class="inst-name">GAYATRI VIDYA PARISHAD<br>INSTITUTE OF HEALTH CARE AND<br>MEDICAL TECHNOLOGY</p>
  <p class="inst-meta">Visakhapatnam &nbsp;·&nbsp; Andhra Pradesh</p>
  <p class="inst-meta">#6-25, Maridi Valley, Marikavalasa, Madhurawada, Visakhapatnam – 530048</p>
  <p class="inst-meta">Affiliated to Dr. NTR University of Health Sciences &nbsp;·&nbsp; Recognised by NMC</p>
  <hr class="rule">
  <p class="small" style="letter-spacing:.18em; font-weight:700; color:#0b3d5c;">CBME 2024 · NMC MENTOR–MENTEE PROGRAMME</p>
  <h1>MENTOR–MENTEE<br>LOGBOOK</h1>
  <p style="font-size:13pt; margin:4px 0 18px;">Phase I MBBS &nbsp;·&nbsp; One mentor : three mentees</p>
  <div class="box" style="text-align:left; margin: 0 18mm;">
    <div class="row"><div class="col"><label>Academic year</label>{lines()}</div>
        <div class="col"><label>Batch / admission year</label>{lines()}</div></div>
    <div class="row"><div class="col"><label>Faculty mentor (full name)</label><div class="filled">Dr. Sushma Korukonda, MD, ACME</div></div></div>
    <div class="row"><div class="col"><label>Designation</label><div class="filled">Professor</div></div>
        <div class="col"><label>Department</label><div class="filled">Anatomy</div></div></div>
    <div class="row"><div class="col"><label>Employee / faculty ID</label>{lines()}</div>
        <div class="col"><label>Mobile</label>{lines()}</div></div>
    <label>College email</label>{lines()}
    <label>MEU / Mentoring cell in-charge (name)</label>{lines()}
  </div>
  <p class="tiny" style="margin-top:18px;">GVPIHCMT, Visakhapatnam &nbsp;·&nbsp; Confidential faculty record &nbsp;·&nbsp; Not for student circulation &nbsp;·&nbsp; Retain till CRMI as per CBME 2024<br>
  Allotment during Foundation Course &nbsp;·&nbsp; Mentee remains with the same mentor till CRMI</p>
</section>
"""


def how_to_use():
    return f"""
<section class="page">
  <div class="banner">HOW TO USE THIS LOGBOOK</div>
  <p>This book is for <strong>one faculty mentor</strong> and <strong>three Phase I mentees</strong> (NMC CBME 2024 ratio 1:3). Meet about <strong>once a month</strong>. There are <strong>12 meeting sheets per mentee</strong> for this academic year. Add extra sheets later if needed.</p>
  <h3>Before the first meeting</h3>
  <ol>
    <li>Confirm the cover (already printed with your name) and add academic year / batch.</li>
    <li>Complete one <strong>Student profile</strong> with each mentee in the Foundation Course week.</li>
    <li>Fill SWOC together. Keep health and family issues brief; use the confidential note if needed.</li>
  </ol>
  <h3>Each monthly meeting (aim: 15–20 minutes)</h3>
  <ol>
    <li>Open that mentee’s next numbered sheet. Write date, time and place first.</li>
    <li>Tick topics. Write only three short notes: issue → student action → your follow-up.</li>
    <li>Both sign. Write the next date before they leave.</li>
    <li>Tick the yearly tracker (front) so you can see missed months at a glance.</li>
  </ol>
  <h3>What to cover over the year (not all in one meeting)</h3>
  <p class="small">Adjustment &amp; hostel · attendance (75% eligibility) · Anatomy / Physiology / Biochemistry · internal assessment · FAP · AETCOM · exam stress · sleep/health · ragging/safety · career curiosity · parent contact as required by college.</p>
  <div class="red">
    <strong>Escalate the same day</strong> (do not only write it here): thoughts of self-harm, ragging, sexual harassment, acute medical illness, or a student who stops attending. Inform the Mentoring cell / MEU / Dean as per college SOP. Record “referred on (date)” — not the clinical detail.
  </div>
  <div class="note">
    <strong>Privacy.</strong> This is a faculty log. Do not leave it in a shared staff room unlocked. Do not photograph pages onto a class WhatsApp group. Parent meeting records may be required by UGMEB/NMC — keep those factual and short.
  </div>
  <h3>Suggested month map (adapt to your college calendar)</h3>
  <table class="table">
    <tr><th>Sheet</th><th>When</th><th>Focus (optional prompt)</th></tr>
    <tr><td>1</td><td>Foundation / Month 1</td><td>Settling in, hostel, language, first-week fears</td></tr>
    <tr><td>2</td><td>Month 2</td><td>Study method, attendance habit</td></tr>
    <tr><td>3</td><td>Month 3</td><td>1st IA / dissection hall, SWOC review</td></tr>
    <tr><td>4–5</td><td>Months 4–5</td><td>Subject-wise difficulty (AN / PY / BC)</td></tr>
    <tr><td>6</td><td>Month 6</td><td>Mid-year: morale, FAP, AETCOM</td></tr>
    <tr><td>7–8</td><td>Months 7–8</td><td>Pre-professional, weak areas</td></tr>
    <tr><td>9</td><td>Month 9</td><td>3rd quarter IA, eligibility (attendance)</td></tr>
    <tr><td>10–11</td><td>Months 10–11</td><td>University exam plan, sleep, family support</td></tr>
    <tr><td>12</td><td>Month 12</td><td>Year-end, next phase, keep the same mentor</td></tr>
  </table>
</section>
"""


def mentor_and_tracker():
    rows = ""
    for letter, _cls, _c, name in MENTEE_META:
        rows += f"""<tr>
          <td><strong>{name}</strong><br><span class="tiny">Roll / name:</span></td>
          {"".join("<td></td>" for _ in range(12))}
          <td></td>
        </tr>"""
    return f"""
<section class="page">
  <div class="banner">MENTOR RECORD</div>
  <div class="box">
    <div class="row">
      <div class="col"><label>Name</label><div class="filled">Dr. Sushma Korukonda, MD, ACME</div></div>
      <div class="col"><label>Department &amp; designation</label><div class="filled">Professor, Department of Anatomy</div></div>
    </div>
    <div class="row">
      <div class="col"><label>Allotted on (Foundation Course date)</label>{lines()}</div>
      <div class="col"><label>Mentoring cell / MEU reference no. (if any)</label>{lines()}</div>
    </div>
    <label>Preferred meeting slot (day / time / place)</label>{lines()}
    <p class="tiny">NMC CBME 2024: Mentor from Professor/HOD to Assistant Professor. Mentees allotted in Foundation Course (Phase I). Same mentor continues till CRMI. Each new year, three new Phase I mentees may be added; seniors support juniors (sibling environment, not ragging).</p>
  </div>
  <div class="subbanner">Year at a glance — tick when that monthly meeting is done</div>
  <table class="table">
    <tr>
      <th style="width:18%">Mentee</th>
      {"".join(f"<th style='width:6%;text-align:center'>{i}</th>" for i in range(1,13))}
      <th>Notes</th>
    </tr>
    {rows}
  </table>
  <p class="tiny">Put a ✓ in the month column. Circle the number if the meeting was missed and rescheduled. This one table is enough to see who you have not seen.</p>
  <div class="subbanner">Parent / guardian meeting (college may need this for UGMEB)</div>
  <table class="table">
    <tr><th>Date</th><th>Mentee</th><th>Who attended</th><th>Mode</th><th>Outcome (one line)</th><th>Sign</th></tr>
    {"".join("<tr>" + "<td><br></td>"*6 + "</tr>" for _ in range(6))}
  </table>
</section>
"""


def profile_page(letter, cls, title):
    return f"""
<section class="page">
  <div class="banner {cls}">STUDENT PROFILE · {title}</div>
  <div class="row">
    <div class="col-2">
      <label>Full name (as in college records)</label>{lines()}
      <div class="row">
        <div class="col"><label>University / college roll no.</label>{lines()}</div>
        <div class="col"><label>Register / admission no.</label>{lines()}</div>
      </div>
      <div class="row">
        <div class="col"><label>Date of birth</label>{lines()}</div>
        <div class="col"><label>Gender</label>{lines()}</div>
      </div>
      <div class="row">
        <div class="col"><label>Blood group</label>{lines()}</div>
        <div class="col"><label>Hostel / day scholar</label>{lines()}</div>
      </div>
    </div>
    <div class="col" style="max-width:38mm;">
      <div class="logo-box" style="width:36mm;height:42mm;margin:0;">Passport<br>photo<br>(optional)</div>
    </div>
  </div>
  <div class="row">
    <div class="col"><label>Mobile (student)</label>{lines()}</div>
    <div class="col"><label>Email</label>{lines()}</div>
  </div>
  <label>Permanent address</label>{lines(2, "line tall")}
  <label>Local / hostel address</label>{lines()}
  <div class="row">
    <div class="col"><label>Parent / guardian name</label>{lines()}</div>
    <div class="col"><label>Relationship</label>{lines()}</div>
  </div>
  <div class="row">
    <div class="col"><label>Parent mobile</label>{lines()}</div>
    <div class="col"><label>Parent email</label>{lines()}</div>
  </div>
  <div class="row">
    <div class="col"><label>Father’s occupation</label>{lines()}</div>
    <div class="col"><label>Mother’s occupation</label>{lines()}</div>
  </div>
  <div class="row">
    <div class="col"><label>Mother tongue</label>{lines()}</div>
    <div class="col"><label>Other languages</label>{lines()}</div>
  </div>
  <div class="row">
    <div class="col"><label>+2 / NEET board &amp; % (approx.)</label>{lines()}</div>
    <div class="col"><label>Medium of school</label>{lines()}</div>
  </div>
  <label>Hobbies / sports / cultural / other talent</label>{lines()}
  <label>Career interest (if any yet)</label>{lines()}
  <label>Health issues the student wants the mentor to know (optional; keep brief)</label>{lines()}
  <label>Any other support needed (language, finance flag without amounts, commuting)</label>{lines()}
  <div class="sig-row">
    <div class="sig"><div class="line"></div><span class="tiny">Student signature / date</span></div>
    <div class="sig"><div class="line"></div><span class="tiny">Mentor signature / date</span></div>
  </div>
</section>
"""


def swoc_academic(letter, cls, title):
    return f"""
<section class="page">
  <div class="banner {cls}">SWOC · {title}</div>
  <p class="tiny">Fill once in Month 1. Revisit at Meeting 6 and Meeting 12. Student writes; mentor may add a line.</p>
  <div class="row">
    <div class="col box"><strong>Strengths</strong><p class="tiny">What they already do well</p>{lines(4)}</div>
    <div class="col box"><strong>Weaknesses</strong><p class="tiny">What to improve this year</p>{lines(4)}</div>
  </div>
  <div class="row">
    <div class="col box"><strong>Opportunities</strong><p class="tiny">College / FAP / skills they can use</p>{lines(4)}</div>
    <div class="col box"><strong>Challenges</strong><p class="tiny">What might get in the way</p>{lines(4)}</div>
  </div>
  <div class="subbanner">Phase I academic snapshot (fill at meetings 3, 6, 9, 12)</div>
  <table class="table">
    <tr>
      <th></th><th>Q1 (M3)</th><th>Q2 (M6)</th><th>Q3 (M9)</th><th>Q4 (M12)</th>
    </tr>
    <tr><td>Attendance AN % (Th / Pr)</td><td></td><td></td><td></td><td></td></tr>
    <tr><td>Attendance PY % (Th / Pr)</td><td></td><td></td><td></td><td></td></tr>
    <tr><td>Attendance BC % (Th / Pr)</td><td></td><td></td><td></td><td></td></tr>
    <tr><td>IA Anatomy</td><td></td><td></td><td></td><td></td></tr>
    <tr><td>IA Physiology</td><td></td><td></td><td></td><td></td></tr>
    <tr><td>IA Biochemistry</td><td></td><td></td><td></td><td></td></tr>
    <tr><td>Overall: L / Avg / Good / Outstanding</td><td></td><td></td><td></td><td></td></tr>
  </table>
  <label>Mentor remark on academics (one line each quarter)</label>
  <p class="tiny">Q1</p>{lines()}
  <p class="tiny">Q2</p>{lines()}
  <p class="tiny">Q3</p>{lines()}
  <p class="tiny">Q4 / university result</p>{lines()}
</section>
"""


def meeting_sheet(letter, cls, title, number, prompt):
    return f"""
<section class="page">
  <div class="banner {cls}">{title} · MEETING {number} OF 12</div>
  <p class="tiny">{prompt}</p>
  <div class="row">
    <div class="col"><label>Date</label>{lines()}</div>
    <div class="col"><label>Time</label>{lines()}</div>
    <div class="col"><label>Place</label>{lines()}</div>
  </div>
  <p><span class="item-3"><span class="tick"></span>In person</span>
     <span class="item-3"><span class="tick"></span>Phone</span>
     <span class="item-3"><span class="tick"></span>Online</span>
     &nbsp; Duration:
     <span class="item-3"><span class="tick"></span>15 min</span>
     <span class="item-3"><span class="tick"></span>20–30 min</span>
  </p>
  <div class="subbanner">Topics (tick all that applied)</div>
  <p>
    <span class="item"><span class="tick"></span>Settling in / hostel</span>
    <span class="item"><span class="tick"></span>Attendance</span>
    <span class="item"><span class="tick"></span>Anatomy</span>
    <span class="item"><span class="tick"></span>Physiology</span>
    <span class="item"><span class="tick"></span>Biochemistry</span>
    <span class="item"><span class="tick"></span>IA / exams</span>
    <span class="item"><span class="tick"></span>Study method</span>
    <span class="item"><span class="tick"></span>FAP / AETCOM</span>
    <span class="item"><span class="tick"></span>Health / sleep / stress</span>
    <span class="item"><span class="tick"></span>Language / communication</span>
    <span class="item"><span class="tick"></span>Family / finance (no amounts)</span>
    <span class="item"><span class="tick"></span>Ragging / safety</span>
    <span class="item"><span class="tick"></span>Career / motivation</span>
    <span class="item"><span class="tick"></span>Other: ___________</span>
  </p>
  <div class="subbanner">This month — circle</div>
  <p class="small">Academics: &nbsp; Struggling &nbsp;/&nbsp; Managing &nbsp;/&nbsp; Comfortable<br>
  Morale: &nbsp; Low &nbsp;/&nbsp; Mixed &nbsp;/&nbsp; Steady &nbsp;/&nbsp; High<br>
  Attendance worry: &nbsp; No &nbsp;/&nbsp; Yes — subject(s): _______________</p>
  <label>1. What the mentee raised (three lines max)</label>{lines(3)}
  <label>2. Action the student will take before next meeting</label>{lines(2)}
  <label>3. What I (mentor) will do / already did</label>{lines(2)}
  <p class="small"><span class="tick"></span> Referred (counselling / MEU / HoD / medical) on date: ___________ &nbsp;&nbsp;
     <span class="tick"></span> Parent informed (date): ___________</p>
  <div class="row">
    <div class="col"><label>Next meeting date</label>{lines()}</div>
    <div class="col"><label>Next focus (one line)</label>{lines()}</div>
  </div>
  <div class="sig-row">
    <div class="sig"><div class="line"></div><span class="tiny">Mentee signature</span></div>
    <div class="sig"><div class="line"></div><span class="tiny">Mentor signature</span></div>
  </div>
</section>
"""


def year_end(letter, cls, title):
    return f"""
<section class="page">
  <div class="banner {cls}">YEAR-END NOTE · {title}</div>
  <p class="tiny">Complete after Meeting 12. One page. Carry this mentee forward next year (same mentor till CRMI).</p>
  <label>Meetings held this year ( / 12 )</label>{lines()}
  <label>What went well</label>{lines(3)}
  <label>What still needs support in Phase II</label>{lines(3)}
  <label>University exam: appeared / result (if known)</label>{lines()}
  <label>Any pending referral</label>{lines()}
  <div class="ok">Continue with the same mentor next academic year as per CBME 2024. Senior mentees should be asked to support the next Phase I batch (sibling environment).</div>
  <div class="sig-row">
    <div class="sig"><div class="line"></div><span class="tiny">Mentee</span></div>
    <div class="sig"><div class="line"></div><span class="tiny">Mentor</span></div>
  </div>
</section>
"""


def extras():
    return f"""
<section class="page">
  <div class="banner">BLANK / EXTRA MEETING (photocopy if mentoring continues)</div>
  <p class="tiny">Use if you need a 13th meeting this year or a short extra contact. Write mentee A / B / C at the top.</p>
  <div class="row">
    <div class="col"><label>Mentee (A / B / C) and name</label>{lines()}</div>
    <div class="col"><label>Date / time / place</label>{lines()}</div>
  </div>
  <label>Topics &amp; notes</label>{lines(8, "line tall")}
  <div class="sig-row">
    <div class="sig"><div class="line"></div><span class="tiny">Mentee</span></div>
    <div class="sig"><div class="line"></div><span class="tiny">Mentor</span></div>
  </div>
  <hr class="rule">
  <div class="subbanner">Confidential incident log (date + action only)</div>
  <table class="table">
    <tr><th>Date</th><th>Mentee</th><th>Referred to</th><th>Closed? (Y/N)</th></tr>
    {"".join("<tr>" + "<td><br><br></td>"*4 + "</tr>" for _ in range(6))}
  </table>
</section>
<section class="page">
  <div class="banner">CONTENTS</div>
  <ol>
    <li>Cover — institution, logo, mentor</li>
    <li>How to use</li>
    <li>Mentor record + yearly tracker + parent meetings</li>
    <li>Mentee A — profile, SWOC &amp; academics, meetings 1–12, year-end</li>
    <li>Mentee B — same</li>
    <li>Mentee C — same</li>
    <li>Extra meeting + confidential referral log</li>
  </ol>
  <p>Print <strong>single-sided</strong> if you write in pen; or duplex and use a ring file with three colour flags (A / B / C).</p>
  <div class="note">Gayatri Vidya Parishad Institute of Health Care and Medical Technology, Visakhapatnam. Prepared for Phase I MBBS faculty mentors under NMC CBME 2024 (1 mentor : 3 mentees; allotment in Foundation Course; continuity till CRMI). This is a documentation aid, not a substitute for college SOP or counselling services.</div>
</section>
"""


def build():
    parts = [
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>",
        "<title>Mentor–Mentee Logbook · Phase I MBBS</title>",
        f"<style>{CSS}</style></head><body>",
        cover(),
        how_to_use(),
        mentor_and_tracker(),
    ]
    for letter, cls, _colour, title in MENTEE_META:
        parts.append(profile_page(letter, cls, title))
        parts.append(swoc_academic(letter, cls, title))
        for i, prompt in enumerate(MONTHS, start=1):
            parts.append(meeting_sheet(letter, cls, title, i, prompt))
        parts.append(year_end(letter, cls, title))
    parts.append(extras())
    parts.append("</body></html>")
    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
