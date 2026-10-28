import json, os

with open(r'C:\Users\ALMadina\.gemini\antigravity\scratch\delta-team-dashboard\logo_b64.txt', 'r') as f:
    logo_b64 = f.read().strip()

from data import PRODUCTS, REPS_DATA

REPS_EN = []
for r in REPS_DATA:
    rep_copy = dict(r)
    if rep_copy.get("startQ") == 2:
        rep_copy["note"] = "Joined the team in Q2 — No Q1 records available"
    elif rep_copy.get("startQ") == 3:
        rep_copy["note"] = "Joined the team in Q3 — No Q1 or Q2 records available"
    elif rep_copy.get("noData"):
        rep_copy["note"] = "Pending Data / Onboarding"
    else:
        rep_copy["note"] = "Medical Representative — Delta Team (EVA Insulin 2026)"
    
    if rep_copy.get("quarters"):
        for q, qdata in rep_copy["quarters"].items():
            if qdata and "products" in qdata:
                for p in qdata["products"]:
                    if p.get("note") == "محسوب من السعر الموحد":
                        p["note"] = "Standard pricing"
                    elif p.get("note") == "مبيعات بدون تارجت":
                        p["note"] = "Sales without quota"
    REPS_EN.append(rep_copy)

HTML_CONTENT = r'''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover">
<title>EVA INSULIN | Delta Team — Sales Dashboard 2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<!-- Microsoft Authentication Library (MSAL Browser) -->
<script src="https://cdn.jsdelivr.net/npm/@azure/msal-browser@2.38.0/lib/msal-browser.min.js"></script>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:             #f8fafc;
    --surface:        #ffffff;
    --surface-alt:    #f1f5f9;
    --border:         #e2e8f0;
    --border-dark:    #cbd5e1;
    
    /* EVA Yellow & Black Brand Identity */
    --black:          #090c10;
    --dark:           #1e293b;
    --gold:           #f59e0b;
    --gold-light:     #fef3c7;
    --gold-dark:      #b45309;
    --gold-text:      #92400e;
    
    /* High contrast text */
    --text-primary:   #0f172a;
    --text-secondary: #475569;
    --text-muted:     #64748b;
    
    /* Status indicators */
    --green-bg:       #dcfce7;
    --green-text:     #15803d;
    --green-border:   #86efac;
    
    --red-bg:         #fee2e2;
    --red-text:       #b91c1c;
    --red-border:     #fca5a5;
    
    --orange-bg:      #ffedd5;
    --orange-text:    #c2410c;
    --orange-border:  #fdba74;

    --header-h:       74px;
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
    background: #090c12;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 32px;
    border-bottom: 3px solid var(--gold);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  }
  .brand { display: flex; align-items: center; gap: 16px; cursor: pointer; text-decoration: none; }
  .brand-logo-img {
    height: 50px; border-radius: 8px; border: 1px solid rgba(245, 158, 11, 0.4);
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    background: #000;
  }
  .brand-titles { display: flex; flex-direction: column; }
  .brand-name {
    color: #ffffff; font-weight: 900; font-size: 20px; letter-spacing: 0.5px;
    display: flex; align-items: center; gap: 10px; line-height: 1.1;
  }
  .brand-tag {
    background: var(--gold); color: #000000; font-size: 11px; font-weight: 900;
    padding: 2px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.5px;
  }
  .brand-sub { color: #94a3b8; font-size: 12px; font-weight: 500; margin-top: 2px; }

  .topbar-right { display: flex; align-items: center; gap: 14px; }

  /* ── USER PROFILE PILL IN TOPBAR ── */
  .user-profile-pill {
    display: none; align-items: center; gap: 10px;
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15);
    padding: 4px 12px 4px 6px; border-radius: 24px;
    color: #f1f5f9; font-size: 12px; font-weight: 600;
  }
  .user-avatar-mini {
    width: 28px; height: 28px; border-radius: 50%;
    background: var(--gold); color: #090c10;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 11px;
  }
  .btn-signout {
    background: none; border: none; color: #94a3b8; font-size: 11.5px;
    cursor: pointer; font-weight: 700; padding: 2px 6px; border-radius: 4px;
    transition: all 0.2s; font-family: inherit; margin-left: 4px;
  }
  .btn-signout:hover { color: #f87171; background: rgba(239, 68, 68, 0.1); }

  /* ── MICROSOFT AUTHENTICATION & LOGIN GATE ── */
  #auth-overlay {
    position: fixed; inset: 0; z-index: 10000;
    background: radial-gradient(circle at 50% 30%, #1e293b 0%, #090c12 70%);
    display: none; align-items: center; justify-content: center;
    padding: 24px;
  }
  .auth-card {
    background: #ffffff;
    border-radius: 20px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.1);
    width: 100%;
    max-width: 480px;
    overflow: hidden;
    text-align: center;
    position: relative;
    animation: fadeIn 0.3s ease-out;
  }
  .auth-header {
    background: #090c12;
    padding: 36px 32px 28px;
    border-bottom: 3px solid var(--gold);
    display: flex; flex-direction: column; align-items: center; gap: 12px;
  }
  .auth-logo {
    height: 52px; border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  }
  .auth-header h2 {
    color: #ffffff; font-size: 20px; font-weight: 800; letter-spacing: -0.3px;
  }
  .auth-header p {
    color: #94a3b8; font-size: 13px; font-weight: 500;
  }
  .auth-body {
    padding: 30px 28px 26px;
    display: flex; flex-direction: column; gap: 18px;
  }
  .auth-domain-badge {
    display: inline-flex; align-items: center; justify-content: center; gap: 8px;
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.3);
    color: #92400e; font-size: 12.5px; font-weight: 700;
    padding: 8px 16px; border-radius: 30px;
  }
  .btn-ms-login {
    display: flex; align-items: center; justify-content: center; gap: 12px;
    width: 100%; padding: 14px 20px;
    background: #0f172a; color: #ffffff;
    border: 1.5px solid #1e293b; border-radius: 12px;
    font-size: 14.5px; font-weight: 700;
    cursor: pointer; transition: all 0.2s;
    font-family: inherit;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.2);
  }
  .btn-ms-login:hover {
    background: #000000; border-color: var(--gold);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(245, 158, 11, 0.25);
  }
  .auth-alert {
    display: none; padding: 12px 16px; border-radius: 10px; font-size: 12.5px;
    text-align: left; line-height: 1.45;
  }
  .auth-alert.error {
    display: block; background: #fee2e2; border: 1px solid #fca5a5; color: #991b1b;
  }
  .auth-alert.info {
    display: block; background: #e0f2fe; border: 1px solid #bae6fd; color: #075985;
  }
  .auth-config-toggle {
    background: none; border: none; color: #64748b; font-size: 12px; font-weight: 600;
    cursor: pointer; text-decoration: underline; padding: 4px; font-family: inherit;
  }
  .auth-config-panel {
    display: none; text-align: left; background: var(--surface-alt);
    border: 1px solid var(--border); border-radius: 10px; padding: 14px;
    font-size: 12px;
  }
  .auth-config-panel.active { display: block; }
  .auth-config-panel input {
    width: 100%; padding: 8px 10px; border: 1px solid var(--border-dark);
    border-radius: 6px; font-size: 12px; font-family: monospace; margin: 4px 0 10px;
  }

  .topbar-date {
    color: #cbd5e1; font-size: 12px; font-weight: 600;
    background: rgba(255,255,255,0.08); padding: 7px 16px; border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.15);
  }
  #back-btn {
    display: none; align-items: center; gap: 8px;
    background: var(--gold); color: #000000; padding: 9px 20px;
    border-radius: 8px; border: none; cursor: pointer; font-family: inherit;
    font-size: 13.5px; font-weight: 800; transition: all 0.2s;
    box-shadow: 0 2px 10px rgba(245, 158, 11, 0.35);
  }
  #back-btn:hover {
    background: #ffffff; color: #000000; transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
  }
  #back-btn.visible { display: flex; }
  .back-text-short { display: none; }
  .back-text-full { display: inline; }

  /* ── MAIN CONTAINER ── */
  #main { padding: 32px 32px; max-width: 1480px; margin: 0 auto; width: 100%; }

  .view { display: none; }
  .view.active { display: block; animation: fadeIn 0.25s ease; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

  /* ── HERO BANNER / PAGE TITLE ── */
  .page-title {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 28px; flex-wrap: wrap; gap: 16px;
    padding-bottom: 20px; border-bottom: 1px solid var(--border);
  }
  .title-content { display: flex; align-items: center; gap: 16px; }
  .title-badge-icon {
    width: 52px; height: 52px; border-radius: 14px;
    background: #090c12; color: var(--gold); border: 2px solid var(--gold);
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; font-weight: 900;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.25);
  }
  .page-title h1 {
    font-size: 24px; font-weight: 800; color: var(--text-primary); letter-spacing: -0.3px;
  }
  .page-title .subtitle { font-size: 13.5px; color: var(--text-secondary); margin-top: 3px; }

  /* ── STAT CARDS GRID ── */
  .stat-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(215px, 1fr));
    gap: 16px; margin-bottom: 32px;
  }
  .stat-card {
    background: var(--surface); border-radius: 14px;
    padding: 20px 22px; border: 1px solid var(--border);
    position: relative; overflow: hidden;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  }
  .stat-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3.5px;
    background: var(--gold);
  }
  .stat-card:hover {
    transform: translateY(-3px); border-color: var(--gold);
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
  }
  .stat-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
  .stat-label { font-size: 11.5px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
  .stat-icon { font-size: 20px; }
  .stat-val { font-size: 24px; font-weight: 900; color: var(--text-primary); letter-spacing: -0.3px; }
  .stat-sub { font-size: 12px; color: var(--text-secondary); margin-top: 5px; font-weight: 500; }

  /* ── TEAM GRID ── */
  .team-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
  }
  .rep-card {
    background: var(--surface); border-radius: 16px;
    padding: 24px; cursor: pointer;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    border: 1px solid var(--border);
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative; overflow: hidden;
    display: flex; flex-direction: column; justify-content: space-between;
  }
  .rep-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3.5px;
    background: var(--gold);
  }
  .rep-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.09);
    border-color: var(--gold);
  }
  .rep-card.no-data { cursor: default; opacity: 0.75; }
  .rep-card.no-data::before { background: var(--border-dark); }
  .rep-card.no-data:hover {
    transform: none; box-shadow: 0 2px 10px rgba(0,0,0,0.04); border-color: var(--border);
  }

  .rep-card-header { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
  .rep-avatar {
    width: 48px; height: 48px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; font-weight: 900; color: #000000; flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    background: var(--gold);
  }
  .rep-card-title { font-size: 17.5px; font-weight: 800; color: var(--text-primary); }
  .rep-card-badge {
    display: inline-block; font-size: 10px; font-weight: 800;
    padding: 2px 9px; border-radius: 4px; margin-top: 3px;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .badge-active { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }
  .badge-nodata { background: var(--surface-alt); color: var(--text-muted); border: 1px solid var(--border); }
  .badge-q2start { background: var(--orange-bg); color: var(--orange-text); border: 1px solid var(--orange-border); }

  .rep-card-kpi {
    background: var(--surface-alt); border-radius: 12px; padding: 14px 16px;
    margin-bottom: 16px; border: 1px solid var(--border);
  }
  .kpi-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .kpi-row:last-child { margin-bottom: 0; }
  .kpi-row-stacked {
    display: flex; flex-direction: column; gap: 4px; margin-bottom: 8px;
    padding-top: 6px; border-top: 1px dashed var(--border);
  }
  .prod-unit-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 4px 8px;
    background: #ffffff; padding: 6px 10px; border-radius: 6px;
    border: 1px solid var(--border); font-size: 11px;
  }
  .prod-unit-item {
    display: flex; justify-content: space-between; align-items: center;
  }
  .kpi-label { font-size: 12px; color: var(--text-secondary); font-weight: 600; }
  .kpi-value { font-size: 14px; font-weight: 800; color: var(--text-primary); }

  .progress-wrap { margin-bottom: 16px; }
  .progress-label { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; font-weight: 700; color: var(--text-secondary); }
  .progress-bar { height: 9px; background: #e2e8f0; border-radius: 6px; overflow: hidden; }
  .progress-fill { height: 100%; border-radius: 6px; transition: width 0.6s ease; }

  .rep-card-footer {
    display: flex; justify-content: space-between; align-items: center;
    padding-top: 14px; border-top: 1px solid var(--border);
  }
  .quarters-pills { display: flex; gap: 6px; }
  .q-pill {
    font-size: 10.5px; font-weight: 800; padding: 3px 9px; border-radius: 4px;
    text-transform: uppercase; letter-spacing: 0.3px;
  }
  .q-pill.available { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
  .q-pill.missing   { background: #f1f5f9; color: #94a3b8; border: 1px solid var(--border); }
  .q-pill.entered   { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }
  .rep-card-arrow   { color: var(--text-primary); font-size: 13px; font-weight: 800; display: flex; align-items: center; gap: 4px; }
  .rep-card:hover .rep-card-arrow { color: var(--gold-dark); }

  /* ── REP VIEW ── */
  .rep-header-bar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 24px; flex-wrap: wrap; gap: 16px;
  }
  .rep-profile { display: flex; align-items: center; gap: 18px; }
  .rep-profile-name { font-size: 26px; font-weight: 900; color: var(--text-primary); letter-spacing: -0.3px; }
  .rep-profile-note { font-size: 13.5px; color: var(--text-secondary); margin-top: 4px; font-weight: 500; }

  /* YTD STRIP */
  .ytd-strip {
    background: #090c12; color: #ffffff;
    border-radius: 16px; padding: 22px 30px; margin-bottom: 26px;
    display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)) auto;
    gap: 20px; align-items: center;
    border-bottom: 3px solid var(--gold);
    box-shadow: 0 4px 18px rgba(0,0,0,0.1);
  }
  .ytd-item .ytd-label { font-size: 11.5px; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
  .ytd-item .ytd-val   { font-size: 22px; font-weight: 900; color: #ffffff; }
  .ytd-item .ytd-unit  { font-size: 11.5px; color: #cbd5e1; margin-top: 3px; font-weight: 500; }
  .ytd-badge-box {
    text-align: center; background: rgba(255,255,255,0.08); padding: 14px 26px;
    border-radius: 12px; border: 1px solid rgba(255,255,255,0.15);
  }
  .ytd-badge-label { font-size: 11px; color: #cbd5e1; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
  .ytd-badge-val   { font-size: 28px; font-weight: 900; }

  /* TABS */
  .tabs-nav {
    display: flex; gap: 8px; margin-bottom: 22px; flex-wrap: wrap;
    background: var(--surface); padding: 6px; border-radius: 12px;
    border: 1px solid var(--border); width: fit-content;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
  }
  .tab-btn {
    padding: 10px 22px; border-radius: 8px; border: none;
    background: transparent; cursor: pointer; font-family: inherit;
    font-size: 13.5px; font-weight: 700; color: var(--text-secondary);
    transition: all 0.2s; display: flex; align-items: center; gap: 8px;
  }
  .tab-btn:hover { color: var(--text-primary); background: var(--surface-alt); }
  .tab-btn.active {
    background: #090c12; color: #ffffff; font-weight: 800;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }
  .tab-btn.q4-tab { color: var(--gold-dark); background: var(--gold-light); }
  .tab-btn.q4-tab.active { background: var(--gold); color: #000000; font-weight: 900; }
  .tab-btn.disabled { opacity: 0.4; cursor: not-allowed; pointer-events: none; }

  .tab-panel { display: none; }
  .tab-panel.active { display: block; animation: fadeIn 0.2s ease; }

  /* ── TABLES ── */
  .card {
    background: var(--surface); border-radius: 16px;
    border: 1px solid var(--border); box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    overflow: hidden; margin-bottom: 26px;
  }
  .card-header {
    padding: 18px 24px; background: #ffffff;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
  }
  .card-header h3 { font-size: 16px; font-weight: 800; color: var(--text-primary); display: flex; align-items: center; gap: 10px; }
  .card-header-sub { font-size: 12px; color: var(--text-secondary); font-weight: 600; }

  .table-scroll { overflow-x: auto; width: 100%; }
  table.data-table {
    width: 100%; border-collapse: separate; border-spacing: 0;
    font-size: 13px; text-align: left; min-width: 1040px;
  }
  table.data-table th {
    background: #0f172a; color: #ffffff; font-weight: 700;
    padding: 13px 14px; font-size: 11px; white-space: nowrap;
    border-bottom: 2px solid #000000; text-transform: uppercase; letter-spacing: 0.4px;
  }
  table.data-table th.th-grp-unit  { background: #1e3a8a; color: #ffffff; }
  table.data-table th.th-grp-val   { background: #0f172a; color: #fbbf24; }
  table.data-table th.th-grp-pts   { background: #14532d; color: #ffffff; }
  table.data-table th.th-grp-ratio { background: #090c10; text-align: center; }

  table.data-table td {
    padding: 13px 14px; border-bottom: 1px solid var(--border);
    white-space: nowrap; vertical-align: middle; color: var(--text-primary);
  }
  table.data-table tbody tr:hover td { background: #f8fafc; }

  .prod-title { font-weight: 800; color: var(--text-primary); font-size: 13.5px; line-height: 1.3; }
  .prod-code  { font-size: 11px; color: var(--text-muted); font-weight: 600; font-family: monospace; }
  .prod-tag   { font-size: 10px; padding: 2px 7px; border-radius: 4px; font-weight: 700; display: inline-block; margin-top: 3px; }
  .tag-est    { background: var(--gold-light); color: var(--gold-dark); border: 1px solid var(--orange-border); }

  /* DEFICIT & SURPLUS BADGES */
  .deficit-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3.5px 10px; border-radius: 6px; font-size: 12px; font-weight: 800;
  }
  .deficit-red {
    background: var(--red-bg); color: var(--red-text); border: 1px solid var(--red-border);
  }
  .deficit-green {
    background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border);
  }
  .ratio-badge {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 12px; font-weight: 800; text-align: center;
  }
  .ratio-green  { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }
  .ratio-orange { background: var(--orange-bg); color: var(--orange-text); border: 1px solid var(--orange-border); }
  .ratio-red    { background: var(--red-bg); color: var(--red-text); border: 1px solid var(--red-border); }

  /* TOTAL ROW */
  tr.row-total td {
    background: #0f172a !important; font-weight: 900;
    color: #ffffff !important; font-size: 13.5px;
    border-top: 2px solid var(--gold); border-bottom: none;
  }
  tr.row-total td:first-child { color: var(--gold) !important; }

  /* ── CHART FILTERS ── */
  .chart-filters { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
  .filter-group { display: flex; align-items: center; gap: 6px; }
  .filter-group label { font-size: 11px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.4px; }
  .chart-select {
    padding: 6px 12px; border-radius: 8px; border: 1px solid var(--border-dark);
    font-family: inherit; font-size: 12px; font-weight: 700; color: var(--text-primary);
    background: #ffffff; cursor: pointer; transition: all 0.2s;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }
  .chart-select:hover { border-color: var(--gold); }
  .chart-select:focus { outline: none; border-color: var(--gold); box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2); }

  /* ── CHARTS ROW ── */
  .charts-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
    gap: 20px; margin-bottom: 26px;
  }
  .chart-box { padding: 20px; height: 330px; position: relative; }

  /* ── Q4 FORM ── */
  .q4-wrapper { padding: 26px; }
  .q4-alert {
    background: var(--gold-light); border: 1px solid var(--orange-border); border-radius: 12px;
    padding: 14px 18px; margin-bottom: 24px; display: flex; align-items: center; gap: 12px;
  }
  .q4-alert-text { font-size: 13px; color: var(--gold-text); font-weight: 700; }
  .q4-prod-card {
    background: #ffffff; border: 1px solid var(--border); border-radius: 14px;
    margin-bottom: 20px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.03);
  }
  .q4-prod-header {
    background: #f8fafc; padding: 13px 20px; font-weight: 800;
    font-size: 14px; color: var(--text-primary); display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid var(--border);
  }
  .q4-inputs-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px; padding: 20px;
  }
  .q4-field label {
    display: block; font-size: 11.5px; font-weight: 700; color: var(--text-secondary); margin-bottom: 6px;
    text-transform: uppercase; letter-spacing: 0.3px;
  }
  .q4-field input {
    width: 100%; padding: 10px 12px; border: 1px solid var(--border-dark);
    border-radius: 8px; font-family: inherit; font-size: 13.5px;
    font-weight: 700; color: var(--text-primary); background: #ffffff;
    transition: all 0.2s;
  }
  .q4-field input:focus {
    outline: none; border-color: var(--gold);
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.25);
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
    background: #090c12; color: var(--gold); border: 2px solid var(--gold);
    box-shadow: 0 4px 14px rgba(0,0,0,0.15);
  }
  .btn-save:hover {
    background: var(--gold); color: #000000; transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(245, 158, 11, 0.35);
  }
  .btn-clear {
    background: #ffffff; color: var(--red-text); border: 1px solid var(--red-border);
  }
  .btn-clear:hover { background: var(--red-bg); }
  .save-toast {
    display: none; padding: 10px 18px; border-radius: 8px; font-size: 13px;
    font-weight: 700; background: var(--green-bg); color: var(--green-text);
    border: 1px solid var(--green-border); align-items: center; gap: 8px;
  }
  .save-toast.visible { display: flex; animation: fadeIn 0.2s; }

  .upload-dropzone {
    border: 2px dashed var(--gold); border-radius: 14px;
    background: var(--surface-alt); padding: 32px 20px; text-align: center;
    cursor: pointer; transition: all 0.2s;
  }
  .upload-dropzone:hover, .upload-dropzone.dragover {
    background: var(--gold-light); border-color: var(--gold-dark);
    transform: scale(1.01);
  }

  .mobile-table-hint {
    display: none; font-size: 11px; color: var(--text-muted); background: var(--surface-alt);
    padding: 8px 14px; border-bottom: 1px solid var(--border); font-weight: 700;
    text-align: center; align-items: center; justify-content: center; gap: 6px;
  }

  /* ── ADVANCED MOBILE & TABLET OPTIMIZATIONS ── */
  @media (max-width: 900px) {
    .charts-grid { grid-template-columns: 1fr; }
  }

  @media (max-width: 768px) {
    :root {
      --header-h: 62px;
    }
    
    body {
      font-size: 13px;
      -webkit-tap-highlight-color: transparent;
    }

    #topbar {
      padding: 0 12px;
      height: var(--header-h);
    }
    .brand { gap: 10px; }
    .brand-logo-img { height: 38px; border-radius: 6px; }
    .brand-name { font-size: 15px; gap: 6px; }
    .brand-tag { font-size: 9px; padding: 2px 6px; }
    .brand-sub { display: none; }
    .topbar-date { display: none; }
    #back-btn { padding: 6px 12px; font-size: 12px; }
    #back-btn span.back-text-full { display: none; }

    #main {
      padding: 14px 12px 36px 12px;
    }

    .page-title {
      margin-bottom: 16px;
      padding-bottom: 12px;
      gap: 12px;
    }
    .title-content { gap: 12px; }
    .title-badge-icon {
      width: 42px; height: 42px; font-size: 20px; border-radius: 10px;
    }
    .page-title h1 { font-size: 18px; }
    .page-title .subtitle { font-size: 12px; }

    /* STAT CARDS: 2 COLUMNS ON MOBILE */
    .stat-grid {
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 20px;
    }
    .stat-card {
      padding: 12px 14px;
      border-radius: 12px;
    }
    .stat-header { margin-bottom: 6px; }
    .stat-label { font-size: 9.5px; letter-spacing: 0.2px; }
    .stat-icon { font-size: 16px; }
    .stat-val { font-size: 17px; }
    .stat-sub { font-size: 10.5px; margin-top: 3px; }

    /* TEAM GRID CARDS */
    .team-grid {
      grid-template-columns: 1fr;
      gap: 14px;
    }
    .rep-card {
      padding: 16px;
      border-radius: 14px;
    }
    .rep-card-kpi {
      padding: 12px;
      margin-bottom: 12px;
    }
    .kpi-row { margin-bottom: 6px; }
    .kpi-label { font-size: 11.5px; }
    .kpi-value { font-size: 13px; }
    .prod-unit-grid {
      font-size: 10.5px;
      padding: 6px 8px;
    }
    .progress-wrap { margin-bottom: 12px; }
    .rep-card-footer { padding-top: 10px; }

    /* REP PROFILE VIEW */
    .rep-header-bar {
      margin-bottom: 16px;
      gap: 12px;
    }
    .rep-profile { gap: 12px; }
    #rep-avatar-large {
      width: 46px !important; height: 46px !important;
      font-size: 20px !important; border-radius: 12px !important;
    }
    .rep-profile-name { font-size: 20px; }
    .rep-profile-note { font-size: 12px; }

    /* YTD STRIP ON MOBILE */
    .ytd-strip {
      grid-template-columns: 1fr 1fr !important;
      padding: 14px 14px !important;
      gap: 12px !important;
      border-radius: 14px !important;
      margin-bottom: 18px !important;
    }
    .ytd-item .ytd-label { font-size: 10px !important; letter-spacing: 0.3px !important; margin-bottom: 2px !important; }
    .ytd-item .ytd-val { font-size: 17px !important; }
    .ytd-item .ytd-unit { font-size: 10.5px !important; }
    .ytd-badge-box {
      grid-column: span 2 !important;
      padding: 10px 16px !important;
      border-radius: 10px !important;
    }
    .ytd-badge-label { font-size: 10px !important; }
    .ytd-badge-val { font-size: 24px !important; }

    /* DEDICATED PER-PRODUCT UNITS SECTION */
    .unit-breakdown-card {
      padding: 14px 14px !important;
      margin-bottom: 18px !important;
    }
    .unit-prod-cards-grid {
      grid-template-columns: 1fr 1fr !important;
      gap: 10px !important;
    }
    .unit-prod-box {
      padding: 10px 12px !important;
      border-radius: 10px !important;
    }

    /* TABS BAR: SWIPEABLE HORIZONTAL PILL BAR */
    .tabs-nav {
      display: flex !important;
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      -webkit-overflow-scrolling: touch !important;
      width: 100% !important;
      scrollbar-width: none !important;
      padding: 5px !important;
      gap: 6px !important;
      margin-bottom: 16px !important;
      border-radius: 10px !important;
    }
    .tabs-nav::-webkit-scrollbar { display: none !important; }
    .tab-btn {
      white-space: nowrap !important;
      flex-shrink: 0 !important;
      padding: 8px 14px !important;
      font-size: 12px !important;
    }

    /* CHARTS ON MOBILE */
    .card-header {
      padding: 14px 16px;
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }
    .chart-filters {
      width: 100%;
      flex-direction: column;
      gap: 8px;
    }
    .filter-group {
      width: 100%;
      justify-content: space-between;
    }
    .chart-select {
      width: 55%;
      min-height: 38px;
      font-size: 12.5px;
    }
    .chart-box {
      height: 270px;
      padding: 10px;
    }

    /* TABLES ON MOBILE */

  .mobile-table-hint { display: flex; }
    .card {
      border-radius: 14px;
      margin-bottom: 18px;
    }
    table.data-table {
      font-size: 12px;
      min-width: 880px;
    }
    table.data-table th,
    table.data-table td {
      padding: 10px 10px;
    }
    .deficit-badge {
      font-size: 11px;
      padding: 3px 7px;
    }

    /* STICKY FIRST COLUMN ON MOBILE SWIPE */
    table.data-table th:first-child,
    table.data-table td:first-child {
      position: sticky;
      left: 0;
      z-index: 2;
      background: #ffffff;
      min-width: 130px !important;
      max-width: 150px !important;
      width: 140px !important;
      white-space: normal !important;
      word-break: break-word !important;
      box-shadow: 2px 0 6px rgba(0,0,0,0.08);
    }
    table.data-table thead tr:first-child th:first-child {
      background: #0f172a;
      z-index: 10;
    }
    table.data-table thead tr:nth-child(2) th:first-child {
      background: #0f172a;
      z-index: 10;
    }
    table.data-table tr.row-total td:first-child {
      background: #0f172a !important;
      z-index: 3;
    }
    table.data-table tbody tr:hover td:first-child {
      background: #f8fafc;
    }

    /* Q4 FORM ON MOBILE */
    .q4-wrapper { padding: 14px; }
    .q4-inputs-grid {
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      padding: 14px;
    }
    .q4-field input {
      font-size: 16px !important; /* Prevents auto zoom in iOS */
      padding: 9px 10px;
    }
    .q4-actions {
      flex-direction: column;
      gap: 10px;
    }
    .btn {
      width: 100%;
      justify-content: center;
      min-height: 44px;
    }
  }

  @media (max-width: 440px) {
    .unit-prod-cards-grid {
      grid-template-columns: 1fr !important;
    }
  }

  @media (max-width: 380px) {
    .stat-grid { grid-template-columns: 1fr !important; }
    .ytd-strip { grid-template-columns: 1fr !important; }
    .ytd-badge-box { grid-column: span 1 !important; }
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
    <div id="topbar-user-pill" class="user-profile-pill"></div>
    <div class="topbar-date" id="topbar-date"></div>
    <button id="back-btn" onclick="showHome()">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
      <span class="back-text-full">Team Overview</span>
      <span class="back-text-short">Back</span>
    </button>
  </div>
</header>

<!-- AUTHENTICATION OVERLAY / LOGIN GATE -->
<div id="auth-overlay">
  <div class="auth-card">
    <div class="auth-header">
      <img src="data:image/jpeg;base64,__LOGO_B64__" alt="EVA INSULIN" class="auth-logo">
      <h2>EVA Insulin Delta Team</h2>
      <p>Executive Sales Performance Portal</p>
    </div>
    <div class="auth-body">
      <div class="auth-domain-badge">
        <span>🔒</span> Restricted to <strong>@evapharma.com</strong> accounts
      </div>

      <div id="auth-alert" class="auth-alert"></div>

      <button id="btn-login-ms" class="btn-ms-login" onclick="loginWithMicrosoft()">
        <!-- Microsoft 4-Color Logo SVG -->
        <svg width="20" height="20" viewBox="0 0 21 21">
          <rect x="1" y="1" width="9" height="9" fill="#f25022"/>
          <rect x="11" y="1" width="9" height="9" fill="#7fba00"/>
          <rect x="1" y="11" width="9" height="9" fill="#00a4ef"/>
          <rect x="11" y="11" width="9" height="9" fill="#ffb900"/>
        </svg>
        <span>Sign in with Microsoft 365</span>
      </button>

      <!-- Instant Preview / Corporate Sign In Gate for @evapharma.com -->
      <div id="auth-quick-login-section" style="border-top: 1px solid var(--border); padding-top: 14px; margin-top: 4px;">
        <div style="font-size: 11.5px; color: var(--text-muted); margin-bottom: 8px;">
          Direct Corporate Sign In (Verification Gate):
        </div>
        <div style="display:flex; gap: 6px;">
          <input type="email" id="direct-email-input" placeholder="e.g. hady.mohamed@evapharma.com" onkeydown="if(event.key==='Enter') directEvaSignIn()" style="flex:1; padding: 8px 12px; border: 1.5px solid var(--border-dark); border-radius: 8px; font-size: 12.5px; font-family: inherit;">
          <button class="btn" onclick="directEvaSignIn()" style="padding: 8px 14px; font-size: 12px; background: var(--gold); color: #000; font-weight: 800; border: none; border-radius: 8px; cursor: pointer;">
            Enter &rarr;
          </button>
        </div>
      </div>

      <!-- Advanced Azure App Settings Toggle -->
      <div style="margin-top: 6px;">
        <button class="auth-config-toggle" onclick="toggleAuthConfigPanel()">
          ⚙️ Azure AD App Configuration (Client ID)
        </button>
        <div id="auth-config-panel" class="auth-config-panel">
          <label style="font-weight:700; color:var(--text-primary); display:block; margin-bottom:2px;">Azure App (Client) ID:</label>
          <input type="text" id="cfg-client-id" placeholder="e.g. 48ff9361-0f30-4367-a0b0-7cf26005dab6">
          
          <label style="font-weight:700; color:var(--text-primary); display:block; margin-bottom:2px;">Directory (Tenant) ID:</label>
          <input type="text" id="cfg-tenant-id" placeholder="organizations or EVA Tenant ID">
          
          <button class="btn" onclick="saveAzureConfig()" style="width:100%; background:#0f172a; color:#fff; padding:7px 10px; font-size:11.5px; font-weight:700; border-radius:6px; cursor:pointer;">
            Save Azure Settings
          </button>
        </div>
      </div>

      <div style="font-size: 11px; color: var(--text-muted); line-height: 1.4; margin-top: 4px;">
        This portal contains proprietary and confidential commercial performance data for EVA Pharma. Unauthorized access is strictly prohibited.
      </div>
    </div>
  </div>
</div>

<main id="main">

  <!-- VIEW: TEAM OVERVIEW -->
  <div id="view-home" class="view active">
    <div class="page-title">
      <div class="title-content">
        <div class="title-badge-icon">Δ</div>
        <div>
          <h1>EVA Insulin — Delta Team Performance (YTD 2026)</h1>
          <div class="subtitle">Executive sales tracking, quota achievement, and deficit monitoring across all representatives</div>
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

    <!-- UNITS BREAKDOWN CARD PER PRODUCT -->
    <div id="rep-unit-cards-container"></div>

    <!-- TABS -->
    <div class="tabs-nav" id="rep-tabs-nav"></div>

    <!-- PANELS CONTAINER -->
    <div id="rep-panels-container"></div>

    <!-- CHARTS -->
    <div class="charts-grid">
      <!-- BAR CHART CARD WITH FILTERS -->
      <div class="card">
        <div class="card-header">
          <div>
            <h3>📊 Sales vs Target Units by Product</h3>
            <div class="card-header-sub" id="barChartSub">Volume in Physical Units / Packs</div>
          </div>
          <div class="chart-filters">
            <div class="filter-group">
              <label>Quarter:</label>
              <select id="barQuarterFilter" class="chart-select" onchange="updateBarChart()">
                <option value="YTD">Full Year (YTD)</option>
                <option value="Q1">Quarter 1 (Q1)</option>
                <option value="Q2">Quarter 2 (Q2)</option>
                <option value="Q3">Quarter 3 (Q3)</option>
                <option value="Q4">Quarter 4 (Q4)</option>
              </select>
            </div>
            <div class="filter-group">
              <label>Product:</label>
              <select id="barProductFilter" class="chart-select" onchange="updateBarChart()">
                <option value="all">All Products</option>
              </select>
            </div>
          </div>
        </div>
        <div class="chart-box"><canvas id="repBarChart"></canvas></div>
      </div>

      <!-- LINE CHART CARD WITH PRODUCT FILTER -->
      <div class="card">
        <div class="card-header">
          <div>
            <h3>📈 Quarterly Units Progression vs Target</h3>
            <div class="card-header-sub" id="lineChartSub">Quarterly Units Trend (Q1 - Q4)</div>
          </div>
          <div class="chart-filters">
            <div class="filter-group">
              <label>Product:</label>
              <select id="lineProductFilter" class="chart-select" onchange="updateLineChart()">
                <option value="all">Total (All Products)</option>
              </select>
            </div>
          </div>
        </div>
        <div class="chart-box"><canvas id="repLineChart"></canvas></div>
      </div>
    </div>
  </div>

</main>

<script>
/* ── DATA DEFINITIONS ── */
const PRODUCTS = __PRODUCTS_JSON__;
let REPS = __REPS_JSON__; // Mutable for live cloud updates

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

/* ── SHORT PRODUCT NAME HELPER ── */
function getShortProdName(pid) {
  switch (Number(pid)) {
    case 1260: return 'Mix 70/30';
    case 1259: return 'Rapid';
    case 1251: return 'G. UPA';
    case 1110: return 'G. 100IU';
    default: return 'Product';
  }
}

/* ── DEFICIT FORMATTERS ── */
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

function renderDeficitUnitCompact(targetUnits, salesUnits) {
  if (targetUnits === null || salesUnits === null || targetUnits === undefined || salesUnits === undefined) {
    return '<span style="color:var(--text-muted);font-weight:500;">—</span>';
  }
  const diff = targetUnits - salesUnits;
  if (diff > 0.001) {
    return `<span class="deficit-badge deficit-red" style="padding:1px 5px;font-size:10px;letter-spacing:0;font-weight:700;">-${fmt(diff)}</span>`;
  } else if (diff <= -0.001) {
    return `<span class="deficit-badge deficit-green" style="padding:1px 5px;font-size:10px;letter-spacing:0;font-weight:700;">+${fmt(Math.abs(diff))}</span>`;
  } else {
    return `<span class="deficit-badge deficit-green" style="padding:1px 5px;font-size:10px;letter-spacing:0;font-weight:700;">0</span>`;
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
      <div class="stat-val">${fmt(totalSales)} <span style="font-size:12px;color:var(--gold-dark);font-weight:700;">EGP</span></div>
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
            <div class="rep-avatar" style="background:#e2e8f0;color:var(--text-muted);">${rep.name[0]}</div>
            <div>
              <div class="rep-card-title">${rep.name}</div>
              <span class="rep-card-badge badge-nodata">No Records Uploaded</span>
            </div>
          </div>
          <div style="text-align:center;padding:26px 0;color:var(--text-muted);">
            <div style="font-size:32px;margin-bottom:8px;opacity:0.4;">📁</div>
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
      const progressColor = ratio >= 100 ? 'background:#16a34a;' : ratio >= 70 ? 'background:var(--gold);' : 'background:#dc2626;';
      const badgeClass = (rep.startQ === 2 || rep.startQ === 3) ? 'badge-q2start' : 'badge-active';
      const badgeText  = rep.startQ === 2 ? 'Joined Q2' : rep.startQ === 3 ? 'Joined Q3' : 'Active (Q1 - Q3)';

      const qPills = ['Q1', 'Q2', 'Q3', 'Q4'].map(q => {
        if (q === 'Q4') {
          return q4saved ? `<span class="q-pill entered">Q4: Entered</span>` : `<span class="q-pill missing">Q4: Available</span>`;
        }
        if (rep.startQ && ((rep.startQ === 2 && q === 'Q1') || (rep.startQ === 3 && (q === 'Q1' || q === 'Q2')))) {
          return `<span class="q-pill missing">${q}: N/A</span>`;
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
              <span class="kpi-value">${ytd ? fmt(ytd.salesValue) : '—'} <span style="font-size:11px;color:var(--gold-dark);">EGP</span></span>
            </div>
            <div class="kpi-row">
              <span class="kpi-label">Target Quota (YTD):</span>
              <span class="kpi-value">${ytd ? fmt(ytd.targetValue) : '—'} <span style="font-size:11px;color:var(--text-muted);">EGP</span></span>
            </div>
            <div class="kpi-row">
              <span class="kpi-label">Deficit / Surplus:</span>
              <span>${ytd ? renderDeficitVal(ytd.targetValue, ytd.salesValue) : '—'}</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-label">Units Sold:</span>
              <span class="kpi-value">${ytd ? fmt(ytd.salesUnits) : '—'} units</span>
            </div>
            <div class="kpi-row-stacked">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span class="kpi-label" style="font-size:11.5px;color:var(--text-primary);font-weight:700;">Unit Deficit / Surplus (Per Product):</span>
              </div>
              <div class="prod-unit-grid">
                ${PRODUCTS.map(pr => {
                  const p = ytd && ytd.productsYTD ? ytd.productsYTD[pr.id] : null;
                  return `<div class="prod-unit-item"><span style="color:var(--text-muted);font-weight:600;">${getShortProdName(pr.id)}:</span> ${p ? renderDeficitUnitCompact(p.targetUnits, p.salesUnits) : '—'}</div>`;
                }).join('')}
              </div>
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
        <td><strong>${fmt(p.salesValue)}</strong> <span style="font-size:11px;color:var(--gold-dark);font-weight:700;">EGP</span></td>
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
      <div class="mobile-table-hint">👉 Swipe horizontally to view full table metrics (Units, Revenue & Points)</div>
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
          <span style="font-size:11.5px;color:var(--text-muted);font-family:monospace;font-weight:700;">${prod.code}</span>
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
        <div class="card-header-sub">Each representative can submit their Q4 numbers directly to the Google Sheet</div>
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
          <button class="btn btn-save" id="btnSaveQ4_${rep.key}" onclick="saveQ4Data('${rep.key}')">
            💾 Save & Sync to Google Sheets
          </button>
          <button class="btn btn-clear" onclick="clearQ4Data('${rep.key}')">
            🗑️ Clear Q4 Records
          </button>
          <div class="save-toast" id="toast-${rep.key}">
            ✅ Q4 data successfully saved and integrated!
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

async function saveQ4Data(repKey) {
  const saveBtn = document.getElementById(`btnSaveQ4_${repKey}`);
  if (saveBtn) { saveBtn.disabled = true; saveBtn.textContent = '⏳ Saving...'; }

  const repObj = REPS.find(r => r.key === repKey);
  const repName = repObj ? repObj.name : repKey;

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
    repKey, repName, quarter: 'Q4',
    products,
    total: {
      salesUnits: totalSalesUnits, targetUnits: totalTargetUnits,
      salesValue: totalSalesValue, targetValue: totalTargetValue,
      salesPoints: totalSalesPoints, targetPoints: totalTargetPoints,
      ratio: totalRatio
    }
  };

  // 1. Save locally
  saveQ4(repKey, q4Data);

  // 2. Sync to Google Sheets if connected
  const sheetsUrl = getSheetsUrl();
  if (sheetsUrl) {
    try {
      // Use GET with query string fallback for maximum CORS compatibility with Google Apps Script
      const payloadStr = encodeURIComponent(JSON.stringify(q4Data));
      const syncUrl = sheetsUrl + (sheetsUrl.includes('?') ? '&' : '?') + 'action=saveQ4&payload=' + payloadStr;
      await fetch(syncUrl, { mode: 'no-cors' });
      console.log('Dispatched Q4 save to Google Sheets live backend');
    } catch (e) {
      console.warn('Google Sheets cloud sync notice:', e);
    }
  }

  if (saveBtn) { saveBtn.disabled = false; saveBtn.textContent = '💾 Save & Sync to Google Sheets'; }

  const toast = document.getElementById(`toast-${repKey}`);
  if (toast) {
    toast.textContent = sheetsUrl ? '✅ Q4 data saved & synced to Google Sheets!' : '✅ Q4 data saved locally!';
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
        <div class="ytd-val">${fmt(ytd.targetValue)} <span style="font-size:12px;color:#94a3b8;">EGP</span></div>
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

  // UNITS BREAKDOWN CARDS PER PRODUCT
  const unitCardsContainer = document.getElementById('rep-unit-cards-container');
  if (unitCardsContainer && ytd) {
    unitCardsContainer.innerHTML = `
      <div class="card unit-breakdown-card" style="margin-bottom:24px;padding:20px 24px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px;">
          <div>
            <h4 style="font-size:14.5px;font-weight:800;color:var(--text-primary);display:flex;align-items:center;gap:8px;">
              <span>📦</span> Units Sold & Unit Deficit / Surplus per Product (YTD 2026)
            </h4>
            <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">Physical units performance and quota evaluation per individual insulin product</div>
          </div>
          <span style="font-size:11.5px;background:var(--surface-alt);border:1px solid var(--border);padding:4px 10px;border-radius:6px;font-weight:700;color:var(--text-secondary);">Per-Product Units Breakdown</span>
        </div>
        <div class="unit-prod-cards-grid" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(230px, 1fr));gap:14px;">
          ${PRODUCTS.map(prod => {
            const p = ytd.productsYTD[prod.id];
            const su = p ? p.salesUnits : null;
            const tu = p ? p.targetUnits : null;
            return `
              <div class="unit-prod-box" style="background:var(--surface-alt);border:1px solid var(--border);border-radius:12px;padding:14px 16px;">
                <div style="font-weight:800;font-size:13px;color:var(--text-primary);margin-bottom:2px;">${prod.name}</div>
                <div style="font-size:10.5px;color:var(--text-muted);font-family:monospace;margin-bottom:12px;font-weight:600;">${prod.code}</div>
                
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:12.5px;">
                  <span style="color:var(--text-secondary);font-weight:600;">Units Sold:</span>
                  <strong style="color:var(--text-primary);">${su !== null ? fmt(su) + ' u' : '—'}</strong>
                </div>
                
                <div style="display:flex;justify-content:space-between;margin-bottom:10px;font-size:12.5px;">
                  <span style="color:var(--text-secondary);font-weight:600;">Target Units:</span>
                  <span style="color:var(--text-muted);">${tu !== null ? fmt(tu) + ' u' : '—'}</span>
                </div>
                
                <div style="display:flex;justify-content:space-between;align-items:center;padding-top:10px;border-top:1px dashed var(--border);">
                  <span style="font-size:11.5px;color:var(--text-secondary);font-weight:700;">Unit Deficit:</span>
                  <span>${renderDeficitUnit(tu, su)}</span>
                </div>
              </div>
            `;
          }).join('')}
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
    const isQDisabled = rep.startQ && (
      (rep.startQ === 2 && t.q === 'Q1') ||
      (rep.startQ === 3 && (t.q === 'Q1' || t.q === 'Q2'))
    );
    const btn = document.createElement('button');
    btn.className = 'tab-btn' + (t.isQ4 ? ' q4-tab' : '') + (isQDisabled ? ' disabled' : '');
    btn.innerHTML = isQDisabled ? `${t.q} (Not Joined Yet)` : t.label;
    btn.dataset.tab = t.id;
    if (!isQDisabled) {
      btn.onclick = () => switchTab(t.id);
    }
    tabsNav.appendChild(btn);

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
      if (isQDisabled) {
        panel.innerHTML = `
          <div class="card" style="padding:48px;text-align:center;color:var(--text-muted);">
            <div style="font-size:42px;margin-bottom:12px;">📅</div>
            <div style="font-size:17px;font-weight:800;color:var(--text-primary);">Representative was not with the company in ${t.q}</div>
            <div style="font-size:13px;margin-top:6px;">Official start date was in Quarter ${rep.startQ} (Q${rep.startQ} 2026)</div>
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

/* ── CHARTS RENDERING & DYNAMIC FILTERS (IN UNITS) ── */
let currentRepForCharts = null;

function initChartFilterOptions() {
  const barProd = document.getElementById('barProductFilter');
  const lineProd = document.getElementById('lineProductFilter');
  if (barProd && barProd.options.length <= 1) {
    PRODUCTS.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.name;
      barProd.appendChild(opt);
    });
  }
  if (lineProd && lineProd.options.length <= 1) {
    PRODUCTS.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.name;
      lineProd.appendChild(opt);
    });
  }
}

function renderRepCharts(rep) {
  currentRepForCharts = rep;
  initChartFilterOptions();

  const barQFilter = document.getElementById('barQuarterFilter');
  if (barQFilter) {
    const q1Opt = barQFilter.querySelector('option[value="Q1"]');
    const q2Opt = barQFilter.querySelector('option[value="Q2"]');
    if (q1Opt) q1Opt.disabled = !!(rep.startQ && rep.startQ >= 2);
    if (q2Opt) q2Opt.disabled = !!(rep.startQ && rep.startQ >= 3);
  }

  updateBarChart();
  updateLineChart();
}

function updateBarChart() {
  if (!currentRepForCharts) return;
  const rep = currentRepForCharts;
  const qVal = document.getElementById('barQuarterFilter')?.value || 'YTD';
  const prodVal = document.getElementById('barProductFilter')?.value || 'all';

  if (barChartInstance) {
    barChartInstance.destroy();
    barChartInstance = null;
  }

  let prodSource = [];
  const ytd = computeRepYTD(rep);

  if (qVal === 'YTD') {
    if (ytd) {
      prodSource = PRODUCTS.map(p => ({
        pid: p.id,
        name: p.name,
        salesUnits: ytd.productsYTD[p.id]?.salesUnits || 0,
        targetUnits: ytd.productsYTD[p.id]?.targetUnits || 0
      }));
    }
  } else if (qVal === 'Q4') {
    const q4 = loadQ4(rep.key);
    if (q4 && q4.products) {
      prodSource = q4.products.map(p => ({
        pid: p.pid,
        name: PRODUCTS.find(pr => pr.id === p.pid)?.name || p.pid,
        salesUnits: p.salesUnits || 0,
        targetUnits: p.targetUnits || 0
      }));
    }
  } else {
    const qd = rep.quarters && rep.quarters[qVal];
    if (qd && qd.products) {
      prodSource = qd.products.map(p => ({
        pid: p.pid,
        name: PRODUCTS.find(pr => pr.id === p.pid)?.name || p.pid,
        salesUnits: p.salesUnits !== null ? p.salesUnits : 0,
        targetUnits: p.targetUnits !== null ? p.targetUnits : 0
      }));
    }
  }

  if (prodVal !== 'all') {
    const targetPid = parseInt(prodVal);
    prodSource = prodSource.filter(p => p.pid === targetPid);
  }

  const labels = prodSource.map(p => p.name);
  const salesUnits = prodSource.map(p => p.salesUnits);
  const targetUnits = prodSource.map(p => p.targetUnits);

  const subEl = document.getElementById('barChartSub');
  if (subEl) {
    subEl.textContent = `Showing ${qVal} volume breakdown for ${prodVal === 'all' ? 'all products' : 'selected product'}`;
  }

  const barCtx = document.getElementById('repBarChart').getContext('2d');
  barChartInstance = new Chart(barCtx, {
    type: 'bar',
    data: {
      labels: labels.length ? labels : ['No Data Available'],
      datasets: [
        {
          label: 'Units Sold (Actual)',
          data: salesUnits.length ? salesUnits : [0],
          backgroundColor: '#090c12',
          borderRadius: 6,
          borderSkipped: false
        },
        {
          label: 'Target Quota (Units)',
          data: targetUnits.length ? targetUnits : [0],
          backgroundColor: '#f59e0b',
          borderRadius: 6,
          borderSkipped: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#0f172a', font: { family: 'Plus Jakarta Sans', weight: '700' } } },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${fmt(ctx.parsed.y)} units`
          }
        }
      },
      scales: {
        y: {
          ticks: { color: '#64748b', font: { family: 'Plus Jakarta Sans' }, callback: v => fmt(v) + ' u' },
          grid: { color: '#f1f5f9' }
        },
        x: {
          ticks: { color: '#0f172a', font: { family: 'Plus Jakarta Sans', weight: '600' } },
          grid: { display: false }
        }
      }
    }
  });
}

function updateLineChart() {
  if (!currentRepForCharts) return;
  const rep = currentRepForCharts;
  const prodVal = document.getElementById('lineProductFilter')?.value || 'all';

  if (lineChartInstance) {
    lineChartInstance.destroy();
    lineChartInstance = null;
  }

  const quartersList = ['Q1', 'Q2', 'Q3', 'Q4'];
  const lineLabels = [];
  const lineSalesUnits = [];
  const lineTargetUnits = [];

  quartersList.forEach(q => {
    let qData = null;
    let labelText = q;

    if (q === 'Q4') {
      const q4 = loadQ4(rep.key);
      if (q4) {
        qData = q4;
        labelText = 'Q4 (Entered)';
      }
    } else {
      qData = rep.quarters && rep.quarters[q];
    }

    if (rep.startQ && (
      (rep.startQ === 2 && q === 'Q1') ||
      (rep.startQ === 3 && (q === 'Q1' || q === 'Q2'))
    )) {
      return;
    }

    if (qData) {
      lineLabels.push(labelText);
      if (prodVal === 'all') {
        lineSalesUnits.push(qData.total?.salesUnits || 0);
        lineTargetUnits.push(qData.total?.targetUnits || 0);
      } else {
        const targetPid = parseInt(prodVal);
        const pObj = qData.products ? qData.products.find(pr => pr.pid === targetPid) : null;
        lineSalesUnits.push(pObj && pObj.salesUnits !== null ? pObj.salesUnits : 0);
        lineTargetUnits.push(pObj && pObj.targetUnits !== null ? pObj.targetUnits : 0);
      }
    }
  });

  const subEl = document.getElementById('lineChartSub');
  if (subEl) {
    const prodName = prodVal === 'all' ? 'All Products Aggregate' : (PRODUCTS.find(p => p.id === parseInt(prodVal))?.name || 'Product');
    subEl.textContent = `Quarterly trend (Q1 - Q4) for ${prodName}`;
  }

  const lineCtx = document.getElementById('repLineChart').getContext('2d');
  lineChartInstance = new Chart(lineCtx, {
    type: 'line',
    data: {
      labels: lineLabels,
      datasets: [
        {
          label: 'Quarterly Units Sold',
          data: lineSalesUnits,
          borderColor: '#090c12',
          backgroundColor: 'rgba(9, 12, 18, 0.05)',
          tension: 0.35,
          borderWidth: 3,
          pointRadius: 6,
          pointBackgroundColor: '#f59e0b',
          fill: true
        },
        {
          label: 'Quarterly Target Units',
          data: lineTargetUnits,
          borderColor: '#f59e0b',
          backgroundColor: 'transparent',
          borderDash: [6, 4],
          borderWidth: 2.5,
          pointRadius: 6,
          pointBackgroundColor: '#090c12',
          tension: 0.35
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#0f172a', font: { family: 'Plus Jakarta Sans', weight: '700' } } },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${fmt(ctx.parsed.y)} units`
          }
        }
      },
      scales: {
        y: {
          ticks: { color: '#64748b', font: { family: 'Plus Jakarta Sans' }, callback: v => fmt(v) + ' u' },
          grid: { color: '#f1f5f9' }
        },
        x: {
          ticks: { color: '#0f172a', font: { family: 'Plus Jakarta Sans', weight: '600' } },
          grid: { color: '#f1f5f9' }
        }
      }
    }
  });
}

/* ── LOAD LIVE DATA.JSON FROM ONEDRIVE SYNC ── */
async function loadDataJson() {
  try {
    const res = await fetch('./data.json?_t=' + Date.now());
    if (res.ok) {
      const data = await res.json();
      if (data && data.reps) {
        data.reps.forEach(liveRep => {
          const localRep = REPS.find(r => r.key === liveRep.key);
          if (localRep) {
            localRep.quarters = liveRep.quarters;
            localRep.noData = liveRep.noData;
          }
        });
        if (document.getElementById('view-home').classList.contains('active')) {
          renderHome();
        } else if (currentRepForCharts && currentRepForCharts.key) {
          showRep(currentRepForCharts.key);
        }
        console.log('✅ Loaded latest live data.json from OneDrive / SharePoint sync!');
      }
    }
  } catch (err) {
    console.log('Using baseline data:', err);
  }
}

/* ── MICROSOFT / EVA PHARMA SSO AUTHENTICATION ── */
const MSAL_STORAGE_KEY_USER = 'eva_sso_auth_user';
const MSAL_STORAGE_KEY_CLIENT_ID = 'eva_ms_client_id';
const MSAL_STORAGE_KEY_TENANT_ID = 'eva_ms_tenant_id';

let msalApp = null;
let isDashboardInitialized = false;

function getAzureConfig() {
  return {
    clientId: localStorage.getItem(MSAL_STORAGE_KEY_CLIENT_ID) || '',
    tenantId: localStorage.getItem(MSAL_STORAGE_KEY_TENANT_ID) || 'organizations'
  };
}

function initMsalInstance() {
  const cfg = getAzureConfig();
  if (!cfg.clientId || typeof msal === 'undefined') {
    msalApp = null;
    return null;
  }
  try {
    const msalConfig = {
      auth: {
        clientId: cfg.clientId,
        authority: `https://login.microsoftonline.com/${cfg.tenantId || 'organizations'}`,
        redirectUri: window.location.origin + window.location.pathname
      },
      cache: {
        cacheLocation: "localStorage",
        storeAuthStateInCookie: false
      }
    };
    msalApp = new msal.PublicClientApplication(msalConfig);
    return msalApp;
  } catch (err) {
    console.error('Error initializing MSAL:', err);
    msalApp = null;
    return null;
  }
}

function validateEvaEmail(email) {
  if (!email || typeof email !== 'string') return false;
  const cleanEmail = email.trim().toLowerCase();
  return cleanEmail.endsWith('@evapharma.com');
}

function showAuthAlert(msg, type = 'error') {
  const box = document.getElementById('auth-alert');
  if (!box) return;
  box.className = `auth-alert ${type}`;
  box.textContent = msg;
  box.style.display = 'block';
}

function hideAuthAlert() {
  const box = document.getElementById('auth-alert');
  if (box) box.style.display = 'none';
}

function toggleAuthConfigPanel() {
  const panel = document.getElementById('auth-config-panel');
  if (panel) panel.classList.toggle('active');
}

function saveAzureConfig() {
  const cid = (document.getElementById('cfg-client-id').value || '').trim();
  const tid = (document.getElementById('cfg-tenant-id').value || '').trim();
  if (cid) {
    localStorage.setItem(MSAL_STORAGE_KEY_CLIENT_ID, cid);
  } else {
    localStorage.removeItem(MSAL_STORAGE_KEY_CLIENT_ID);
  }
  if (tid) {
    localStorage.setItem(MSAL_STORAGE_KEY_TENANT_ID, tid);
  } else {
    localStorage.removeItem(MSAL_STORAGE_KEY_TENANT_ID);
  }
  initMsalInstance();
  showAuthAlert('Azure settings saved successfully! You can now sign in with Microsoft.', 'info');
  setTimeout(() => hideAuthAlert(), 3500);
}

async function loginWithMicrosoft() {
  hideAuthAlert();
  const cfg = getAzureConfig();
  if (!cfg.clientId) {
    showAuthAlert('Azure App (Client ID) is not configured yet. Please enter it in the settings below, or use the Direct Corporate Sign In.', 'error');
    const panel = document.getElementById('auth-config-panel');
    if (panel && !panel.classList.contains('active')) panel.classList.add('active');
    return;
  }

  const app = initMsalInstance();
  if (!app) {
    showAuthAlert('Failed to initialize Microsoft Authentication library. Please check your network or Client ID.', 'error');
    return;
  }

  const loginRequest = {
    scopes: ["User.Read"],
    prompt: "select_account"
  };

  try {
    const response = await app.loginPopup(loginRequest);
    handleMsalLoginResponse(response);
  } catch (err) {
    console.error('Microsoft login failed:', err);
    if (err.name === 'BrowserAuthError' || (err.message && err.message.includes('popup'))) {
      try {
        await app.loginRedirect(loginRequest);
      } catch (redirErr) {
        showAuthAlert('Microsoft Sign-In error: ' + (redirErr.message || redirErr), 'error');
      }
    } else {
      showAuthAlert('Authentication cancelled or failed: ' + (err.message || err), 'error');
    }
  }
}

function handleMsalLoginResponse(response) {
  if (!response || !response.account) {
    showAuthAlert('No account information received from Microsoft.', 'error');
    return;
  }
  const account = response.account;
  const email = (account.username || (account.idTokenClaims && account.idTokenClaims.email) || '').trim().toLowerCase();
  
  if (!validateEvaEmail(email)) {
    if (msalApp) {
      try { msalApp.logoutPopup({ account: account }); } catch(e){}
    }
    showAuthAlert(`Access Denied: Account (${email}) is not an authorized @evapharma.com account. Only corporate EVA Pharma credentials are permitted.`, 'error');
    return;
  }

  const user = {
    name: account.name || email.split('@')[0].replace(/[._]/g, ' '),
    email: email,
    authMethod: 'Microsoft 365 (MSAL)',
    loginTime: Date.now()
  };
  localStorage.setItem(MSAL_STORAGE_KEY_USER, JSON.stringify(user));
  unlockDashboard(user);
}

function directEvaSignIn() {
  hideAuthAlert();
  const input = document.getElementById('direct-email-input');
  const email = (input ? input.value : '').trim().toLowerCase();
  
  if (!email) {
    showAuthAlert('Please enter your EVA Pharma corporate email address.', 'error');
    return;
  }
  
  if (!validateEvaEmail(email)) {
    showAuthAlert(`Access Denied: (${email}) is invalid. You must use your corporate @evapharma.com account.`, 'error');
    return;
  }

  const user = {
    name: email.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    email: email,
    authMethod: 'Corporate Verification Gate',
    loginTime: Date.now()
  };
  localStorage.setItem(MSAL_STORAGE_KEY_USER, JSON.stringify(user));
  unlockDashboard(user);
}

function logoutUser() {
  localStorage.removeItem(MSAL_STORAGE_KEY_USER);
  const cfg = getAzureConfig();
  if (cfg.clientId && msalApp) {
    try {
      const accounts = msalApp.getAllAccounts();
      if (accounts && accounts.length > 0) {
        msalApp.logoutPopup({ account: accounts[0] });
      }
    } catch(e) {}
  }
  lockDashboard();
}

function getInitials(name) {
  if (!name) return 'EP';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function unlockDashboard(user) {
  const overlay = document.getElementById('auth-overlay');
  const main = document.getElementById('main');
  const userPill = document.getElementById('topbar-user-pill');
  
  if (overlay) overlay.style.display = 'none';
  if (main) main.style.display = 'block';
  
  if (userPill) {
    const initials = getInitials(user.name);
    userPill.innerHTML = `
      <div class="user-avatar-mini" title="${user.name}">${initials}</div>
      <div style="display:flex; flex-direction:column; line-height:1.2;">
        <span style="font-weight:700; color:#ffffff;">${user.name}</span>
        <span style="font-size:10px; color:#94a3b8;">${user.email}</span>
      </div>
      <button class="btn-signout" onclick="logoutUser()" title="Sign Out of EVA Portal">🚪 Sign Out</button>
    `;
    userPill.style.display = 'flex';
  }

  if (!isDashboardInitialized) {
    isDashboardInitialized = true;
    renderHome();
    loadDataJson();
  }
}

function lockDashboard(errorMsg = '') {
  const overlay = document.getElementById('auth-overlay');
  const main = document.getElementById('main');
  const userPill = document.getElementById('topbar-user-pill');
  
  if (overlay) overlay.style.display = 'flex';
  if (main) main.style.display = 'none';
  if (userPill) userPill.style.display = 'none';
  
  if (errorMsg) {
    showAuthAlert(errorMsg, 'error');
  } else {
    hideAuthAlert();
  }
}

async function checkAuthStatus() {
  const cfg = getAzureConfig();
  const cidInput = document.getElementById('cfg-client-id');
  const tidInput = document.getElementById('cfg-tenant-id');
  if (cidInput) cidInput.value = cfg.clientId;
  if (tidInput) tidInput.value = cfg.tenantId;

  // 1. Check local session
  const savedUserJson = localStorage.getItem(MSAL_STORAGE_KEY_USER);
  if (savedUserJson) {
    try {
      const user = JSON.parse(savedUserJson);
      if (user && validateEvaEmail(user.email)) {
        unlockDashboard(user);
        return;
      }
    } catch(e) {}
  }

  // 2. Check MSAL redirect if applicable
  if (cfg.clientId) {
    const app = initMsalInstance();
    if (app) {
      try {
        const redirectRes = await app.handleRedirectPromise();
        if (redirectRes && redirectRes.account) {
          handleMsalLoginResponse(redirectRes);
          return;
        }
        const accounts = app.getAllAccounts();
        if (accounts && accounts.length > 0) {
          const email = (accounts[0].username || '').trim().toLowerCase();
          if (validateEvaEmail(email)) {
            const user = {
              name: accounts[0].name || email.split('@')[0],
              email: email,
              authMethod: 'Microsoft 365 (Cached)',
              loginTime: Date.now()
            };
            localStorage.setItem(MSAL_STORAGE_KEY_USER, JSON.stringify(user));
            unlockDashboard(user);
            return;
          }
        }
      } catch(err) {
        console.error('MSAL redirect check error:', err);
      }
    }
  }

  // 3. Default: Locked
  lockDashboard();
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
  
  checkAuthStatus();
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

print("Full Web App with Google Sheets backend built successfully! File size:", len(full_html), "bytes")
