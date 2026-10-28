import json, os

# Read base64 logo
with open(r'C:\Users\ALMadina\.gemini\antigravity\scratch\delta-team-dashboard\logo_b64.txt', 'r') as f:
    logo_b64 = f.read().strip()

from data import PRODUCTS, REPS_DATA

# English translated Rep definitions
REPS_EN = []
for r in REPS_DATA:
    rep_copy = dict(r)
    # Translate notes if any
    if rep_copy.get("note"):
        rep_copy["note"] = "Joined the team in Q2 — No Q1 records available"
    else:
        rep_copy["note"] = "Medical Representative — Delta Team (EVA Insulin 2026)"
    
    # Translate quarter notes
    if rep_copy.get("quarters"):
        for q, qdata in rep_copy["quarters"].items():
            if qdata and "products" in qdata:
                for p in qdata["products"]:
                    if p.get("note") == "محسوب من السعر الموحد":
                        p["note"] = "Calculated based on standard price"
                    elif p.get("note") == "مبيعات بدون تارجت":
                        p["note"] = "Sales recorded without target"
    REPS_EN.append(rep_copy)

HTML_CONTENT = r'''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EVA INSULIN | Delta Team — Sales Dashboard 2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:             #0a0c10;
    --surface:        #12161f;
    --surface-hover:  #181e2b;
    --surface-elev:   #1d2433;
    --border:         #232a3b;
    --border-accent:  #d97706;
    
    /* EVA Yellow & Black Brand Palette */
    --gold:           #f59e0b;
    --gold-light:     #fbbf24;
    --gold-bright:    #facc15;
    --gold-dim:       #b45309;
    --gold-glow:      rgba(245, 158, 11, 0.2);
    
    --text-primary:   #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted:     #64748b;
    
    /* Status indicators */
    --green:          #10b981;
    --green-bg:       rgba(16, 185, 129, 0.12);
    --green-border:   rgba(16, 185, 129, 0.3);
    
    --red:            #ef4444;
    --red-bg:         rgba(239, 68, 68, 0.12);
    --red-border:     rgba(239, 68, 68, 0.3);
    
    --orange:         #f97316;
    --orange-bg:      rgba(249, 115, 22, 0.12);
    --orange-border:  rgba(249, 115, 22, 0.3);

    --header-h:       72px;
  }

  body {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text-primary);
    min-height: 100vh;
    font-size: 13.5px;
    direction: ltr;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }

  /* ── TOPBAR ── */
  #topbar {
    position: sticky; top: 0; z-index: 100;
    height: var(--header-h);
    background: linear-gradient(180deg, #07090d 0%, #0f131a 100%);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 28px;
    border-bottom: 2px solid var(--gold);
    box-shadow: 0 4px 24px rgba(0,0,0,0.6);
  }
  .brand { display: flex; align-items: center; gap: 16px; cursor: pointer; text-decoration: none; }
  .brand-logo-img {
    height: 48px; border-radius: 8px; border: 1px solid rgba(245, 158, 11, 0.4);
    box-shadow: 0 0 16px rgba(245, 158, 11, 0.15);
    background: #000;
  }
  .brand-titles { display: flex; flex-direction: column; }
  .brand-name {
    color: #ffffff; font-weight: 900; font-size: 19px; letter-spacing: 0.5px;
    display: flex; align-items: center; gap: 8px;
  }
  .brand-tag {
    background: linear-gradient(135deg, var(--gold), var(--gold-bright));
    color: #000000; font-size: 10.5px; font-weight: 900;
    padding: 2px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.5px;
  }
  .brand-sub { color: var(--text-secondary); font-size: 11.5px; font-weight: 500; }

  .topbar-right { display: flex; align-items: center; gap: 16px; }
  .topbar-date {
    color: #cbd5e1; font-size: 12px; font-weight: 600;
    background: rgba(255,255,255,0.05); padding: 7px 16px; border-radius: 20px;
    border: 1px solid var(--border);
  }
  #back-btn {
    display: none; align-items: center; gap: 8px;
    background: linear-gradient(135deg, var(--gold), var(--gold-light));
    color: #000000; padding: 8px 18px; border-radius: 8px; border: none;
    cursor: pointer; font-family: inherit; font-size: 13px;
    font-weight: 800; transition: all 0.2s;
    box-shadow: 0 2px 12px rgba(245, 158, 11, 0.3);
  }
  #back-btn:hover {
    transform: translateY(-2px); box-shadow: 0 4px 18px rgba(245, 158, 11, 0.5);
    background: #ffffff;
  }
  #back-btn.visible { display: flex; }

  /* ── MAIN CONTAINER ── */
  #main { padding: 32px 28px; max-width: 1480px; margin: 0 auto; width: 100%; }

  .view { display: none; }
  .view.active { display: block; animation: fadeIn 0.25s ease; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

  /* ── HERO BANNER / PAGE TITLE ── */
  .page-title {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 28px; flex-wrap: wrap; gap: 16px;
    padding-bottom: 20px; border-bottom: 1px solid var(--border);
  }
  .title-content { display: flex; align-items: center; gap: 16px; }
  .title-badge-icon {
    width: 52px; height: 52px; border-radius: 14px;
    background: linear-gradient(135deg, #181d26, #0d0f14);
    border: 2px solid var(--gold);
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; color: var(--gold);
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
  }
  .page-title h1 {
    font-size: 25px; font-weight: 800; color: #ffffff; letter-spacing: -0.3px;
  }
  .page-title .subtitle { font-size: 13.5px; color: var(--text-secondary); margin-top: 2px; }

  /* ── STAT CARDS GRID ── */
  .stat-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 16px; margin-bottom: 32px;
  }
  .stat-card {
    background: var(--surface); border-radius: 14px;
    padding: 20px 22px; border: 1px solid var(--border);
    position: relative; overflow: hidden;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
  }
  .stat-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--gold), transparent);
  }
  .stat-card:hover {
    transform: translateY(-3px); border-color: var(--gold-dim);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4), 0 0 12px rgba(245, 158, 11, 0.1);
  }
  .stat-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .stat-label { font-size: 12px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
  .stat-icon { font-size: 18px; }
  .stat-val { font-size: 23px; font-weight: 800; color: #ffffff; letter-spacing: -0.3px; }
  .stat-sub { font-size: 11.5px; color: var(--text-muted); margin-top: 5px; font-weight: 500; }

  /* ── TEAM GRID ── */
  .team-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
  }
  .rep-card {
    background: var(--surface); border-radius: 16px;
    padding: 22px; cursor: pointer;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    border: 1px solid var(--border);
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative; overflow: hidden;
    display: flex; flex-direction: column; justify-content: space-between;
  }
  .rep-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--gold), var(--gold-bright));
  }
  .rep-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.5), 0 0 16px rgba(245, 158, 11, 0.2);
    border-color: var(--gold);
    background: var(--surface-hover);
  }
  .rep-card.no-data { cursor: default; opacity: 0.65; }
  .rep-card.no-data::before { background: var(--border); }
  .rep-card.no-data:hover {
    transform: none; box-shadow: 0 4px 16px rgba(0,0,0,0.25); border-color: var(--border);
    background: var(--surface);
  }

  .rep-card-header { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
  .rep-avatar {
    width: 48px; height: 48px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 19px; font-weight: 900; color: #000000; flex-shrink: 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.4);
    background: linear-gradient(135deg, var(--gold), var(--gold-bright));
  }
  .rep-card-title { font-size: 17px; font-weight: 800; color: #ffffff; }
  .rep-card-badge {
    display: inline-block; font-size: 10px; font-weight: 800;
    padding: 2px 9px; border-radius: 4px; margin-top: 3px;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .badge-active { background: var(--green-bg); color: var(--green); border: 1px solid var(--green-border); }
  .badge-nodata { background: rgba(255,255,255,0.06); color: var(--text-muted); border: 1px solid var(--border); }
  .badge-q2start { background: var(--orange-bg); color: var(--gold-light); border: 1px solid var(--orange-border); }

  .rep-card-kpi {
    background: rgba(0,0,0,0.3); border-radius: 10px; padding: 12px 14px;
    margin-bottom: 14px; border: 1px solid rgba(255,255,255,0.04);
  }
  .kpi-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px; }
  .kpi-row:last-child { margin-bottom: 0; }
  .kpi-label { font-size: 12px; color: var(--text-secondary); font-weight: 500; }
  .kpi-value { font-size: 13.5px; font-weight: 700; color: #ffffff; }

  .progress-wrap { margin-bottom: 14px; }
  .progress-label { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; font-weight: 600; color: var(--text-secondary); }
  .progress-bar { height: 8px; background: #1c2333; border-radius: 6px; overflow: hidden; }
  .progress-fill { height: 100%; border-radius: 6px; transition: width 0.6s ease; }

  .rep-card-footer {
    display: flex; justify-content: space-between; align-items: center;
    padding-top: 12px; border-top: 1px solid var(--border);
  }
  .quarters-pills { display: flex; gap: 5px; }
  .q-pill {
    font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 4px;
    text-transform: uppercase; letter-spacing: 0.3px;
  }
  .q-pill.available { background: rgba(245, 158, 11, 0.15); color: var(--gold-light); border: 1px solid rgba(245, 158, 11, 0.3); }
  .q-pill.missing   { background: rgba(255,255,255,0.04); color: var(--text-muted); border: 1px solid var(--border); }
  .q-pill.entered   { background: var(--green-bg); color: var(--green); border: 1px solid var(--green-border); }
  .rep-card-arrow   { color: var(--gold); font-size: 12.5px; font-weight: 800; display: flex; align-items: center; gap: 4px; }

  /* ── REP VIEW ── */
  .rep-header-bar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 24px; flex-wrap: wrap; gap: 16px;
  }
  .rep-profile { display: flex; align-items: center; gap: 18px; }
  .rep-profile-name { font-size: 26px; font-weight: 900; color: #ffffff; letter-spacing: -0.3px; }
  .rep-profile-note { font-size: 13px; color: var(--text-secondary); margin-top: 4px; font-weight: 500; }

  /* YTD STRIP */
  .ytd-strip {
    background: linear-gradient(135deg, #0d1117 0%, #161b24 100%);
    border-radius: 16px; padding: 22px 28px; margin-bottom: 26px;
    display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)) auto;
    gap: 20px; align-items: center;
    border: 1px solid var(--border);
    border-left: 4px solid var(--gold);
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  }
  .ytd-item .ytd-label { font-size: 11.5px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
  .ytd-item .ytd-val   { font-size: 21px; font-weight: 900; color: #ffffff; }
  .ytd-item .ytd-unit  { font-size: 11px; color: var(--text-muted); margin-top: 3px; }
  .ytd-badge-box {
    text-align: center; background: rgba(0,0,0,0.4); padding: 14px 24px;
    border-radius: 12px; border: 1px solid rgba(245, 158, 11, 0.3);
  }
  .ytd-badge-label { font-size: 11px; color: var(--text-secondary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
  .ytd-badge-val   { font-size: 28px; font-weight: 900; }

  /* TABS */
  .tabs-nav {
    display: flex; gap: 8px; margin-bottom: 22px; flex-wrap: wrap;
    background: #0f131a; padding: 6px; border-radius: 12px;
    border: 1px solid var(--border); width: fit-content;
  }
  .tab-btn {
    padding: 10px 22px; border-radius: 8px; border: none;
    background: transparent; cursor: pointer; font-family: inherit;
    font-size: 13.5px; font-weight: 700; color: var(--text-secondary);
    transition: all 0.2s; display: flex; align-items: center; gap: 8px;
  }
  .tab-btn:hover { color: #ffffff; background: rgba(255,255,255,0.05); }
  .tab-btn.active {
    background: var(--gold); color: #000000; font-weight: 800;
    box-shadow: 0 2px 10px rgba(245, 158, 11, 0.35);
  }
  .tab-btn.q4-tab { color: var(--gold-light); background: rgba(245, 158, 11, 0.08); }
  .tab-btn.q4-tab.active { background: linear-gradient(135deg, var(--gold), var(--gold-bright)); color: #000000; }
  .tab-btn.disabled { opacity: 0.35; cursor: not-allowed; pointer-events: none; }

  .tab-panel { display: none; }
  .tab-panel.active { display: block; animation: fadeIn 0.2s ease; }

  /* ── TABLES ── */
  .card {
    background: var(--surface); border-radius: 16px;
    border: 1px solid var(--border); box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    overflow: hidden; margin-bottom: 26px;
  }
  .card-header {
    padding: 18px 24px; background: #0f131c;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
  }
  .card-header h3 { font-size: 16px; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 10px; }
  .card-header-sub { font-size: 12px; color: var(--text-secondary); font-weight: 500; }

  .table-scroll { overflow-x: auto; width: 100%; }
  table.data-table {
    width: 100%; border-collapse: separate; border-spacing: 0;
    font-size: 12.5px; text-align: left; min-width: 1020px;
  }
  table.data-table th {
    background: #090b10; color: #cbd5e1; font-weight: 700;
    padding: 12px 14px; font-size: 11px; white-space: nowrap;
    border-bottom: 2px solid var(--border); text-transform: uppercase; letter-spacing: 0.4px;
  }
  table.data-table th.th-grp-unit  { background: #0c1424; color: #93c5fd; border-bottom: 2px solid #1e3a8a; }
  table.data-table th.th-grp-val   { background: #1a160b; color: #fde047; border-bottom: 2px solid var(--gold-dim); }
  table.data-table th.th-grp-pts   { background: #0c1b18; color: #6ee7b7; border-bottom: 2px solid #065f46; }
  table.data-table th.th-grp-ratio { background: #131720; text-align: center; }

  table.data-table td {
    padding: 13px 14px; border-bottom: 1px solid var(--border);
    white-space: nowrap; vertical-align: middle; color: #e2e8f0;
  }
  table.data-table tbody tr:hover td { background: var(--surface-hover); }

  .prod-title { font-weight: 800; color: #ffffff; font-size: 13px; line-height: 1.3; }
  .prod-code  { font-size: 11px; color: var(--gold-light); font-weight: 600; font-family: monospace; }
  .prod-tag   { font-size: 10px; padding: 2px 7px; border-radius: 4px; font-weight: 700; display: inline-block; margin-top: 3px; }
  .tag-est    { background: rgba(245, 158, 11, 0.15); color: var(--gold-light); border: 1px solid rgba(245, 158, 11, 0.3); }

  /* DEFICIT & SURPLUS BADGES */
  .deficit-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 9px; border-radius: 5px; font-size: 11.5px; font-weight: 800;
  }
  .deficit-red {
    background: var(--red-bg); color: #fca5a5; border: 1px solid var(--red-border);
  }
  .deficit-green {
    background: var(--green-bg); color: #86efac; border: 1px solid var(--green-border);
  }
  .ratio-badge {
    display: inline-block; padding: 4px 11px; border-radius: 20px;
    font-size: 11.5px; font-weight: 800; text-align: center;
  }
  .ratio-green  { background: var(--green-bg); color: #4ade80; border: 1px solid var(--green-border); }
  .ratio-orange { background: var(--orange-bg); color: #fdba74; border: 1px solid var(--orange-border); }
  .ratio-red    { background: var(--red-bg); color: #f87171; border: 1px solid var(--red-border); }

  /* TOTAL ROW */
  tr.row-total td {
    background: #090c12 !important; font-weight: 900;
    color: #ffffff; font-size: 13px;
    border-top: 2px solid var(--gold); border-bottom: none;
  }
  tr.row-total td:first-child { color: var(--gold); }

  /* ── CHARTS ROW ── */
  .charts-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
    gap: 20px; margin-bottom: 26px;
  }
  .chart-box { padding: 20px; height: 330px; position: relative; }

  /* ── Q4 FORM ── */
  .q4-wrapper { padding: 24px; }
  .q4-alert {
    background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px;
    padding: 14px 18px; margin-bottom: 24px; display: flex; align-items: center; gap: 12px;
  }
  .q4-alert-text { font-size: 13px; color: var(--gold-light); font-weight: 600; }
  .q4-prod-card {
    background: #0f131c; border: 1px solid var(--border); border-radius: 12px;
    margin-bottom: 18px; overflow: hidden;
  }
  .q4-prod-header {
    background: #171d29; padding: 12px 18px; font-weight: 800;
    font-size: 13.5px; color: #ffffff; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid var(--border);
  }
  .q4-inputs-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 14px; padding: 18px;
  }
  .q4-field label {
    display: block; font-size: 11px; font-weight: 700; color: var(--text-secondary); margin-bottom: 6px;
    text-transform: uppercase; letter-spacing: 0.3px;
  }
  .q4-field input {
    width: 100%; padding: 9px 12px; border: 1px solid var(--border);
    border-radius: 8px; font-family: inherit; font-size: 13px;
    font-weight: 700; color: #ffffff; background: #07090e;
    transition: all 0.2s;
  }
  .q4-field input:focus {
    outline: none; border-color: var(--gold);
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
  }
  .q4-actions {
    display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin-top: 24px;
  }
  .btn {
    padding: 11px 26px; border-radius: 8px; border: none; cursor: pointer;
    font-family: inherit; font-size: 13.5px; font-weight: 800;
    display: flex; align-items: center; gap: 8px; transition: all 0.2s;
  }
  .btn-save {
    background: linear-gradient(135deg, var(--gold), var(--gold-bright)); color: #000000;
    box-shadow: 0 4px 16px rgba(245, 158, 11, 0.35);
  }
  .btn-save:hover {
    transform: translateY(-2px); box-shadow: 0 6px 20px rgba(245, 158, 11, 0.5);
    background: #ffffff;
  }
  .btn-clear {
    background: transparent; color: #f87171; border: 1px solid var(--red-border);
  }
  .btn-clear:hover { background: var(--red-bg); }
  .save-toast {
    display: none; padding: 10px 18px; border-radius: 8px; font-size: 13px;
    font-weight: 700; background: var(--green-bg); color: #86efac;
    border: 1px solid var(--green-border); align-items: center; gap: 8px;
  }
  .save-toast.visible { display: flex; animation: fadeIn 0.2s; }

  /* RESPONSIVE */
  @media (max-width: 768px) {
    #topbar { padding: 0 16px; }
    #main { padding: 20px 14px; }
    .page-title h1 { font-size: 21px; }
    .ytd-strip { grid-template-columns: 1fr 1fr; }
    .charts-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<!-- TOPBAR -->
<header id="topbar">
  <div class="brand" onclick="showHome()">
    <img src="data:image/jpeg;base64,__LOGO_B64__" alt="EVA INSULIN" class="brand-logo-img">
    <div class="brand-titles">
      <div class="brand-name">
        EVA INSULIN
        <span class="brand-tag">Delta Team</span>
      </div>
      <div class="brand-sub">Sales Performance & Deficit Tracking System 2026</div>
    </div>
  </div>
  <div class="topbar-right">
    <div class="topbar-date" id="topbar-date"></div>
    <button id="back-btn" onclick="showHome()">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
      Team Overview
    </button>
  </div>
</header>

<main id="main">

  <!-- VIEW: TEAM OVERVIEW -->
  <div id="view-home" class="view active">
    <div class="page-title">
      <div class="title-content">
        <div class="title-badge-icon">Δ</div>
        <div>
          <h1>EVA Insulin — Delta Team Performance (YTD 2026)</h1>
          <div class="subtitle">Comprehensive sales analysis, quota achievement, and deficit tracking across all team representatives</div>
        </div>
      </div>
    </div>

    <!-- STAT ROW -->
    <div class="stat-grid" id="team-stat-grid"></div>

    <!-- REP CARDS -->
    <div class="team-grid" id="team-grid"></div>
  </div>

  <!-- VIEW: INDIVIDUAL REP -->
  <div id="view-rep" class="view">
    <div class="rep-header-bar">
      <div class="rep-profile">
        <div id="rep-avatar-large" class="rep-avatar" style="width:58px;height:58px;font-size:24px;border-radius:14px;"></div>
        <div>
          <div class="rep-profile-name" id="rep-profile-name"></div>
          <div class="rep-profile-note" id="rep-profile-note"></div>
        </div>
      </div>
    </div>

    <!-- YTD STRIP -->
    <div class="ytd-strip" id="rep-ytd-strip"></div>

    <!-- TABS -->
    <div class="tabs-nav" id="rep-tabs-nav"></div>

    <!-- PANELS CONTAINER -->
    <div id="rep-panels-container"></div>

    <!-- CHARTS -->
    <div class="charts-grid">
      <div class="card">
        <div class="card-header">
          <h3>📊 Sales vs Target by Product (YTD)</h3>
          <div class="card-header-sub">Value in Egyptian Pounds (EGP)</div>
        </div>
        <div class="chart-box"><canvas id="repBarChart"></canvas></div>
      </div>
      <div class="card">
        <div class="card-header">
          <h3>📈 Quarterly Sales Progression vs Target</h3>
          <div class="card-header-sub">Quarterly Sales Trend (Q1 - Q4)</div>
        </div>
        <div class="chart-box"><canvas id="repLineChart"></canvas></div>
      </div>
    </div>
  </div>

</main>

<script>
/* ── DATA DEFINITIONS ── */
const PRODUCTS = __PRODUCTS_JSON__;
const REPS = __REPS_JSON__;

/* ── NUMBER FORMATTERS ── */
function fmt(n) {
  if (n === null || n === undefined || isNaN(n)) return '—';
  return Number(n).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 });
}
function fmtPct(r) {
  if (r === null || r === undefined || isNaN(r)) return '—';
  return Number(r).toFixed(2) + '%';
}
function ratioClass(r) {
  if (r === null || r === undefined || isNaN(r)) return '';
  if (r >= 100) return 'ratio-green';
  if (r >= 70)  return 'ratio-orange';
  return 'ratio-red';
}

/* ── DEFICIT FORMATTERS ── */
// Deficit = Target - Sales
// If Target > Sales => Deficit => RED
// If Sales >= Target => Surplus => GREEN
function renderDeficitUnit(targetUnits, salesUnits) {
  if (targetUnits === null || salesUnits === null || targetUnits === undefined || salesUnits === undefined) {
    return '—';
  }
  const diff = targetUnits - salesUnits;
  if (diff > 0.001) {
    return `<span class="deficit-badge deficit-red">Deficit -${fmt(diff)}</span>`;
  } else if (diff <= -0.001) {
    return `<span class="deficit-badge deficit-green">Surplus +${fmt(Math.abs(diff))}</span>`;
  } else {
    return `<span class="deficit-badge deficit-green">Target Met</span>`;
  }
}

function renderDeficitVal(targetVal, salesVal) {
  if (targetVal === null || salesVal === null || targetVal === undefined || salesVal === undefined) {
    return '—';
  }
  const diff = targetVal - salesVal;
  if (diff > 0.01) {
    return `<span class="deficit-badge deficit-red">Deficit -${fmt(diff)} EGP</span>`;
  } else if (diff <= -0.01) {
    return `<span class="deficit-badge deficit-green">Surplus +${fmt(Math.abs(diff))} EGP</span>`;
  } else {
    return `<span class="deficit-badge deficit-green">Target Met</span>`;
  }
}

function renderDeficitPts(targetPts, salesPts) {
  if (targetPts === null || salesPts === null || targetPts === undefined || salesPts === undefined) {
    return '—';
  }
  const diff = targetPts - salesPts;
  if (diff > 0.01) {
    return `<span class="deficit-badge deficit-red">Deficit -${fmt(diff)}</span>`;
  } else if (diff <= -0.01) {
    return `<span class="deficit-badge deficit-green">Surplus +${fmt(Math.abs(diff))}</span>`;
  } else {
    return `<span class="deficit-badge deficit-green">Met</span>`;
  }
}

/* ── LOCAL STORAGE Q4 ── */
function getQ4Key(repKey) { return 'eva_delta_q4_' + repKey; }
function loadQ4(repKey) {
  try { return JSON.parse(localStorage.getItem(getQ4Key(repKey))); } catch { return null; }
}
function saveQ4(repKey, data) {
  localStorage.setItem(getQ4Key(repKey), JSON.stringify(data));
}

/* ── COMPUTE YTD TOTALS FOR REP ── */
function computeRepYTD(rep) {
  if (rep.noData) return null;

  const summary = {
    salesUnits: 0, targetUnits: 0,
    salesValue: 0, targetValue: 0,
    salesPoints: 0, targetPoints: 0,
    hasData: false,
    productsYTD: {}
  };

  PRODUCTS.forEach(p => {
    summary.productsYTD[p.id] = {
      pid: p.id, salesUnits: 0, targetUnits: 0,
      salesValue: 0, targetValue: 0,
      salesPoints: 0, targetPoints: 0,
      hasData: false
    };
  });

  const quarters = ['Q1', 'Q2', 'Q3'];
  quarters.forEach(q => {
    const qd = rep.quarters && rep.quarters[q];
    if (qd && qd.products) {
      summary.hasData = true;
      qd.products.forEach(p => {
        const py = summary.productsYTD[p.pid];
        if (py) {
          if (p.salesUnits !== null)  { py.salesUnits  += p.salesUnits; summary.salesUnits += p.salesUnits; }
          if (p.targetUnits !== null) { py.targetUnits += p.targetUnits; summary.targetUnits += p.targetUnits; }
          if (p.salesValue !== null)  { py.salesValue  += p.salesValue; summary.salesValue += p.salesValue; }
          if (p.targetValue !== null) { py.targetValue += p.targetValue; summary.targetValue += p.targetValue; }
          if (p.salesPoints !== null) { py.salesPoints += p.salesPoints; summary.salesPoints += p.salesPoints; }
          if (p.targetPoints !== null){ py.targetPoints+= p.targetPoints; summary.targetPoints += p.targetPoints; }
          if (p.salesValue !== null || p.targetValue !== null) py.hasData = true;
        }
      });
    }
  });

  // Include Q4 if entered
  const q4 = loadQ4(rep.key);
  if (q4 && q4.products) {
    summary.hasData = true;
    q4.products.forEach(p => {
      const py = summary.productsYTD[p.pid];
      if (py) {
        if (p.salesUnits)  { py.salesUnits  += p.salesUnits; summary.salesUnits += p.salesUnits; }
        if (p.targetUnits) { py.targetUnits += p.targetUnits; summary.targetUnits += p.targetUnits; }
        if (p.salesValue)  { py.salesValue  += p.salesValue; summary.salesValue += p.salesValue; }
        if (p.targetValue) { py.targetValue += p.targetValue; summary.targetValue += p.targetValue; }
        if (p.salesPoints) { py.salesPoints += p.salesPoints; summary.salesPoints += p.salesPoints; }
        if (p.targetPoints){ py.targetPoints+= p.targetPoints; summary.targetPoints += p.targetPoints; }
        if (p.salesValue || p.targetValue) py.hasData = true;
      }
    });
  }

  if (!summary.hasData) return null;

  summary.ratio = summary.targetValue > 0 ? (summary.salesValue / summary.targetValue) * 100 : null;
  summary.deficitValue = summary.targetValue - summary.salesValue;
  summary.deficitUnits = summary.targetUnits - summary.salesUnits;
  summary.deficitPoints = summary.targetPoints - summary.salesPoints;

  // Compute ratio for each product
  PRODUCTS.forEach(p => {
    const py = summary.productsYTD[p.id];
    py.ratio = py.targetValue > 0 ? (py.salesValue / py.targetValue) * 100 : null;
    py.deficitValue = py.targetValue - py.salesValue;
    py.deficitUnits = py.targetUnits - py.salesUnits;
    py.deficitPoints = py.targetPoints - py.salesPoints;
  });

  return summary;
}

/* ── CHARTS ── */
let barChartInstance = null;
let lineChartInstance = null;
function destroyCharts() {
  if (barChartInstance)  { barChartInstance.destroy();  barChartInstance = null; }
  if (lineChartInstance) { lineChartInstance.destroy(); lineChartInstance = null; }
}

/* ── RENDER HOME VIEW ── */
function renderHome() {
  destroyCharts();

  let totalSales = 0, totalTarget = 0, totalUnits = 0, totalPoints = 0, activeCount = 0;
  REPS.forEach(r => {
    const ytd = computeRepYTD(r);
    if (ytd) {
      totalSales  += ytd.salesValue;
      totalTarget += ytd.targetValue;
      totalUnits  += ytd.salesUnits;
      totalPoints += ytd.salesPoints;
      activeCount++;
    }
  });
  const teamRatio = totalTarget > 0 ? (totalSales / totalTarget) * 100 : 0;
  const teamDeficit = totalTarget - totalSales;

  document.getElementById('team-stat-grid').innerHTML = `
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">Total Team Sales (YTD)</span>
        <span class="stat-icon">💰</span>
      </div>
      <div class="stat-val">${fmt(totalSales)} <span style="font-size:12px;color:var(--gold);font-weight:700;">EGP</span></div>
      <div class="stat-sub">Cumulative actual sales revenue</div>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">Total Team Target (YTD)</span>
        <span class="stat-icon">🎯</span>
      </div>
      <div class="stat-val">${fmt(totalTarget)} <span style="font-size:12px;color:var(--text-muted);font-weight:700;">EGP</span></div>
      <div class="stat-sub">Assigned annual quota to date</div>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">Net Team Deficit / Surplus</span>
        <span class="stat-icon">⚖️</span>
      </div>
      <div class="stat-val">
        ${renderDeficitVal(totalTarget, totalSales)}
      </div>
      <div class="stat-sub">${teamDeficit <= 0 ? 'Team exceeded aggregate quota' : 'Gap remaining to hit team target'}</div>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">Achievement Rate</span>
        <span class="stat-icon">📈</span>
      </div>
      <div class="stat-val"><span class="ratio-badge ${ratioClass(teamRatio)}" style="font-size:18px;">${fmtPct(teamRatio)}</span></div>
      <div class="stat-sub">Overall team fulfillment ratio</div>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">Total Sales Points</span>
        <span class="stat-icon">⭐</span>
      </div>
      <div class="stat-val">${fmt(totalPoints)}</div>
      <div class="stat-sub">Points earned by team</div>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">Representatives</span>
        <span class="stat-icon">👥</span>
      </div>
      <div class="stat-val">${REPS.length} Reps</div>
      <div class="stat-sub">${activeCount} active with uploaded records</div>
    </div>
  `;

  // Render Rep Cards
  const grid = document.getElementById('team-grid');
  grid.innerHTML = '';

  REPS.forEach(rep => {
    const card = document.createElement('div');
    card.className = 'rep-card' + (rep.noData ? ' no-data' : '');
    if (!rep.noData) {
      card.onclick = () => showRep(rep.key);
    }

    if (rep.noData) {
      card.innerHTML = `
        <div>
          <div class="rep-card-header">
            <div class="rep-avatar" style="background:#232a3b;color:var(--text-muted);">${rep.name[0]}</div>
            <div>
              <div class="rep-card-title">${rep.name}</div>
              <span class="rep-card-badge badge-nodata">No Records Uploaded</span>
            </div>
          </div>
          <div style="text-align:center;padding:26px 0;color:var(--text-muted);">
            <div style="font-size:32px;margin-bottom:8px;opacity:0.5;">📁</div>
            <div style="font-weight:700;font-size:13.5px;color:var(--text-secondary);">Folder is Currently Empty</div>
            <div style="font-size:11.5px;margin-top:4px;">No quarterly Excel files provided yet</div>
          </div>
        </div>
        <div class="rep-card-footer">
          <div class="quarters-pills">
            <span class="q-pill missing">Q1</span>
            <span class="q-pill missing">Q2</span>
            <span class="q-pill missing">Q3</span>
            <span class="q-pill missing">Q4</span>
          </div>
          <span style="font-size:11.5px;color:var(--text-muted);">Pending</span>
        </div>
      `;
    } else {
      const ytd = computeRepYTD(rep);
      const q4saved = loadQ4(rep.key);
      const ratio = ytd ? ytd.ratio : 0;
      const progressWidth = ratio ? Math.min(ratio, 130) / 130 * 100 : 0;
      const progressColor = ratio >= 100 ? 'background:var(--green);' : ratio >= 70 ? 'background:var(--gold);' : 'background:var(--red);';
      const badgeClass = rep.startQ === 2 ? 'badge-q2start' : 'badge-active';
      const badgeText  = rep.startQ === 2 ? 'Joined Q2' : 'Active (Q1 - Q3)';

      const qPills = ['Q1', 'Q2', 'Q3', 'Q4'].map(q => {
        if (q === 'Q4') {
          return q4saved ? `<span class="q-pill entered">Q4: Entered</span>` : `<span class="q-pill missing">Q4: Available</span>`;
        }
        if (rep.startQ === 2 && q === 'Q1') {
          return `<span class="q-pill missing">Q1: N/A</span>`;
        }
        const has = rep.quarters && rep.quarters[q];
        return `<span class="q-pill ${has ? 'available' : 'missing'}">${q}</span>`;
      }).join('');

      card.innerHTML = `
        <div>
          <div class="rep-card-header">
            <div class="rep-avatar">${rep.name[0]}</div>
            <div>
              <div class="rep-card-title">${rep.name}</div>
              <span class="rep-card-badge ${badgeClass}">${badgeText}</span>
            </div>
          </div>

          <div class="rep-card-kpi">
            <div class="kpi-row">
              <span class="kpi-label">Actual Sales (YTD):</span>
              <span class="kpi-value">${ytd ? fmt(ytd.salesValue) : '—'} <span style="font-size:10.5px;color:var(--gold);">EGP</span></span>
            </div>
            <div class="kpi-row">
              <span class="kpi-label">Target Quota (YTD):</span>
              <span class="kpi-value">${ytd ? fmt(ytd.targetValue) : '—'} <span style="font-size:10.5px;color:var(--text-muted);">EGP</span></span>
            </div>
            <div class="kpi-row">
              <span class="kpi-label">Deficit / Surplus:</span>
              <span>${ytd ? renderDeficitVal(ytd.targetValue, ytd.salesValue) : '—'}</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-label">Units Sold:</span>
              <span class="kpi-value">${ytd ? fmt(ytd.salesUnits) : '—'} units</span>
            </div>
          </div>

          <div class="progress-wrap">
            <div class="progress-label">
              <span>Quota Fulfillment:</span>
              <span class="ratio-badge ${ratioClass(ratio)}">${fmtPct(ratio)}</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width:${progressWidth}%;${progressColor}"></div>
            </div>
          </div>
        </div>

        <div class="rep-card-footer">
          <div class="quarters-pills">${qPills}</div>
          <span class="rep-card-arrow">View Details &rarr;</span>
        </div>
      `;
    }
    grid.appendChild(card);
  });
}

/* ── BUILD TABLE HTML FOR A QUARTER OR YTD ── */
function buildProductsTable(title, sub, productsList, totalData) {
  const rows = productsList.map(p => {
    const prod = PRODUCTS.find(pr => pr.id === p.pid) || { name: 'Product ' + p.pid, code: '' };
    return `
      <tr>
        <td>
          <div class="prod-title">${prod.name}</div>
          <div class="prod-code">${prod.code}</div>
          ${p.note ? `<span class="prod-tag tag-est">${p.note}</span>` : ''}
        </td>
        <td><strong>${fmt(p.salesUnits)}</strong></td>
        <td>${fmt(p.targetUnits)}</td>
        <td>${renderDeficitUnit(p.targetUnits, p.salesUnits)}</td>
        <td><strong>${fmt(p.salesValue)}</strong> <span style="font-size:10.5px;color:var(--gold);">EGP</span></td>
        <td>${fmt(p.targetValue)} EGP</td>
        <td>${renderDeficitVal(p.targetValue, p.salesValue)}</td>
        <td><strong>${fmt(p.salesPoints)}</strong></td>
        <td>${fmt(p.targetPoints)}</td>
        <td>${renderDeficitPts(p.targetPoints, p.salesPoints)}</td>
        <td style="text-align:center;"><span class="ratio-badge ${ratioClass(p.ratio)}">${fmtPct(p.ratio)}</span></td>
      </tr>
    `;
  }).join('');

  return `
    <div class="card">
      <div class="card-header">
        <h3>📋 ${title}</h3>
        <div class="card-header-sub">${sub}</div>
      </div>
      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th rowspan="2" style="min-width:180px;">Pharmaceutical Product</th>
              <th colspan="3" class="th-grp-unit">Units Breakdown</th>
              <th colspan="3" class="th-grp-val">Revenue in EGP (Sales vs Target)</th>
              <th colspan="3" class="th-grp-pts">Points Performance</th>
              <th rowspan="2" class="th-grp-ratio">Ratio %</th>
            </tr>
            <tr>
              <th class="th-grp-unit">Sales Units</th>
              <th class="th-grp-unit">Target Units</th>
              <th class="th-grp-unit">Unit Deficit / Surplus</th>
              <th class="th-grp-val">Sales Value</th>
              <th class="th-grp-val">Target Value</th>
              <th class="th-grp-val">Value Deficit / Surplus</th>
              <th class="th-grp-pts">Sales Points</th>
              <th class="th-grp-pts">Target Points</th>
              <th class="th-grp-pts">Points Deficit / Surplus</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
            <tr class="row-total">
              <td>Total Performance</td>
              <td><strong>${fmt(totalData.salesUnits)}</strong></td>
              <td><strong>${fmt(totalData.targetUnits)}</strong></td>
              <td>${renderDeficitUnit(totalData.targetUnits, totalData.salesUnits)}</td>
              <td><strong>${fmt(totalData.salesValue)}</strong> EGP</td>
              <td><strong>${fmt(totalData.targetValue)}</strong> EGP</td>
              <td>${renderDeficitVal(totalData.targetValue, totalData.salesValue)}</td>
              <td><strong>${fmt(totalData.salesPoints)}</strong></td>
              <td><strong>${fmt(totalData.targetPoints)}</strong></td>
              <td>${renderDeficitPts(totalData.targetPoints, totalData.salesPoints)}</td>
              <td style="text-align:center;"><span class="ratio-badge ${ratioClass(totalData.ratio)}">${fmtPct(totalData.ratio)}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
}

/* ── BUILD Q4 PANEL ── */
function buildQ4Form(rep) {
  const q4saved = loadQ4(rep.key);
  const prodCards = PRODUCTS.map((prod, idx) => {
    const saved = q4saved && q4saved.products ? q4saved.products[idx] : null;
    return `
      <div class="q4-prod-card">
        <div class="q4-prod-header">
          <span>📦 ${prod.name}</span>
          <span style="font-size:11px;color:var(--gold-light);font-family:monospace;">${prod.code}</span>
        </div>
        <div class="q4-inputs-grid">
          <div class="q4-field">
            <label>Sales Units</label>
            <input type="number" step="any" id="q4_su_${idx}_${rep.key}" placeholder="0" value="${saved && saved.salesUnits !== null ? saved.salesUnits : ''}">
          </div>
          <div class="q4-field">
            <label>Sales Value (EGP)</label>
            <input type="number" step="any" id="q4_sv_${idx}_${rep.key}" placeholder="0.00" value="${saved && saved.salesValue !== null ? saved.salesValue : ''}" oninput="autoPoints(${idx}, '${rep.key}')">
          </div>
          <div class="q4-field">
            <label>Sales Points</label>
            <input type="number" step="any" id="q4_sp_${idx}_${rep.key}" placeholder="0.00" value="${saved && saved.salesPoints !== null ? saved.salesPoints : ''}">
          </div>
          <div class="q4-field">
            <label>Target Units</label>
            <input type="number" step="any" id="q4_tu_${idx}_${rep.key}" placeholder="0" value="${saved && saved.targetUnits !== null ? saved.targetUnits : ''}">
          </div>
          <div class="q4-field">
            <label>Target Value (EGP)</label>
            <input type="number" step="any" id="q4_tv_${idx}_${rep.key}" placeholder="0.00" value="${saved && saved.targetValue !== null ? saved.targetValue : ''}" oninput="autoPoints(${idx}, '${rep.key}')">
          </div>
          <div class="q4-field">
            <label>Target Points</label>
            <input type="number" step="any" id="q4_tp_${idx}_${rep.key}" placeholder="0.00" value="${saved && saved.targetPoints !== null ? saved.targetPoints : ''}">
          </div>
        </div>
      </div>
    `;
  }).join('');

  let savedTableHtml = '';
  if (q4saved && q4saved.products) {
    savedTableHtml = buildProductsTable('Current Saved Q4 Records', 'Q4 achievements & deficit review', q4saved.products, q4saved.total);
  }

  return `
    <div class="card">
      <div class="card-header">
        <h3>✍️ Q4 2026 Data Upload & Entry Portal</h3>
        <div class="card-header-sub">Each representative can submit their Q4 numbers directly</div>
      </div>
      <div class="q4-wrapper">
        <div class="q4-alert">
          <span style="font-size:22px;">ℹ️</span>
          <div class="q4-alert-text">
            Enter Q4 sales units, revenue, and quotas. Deficits/surplus and full-year cumulative YTD metrics will recalculate dynamically upon saving.
          </div>
        </div>
        ${prodCards}
        <div class="q4-actions">
          <button class="btn btn-save" onclick="saveQ4Data('${rep.key}')">
            💾 Save & Apply Q4 Records
          </button>
          <button class="btn btn-clear" onclick="clearQ4Data('${rep.key}')">
            🗑️ Clear Q4 Records
          </button>
          <div class="save-toast" id="toast-${rep.key}">
            ✅ Q4 data successfully saved and integrated into YTD!
          </div>
        </div>
      </div>
    </div>
    <div id="q4-saved-preview-${rep.key}">${savedTableHtml}</div>
  `;
}

function autoPoints(idx, repKey) {
  const sv = parseFloat(document.getElementById(`q4_sv_${idx}_${repKey}`)?.value);
  const tv = parseFloat(document.getElementById(`q4_tv_${idx}_${repKey}`)?.value);
  const spInput = document.getElementById(`q4_sp_${idx}_${repKey}`);
  const tpInput = document.getElementById(`q4_tp_${idx}_${repKey}`);
  if (!isNaN(sv) && spInput && !spInput.value) spInput.value = (sv * 2).toFixed(2);
  if (!isNaN(tv) && tpInput && !tpInput.value) tpInput.value = (tv * 2).toFixed(2);
}

function saveQ4Data(repKey) {
  const products = PRODUCTS.map((prod, idx) => {
    const su = parseFloat(document.getElementById(`q4_su_${idx}_${repKey}`)?.value) || 0;
    const sv = parseFloat(document.getElementById(`q4_sv_${idx}_${repKey}`)?.value) || 0;
    const sp = parseFloat(document.getElementById(`q4_sp_${idx}_${repKey}`)?.value) || (sv * 2);
    const tu = parseFloat(document.getElementById(`q4_tu_${idx}_${repKey}`)?.value) || 0;
    const tv = parseFloat(document.getElementById(`q4_tv_${idx}_${repKey}`)?.value) || 0;
    const tp = parseFloat(document.getElementById(`q4_tp_${idx}_${repKey}`)?.value) || (tv * 2);
    const ratio = tv > 0 ? (sv / tv) * 100 : null;
    return {
      pid: prod.id,
      salesUnits: su, salesValue: sv, salesPoints: sp,
      targetUnits: tu, targetValue: tv, targetPoints: tp,
      ratio: ratio
    };
  });

  const totalSalesUnits  = products.reduce((a, p) => a + p.salesUnits,  0);
  const totalTargetUnits = products.reduce((a, p) => a + p.targetUnits, 0);
  const totalSalesValue  = products.reduce((a, p) => a + p.salesValue,  0);
  const totalTargetValue = products.reduce((a, p) => a + p.targetValue, 0);
  const totalSalesPoints = products.reduce((a, p) => a + p.salesPoints, 0);
  const totalTargetPoints= products.reduce((a, p) => a + p.targetPoints,0);
  const totalRatio = totalTargetValue > 0 ? (totalSalesValue / totalTargetValue) * 100 : null;

  const q4Data = {
    products,
    total: {
      salesUnits: totalSalesUnits, targetUnits: totalTargetUnits,
      salesValue: totalSalesValue, targetValue: totalTargetValue,
      salesPoints: totalSalesPoints, targetPoints: totalTargetPoints,
      ratio: totalRatio
    }
  };

  saveQ4(repKey, q4Data);

  const toast = document.getElementById(`toast-${repKey}`);
  if (toast) {
    toast.classList.add('visible');
    setTimeout(() => toast.classList.remove('visible'), 3500);
  }

  showRep(repKey, 'tab-Q4');
}

function clearQ4Data(repKey) {
  if (!confirm('Are you sure you want to delete all saved Q4 entries for this representative?')) return;
  localStorage.removeItem(getQ4Key(repKey));
  showRep(repKey, 'tab-Q4');
}

/* ── SHOW REP VIEW ── */
function showRep(repKey, targetTabId = null) {
  const rep = REPS.find(r => r.key === repKey);
  if (!rep || rep.noData) return;

  destroyCharts();

  document.getElementById('view-home').classList.remove('active');
  document.getElementById('view-rep').classList.add('active');
  document.getElementById('back-btn').classList.add('visible');

  // Header info
  const av = document.getElementById('rep-avatar-large');
  av.textContent = rep.name[0];
  document.getElementById('rep-profile-name').textContent = rep.name;
  document.getElementById('rep-profile-note').textContent = rep.note;

  // YTD Strip
  const ytd = computeRepYTD(rep);
  const strip = document.getElementById('rep-ytd-strip');
  if (ytd) {
    strip.innerHTML = `
      <div class="ytd-item">
        <div class="ytd-label">Actual Sales (YTD)</div>
        <div class="ytd-val">${fmt(ytd.salesValue)} <span style="font-size:12px;color:var(--gold);">EGP</span></div>
        <div class="ytd-unit">${fmt(ytd.salesUnits)} units sold</div>
      </div>
      <div class="ytd-item">
        <div class="ytd-label">Quota Target (YTD)</div>
        <div class="ytd-val">${fmt(ytd.targetValue)} <span style="font-size:12px;color:var(--text-muted);">EGP</span></div>
        <div class="ytd-unit">${fmt(ytd.targetUnits)} units target</div>
      </div>
      <div class="ytd-item">
        <div class="ytd-label">Value Deficit / Surplus</div>
        <div class="ytd-val">${renderDeficitVal(ytd.targetValue, ytd.salesValue)}</div>
        <div class="ytd-unit">Net annual financial variance</div>
      </div>
      <div class="ytd-item">
        <div class="ytd-label">Unit Deficit / Surplus</div>
        <div class="ytd-val">${renderDeficitUnit(ytd.targetUnits, ytd.salesUnits)}</div>
        <div class="ytd-unit">Net physical units gap</div>
      </div>
      <div class="ytd-item">
        <div class="ytd-label">Sales Points</div>
        <div class="ytd-val">${fmt(ytd.salesPoints)} pts</div>
        <div class="ytd-unit">Target: ${fmt(ytd.targetPoints)} pts</div>
      </div>
      <div class="ytd-badge-box">
        <div class="ytd-badge-label">YTD Fulfillment</div>
        <div class="ytd-badge-val" style="color:${ytd.ratio >= 100 ? '#4ade80' : ytd.ratio >= 70 ? '#fbbf24' : '#f87171'};">
          ${fmtPct(ytd.ratio)}
        </div>
      </div>
    `;
  }

  // TABS & PANELS
  const tabsNav = document.getElementById('rep-tabs-nav');
  const panelsContainer = document.getElementById('rep-panels-container');
  tabsNav.innerHTML = '';
  panelsContainer.innerHTML = '';

  const tabs = [
    { id: 'tab-YTD', label: '📊 Full Year Cumulative (YTD)', isYTD: true },
    { id: 'tab-Q1',  label: 'Quarter 1 (Q1)', q: 'Q1' },
    { id: 'tab-Q2',  label: 'Quarter 2 (Q2)', q: 'Q2' },
    { id: 'tab-Q3',  label: 'Quarter 3 (Q3)', q: 'Q3' },
    { id: 'tab-Q4',  label: 'Quarter 4 (Q4 Entry)', isQ4: true }
  ];

  tabs.forEach(t => {
    const isQ1Disabled = rep.startQ === 2 && t.q === 'Q1';
    const btn = document.createElement('button');
    btn.className = 'tab-btn' + (t.isQ4 ? ' q4-tab' : '') + (isQ1Disabled ? ' disabled' : '');
    btn.innerHTML = isQ1Disabled ? 'Q1 (Not Joined Yet)' : t.label;
    btn.dataset.tab = t.id;
    if (!isQ1Disabled) {
      btn.onclick = () => switchTab(t.id);
    }
    tabsNav.appendChild(btn);

    // Panel
    const panel = document.createElement('div');
    panel.className = 'tab-panel';
    panel.id = t.id;

    if (t.isYTD) {
      if (ytd) {
        const prodList = PRODUCTS.map(p => ytd.productsYTD[p.id]);
        panel.innerHTML = buildProductsTable(
          'Annual Cumulative Product Performance (YTD 2026)',
          'Consolidated quarterly results with net deficit and surplus per insulin product',
          prodList,
          ytd
        );
      }
    } else if (t.isQ4) {
      panel.innerHTML = buildQ4Form(rep);
    } else {
      const qData = rep.quarters && rep.quarters[t.q];
      if (isQ1Disabled) {
        panel.innerHTML = `
          <div class="card" style="padding:48px;text-align:center;color:var(--text-muted);">
            <div style="font-size:42px;margin-bottom:12px;">📅</div>
            <div style="font-size:17px;font-weight:800;color:#ffffff;">Representative was not with the company in Q1</div>
            <div style="font-size:13px;margin-top:6px;">Official start date was in Quarter 2 (Q2 2026)</div>
          </div>
        `;
      } else if (qData) {
        panel.innerHTML = buildProductsTable(
          `Product Sales & Quota Breakdown — ${t.q} 2026`,
          `Units, revenue in EGP, points, and deficit evaluation for ${t.q}`,
          qData.products,
          qData.total
        );
      }
    }
    panelsContainer.appendChild(panel);
  });

  // Activate tab
  let initialTab = targetTabId || 'tab-YTD';
  switchTab(initialTab);

  setTimeout(() => renderRepCharts(rep), 80);
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.tab === tabId);
  });
  document.querySelectorAll('.tab-panel').forEach(p => {
    p.classList.toggle('active', p.id === tabId);
  });
}

/* ── CHARTS RENDERING ── */
function renderRepCharts(rep) {
  destroyCharts();

  const ytd = computeRepYTD(rep);
  if (!ytd) return;

  // Chart 1: Bar chart of Products Sales vs Target Value YTD
  const barCtx = document.getElementById('repBarChart').getContext('2d');
  const labels = PRODUCTS.map(p => p.name);
  const salesVals  = PRODUCTS.map(p => ytd.productsYTD[p.id]?.salesValue || 0);
  const targetVals = PRODUCTS.map(p => ytd.productsYTD[p.id]?.targetValue || 0);

  barChartInstance = new Chart(barCtx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Actual Sales (EGP)',
          data: salesVals,
          backgroundColor: '#f59e0b',
          borderRadius: 6,
          borderSkipped: false
        },
        {
          label: 'Target Quota (EGP)',
          data: targetVals,
          backgroundColor: '#3b82f6',
          borderRadius: 6,
          borderSkipped: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', weight: '700' } } },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${fmt(ctx.parsed.y)} EGP`
          }
        }
      },
      scales: {
        y: {
          ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' }, callback: v => fmt(v) },
          grid: { color: 'rgba(255,255,255,0.06)' }
        },
        x: {
          ticks: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', weight: '600' } },
          grid: { display: false }
        }
      }
    }
  });

  // Chart 2: Line chart Quarterly progression
  const lineCtx = document.getElementById('repLineChart').getContext('2d');
  const quartersList = ['Q1', 'Q2', 'Q3', 'Q4'];
  const lineLabels = [];
  const lineSales = [];
  const lineTargets = [];

  quartersList.forEach(q => {
    if (q === 'Q4') {
      const q4 = loadQ4(rep.key);
      if (q4 && q4.total) {
        lineLabels.push('Q4 (Entered)');
        lineSales.push(q4.total.salesValue);
        lineTargets.push(q4.total.targetValue);
      }
    } else {
      const qd = rep.quarters && rep.quarters[q];
      if (qd && qd.total) {
        lineLabels.push(q);
        lineSales.push(qd.total.salesValue);
        lineTargets.push(qd.total.targetValue);
      }
    }
  });

  lineChartInstance = new Chart(lineCtx, {
    type: 'line',
    data: {
      labels: lineLabels,
      datasets: [
        {
          label: 'Quarterly Sales (EGP)',
          data: lineSales,
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          tension: 0.35,
          borderWidth: 3,
          pointRadius: 6,
          pointBackgroundColor: '#f59e0b',
          fill: true
        },
        {
          label: 'Quarterly Target (EGP)',
          data: lineTargets,
          borderColor: '#10b981',
          backgroundColor: 'transparent',
          borderDash: [6, 4],
          borderWidth: 2.5,
          pointRadius: 6,
          pointBackgroundColor: '#10b981',
          tension: 0.35
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', weight: '700' } } },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${fmt(ctx.parsed.y)} EGP`
          }
        }
      },
      scales: {
        y: {
          ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' }, callback: v => fmt(v) },
          grid: { color: 'rgba(255,255,255,0.06)' }
        },
        x: {
          ticks: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', weight: '600' } },
          grid: { color: 'rgba(255,255,255,0.06)' }
        }
      }
    }
  });
}

/* ── NAVIGATION ── */
function showHome() {
  destroyCharts();
  document.getElementById('view-rep').classList.remove('active');
  document.getElementById('view-home').classList.add('active');
  document.getElementById('back-btn').classList.remove('visible');
  renderHome();
}

/* ── INIT ── */
document.addEventListener('DOMContentLoaded', () => {
  const now = new Date();
  document.getElementById('topbar-date').textContent =
    now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  renderHome();
});
</script>
</body>
</html>
'''

full_html = HTML_CONTENT.replace('__LOGO_B64__', logo_b64)
full_html = full_html.replace('__PRODUCTS_JSON__', json.dumps(PRODUCTS, ensure_ascii=False, indent=2))
full_html = full_html.replace('__REPS_JSON__', json.dumps(REPS_EN, ensure_ascii=False, indent=2))

output_path = r"C:\Users\ALMadina\.gemini\antigravity\scratch\delta-team-dashboard\index.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(full_html)

print("English Black & Yellow Dashboard built successfully! File size:", len(full_html), "bytes")
