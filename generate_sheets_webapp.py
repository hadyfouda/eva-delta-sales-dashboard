import json, os

with open(r'C:\Users\ALMadina\.gemini\antigravity\scratch\delta-team-dashboard\logo_b64.txt', 'r') as f:
    logo_b64 = f.read().strip()

from data import PRODUCTS, REPS_DATA

REPS_EN = []
for r in REPS_DATA:
    rep_copy = dict(r)
    if "nameAr" in rep_copy:
        del rep_copy["nameAr"]
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
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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

  /* ── DELTA TEAM RESTRICTED ACCESS GATE ── */
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
    max-width: 460px;
    overflow: hidden;
    text-align: center;
    position: relative;
    animation: fadeIn 0.3s ease-out;
  }
  .auth-header {
    background: #090c12;
    padding: 34px 30px 26px;
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
    padding: 28px 26px 24px;
    display: flex; flex-direction: column; gap: 18px;
  }
  .auth-domain-badge {
    display: inline-flex; align-items: center; justify-content: center; gap: 8px;
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.3);
    color: #92400e; font-size: 12.5px; font-weight: 700;
    padding: 8px 16px; border-radius: 30px;
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
  .auth-input {
    width: 100%; padding: 13px 14px;
    border: 1.5px solid var(--border-dark); border-radius: 10px;
    font-size: 13.5px; font-family: inherit; transition: border 0.2s, box-shadow 0.2s;
    outline: none; box-sizing: border-box; background: #ffffff; color: var(--text-primary);
  }
  .auth-input:focus {
    border-color: var(--gold);
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
  }
  .btn-auth-submit {
    display: flex; align-items: center; justify-content: center; gap: 8px;
    width: 100%; padding: 13px 20px;
    background: #090c10; color: #ffffff;
    border: 1.5px solid var(--gold); border-radius: 10px;
    font-size: 14px; font-weight: 800;
    cursor: pointer; transition: all 0.2s; font-family: inherit;
    box-shadow: 0 4px 14px rgba(0,0,0,0.15);
  }
  .btn-auth-submit:hover {
    background: var(--gold); color: #000000;
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(245, 158, 11, 0.3);
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

  /* ── YEAR-END DEFICIT REPORT BUTTON ── */
  .btn-deficit-report {
    display: inline-flex; align-items: center; gap: 8px;
    background: linear-gradient(135deg, #090c12 0%, #1e293b 100%);
    color: #ffffff;
    border: 1.5px solid var(--gold);
    padding: 8px 16px; border-radius: 10px;
    font-size: 13px; font-weight: 700;
    cursor: pointer; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 14px rgba(9, 12, 18, 0.25);
    font-family: inherit; text-decoration: none;
    white-space: nowrap;
  }
  .btn-deficit-report:hover {
    background: #000000;
    border-color: #fbbf24;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(245, 158, 11, 0.35);
    color: var(--gold-light);
  }
  .report-btn-tag {
    background: var(--gold); color: #000000;
    font-size: 11px; font-weight: 800;
    padding: 2px 8px; border-radius: 6px;
    letter-spacing: 0.3px;
  }

  /* ── DEFICIT REPORT MODAL STYLES ── */
  #deficitModal.modal-overlay {
    position: fixed; inset: 0; z-index: 10000;
    background: rgba(9, 12, 18, 0.85);
    backdrop-filter: blur(6px);
    display: none; align-items: center; justify-content: center;
    padding: 20px;
    overflow-y: auto;
  }
  #deficitModal.modal-overlay.active {
    display: flex; animation: fadeIn 0.2s ease-out;
  }
  .report-modal-box {
    background: #ffffff;
    border-radius: 20px;
    width: 100%; max-width: 1100px; max-height: 92vh;
    box-shadow: 0 25px 60px rgba(0,0,0,0.5);
    border: 1px solid var(--border);
    display: flex; flex-direction: column;
    overflow: hidden;
    animation: slideUp 0.25s ease-out;
  }
  @keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .report-modal-header {
    background: #090c12; color: #ffffff;
    padding: 20px 28px;
    border-bottom: 3px solid var(--gold);
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 14px;
  }
  .report-modal-body {
    padding: 28px;
    overflow-y: auto;
    max-height: calc(92vh - 90px);
    background: var(--bg);
  }
  .report-actions-toolbar {
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  }
  .report-action-btn {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 14px; border-radius: 8px; font-size: 12px; font-weight: 700;
    cursor: pointer; transition: all 0.2s; font-family: inherit;
    border: 1px solid transparent;
  }
  .report-action-excel {
    background: #15803d; color: #ffffff;
  }
  .report-action-excel:hover {
    background: #166534; box-shadow: 0 4px 12px rgba(22, 101, 52, 0.35); transform: translateY(-1px);
  }
  .report-action-print {
    background: #1e293b; color: #ffffff; border-color: rgba(255,255,255,0.2);
  }
  .report-action-print:hover {
    background: #334155; transform: translateY(-1px);
  }
  .report-action-copy {
    background: rgba(245, 158, 11, 0.15); color: #fbbf24; border-color: var(--gold);
  }
  .report-action-copy:hover {
    background: var(--gold); color: #000000; transform: translateY(-1px);
  }
  .report-modal-close {
    background: rgba(255,255,255,0.1); border: none; color: #cbd5e1;
    width: 34px; height: 34px; border-radius: 50%;
    font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center;
    transition: all 0.2s;
  }
  .report-modal-close:hover {
    background: #ef4444; color: #ffffff;
  }

  /* ── REPORT CARDS & TABLES ── */
  .report-kpi-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 16px; margin-bottom: 24px;
  }
  .report-kpi-card {
    background: #ffffff; border: 1px solid var(--border); border-radius: 14px;
    padding: 18px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    position: relative; overflow: hidden;
  }
  .report-kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
    background: var(--gold);
  }
  .report-kpi-card.kpi-deficit::before {
    background: #ef4444;
  }
  .report-kpi-card.kpi-surplus::before {
    background: #22c55e;
  }
  .report-kpi-title {
    font-size: 12px; font-weight: 700; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;
    display: flex; justify-content: space-between; align-items: center;
  }
  .report-kpi-val {
    font-size: 22px; font-weight: 900; color: var(--text-primary);
    line-height: 1.2; margin-bottom: 4px;
  }
  .report-kpi-sub {
    font-size: 11.5px; color: var(--text-secondary); font-weight: 500;
  }

  .report-section-title {
    font-size: 15px; font-weight: 800; color: var(--text-primary);
    margin: 24px 0 14px; display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 8px;
  }
  .report-table-box {
    background: #ffffff; border: 1px solid var(--border); border-radius: 14px;
    overflow-x: auto; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 24px;
  }
  .report-table {
    width: 100%; border-collapse: collapse; font-size: 13px; text-align: left;
  }
  .report-table th {
    background: #090c12; color: #ffffff; padding: 12px 16px;
    font-size: 11.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;
    white-space: nowrap; border-bottom: 2px solid var(--gold);
  }
  .report-table td {
    padding: 13px 16px; border-bottom: 1px solid var(--border);
    vertical-align: middle;
  }
  .report-table tr:last-child td { border-bottom: none; }
  .report-table tr:hover td { background: #f8fafc; }
  .report-table tr.total-row td {
    background: #fef3c7; font-weight: 800; color: #000000;
    border-top: 2px solid var(--gold); border-bottom: none;
  }

  .priority-tag {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 800;
  }
  .priority-critical { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
  .priority-warning { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
  .priority-success { background: #dcfce7; color: #166534; border: 1px solid #86efac; }

  .report-insight-box {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border: 1px solid var(--border); border-left: 4px solid var(--gold);
    border-radius: 12px; padding: 16px 20px; margin-top: 16px;
    font-size: 12.5px; color: var(--text-secondary); line-height: 1.6;
  }

  /* ── PRINT MEDIA OPTIMIZATIONS (A4 LANDSCAPE) ── */
  @page {
    size: A4 landscape;
    margin: 8mm 10mm;
  }

  @media print {
    html, body {
      background: #ffffff !important;
      color: #0f172a !important;
      width: 100% !important;
      height: auto !important;
      margin: 0 !important;
      padding: 0 !important;
      overflow: visible !important;
      font-size: 10px !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }

    /* When printing report, hide everything else */
    body > *:not(#deficitModal) {
      display: none !important;
    }

    #deficitModal.modal-overlay {
      display: block !important;
      position: static !important;
      width: 100% !important;
      height: auto !important;
      margin: 0 !important;
      padding: 0 !important;
      background: transparent !important;
      backdrop-filter: none !important;
      overflow: visible !important;
    }

    .report-modal-box {
      display: block !important;
      position: static !important;
      width: 100% !important;
      max-width: 100% !important;
      height: auto !important;
      max-height: none !important;
      margin: 0 !important;
      padding: 0 !important;
      border: none !important;
      box-shadow: none !important;
      overflow: visible !important;
    }

    .report-modal-header {
      background: #090c12 !important;
      color: #ffffff !important;
      padding: 10px 16px !important;
      border-radius: 6px !important;
      margin-bottom: 12px !important;
      border-bottom: 3px solid #f59e0b !important;
      page-break-after: avoid !important;
    }

    .report-actions-toolbar,
    .report-modal-close,
    .col-action,
    .report-section-title button {
      display: none !important;
    }

    .report-modal-body {
      display: block !important;
      width: 100% !important;
      height: auto !important;
      max-height: none !important;
      overflow: visible !important;
      padding: 0 !important;
      background: #ffffff !important;
    }

    /* KPI Grid in single landscape row */
    .report-kpi-grid {
      display: grid !important;
      grid-template-columns: repeat(6, 1fr) !important;
      gap: 8px !important;
      margin-bottom: 12px !important;
      page-break-inside: avoid !important;
    }

    .report-kpi-card {
      padding: 8px 10px !important;
      border: 1px solid #cbd5e1 !important;
      border-radius: 6px !important;
      background: #f8fafc !important;
      box-shadow: none !important;
      page-break-inside: avoid !important;
    }

    .report-kpi-title {
      font-size: 8.5px !important;
      margin-bottom: 2px !important;
      color: #475569 !important;
    }

    .report-kpi-val {
      font-size: 14px !important;
      margin-bottom: 2px !important;
      color: #0f172a !important;
    }

    .report-kpi-sub {
      font-size: 8px !important;
      color: #64748b !important;
      line-height: 1.2 !important;
    }

    .report-section-title {
      font-size: 11.5px !important;
      font-weight: 800 !important;
      color: #0f172a !important;
      margin: 10px 0 6px 0 !important;
      page-break-after: avoid !important;
    }

    .report-table-box {
      display: block !important;
      width: 100% !important;
      overflow: visible !important;
      border: 1px solid #cbd5e1 !important;
      border-radius: 6px !important;
      margin-bottom: 12px !important;
      box-shadow: none !important;
      page-break-inside: auto !important;
    }

    .report-table {
      width: 100% !important;
      table-layout: fixed !important;
      border-collapse: collapse !important;
      font-size: 9.5px !important;
    }

    .report-table thead {
      display: table-header-group !important;
    }

    .report-table tr {
      page-break-inside: avoid !important;
    }

    .report-table th {
      background: #090c12 !important;
      color: #ffffff !important;
      padding: 5px 4px !important;
      font-size: 8.5px !important;
      font-weight: 800 !important;
      text-transform: uppercase !important;
      text-align: center !important;
      border: 1px solid #334155 !important;
      white-space: normal !important;
      min-width: 0 !important;
    }

    .report-table td {
      padding: 4px 4px !important;
      font-size: 9px !important;
      border: 1px solid #cbd5e1 !important;
      vertical-align: middle !important;
      line-height: 1.2 !important;
      min-width: 0 !important;
      white-space: normal !important;
      word-break: break-word !important;
    }

    .report-table tr.total-row td {
      background: #fef3c7 !important;
      color: #000000 !important;
      font-weight: 800 !important;
      font-size: 9px !important;
      border-top: 2px solid #d97706 !important;
    }

    /* Specific column widths for Manager Matrix in Print (10 visible columns = 100%) */
    .matrix-table th:nth-child(1), .matrix-table td:nth-child(1) { width: 13% !important; text-align: left !important; }
    .matrix-table th:nth-child(2), .matrix-table td:nth-child(2) { width: 11% !important; text-align: left !important; }
    .matrix-table th:nth-child(3), .matrix-table td:nth-child(3) { width: 8.5% !important; text-align: center !important; }
    .matrix-table th:nth-child(4), .matrix-table td:nth-child(4) { width: 8.5% !important; text-align: center !important; }
    .matrix-table th:nth-child(5), .matrix-table td:nth-child(5) { width: 8.5% !important; text-align: center !important; }
    .matrix-table th:nth-child(6), .matrix-table td:nth-child(6) { width: 8.5% !important; text-align: center !important; }
    .matrix-table th:nth-child(7), .matrix-table td:nth-child(7) { width: 11% !important; text-align: center !important; }
    .matrix-table th:nth-child(8), .matrix-table td:nth-child(8) { width: 10% !important; text-align: center !important; }
    .matrix-table th:nth-child(9), .matrix-table td:nth-child(9) { width: 10.5% !important; text-align: center !important; }
    .matrix-table th:nth-child(10), .matrix-table td:nth-child(10) { width: 10.5% !important; text-align: center !important; }

    /* Specific column widths for Medicine Table in Print (7 columns = 100%) */
    .medicine-table th:nth-child(1), .medicine-table td:nth-child(1) { width: 25% !important; text-align: left !important; }
    .medicine-table th:nth-child(2), .medicine-table td:nth-child(2) { width: 8% !important; text-align: center !important; }
    .medicine-table th:nth-child(3), .medicine-table td:nth-child(3) { width: 13% !important; text-align: center !important; }
    .medicine-table th:nth-child(4), .medicine-table td:nth-child(4) { width: 13% !important; text-align: center !important; }
    .medicine-table th:nth-child(5), .medicine-table td:nth-child(5) { width: 15% !important; text-align: center !important; }
    .medicine-table th:nth-child(6), .medicine-table td:nth-child(6) { width: 13% !important; text-align: center !important; }
    .medicine-table th:nth-child(7), .medicine-table td:nth-child(7) { width: 13% !important; text-align: center !important; }

    .priority-tag {
      padding: 1px 4px !important;
      font-size: 8px !important;
      border-radius: 3px !important;
      display: inline-block !important;
      font-weight: 800 !important;
      white-space: nowrap !important;
    }
    .priority-critical {
      background: #fee2e2 !important;
      color: #991b1b !important;
      border: 1px solid #fca5a5 !important;
    }
    .priority-warning {
      background: #fef3c7 !important;
      color: #92400e !important;
      border: 1px solid #fcd34d !important;
    }
    .priority-success {
      background: #dcfce7 !important;
      color: #166534 !important;
      border: 1px solid #86efac !important;
    }

    .report-insight-box {
      background: #f8fafc !important;
      border: 1px solid #cbd5e1 !important;
      border-left: 4px solid #f59e0b !important;
      padding: 8px 12px !important;
      font-size: 9px !important;
      border-radius: 6px !important;
      page-break-inside: avoid !important;
      margin-top: 8px !important;
    }
  }

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

  .save-toast {
    display: none; padding: 10px 18px; border-radius: 8px; font-size: 13px;
    font-weight: 700; background: var(--green-bg); color: var(--green-text);
    border: 1px solid var(--green-border); align-items: center; gap: 8px;
  }
  .save-toast.visible { display: flex; animation: fadeIn 0.2s; }

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

  
  /* ── DUAL FORECAST & UPA SIMULATOR STYLES ── */
  .sim-dual-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
    margin-bottom: 22px;
  }
  @media (max-width: 960px) {
    .sim-dual-grid { grid-template-columns: 1fr; }
  }
  .rep-forecast-cell {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-radius: 8px;
    padding: 3px 6px;
    transition: all 0.2s;
  }
  .rep-forecast-cell:focus-within {
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  }
  .rep-forecast-cell.overridden {
    border-color: #f59e0b;
    background: #fffbeb;
  }
  .rep-forecast-box {
    width: 52px;
    border: none;
    background: transparent;
    font-size: 13px;
    font-weight: 800;
    color: #0f172a;
    text-align: right;
    font-family: inherit;
    outline: none;
  }
  .rep-forecast-pct-symbol {
    font-size: 11px;
    font-weight: 800;
    color: #64748b;
  }
  .rep-reset-btn {
    background: none;
    border: none;
    color: #94a3b8;
    cursor: pointer;
    font-size: 12px;
    padding: 0 2px;
    border-radius: 4px;
    transition: all 0.2s;
  }
  .rep-reset-btn:hover {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }
  .btn-reset-overrides {
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #fca5a5;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 10.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
  }
  .btn-reset-overrides:hover {
    background: #ef4444;
    color: #ffffff;
  }

  /* ── GLARGIVIN UPA SIMULATOR STYLES ── */
  .btn-upa-accent {
    border-color: #f59e0b !important;
    background: linear-gradient(135deg, #090c12 0%, #1e293b 100%) !important;
  }
  .btn-upa-accent:hover {
    border-color: #fbbf24 !important;
    box-shadow: 0 8px 24px rgba(245, 158, 11, 0.4) !important;
  }

  .upa-sim-banner {
    background: linear-gradient(135deg, #090c12 0%, #1e293b 100%);
    border: 1.5px solid rgba(245, 158, 11, 0.4);
    border-radius: 16px;
    padding: 14px 20px;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    cursor: pointer;
    transition: all 0.25s ease;
  }
  .upa-sim-banner:hover {
    border-color: var(--gold);
    transform: translateY(-2px);
    box-shadow: 0 12px 30px rgba(245, 158, 11, 0.25);
  }
  .upa-sim-banner-left {
    display: flex; align-items: center; gap: 14px;
  }
  .upa-sim-icon {
    width: 42px; height: 42px; border-radius: 12px;
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid rgba(245, 158, 11, 0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
  }
  .upa-sim-title {
    font-size: 14.5px; font-weight: 800; color: #ffffff;
  }
  .upa-sim-desc {
    font-size: 11.5px; color: #94a3b8; margin-top: 2px;
  }
  .upa-sim-banner-right {
    display: flex; align-items: center; gap: 12px; flex-shrink: 0;
  }
  .upa-sim-pill {
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid var(--gold);
    color: #fbbf24;
    font-size: 11.5px; font-weight: 800;
    padding: 5px 12px; border-radius: 20px;
  }

  /* Modal Specifics */
  #upaSimModal.modal-overlay {
    position: fixed; inset: 0; z-index: 10000;
    background: rgba(9, 12, 18, 0.85);
    backdrop-filter: blur(6px);
    display: none; align-items: center; justify-content: center;
    padding: 20px;
    overflow-y: auto;
  }
  #upaSimModal.modal-overlay.active {
    display: flex; animation: fadeIn 0.2s ease-out;
  }
  
  .upa-sim-controls-card {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  }
  .upa-sim-controls-grid {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 22px;
    align-items: center;
  }
  @media (max-width: 860px) {
    .upa-sim-controls-grid { grid-template-columns: 1fr; }
  }
  .upa-slider-row {
    display: flex; align-items: center; gap: 16px; margin: 12px 0 14px 0;
  }
  .upa-slider {
    flex: 1; height: 8px; border-radius: 4px;
    background: #e2e8f0; outline: none;
    -webkit-appearance: none; appearance: none;
    accent-color: var(--gold);
    cursor: pointer;
  }
  .upa-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 22px; height: 22px; border-radius: 50%;
    background: var(--gold);
    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    cursor: pointer;
  }
  .upa-input-wrap {
    display: flex; align-items: center; gap: 6px;
    background: #f8fafc; border: 1.5px solid var(--gold);
    padding: 5px 10px; border-radius: 10px;
  }
  .upa-input-box {
    width: 65px; border: none; background: transparent;
    font-size: 16px; font-weight: 800; color: #090c10;
    text-align: right; font-family: inherit; outline: none;
  }
  .upa-preset-btns {
    display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
  }
  .upa-preset-btn {
    background: #f1f5f9; border: 1px solid var(--border);
    padding: 5px 11px; border-radius: 8px;
    font-size: 11.5px; font-weight: 700; color: var(--text-secondary);
    cursor: pointer; transition: all 0.2s; font-family: inherit;
  }
  .upa-preset-btn:hover {
    background: var(--gold-light); color: var(--gold-dark); border-color: var(--gold);
  }
  .upa-preset-btn.active {
    background: var(--gold); color: #090c10; border-color: var(--gold); font-weight: 800;
  }

  .upa-mode-toggle {
    display: inline-flex; background: #f1f5f9; padding: 4px; border-radius: 10px; border: 1px solid var(--border);
  }
  .upa-mode-btn {
    padding: 6px 13px; border-radius: 8px; border: none; background: transparent;
    font-size: 11.5px; font-weight: 700; color: var(--text-secondary); cursor: pointer;
    transition: all 0.2s; font-family: inherit;
  }
  .upa-mode-btn.active {
    background: #090c10; color: #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }


  /* ── PRODUCT UNITS FORECAST DECK STYLES ── */
  .prod-deck-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 22px;
  }
  @media (max-width: 1200px) {
    .prod-deck-grid { grid-template-columns: repeat(2, 1fr); }
  }
  @media (max-width: 640px) {
    .prod-deck-grid { grid-template-columns: 1fr; }
  }

  .prod-forecast-card {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
    padding: 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
  }
  .prod-forecast-card:hover {
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.09);
    transform: translateY(-2px);
  }

  .prod-card-top-bar {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
  }

  .prod-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 12px;
  }
  .prod-card-title-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .prod-card-icon {
    width: 34px;
    height: 34px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    background: #f1f5f9;
  }
  .prod-card-name {
    font-size: 13.5px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.25;
  }
  .prod-card-pack {
    font-size: 10.5px;
    color: #64748b;
    font-weight: 600;
  }

  .prod-baseline-pills {
    display: flex;
    flex-direction: column;
    gap: 4px;
    background: #f8fafc;
    border: 1px solid #f1f5f9;
    border-radius: 8px;
    padding: 8px 10px;
    margin-bottom: 14px;
    font-size: 11px;
  }
  .prod-baseline-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #475569;
  }
  .prod-baseline-val {
    font-weight: 700;
    color: #0f172a;
  }

  .prod-input-group {
    background: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-radius: 10px;
    padding: 8px 10px;
    margin-bottom: 10px;
    transition: all 0.2s;
  }
  .prod-input-group:focus-within {
    border-color: #3b82f6;
    background: #ffffff;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
  }
  .prod-input-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 10.5px;
    font-weight: 700;
    text-transform: uppercase;
    color: #64748b;
    letter-spacing: 0.3px;
    margin-bottom: 4px;
  }
  .prod-input-row {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .prod-unit-input {
    width: 100%;
    border: none;
    background: transparent;
    font-size: 18px;
    font-weight: 900;
    color: #0f172a;
    font-family: inherit;
    outline: none;
  }
  .prod-unit-suffix {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    white-space: nowrap;
  }

  .prod-slider-wrap {
    margin-bottom: 10px;
  }
  .prod-slider {
    width: 100%;
    height: 5px;
    border-radius: 3px;
    outline: none;
    cursor: pointer;
  }

  .prod-presets-row {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 14px;
  }
  .prod-preset-chip {
    background: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
    padding: 2.5px 7px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s;
  }
  .prod-preset-chip:hover {
    background: #e2e8f0;
    color: #0f172a;
  }
  .prod-preset-chip.active {
    background: #0f172a;
    color: #ffffff;
    border-color: #0f172a;
  }

  .prod-card-metrics {
    border-top: 1px dashed #e2e8f0;
    padding-top: 10px;
    display: flex;
    flex-direction: column;
    gap: 5px;
    font-size: 11px;
  }
  .prod-metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .prod-metric-label {
    color: #64748b;
  }
  .prod-metric-val {
    font-weight: 800;
    color: #0f172a;
  }
  .prod-ach-badge {
    padding: 2px 7px;
    border-radius: 6px;
    font-weight: 800;
    font-size: 11px;
  }

  /* Preset strip */
  .master-preset-strip {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 18px;
  }
  .master-preset-label {
    font-size: 11.5px;
    font-weight: 800;
    color: #334155;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .master-preset-btn {
    background: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
    padding: 5px 11px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
  }
  .master-preset-btn:hover {
    background: #f1f5f9;
    border-color: #94a3b8;
    color: #0f172a;
  }
  .master-preset-btn.active {
    background: #3b82f6;
    color: #ffffff;
    border-color: #2563eb;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  }

  /* Table units styling */
  .rep-unit-pill {
    display: inline-block;
    font-size: 12px;
    font-weight: 800;
    color: #0f172a;
  }
  .rep-unit-sub {
    font-size: 10px;
    color: #64748b;
    margin-top: 1px;
  }
  .rep-unit-edit-btn {
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    color: #475569;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 8px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }
  .rep-unit-edit-btn:hover {
    background: #3b82f6;
    color: #ffffff;
    border-color: #2563eb;
  }

</style>
</head>
<body>

<!-- TOPBAR -->
<header id="topbar">
  <div class="brand" onclick="handleBrandClick()">
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

<!-- AUTHENTICATION OVERLAY / RESTRICTED LOGIN GATE -->
<div id="auth-overlay">
  <div class="auth-card">
    <div class="auth-header">
      <img src="data:image/jpeg;base64,__LOGO_B64__" alt="EVA INSULIN" class="auth-logo">
      <h2>EVA Insulin Delta Team</h2>
      <p>Sales Performance & Deficit Tracking Portal 2026</p>
    </div>
    <div class="auth-body">
      <div class="auth-domain-badge">
        <span>🔒</span> Restricted Access — Authorized Team Members Only
      </div>

      <div id="auth-alert" class="auth-alert"></div>

      <div style="text-align: left;">
        <label style="display:block; font-size:12px; font-weight:700; color:var(--text-secondary); margin-bottom:6px;">
          Corporate Email Address:
        </label>
        <input type="email" id="login-email-input" class="auth-input" placeholder="e.g. name@evapharma.com" onkeydown="if(event.key==='Enter') handleUserLogin()">
      </div>

      <button id="btn-login-submit" class="btn-auth-submit" onclick="handleUserLogin()">
        <span>Sign In to Dashboard</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
      </button>

      <div style="font-size: 11px; color: var(--text-muted); line-height: 1.45; margin-top: 4px; padding-top: 10px; border-top: 1px solid var(--border);">
        Access is strictly restricted to authorized Delta Team representatives and management. Your verified session will remain active on this device.
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
      <div class="team-header-actions">
                <button class="btn btn-deficit-report btn-upa-accent" onclick="openUpaSimulator()" title="Q4 Closing Forecast & Glargivin UPA Dual Simulator">
          <span style="font-size:16px;">🎛️</span>
          <span>Q4 Units Forecast & Simulator</span>
          <span class="report-btn-tag" style="background:#f59e0b;color:#090c10;">Units & Ach %</span>
        </button>

        <button class="btn btn-deficit-report" onclick="openDeficitReport('team')" title="Generate Annual Quota Deficit & Gap Analysis Report for Delta Team">
          <span style="font-size:16px;">📊</span>
          <span>Team Year-End Deficit Report</span>
          <span class="report-btn-tag">Units & Quota</span>
        </button>
      </div>
    </div>

    <!-- STAT ROW -->
    <div class="stat-grid" id="team-stat-grid"></div>

        <!-- GLARGIVIN UPA SIMULATOR BANNER -->
    <div class="upa-sim-banner" onclick="openUpaSimulator()">
      <div class="upa-sim-banner-left">
        <div class="upa-sim-icon">🎛️</div>
        <div>
          <div class="upa-sim-title">Q4 Closing Forecast & Glargivin UPA Dual Simulator</div>
          <div class="upa-sim-desc">Simulate Q4 closing forecast and Glargivin UPA line target adjustments to calculate full-year achievement and milestone results.</div>
        </div>
      </div>
      <div class="upa-sim-banner-right">
        <span class="upa-sim-pill">Forecast 85% & UPA 100% &rarr; Team Hits 111.9% YTD 🚀</span>
        <button class="btn btn-primary btn-sm" style="background:var(--gold); color:#090c10; font-weight:800; border:none; padding:7px 14px; border-radius:8px; cursor:pointer;">
          Open Simulator &rarr;
        </button>
      </div>
    </div>

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
      <div class="rep-header-actions" id="rep-header-actions">
                <button class="btn btn-deficit-report btn-upa-accent" onclick="openUpaSimulator(currentActiveRepKey)" title="Simulate Q4 Forecast & Glargivin UPA for this representative">
          <span style="font-size:16px;">🎛️</span>
          <span>Q4 Forecast & UPA</span>
          <span class="report-btn-tag" style="background:#f59e0b;color:#090c10;">What-If</span>
        </button>

        <button class="btn btn-deficit-report" onclick="openDeficitReport(currentActiveRepKey)" title="Generate Annual Quota Deficit & Gap Analysis Report">
          <span style="font-size:16px;">📊</span>
          <span>Year-End Deficit Report</span>
          <span class="report-btn-tag">Units & Quota</span>
        </button>
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

<!-- ── DEFICIT & GAP-TO-TARGET REPORT MODAL ── -->
<div class="modal-overlay" id="deficitModal" onclick="if(event.target===this) closeDeficitReport()">
  <div class="report-modal-box">
    <div class="report-modal-header">
      <div style="display:flex; align-items:center; gap:14px;">
        <div class="title-badge-icon" style="width:44px; height:44px; font-size:20px; border-radius:10px;">Δ</div>
        <div>
          <div id="modalReportTitle" style="font-size:17px; font-weight:800; color:#ffffff; letter-spacing:-0.2px;">
            Year-End Quota Deficit & Gap-to-Target Report 2026
          </div>
          <div id="modalReportSubtitle" style="font-size:12px; color:#94a3b8; margin-top:2px;">
            Detailed breakdown of remaining quota and per-medicine shortage
          </div>
        </div>
      </div>
      <div class="report-actions-toolbar">
        <button class="report-action-btn report-action-excel" onclick="downloadDeficitExcel()" title="Download Excel Spreadsheet">
          <span style="font-size:14px;">📥</span> Download Excel (.xlsx)
        </button>
        <button class="report-action-btn report-action-print" onclick="printDeficitReport()" title="Print or Save PDF Report">
          <span style="font-size:14px;">🖨️</span> Print / PDF
        </button>
        <button class="report-action-btn report-action-copy" onclick="copyDeficitSummary()" title="Copy WhatsApp Text Summary">
          <span style="font-size:14px;">📋</span> Copy WhatsApp
        </button>
        <button class="report-modal-close" onclick="closeDeficitReport()" title="Close">&times;</button>
      </div>
    </div>
    <div class="report-modal-body" id="deficitModalBody">
      <!-- Dynamically generated via JavaScript -->
    </div>
  </div>
</div>

<!-- GLARGIVIN UPA SIMULATOR MODAL -->
<div class="modal-overlay" id="upaSimModal" onclick="if(event.target===this) closeUpaSimulator()">
  <div class="report-modal-box" style="max-width: 1220px;">
    <div class="report-modal-header">
      <div style="display:flex; align-items:center; gap:14px;">
        <div class="title-badge-icon" style="width:44px; height:44px; font-size:20px; border-radius:10px; background:linear-gradient(135deg, #f59e0b 0%, #b45309 100%); color:#090c10; font-weight:900;">🎛️</div>
        <div>
          <div style="font-size:17px; font-weight:800; color:#ffffff; letter-spacing:-0.2px;">
            Q4 Product Units Forecast & Glargivin UPA Simulator 2026
          </div>
          <div style="font-size:12px; color:#94a3b8; margin-top:2px;">
            Simulate Q4 closing by specifying unit quantities per product — real-time total achievement % & YTD calculation
          </div>
        </div>
      </div>
      <div class="report-actions-toolbar">
        <button class="report-action-btn report-action-excel" onclick="downloadUpaSimExcel()" title="Export Simulation Results to Excel">
          <span style="font-size:14px;">📥</span> Export Excel (.xlsx)
        </button>
        <button class="report-action-btn report-action-print" onclick="printUpaSimReport()" title="Print or Save PDF Report">
          <span style="font-size:14px;">🖨️</span> Print / PDF
        </button>
        <button class="report-modal-close" onclick="closeUpaSimulator()" title="Close">&times;</button>
      </div>
    </div>
    <div class="report-modal-body" id="upaSimModalBody">
      <!-- Dynamically generated via JavaScript -->
    </div>
  </div>
</div>

<!-- FLOATING TOAST NOTIFICATION -->
<div id="toastNotification" class="save-toast" style="z-index:10001; position:fixed; bottom:28px; right:28px;"></div>

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

// Clean any legacy manual Q4 overrides from localStorage
try {
  Object.keys(localStorage).forEach(k => {
    if (k && k.startsWith('eva_delta_q4_')) localStorage.removeItem(k);
  });
} catch(e) {}

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

  const quarters = ['Q1', 'Q2', 'Q3', 'Q4'];
  quarters.forEach(q => {
    const qd = rep.quarters && rep.quarters[q];
    if (qd && qd.products) {
      summary.hasData = true;
      qd.products.forEach(p => {
        const py = summary.productsYTD[p.pid];
        if (py) {
          const su = (p.salesUnits !== null && p.salesUnits !== undefined) ? Number(p.salesUnits) : 0;
          const tu = (p.targetUnits !== null && p.targetUnits !== undefined) ? Number(p.targetUnits) : 0;
          const sv = (p.salesValue !== null && p.salesValue !== undefined) ? Number(p.salesValue) : 0;
          const tv = (p.targetValue !== null && p.targetValue !== undefined) ? Number(p.targetValue) : 0;
          const sp = (p.salesPoints !== null && p.salesPoints !== undefined) ? Number(p.salesPoints) : (sv * 2);
          const tp = (p.targetPoints !== null && p.targetPoints !== undefined) ? Number(p.targetPoints) : (tv * 2);

          py.salesUnits  += su; summary.salesUnits += su;
          py.targetUnits += tu; summary.targetUnits += tu;
          py.salesValue  += sv; summary.salesValue += sv;
          py.targetValue += tv; summary.targetValue += tv;
          py.salesPoints += sp; summary.salesPoints += sp;
          py.targetPoints+= tp; summary.targetPoints += tp;

          if (p.salesValue !== null || p.targetValue !== null || p.salesUnits !== null || p.targetUnits !== null) {
            py.hasData = true;
          }
        }
      });
    }
  });

  if (!summary.hasData) return null;

  summary.ratio = (summary.targetPoints !== null && summary.targetPoints > 0)
    ? (summary.salesPoints / summary.targetPoints) * 100
    : (summary.targetValue > 0 ? (summary.salesValue / summary.targetValue) * 100 : null);
  summary.deficitValue = summary.targetValue - summary.salesValue;
  summary.deficitUnits = summary.targetUnits - summary.salesUnits;
  summary.deficitPoints = summary.targetPoints - summary.salesPoints;

  PRODUCTS.forEach(p => {
    const py = summary.productsYTD[p.id];
    py.ratio = (py.targetPoints !== null && py.targetPoints > 0)
      ? (py.salesPoints / py.targetPoints) * 100
      : (py.targetValue > 0 ? (py.salesValue / py.targetValue) * 100 : null);
    py.deficitValue = py.targetValue - py.salesValue;
    py.deficitUnits = py.targetUnits - py.salesUnits;
    py.deficitPoints = py.targetPoints - py.salesPoints;
  });

  // Calculate required Q4 quota % to hit 100% of Total Year
  let spQ1Q3 = 0, svQ1Q3 = 0, suQ1Q3 = 0;
  ['Q1', 'Q2', 'Q3'].forEach(q => {
    const qd = rep.quarters && rep.quarters[q];
    if (qd && qd.total) {
      spQ1Q3 += (qd.total.salesPoints || 0);
      svQ1Q3 += (qd.total.salesValue || 0);
      suQ1Q3 += (qd.total.salesUnits || 0);
    }
  });

  const q4Total = rep.quarters && rep.quarters['Q4'] && rep.quarters['Q4'].total ? rep.quarters['Q4'].total : null;
  const tpQ4 = q4Total ? (q4Total.targetPoints || 0) : 0;
  const tvQ4 = q4Total ? (q4Total.targetValue || 0) : 0;
  const tuQ4 = q4Total ? (q4Total.targetUnits || 0) : 0;
  const spQ4 = q4Total ? (q4Total.salesPoints || 0) : 0;
  const suQ4 = q4Total ? (q4Total.salesUnits || 0) : 0;
  const svQ4 = q4Total ? (q4Total.salesValue || 0) : 0;

  summary.salesPointsQ1Q3 = spQ1Q3;
  summary.targetPointsQ4 = tpQ4;
  summary.salesPointsQ4 = spQ4;
  summary.targetValueQ4 = tvQ4;
  summary.salesValueQ4 = svQ4;
  summary.targetUnitsQ4 = tuQ4;
  summary.salesUnitsQ4 = suQ4;
  summary.actualQ4Ratio = tpQ4 > 0 ? (spQ4 / tpQ4) * 100 : (tvQ4 > 0 ? (svQ4 / tvQ4) * 100 : 0);
  summary.neededPointsQ4 = summary.targetPoints - spQ1Q3;
  summary.requiredQ4Ratio = tpQ4 > 0 ? (summary.neededPointsQ4 / tpQ4) * 100 : 0;

  summary.neededPointsQ4_120 = (summary.targetPoints * 1.20) - spQ1Q3;
  summary.requiredQ4Ratio_120 = tpQ4 > 0 ? (summary.neededPointsQ4_120 / tpQ4) * 100 : 0;

  summary.salesUnitsQ1Q3 = suQ1Q3;
  summary.targetUnitsQ4 = tuQ4;
  summary.salesUnitsQ4 = suQ4;
  summary.neededUnitsQ4 = summary.targetUnits - suQ1Q3;
  summary.requiredQ4UnitsRatio = tuQ4 > 0 ? (summary.neededUnitsQ4 / tuQ4) * 100 : 0;

  summary.neededUnitsQ4_120 = (summary.targetUnits * 1.20) - suQ1Q3;
  summary.requiredQ4UnitsRatio_120 = tuQ4 > 0 ? (summary.neededUnitsQ4_120 / tuQ4) * 100 : 0;

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

  let totalSales = 0, totalTarget = 0, totalUnits = 0, totalTargetUnits = 0, totalPoints = 0, totalTargetPoints = 0, activeCount = 0;
  let teamSpQ1Q3 = 0, teamTpQ4 = 0, teamSpQ4 = 0, teamSvQ4 = 0, teamTvQ4 = 0;
  REPS.forEach(r => {
    const ytd = computeRepYTD(r);
    if (ytd) {
      totalSales        += ytd.salesValue;
      totalTarget       += ytd.targetValue;
      totalUnits        += ytd.salesUnits;
      totalTargetUnits  += ytd.targetUnits;
      totalPoints       += ytd.salesPoints;
      totalTargetPoints += ytd.targetPoints;
      teamSpQ1Q3        += ytd.salesPointsQ1Q3;
      teamTpQ4          += ytd.targetPointsQ4;
      teamSpQ4          += ytd.salesPointsQ4;
      teamSvQ4          += ytd.salesValueQ4;
      teamTvQ4          += ytd.targetValueQ4;
      activeCount++;
    }
  });
  const teamRatio = totalTargetPoints > 0 ? (totalPoints / totalTargetPoints) * 100 : (totalTarget > 0 ? (totalSales / totalTarget) * 100 : 0);
  const teamDeficit = totalTarget - totalSales;
  const teamUnitsDeficit = totalTargetUnits - totalUnits;
  const teamNeededPointsQ4 = totalTargetPoints - teamSpQ1Q3;
  const teamRequiredQ4Ratio = teamTpQ4 > 0 ? (teamNeededPointsQ4 / teamTpQ4) * 100 : 0;
  const teamNeededPointsQ4_120 = (totalTargetPoints * 1.20) - teamSpQ1Q3;
  const teamRequiredQ4Ratio_120 = teamTpQ4 > 0 ? (teamNeededPointsQ4_120 / teamTpQ4) * 100 : 0;
  const teamActualQ4Ratio = teamTpQ4 > 0 ? (teamSpQ4 / teamTpQ4) * 100 : (teamTvQ4 > 0 ? (teamSvQ4 / teamTvQ4) * 100 : 0);

  document.getElementById('team-stat-grid').innerHTML = `
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">Team Sales Revenue (YTD)</span>
        <span class="stat-icon">💰</span>
      </div>
      <div class="stat-val">${fmt(totalSales)} <span style="font-size:13px;color:var(--gold-dark);font-weight:700;">EGP</span></div>
      <div class="stat-sub">Target: <strong>${fmt(totalTarget)}</strong> EGP (${renderDeficitVal(totalTarget, totalSales)})</div>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">Points Achievement Rate</span>
        <span class="stat-icon">📈</span>
      </div>
      <div class="stat-val"><span class="ratio-badge ${ratioClass(teamRatio)}" style="font-size:18px;">${fmtPct(teamRatio)}</span></div>
      <div class="stat-sub">Earned: <strong>${fmt(totalPoints)}</strong> / ${fmt(totalTargetPoints)} pts</div>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">Net Physical Units Deficit</span>
        <span class="stat-icon">📦</span>
      </div>
      <div class="stat-val" style="color:${teamUnitsDeficit > 0 ? '#ef4444' : '#10b981'}; font-weight:800;">
        ${teamUnitsDeficit > 0 ? '-' + fmt(teamUnitsDeficit) : '+' + fmt(Math.abs(teamUnitsDeficit))} <span style="font-size:13px;font-weight:600;">units</span>
      </div>
      <div class="stat-sub">Sold: <strong>${fmt(totalUnits)}</strong> / ${fmt(totalTargetUnits)} quota units</div>
    </div>
    <div class="stat-card" style="border-left: 4px solid var(--gold); background: linear-gradient(145deg, var(--surface), rgba(245, 158, 11, 0.05));">
      <div class="stat-header">
        <span class="stat-label">Q4 Performance & Targets</span>
        <span class="stat-icon">🎯</span>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; margin:2px 0 6px 0;">
        <span style="font-size:12px; font-weight:700; color:var(--text-secondary);">Q4 So Far:</span>
        <div style="display:flex; align-items:center; gap:6px;">
          <span class="ratio-badge ${ratioClass(teamActualQ4Ratio)}" style="font-size:13.5px; font-weight:800; padding:2px 8px;">
            ${fmtPct(teamActualQ4Ratio)}
          </span>
          <span style="font-size:11.5px; color:var(--text-muted); font-weight:600;">(${fmt(teamSvQ4)} EGP)</span>
        </div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:baseline; padding-top:6px; border-top:1px dashed var(--border);">
        <div>
          <span style="font-size:11px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Req. 100%:</span>
          <span style="color:var(--gold); font-size:16px; font-weight:800; margin-left:3px;">${fmtPct(teamRequiredQ4Ratio)}</span>
        </div>
        <div>
          <span style="font-size:11px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Req. 120%:</span>
          <span style="color:#10b981; font-size:16px; font-weight:800; margin-left:3px;">${fmtPct(teamRequiredQ4Ratio_120)}</span>
        </div>
      </div>
      <div class="stat-sub" style="margin-top:4px;">Needed in Q4: <strong>${fmt(teamNeededPointsQ4)}</strong> pts (100%) &bull; <strong>${fmt(teamNeededPointsQ4_120)}</strong> pts (120%)</div>
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
      const ratio = ytd ? ytd.ratio : 0;
      const progressWidth = ratio ? Math.min(ratio, 130) / 130 * 100 : 0;
      const progressColor = ratio >= 100 ? 'background:#16a34a;' : ratio >= 70 ? 'background:var(--gold);' : 'background:#dc2626;';
      const hasQ4 = rep.quarters && rep.quarters['Q4'] && rep.quarters['Q4'].products;
      const badgeClass = (rep.startQ === 2 || rep.startQ === 3) ? 'badge-q2start' : 'badge-active';
      const badgeText  = rep.startQ === 2 ? 'Joined Q2' : rep.startQ === 3 ? 'Joined Q3' : (hasQ4 ? 'Active (Q1 - Q4)' : 'Active (Q1 - Q3)');

      const qPills = ['Q1', 'Q2', 'Q3', 'Q4'].map(q => {
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
              <span class="kpi-label">Sales Points (YTD):</span>
              <span class="kpi-value">${ytd ? fmt(ytd.salesPoints) : '—'} <span style="font-size:11px;color:var(--gold-dark);font-weight:700;">pts</span></span>
            </div>
            <div class="kpi-row">
              <span class="kpi-label">Target Points (YTD):</span>
              <span class="kpi-value">${ytd ? fmt(ytd.targetPoints) : '—'} <span style="font-size:11px;color:var(--text-muted);font-weight:600;">pts</span></span>
            </div>
            <div class="kpi-row" style="background:rgba(245,158,11,0.07); padding:8px 12px; border-radius:8px; margin:8px 0; border:1px solid rgba(245,158,11,0.2); flex-direction:column; gap:6px;">
              <div style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                <span class="kpi-label" style="font-weight:700; color:var(--text-primary); font-size:11px; text-transform:uppercase; letter-spacing:0.3px;">Q4 So Far:</span>
                <div style="display:flex; align-items:center; gap:6px;">
                  <span class="ratio-badge ${ratioClass(ytd ? ytd.actualQ4Ratio : 0)}" style="font-size:11.5px; font-weight:800; padding:1px 6px;">
                    ${ytd ? fmtPct(ytd.actualQ4Ratio) : '—'}
                  </span>
                  <span style="font-size:11px; color:var(--text-muted); font-weight:600;">(${ytd ? fmt(ytd.salesPointsQ4) + ' pts' : '—'})</span>
                </div>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center; width:100%; border-top:1px dashed rgba(245,158,11,0.25); padding-top:5px;">
                <span class="kpi-label" style="font-weight:700; color:var(--text-secondary); font-size:10.5px; text-transform:uppercase;">Req. Targets:</span>
                <div style="display:flex; gap:8px; align-items:center;">
                  <span title="Req. Q4 for 100% Year" style="font-size:11.5px; font-weight:700; color:var(--gold);"><span style="opacity:0.75; font-size:10px; font-weight:600;">100%:</span> ${ytd ? fmtPct(ytd.requiredQ4Ratio) : '—'}</span>
                  <span style="color:var(--border);">|</span>
                  <span title="Req. Q4 for 120% Year" style="font-size:11.5px; font-weight:700; color:#10b981;"><span style="opacity:0.75; font-size:10px; font-weight:600;">120%:</span> ${ytd ? fmtPct(ytd.requiredQ4Ratio_120) : '—'}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="progress-wrap">
            <div class="progress-label">
              <span>Points Quota Fulfillment:</span>
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

/* ── SHOW REP VIEW ── */
function showRep(repKey, targetTabId = null) {
  // Access Restriction: Representatives can ONLY view their own page
  if (currentUser && currentUser.repKey) {
    repKey = currentUser.repKey;
  }

  currentActiveRepKey = repKey;

  const rep = REPS.find(r => r.key === repKey);
  if (!rep || rep.noData) return;

  destroyCharts();

  document.getElementById('view-home').classList.remove('active');
  document.getElementById('view-rep').classList.add('active');

  // Only show Back / Team Overview button for Dr. Sherif (Manager)
  if (currentUser && !currentUser.repKey) {
    document.getElementById('back-btn').classList.add('visible');
  } else {
    document.getElementById('back-btn').classList.remove('visible');
  }

  const av = document.getElementById('rep-avatar-large');
  av.textContent = rep.name[0];
  document.getElementById('rep-profile-name').textContent = rep.name;
  document.getElementById('rep-profile-note').textContent = rep.note;

  // YTD Strip
  const ytd = computeRepYTD(rep);
  const strip = document.getElementById('rep-ytd-strip');
  if (ytd) {
    const repUnitsGap = ytd.targetUnits - ytd.salesUnits;
    strip.innerHTML = `
      <div class="ytd-item">
        <div class="ytd-label">Sales Revenue (YTD)</div>
        <div class="ytd-val">${fmt(ytd.salesValue)} <span style="font-size:13px;color:var(--gold);font-weight:700;">EGP</span></div>
        <div class="ytd-unit">Target: ${fmt(ytd.targetValue)} EGP (${renderDeficitVal(ytd.targetValue, ytd.salesValue)})</div>
      </div>
      <div class="ytd-item">
        <div class="ytd-label">Points Achievement Rate</div>
        <div class="ytd-val" style="display:flex; align-items:center; gap:8px;">
          <span class="ratio-badge ${ratioClass(ytd.ratio)}" style="font-size:18px;">${fmtPct(ytd.ratio)}</span>
        </div>
        <div class="ytd-unit">Earned: ${fmt(ytd.salesPoints)} / ${fmt(ytd.targetPoints)} pts</div>
      </div>
      <div class="ytd-item">
        <div class="ytd-label">Physical Units Deficit</div>
        <div class="ytd-val" style="color:${repUnitsGap > 0 ? '#f87171' : '#4ade80'};">
          ${repUnitsGap > 0 ? '-' + fmt(repUnitsGap) : '+' + fmt(Math.abs(repUnitsGap))} <span style="font-size:13px;font-weight:600;">units</span>
        </div>
        <div class="ytd-unit">Sold: ${fmt(ytd.salesUnits)} / ${fmt(ytd.targetUnits)} quota units</div>
      </div>
      <div class="ytd-item" style="border-left: 2px solid var(--gold); padding-left: 18px; background: rgba(245, 158, 11, 0.05); border-radius: 8px; padding-top: 4px; padding-bottom: 4px;">
        <div class="ytd-label">Q4 Performance & Targets</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin:1px 0 4px 0;">
          <span style="font-size:11px;color:#94a3b8;font-weight:700;text-transform:uppercase;">Q4 So Far:</span>
          <div style="display:flex; align-items:center; gap:6px;">
            <span class="ratio-badge ${ratioClass(ytd.actualQ4Ratio)}" style="font-size:12.5px; font-weight:800; padding:1px 6px;">${fmtPct(ytd.actualQ4Ratio)}</span>
            <span style="font-size:11px;color:#cbd5e1;">(${fmt(ytd.salesValueQ4)} EGP)</span>
          </div>
        </div>
        <div style="display:flex; gap:12px; align-items:baseline; margin:2px 0; border-top:1px dashed rgba(255,255,255,0.1); padding-top:4px;">
          <div><span style="font-size:10.5px;color:#94a3b8;font-weight:600;">Req 100%:</span> <strong style="color:var(--gold); font-size:15px;">${fmtPct(ytd.requiredQ4Ratio)}</strong></div>
          <span style="color:#475569;">|</span>
          <div><span style="font-size:10.5px;color:#94a3b8;font-weight:600;">Req 120%:</span> <strong style="color:#34d399; font-size:15px;">${fmtPct(ytd.requiredQ4Ratio_120)}</strong></div>
        </div>
        <div class="ytd-unit" style="font-size:11px;">Needs: ${fmt(ytd.neededPointsQ4)} pts (100%) &bull; ${fmt(ytd.neededPointsQ4_120)} pts (120%)</div>
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
    { id: 'tab-Q4',  label: 'Quarter 4 (Q4)', q: 'Q4' }
  ];

  tabs.forEach(t => {
    const isQDisabled = rep.startQ && (
      (rep.startQ === 2 && t.q === 'Q1') ||
      (rep.startQ === 3 && (t.q === 'Q1' || t.q === 'Q2'))
    );
    const btn = document.createElement('button');
    btn.className = 'tab-btn' + (isQDisabled ? ' disabled' : '');
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
      } else if (qData && qData.products) {
        const q4Banner = (t.q === 'Q4' && ytd) ? `
          <div class="card" style="margin-bottom:20px; padding:18px 22px; background:linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(16, 185, 129, 0.05)); border:1px solid rgba(245,158,11,0.3); border-radius:12px;">
            <div style="font-size:15px; font-weight:800; color:var(--text-primary); margin-bottom:12px; display:flex; align-items:center; gap:8px;">
              <span>🎯</span> <strong>Quarter 4 Quota Requirements (Annual Milestones)</strong>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:12px;">
              <div style="background:var(--surface); border:1px solid rgba(245, 158, 11, 0.25); border-left:4px solid var(--gold); border-radius:10px; padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <div style="font-size:12px; font-weight:700; color:var(--gold-dark); text-transform:uppercase;">To Hit 100% Annual Quota</div>
                  <div style="font-size:11.5px; color:var(--text-muted); margin-top:2px;">Needs <strong>${fmt(ytd.neededPointsQ4)}</strong> pts of ${fmt(ytd.targetPointsQ4)} pts</div>
                </div>
                <span class="ratio-badge ${ratioClass(ytd.requiredQ4Ratio)}" style="font-size:15px; padding:6px 12px; font-weight:800;">
                  ${fmtPct(ytd.requiredQ4Ratio)}
                </span>
              </div>
              <div style="background:var(--surface); border:1px solid rgba(16, 185, 129, 0.25); border-left:4px solid #10b981; border-radius:10px; padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <div style="font-size:12px; font-weight:700; color:#10b981; text-transform:uppercase;">To Hit 120% Super-Achievement</div>
                  <div style="font-size:11.5px; color:var(--text-muted); margin-top:2px;">Needs <strong>${fmt(ytd.neededPointsQ4_120)}</strong> pts of ${fmt(ytd.targetPointsQ4)} pts</div>
                </div>
                <span class="ratio-badge ${ratioClass(ytd.requiredQ4Ratio_120)}" style="font-size:15px; padding:6px 12px; font-weight:800;">
                  ${fmtPct(ytd.requiredQ4Ratio_120)}
                </span>
              </div>
            </div>
          </div>
        ` : '';
        panel.innerHTML = q4Banner + buildProductsTable(
          `Product Sales & Quota Breakdown — ${t.q} 2026`,
          `Units, revenue in EGP, points, and deficit evaluation for ${t.q}`,
          qData.products,
          qData.total
        );
      } else {
        panel.innerHTML = `
          <div class="card" style="padding:48px;text-align:center;color:var(--text-muted);">
            <div style="font-size:42px;margin-bottom:12px;">⏳</div>
            <div style="font-size:17px;font-weight:800;color:var(--text-primary);">${t.q} 2026 Records Pending Upload</div>
            <div style="font-size:13px;margin-top:6px;">Quarter 4 sales sheets will appear here once officially processed and updated.</div>
          </div>
        `;
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
    const qData = rep.quarters && rep.quarters[q];
    const labelText = q;

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

/* ── AUTHORIZED DELTA TEAM ACCESS LIST (MANAGER + 9 REPS) ── */
const AUTH_STORAGE_KEY_USER = 'eva_delta_auth_user';

// The 10 official Delta Team members (Manager + 9 Representatives)
const AUTHORIZED_TEAM_MEMBERS = {
  // 1. Manager
  "sherif.nessim@evapharma.com": {
    name: "Dr. Sherif Nessim",
    role: "Delta Team District Manager",
    repKey: null
  },

  // 2. Amany
  "amany.mostafa@evapharma.com": {
    name: "Amany Mostafa",
    role: "Medical Representative",
    repKey: "amany"
  },

  // 3. Nadeem
  "nadeem.nasser@evapharma.com": {
    name: "Nadeem Nasser",
    role: "Medical Representative",
    repKey: "nadeem"
  },

  // 4. Ibrahim
  "ibrahim.ragab@evapharma.com": {
    name: "Ibrahim Ragab",
    role: "Medical Representative",
    repKey: "ibrahim"
  },

  // 5. Hassan
  "hassan.khaled@evapharma.com": {
    name: "Hassan Khaled",
    role: "Medical Representative",
    repKey: "hassan"
  },

  // 6. Sabah
  "sabah.safwat@evapharma.com": {
    name: "Sabah Safwat",
    role: "Medical Representative",
    repKey: "sabah"
  },

  // 7. Mohamed Tawfik
  "mohamed.tawfik@evapharma.com": {
    name: "Mohamed Tawfik",
    role: "Medical Representative",
    repKey: "tawfik"
  },

  // 8. Rawda Ahmed
  "rawda.ahmed@evapharma.com": {
    name: "Rawda Ahmed",
    role: "Medical Representative",
    repKey: "radwa"
  },

  // 9. Wedad Esmaeel
  "wedad.esmaeel@evapharma.com": {
    name: "Wedad Esmaeel",
    role: "Medical Representative",
    repKey: "wedad"
  },

  // 10. Hady Mohamed
  "hady.mohamed@evapharma.com": {
    name: "Hady Mohamed",
    role: "Medical Representative",
    repKey: "hady"
  },
  "hady_mohamed@evapharma.com": {
    name: "Hady Mohamed",
    role: "Medical Representative",
    repKey: "hady"
  }
};

let isDashboardInitialized = false;

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

function handleUserLogin() {
  hideAuthAlert();
  const input = document.getElementById('login-email-input');
  const rawEmail = input ? input.value : '';
  let email = (rawEmail || '').trim().toLowerCase();

  // Auto-append domain if user entered username only (e.g. hady.mohamed)
  if (email && !email.includes('@')) {
    email += '@evapharma.com';
  }

  if (!email) {
    showAuthAlert('Please enter your registered EVA Pharma email address.', 'error');
    if (input) input.focus();
    return;
  }

  // Check if email is in the authorized registry
  const member = AUTHORIZED_TEAM_MEMBERS[email];
  if (!member) {
    showAuthAlert(`Access Denied: (${email}) is not authorized to access the Delta Team Sales Dashboard. Please enter your registered corporate email.`, 'error');
    if (input) input.select();
    return;
  }

  // Access Granted!
  const user = {
    email: email,
    name: member.name,
    role: member.role,
    repKey: member.repKey,
    loginTime: Date.now()
  };

  localStorage.setItem(AUTH_STORAGE_KEY_USER, JSON.stringify(user));
  unlockDashboard(user);
}

let currentUser = null;

function logoutUser() {
  currentUser = null;
  localStorage.removeItem(AUTH_STORAGE_KEY_USER);
  lockDashboard();
  const input = document.getElementById('login-email-input');
  if (input) {
    input.value = '';
    setTimeout(() => input.focus(), 100);
  }
}

function getInitials(name) {
  if (!name) return 'EP';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function unlockDashboard(user) {
  currentUser = user;
  const overlay = document.getElementById('auth-overlay');
  const main = document.getElementById('main');
  const userPill = document.getElementById('topbar-user-pill');

  if (overlay) overlay.style.display = 'none';
  if (main) main.style.display = 'block';

  if (userPill) {
    const initials = getInitials(user.name);
    userPill.innerHTML = `
      <div class="user-avatar-mini" title="${user.name} (${user.role})">${initials}</div>
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

  // Role-based routing:
  // - Medical Reps -> strictly their own personal page
  // - Dr. Sherif (Manager) -> Full team dashboard overview
  if (user && user.repKey) {
    showRep(user.repKey);
  } else {
    showHome();
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

function checkAuthStatus() {
  const savedUserJson = localStorage.getItem(AUTH_STORAGE_KEY_USER);
  if (savedUserJson) {
    try {
      const user = JSON.parse(savedUserJson);
      if (user && user.email && AUTHORIZED_TEAM_MEMBERS[user.email.toLowerCase()]) {
        unlockDashboard(user);
        return;
      }
    } catch(e) {}
  }

  lockDashboard();
  setTimeout(() => {
    const input = document.getElementById('login-email-input');
    if (input) input.focus();
  }, 100);
}

/* ── NAVIGATION ── */
function showHome() {
  // Access control: Reps are never allowed to access Team Overview
  if (currentUser && currentUser.repKey) {
    showRep(currentUser.repKey);
    return;
  }

  currentActiveRepKey = 'team';
  destroyCharts();
  document.getElementById('view-rep').classList.remove('active');
  document.getElementById('view-home').classList.add('active');
  document.getElementById('back-btn').classList.remove('visible');
  renderHome();
}

function handleBrandClick() {
  if (currentUser && currentUser.repKey) {
    showRep(currentUser.repKey);
  } else {
    showHome();
  }
}

/* ── DEFICIT & GAP-TO-TARGET REPORT SUITE ── */
let currentActiveRepKey = 'team';
let currentReportScope = 'team';

function computeTeamDeficit() {
  const team = {
    salesUnits: 0, targetUnits: 0, deficitUnits: 0,
    salesValue: 0, targetValue: 0, deficitValue: 0,
    salesPoints: 0, targetPoints: 0, deficitPoints: 0,
    ratio: 0,
    products: {},
    reps: []
  };

  PRODUCTS.forEach(p => {
    team.products[p.id] = {
      pid: p.id,
      name: p.name,
      price: p.price,
      salesUnits: 0, targetUnits: 0, deficitUnits: 0,
      salesValue: 0, targetValue: 0, deficitValue: 0,
      salesPoints: 0, targetPoints: 0, deficitPoints: 0,
      ratio: 0
    };
  });

  REPS.forEach(r => {
    if (r.noData) return;
    const ytd = computeRepYTD(r);
    if (!ytd) return;

    team.salesUnits += ytd.salesUnits;
    team.targetUnits += ytd.targetUnits;
    team.salesValue += ytd.salesValue;
    team.targetValue += ytd.targetValue;
    team.salesPoints += ytd.salesPoints;
    team.targetPoints += ytd.targetPoints;

    const repProdDeficits = {};
    const repProdSales = {};
    const repProdTargets = {};

    PRODUCTS.forEach(p => {
      const py = ytd.productsYTD[p.id];
      if (py) {
        team.products[p.id].salesUnits += py.salesUnits;
        team.products[p.id].targetUnits += py.targetUnits;
        team.products[p.id].salesValue += py.salesValue;
        team.products[p.id].targetValue += py.targetValue;
        team.products[p.id].salesPoints += py.salesPoints;
        team.products[p.id].targetPoints += py.targetPoints;

        repProdDeficits[p.id] = py.deficitUnits;
        repProdSales[p.id] = py.salesUnits;
        repProdTargets[p.id] = py.targetUnits;
      } else {
        repProdDeficits[p.id] = 0;
        repProdSales[p.id] = 0;
        repProdTargets[p.id] = 0;
      }
    });

    team.reps.push({
      key: r.key,
      name: r.name,
      note: r.note,
      salesUnits: ytd.salesUnits,
      targetUnits: ytd.targetUnits,
      deficitUnits: ytd.deficitUnits,
      salesValue: ytd.salesValue,
      targetValue: ytd.targetValue,
      deficitValue: ytd.deficitValue,
      salesPoints: ytd.salesPoints,
      targetPoints: ytd.targetPoints,
      deficitPoints: ytd.deficitPoints,
      ratio: ytd.targetPoints > 0 ? (ytd.salesPoints / ytd.targetPoints) * 100 : 0,
      actualQ4Ratio: ytd.actualQ4Ratio,
      salesValueQ4: ytd.salesValueQ4,
      targetValueQ4: ytd.targetValueQ4,
      salesPointsQ4: ytd.salesPointsQ4,
      requiredQ4Ratio: ytd.requiredQ4Ratio,
      neededPointsQ4: ytd.neededPointsQ4,
      requiredQ4Ratio_120: ytd.requiredQ4Ratio_120,
      neededPointsQ4_120: ytd.neededPointsQ4_120,
      targetPointsQ4: ytd.targetPointsQ4,
      prodDeficits: repProdDeficits,
      prodSales: repProdSales,
      prodTargets: repProdTargets
    });
  });

  let teamSpQ1Q3 = 0, teamTpQ4 = 0, teamSpQ4 = 0, teamSvQ4 = 0, teamTvQ4 = 0;
  REPS.forEach(r => {
    const ytd = computeRepYTD(r);
    if (ytd) {
      teamSpQ1Q3 += ytd.salesPointsQ1Q3;
      teamTpQ4   += ytd.targetPointsQ4;
      teamSpQ4   += ytd.salesPointsQ4;
      teamSvQ4   += ytd.salesValueQ4;
      teamTvQ4   += ytd.targetValueQ4;
    }
  });
  team.neededPointsQ4 = team.targetPoints - teamSpQ1Q3;
  team.targetPointsQ4 = teamTpQ4;
  team.salesPointsQ4  = teamSpQ4;
  team.salesValueQ4   = teamSvQ4;
  team.targetValueQ4  = teamTvQ4;
  team.actualQ4Ratio  = teamTpQ4 > 0 ? (teamSpQ4 / teamTpQ4) * 100 : (teamTvQ4 > 0 ? (teamSvQ4 / teamTvQ4) * 100 : 0);
  team.requiredQ4Ratio = teamTpQ4 > 0 ? (team.neededPointsQ4 / teamTpQ4) * 100 : 0;
  team.neededPointsQ4_120 = (team.targetPoints * 1.20) - teamSpQ1Q3;
  team.requiredQ4Ratio_120 = teamTpQ4 > 0 ? (team.neededPointsQ4_120 / teamTpQ4) * 100 : 0;

  team.deficitUnits = team.targetUnits - team.salesUnits;
  team.deficitValue = team.targetValue - team.salesValue;
  team.deficitPoints = team.targetPoints - team.salesPoints;
  team.ratio = team.targetPoints > 0 ? (team.salesPoints / team.targetPoints) * 100 : 0;

  PRODUCTS.forEach(p => {
    const prod = team.products[p.id];
    prod.deficitUnits = prod.targetUnits - prod.salesUnits;
    prod.deficitValue = prod.targetValue - prod.salesValue;
    prod.deficitPoints = prod.targetPoints - prod.salesPoints;
    prod.ratio = prod.targetPoints > 0 ? (prod.salesPoints / prod.targetPoints) * 100 : 0;
  });

  return team;
}

function computeSingleRepDeficit(repKey) {
  const rep = REPS.find(r => r.key === repKey);
  if (!rep || rep.noData) return null;
  const ytd = computeRepYTD(rep);
  if (!ytd) return null;

  const data = {
    rep: rep,
    salesUnits: ytd.salesUnits,
    targetUnits: ytd.targetUnits,
    deficitUnits: ytd.deficitUnits,
    salesValue: ytd.salesValue,
    targetValue: ytd.targetValue,
    deficitValue: ytd.deficitValue,
    salesPoints: ytd.salesPoints,
    targetPoints: ytd.targetPoints,
    deficitPoints: ytd.deficitPoints,
    ratio: ytd.targetPoints > 0 ? (ytd.salesPoints / ytd.targetPoints) * 100 : 0,
    actualQ4Ratio: ytd.actualQ4Ratio,
    salesValueQ4: ytd.salesValueQ4,
    targetValueQ4: ytd.targetValueQ4,
    salesPointsQ4: ytd.salesPointsQ4,
    requiredQ4Ratio: ytd.requiredQ4Ratio,
    neededPointsQ4: ytd.neededPointsQ4,
    requiredQ4Ratio_120: ytd.requiredQ4Ratio_120,
    neededPointsQ4_120: ytd.neededPointsQ4_120,
    targetPointsQ4: ytd.targetPointsQ4,
    products: []
  };

  PRODUCTS.forEach(p => {
    const py = ytd.productsYTD[p.id];
    data.products.push({
      pid: p.id,
      name: p.name,
      price: p.price,
      salesUnits: py ? py.salesUnits : 0,
      targetUnits: py ? py.targetUnits : 0,
      deficitUnits: py ? py.deficitUnits : 0,
      salesValue: py ? py.salesValue : 0,
      targetValue: py ? py.targetValue : 0,
      deficitValue: py ? py.deficitValue : 0,
      salesPoints: py ? py.salesPoints : 0,
      targetPoints: py ? py.targetPoints : 0,
      deficitPoints: py ? py.deficitPoints : 0,
      ratio: py && py.targetPoints > 0 ? (py.salesPoints / py.targetPoints) * 100 : 0
    });
  });

  return data;
}

function renderUnitDeficitBadge(targetUnits, salesUnits) {
  if (targetUnits === null || salesUnits === null || targetUnits === undefined || salesUnits === undefined) {
    return '<span style="color:#94a3b8;font-weight:600;">—</span>';
  }
  const diff = targetUnits - salesUnits;
  if (diff > 0.001) {
    return `<span class="priority-tag priority-critical" style="font-size:11.5px; font-weight:800; white-space:nowrap;">-${fmt(diff)} u</span>`;
  } else if (diff <= -0.001) {
    return `<span class="priority-tag priority-success" style="font-size:11.5px; font-weight:800; white-space:nowrap;">+${fmt(Math.abs(diff))} u</span>`;
  } else {
    return `<span class="priority-tag priority-success" style="font-size:11.5px; font-weight:800; white-space:nowrap;">Met</span>`;
  }
}

function openDeficitReport(targetType) {
  targetType = targetType || currentActiveRepKey || 'team';
  if (currentUser && currentUser.repKey) {
    targetType = currentUser.repKey;
  }
  currentReportScope = targetType;

  const isTeam = targetType === 'team';
  const modal = document.getElementById('deficitModal');
  const titleEl = document.getElementById('modalReportTitle');
  const subEl = document.getElementById('modalReportSubtitle');
  const bodyEl = document.getElementById('deficitModalBody');

  if (!modal || !bodyEl) return;

  if (isTeam) {
    titleEl.textContent = 'Delta Team — Annual Unit Deficit & Shortage Report 2026';
    subEl.textContent = 'Annual Physical Units Quota & Deficit Analysis Across Representatives and Products';

    const d = computeTeamDeficit();
    const valClass = d.deficitUnits > 0 ? 'kpi-deficit' : 'kpi-surplus';
    const topDeficit = Object.values(d.products).reduce((max, cur) => cur.deficitUnits > max.deficitUnits ? cur : max);

    let html = `
      <!-- KPI CARDS (UNITS FOCUSED) -->
      <div class="report-kpi-grid">
        <div class="report-kpi-card">
          <div class="report-kpi-title">
            <span>Physical Volume Quota</span>
            <span>🎯</span>
          </div>
          <div class="report-kpi-val">${fmt(d.targetUnits)} <span style="font-size:13px; color:var(--gold);">units</span></div>
          <div class="report-kpi-sub">Sold: <strong>${fmt(d.salesUnits)}</strong> units (${d.targetUnits > 0 ? ((d.salesUnits / d.targetUnits) * 100).toFixed(1) : 0}% volume fulfillment)</div>
        </div>

        <div class="report-kpi-card ${valClass}">
          <div class="report-kpi-title">
            <span>Net Units Deficit</span>
            <span>${d.deficitUnits > 0 ? '📉' : '🏆'}</span>
          </div>
          <div class="report-kpi-val" style="color:${d.deficitUnits > 0 ? '#ef4444' : '#22c55e'};">
            ${d.deficitUnits > 0 ? '-' + fmt(d.deficitUnits) : '+' + fmt(Math.abs(d.deficitUnits))} <span style="font-size:13px;">units</span>
          </div>
          <div class="report-kpi-sub">${d.deficitUnits > 0 ? 'Net physical shortage across all products' : 'Volume quota successfully surpassed!'}</div>
        </div>

        <div class="report-kpi-card">
          <div class="report-kpi-title">
            <span>Points Achievement Rate</span>
            <span>⭐</span>
          </div>
          <div class="report-kpi-val" style="color:${d.ratio >= 100 ? '#22c55e' : d.ratio >= 80 ? '#fbbf24' : '#ef4444'};">
            ${fmtPct(d.ratio)}
          </div>
          <div class="report-kpi-sub">Points earned: <strong>${fmt(d.salesPoints)}</strong> / ${fmt(d.targetPoints)} pts</div>
        </div>

        <div class="report-kpi-card" style="border-left: 3px solid var(--gold); background:linear-gradient(135deg, var(--surface), rgba(245, 158, 11, 0.04));">
          <div class="report-kpi-title">
            <span>Q4 Performance & Targets</span>
            <span>🚀</span>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin:2px 0 5px 0;">
            <span style="font-size:11.5px; font-weight:700; color:var(--text-secondary);">Q4 So Far:</span>
            <div style="display:flex; align-items:center; gap:6px;">
              <span class="ratio-badge ${ratioClass(d.actualQ4Ratio)}" style="font-size:13px; font-weight:800; padding:1px 6px;">${fmtPct(d.actualQ4Ratio)}</span>
              <span style="font-size:11px; color:var(--text-muted); font-weight:600;">(${fmt(d.salesValueQ4)} EGP)</span>
            </div>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:baseline; margin:4px 0 6px 0; border-top:1px dashed var(--border); padding-top:4px;">
            <div><span style="font-size:11px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Req 100%:</span> <span style="color:var(--gold); font-size:16px; font-weight:800; margin-left:3px;">${fmtPct(d.requiredQ4Ratio)}</span></div>
            <div><span style="font-size:11px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Req 120%:</span> <span style="color:#10b981; font-size:16px; font-weight:800; margin-left:3px;">${fmtPct(d.requiredQ4Ratio_120)}</span></div>
          </div>
          <div class="report-kpi-sub">Needed: <strong>${fmt(d.neededPointsQ4)}</strong> pts (100%) &bull; <strong>${fmt(d.neededPointsQ4_120)}</strong> pts (120%)</div>
        </div>
      </div>

      <!-- SECTION 1: PER-MEDICINE SHORTAGE BREAKDOWN TABLE -->
      <div class="report-section-title">
        <span>💊 Per-Medicine Shortage Breakdown</span>
        <span style="font-size:12px; font-weight:600; color:var(--text-muted);">Delta Region Aggregate</span>
      </div>

      <div class="report-table-box">
        <table class="report-table medicine-table">
          <thead>
            <tr>
              <th>Medicine / Insulin Product</th>
              <th>Code</th>
              <th>Target Units</th>
              <th>Actual Units Sold</th>
              <th>Unit Deficit / Shortage (Units)</th>
              <th>Points Achievement %</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
    `;

    PRODUCTS.forEach(p => {
      const prod = d.products[p.id];
      const isDeficit = prod.deficitUnits > 0;
      const statusBadge = isDeficit
        ? (prod.ratio < 70 
            ? `<span class="priority-tag priority-critical">⚠️ High Deficit (-${fmt(prod.deficitUnits)} u)</span>`
            : `<span class="priority-tag priority-warning">📉 Deficit (-${fmt(prod.deficitUnits)} u)</span>`)
        : `<span class="priority-tag priority-success">✅ Met (+${fmt(Math.abs(prod.deficitUnits))} u)</span>`;

      html += `
        <tr>
          <td><strong>${prod.name}</strong></td>
          <td><span style="font-size:11px; background:#f1f5f9; padding:2px 6px; border-radius:4px; font-weight:700;">#${prod.pid}</span></td>
          <td>${fmt(prod.targetUnits)} units</td>
          <td><strong>${fmt(prod.salesUnits)}</strong> units</td>
          <td>${renderUnitDeficitBadge(prod.targetUnits, prod.salesUnits)}</td>
          <td>
            <div style="font-weight:800; color:${prod.ratio >= 100 ? '#16a34a' : prod.ratio >= 70 ? '#d97706' : '#dc2626'};">
              ${fmtPct(prod.ratio)}
            </div>
          </td>
          <td>${statusBadge}</td>
        </tr>
      `;
    });

    html += `
          <tr class="total-row">
            <td colspan="2">TOTAL (ALL 4 INSULIN PRODUCTS)</td>
            <td>${fmt(d.targetUnits)} units</td>
            <td>${fmt(d.salesUnits)} units</td>
            <td>${renderUnitDeficitBadge(d.targetUnits, d.salesUnits)}</td>
            <td style="color:${d.ratio >= 100 ? '#16a34a' : '#b45309'}; font-size:14px;">${fmtPct(d.ratio)}</td>
            <td>${d.deficitUnits > 0 ? '<span class="priority-tag priority-warning">Net Shortage</span>' : '<span class="priority-tag priority-success">Surplus</span>'}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- SECTION 2: MANAGER MATRIX — UNIT SHORTAGE PER REP FOR EACH DRUG -->
    <div class="report-section-title">
      <span>👥 Manager's Matrix: Unit Shortage per Representative for Each Medicine</span>
      <span style="font-size:12px; font-weight:600; color:var(--text-muted);">Operational Gap Matrix</span>
    </div>

    <div class="report-table-box">
      <table class="report-table matrix-table">
        <thead>
          <tr>
            <th style="min-width:140px;">Medical Rep</th>
            <th style="min-width:110px;">Territory</th>
            <th style="text-align:center;">Humaxin Mix<br><span style="font-size:10px;font-weight:600;opacity:0.8;">#1260</span></th>
            <th style="text-align:center;">Humaxin Rapid<br><span style="font-size:10px;font-weight:600;opacity:0.8;">#1259</span></th>
            <th style="text-align:center;">Glargivin UPA<br><span style="font-size:10px;font-weight:600;opacity:0.8;">#1251</span></th>
            <th style="text-align:center;">Glargivin 100IU<br><span style="font-size:10px;font-weight:600;opacity:0.8;">#1110</span></th>
            <th style="text-align:center; background:#1e293b; color:var(--gold);">Total Shortage<br><span style="font-size:10px;font-weight:600;">(Units)</span></th>
            <th style="text-align:center; min-width:120px;">Total Ach. %<br><span style="font-size:10px;font-weight:600;opacity:0.8;">(Points)</span></th>
            <th style="text-align:center; min-width:115px; background:#1e293b; color:#38bdf8;">Q4 So Far %<br><span style="font-size:10px;font-weight:600;opacity:0.8;">(Actual Q4 Ach.)</span></th>
            <th style="text-align:center; min-width:125px; background:#1e293b; color:var(--gold);">Req. Q4 (100% Year)<br><span style="font-size:10px;font-weight:600;opacity:0.8;">(Annual Quota)</span></th>
            <th style="text-align:center; min-width:130px; background:#064e3b; color:#34d399;">Req. Q4 (120% Year)<br><span style="font-size:10px;font-weight:600;opacity:0.8;">(Super-Target)</span></th>
            <th style="text-align:center;" class="col-action">Action</th>
          </tr>
        </thead>
        <tbody>
    `;

    d.reps.forEach(r => {
      html += `
        <tr>
          <td><strong>${r.name}</strong></td>
          <td><span style="font-size:12px; color:var(--text-secondary);">${r.note}</span></td>
          <td style="text-align:center;">${renderUnitDeficitBadge(r.prodTargets[1260], r.prodSales[1260])}</td>
          <td style="text-align:center;">${renderUnitDeficitBadge(r.prodTargets[1259], r.prodSales[1259])}</td>
          <td style="text-align:center;">${renderUnitDeficitBadge(r.prodTargets[1251], r.prodSales[1251])}</td>
          <td style="text-align:center;">${renderUnitDeficitBadge(r.prodTargets[1110], r.prodSales[1110])}</td>
          <td style="text-align:center; background:rgba(245, 158, 11, 0.05);">${renderUnitDeficitBadge(r.targetUnits, r.salesUnits)}</td>
          <td style="text-align:center;">
            <div style="font-weight:800; color:${r.ratio >= 100 ? '#16a34a' : r.ratio >= 70 ? '#d97706' : '#dc2626'};">
              ${fmtPct(r.ratio)}
            </div>
          </td>
          <td style="text-align:center; background:rgba(56, 189, 248, 0.04);">
            <div style="font-weight:800; font-size:13px; color:${r.actualQ4Ratio >= 100 ? '#16a34a' : r.actualQ4Ratio >= 50 ? '#d97706' : '#2563eb'};">
              ${fmtPct(r.actualQ4Ratio)}
            </div>
            <div style="font-size:10px; color:var(--text-muted); font-weight:600;">${fmt(r.salesValueQ4)} EGP</div>
          </td>
          <td style="text-align:center; background:rgba(245, 158, 11, 0.04);">
            <div style="font-weight:800; font-size:13px; color:${r.requiredQ4Ratio > 100 ? '#dc2626' : (r.requiredQ4Ratio > 70 ? '#d97706' : '#16a34a')};">
              ${fmtPct(r.requiredQ4Ratio)}
            </div>
          </td>
          <td style="text-align:center; background:rgba(16, 185, 129, 0.04);">
            <div style="font-weight:800; font-size:13px; color:${r.requiredQ4Ratio_120 > 120 ? '#dc2626' : (r.requiredQ4Ratio_120 > 90 ? '#d97706' : '#16a34a')};">
              ${fmtPct(r.requiredQ4Ratio_120)}
            </div>
          </td>
          <td style="text-align:center;" class="col-action">
            <button onclick="openDeficitReport('${r.key}')" style="background:#090c12; color:#fbbf24; border:none; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:700; cursor:pointer;" title="View Rep Deficit Report">
              View Rep ↗
            </button>
          </td>
        </tr>
      `;
    });

    html += `
          <tr class="total-row">
            <td colspan="2">DELTA TEAM TOTAL SHORTAGE</td>
            <td style="text-align:center;">${renderUnitDeficitBadge(d.products[1260].targetUnits, d.products[1260].salesUnits)}</td>
            <td style="text-align:center;">${renderUnitDeficitBadge(d.products[1259].targetUnits, d.products[1259].salesUnits)}</td>
            <td style="text-align:center;">${renderUnitDeficitBadge(d.products[1251].targetUnits, d.products[1251].salesUnits)}</td>
            <td style="text-align:center;">${renderUnitDeficitBadge(d.products[1110].targetUnits, d.products[1110].salesUnits)}</td>
            <td style="text-align:center;">${renderUnitDeficitBadge(d.targetUnits, d.salesUnits)}</td>
            <td style="text-align:center; color:${d.ratio >= 100 ? '#16a34a' : '#b45309'}; font-size:14px;">${fmtPct(d.ratio)}</td>
            <td style="text-align:center; background:rgba(56, 189, 248, 0.08); color:#0284c7; font-size:13.5px; font-weight:800;">
              ${fmtPct(d.actualQ4Ratio)}<br><span style="font-size:10.5px; font-weight:600; opacity:0.9;">(${fmt(d.salesValueQ4)} EGP)</span>
            </td>
            <td style="text-align:center; background:rgba(245, 158, 11, 0.08); color:var(--gold-dark); font-size:14px; font-weight:800;">${fmtPct(d.requiredQ4Ratio)}</td>
            <td style="text-align:center; background:rgba(16, 185, 129, 0.08); color:#10b981; font-size:14px; font-weight:800;">${fmtPct(d.requiredQ4Ratio_120)}</td>
            <td style="text-align:center;" class="col-action">-</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ACTIONABLE INSIGHTS BOX -->
    <div class="report-insight-box">
      <strong>💡 Manager Strategic Insight:</strong><br>
      The primary unit shortage driver across Delta Team is <strong>${topDeficit.name}</strong> with a total deficit of <strong>${fmt(topDeficit.deficitUnits)} units</strong> remaining to achieve the annual quota.
      Focusing sales efforts and pharmacy order placements on this SKU will resolve ${d.deficitUnits > 0 ? ((topDeficit.deficitUnits / d.deficitUnits) * 100).toFixed(1) : 0}% of the entire team's volume shortage!
    </div>
    `;

    bodyEl.innerHTML = html;

  } else {
    // SINGLE REP SCOPE
    const repData = computeSingleRepDeficit(targetType);
    if (!repData) return;
    const rep = repData.rep;

    titleEl.textContent = `${rep.name} — Annual Unit Deficit & Shortage Report 2026`;
    subEl.textContent = `Territory: ${rep.note} | Personal Annual Unit Deficit & Quota Analysis`;

    const valClass = repData.deficitUnits > 0 ? 'kpi-deficit' : 'kpi-surplus';
    const topDeficit = repData.products.reduce((max, cur) => cur.deficitUnits > max.deficitUnits ? cur : max);

    let html = `
      <!-- KPI CARDS (UNITS FOCUSED) -->
      <div class="report-kpi-grid">
        <div class="report-kpi-card">
          <div class="report-kpi-title">
            <span>Physical Volume Quota</span>
            <span>🎯</span>
          </div>
          <div class="report-kpi-val">${fmt(repData.targetUnits)} <span style="font-size:13px; color:var(--gold);">units</span></div>
          <div class="report-kpi-sub">Sold: <strong>${fmt(repData.salesUnits)}</strong> units (${repData.targetUnits > 0 ? ((repData.salesUnits / repData.targetUnits) * 100).toFixed(1) : 0}% volume fulfillment)</div>
        </div>

        <div class="report-kpi-card ${valClass}">
          <div class="report-kpi-title">
            <span>Net Units Deficit</span>
            <span>${repData.deficitUnits > 0 ? '📉' : '🏆'}</span>
          </div>
          <div class="report-kpi-val" style="color:${repData.deficitUnits > 0 ? '#ef4444' : '#22c55e'};">
            ${repData.deficitUnits > 0 ? '-' + fmt(repData.deficitUnits) : '+' + fmt(Math.abs(repData.deficitUnits))} <span style="font-size:13px;">units</span>
          </div>
          <div class="report-kpi-sub">${repData.deficitUnits > 0 ? 'Remaining physical units required to close quota' : 'Personal annual quota surpassed!'}</div>
        </div>

        <div class="report-kpi-card">
          <div class="report-kpi-title">
            <span>Points Achievement Rate</span>
            <span>⭐</span>
          </div>
          <div class="report-kpi-val" style="color:${repData.ratio >= 100 ? '#22c55e' : repData.ratio >= 80 ? '#fbbf24' : '#ef4444'};">
            ${fmtPct(repData.ratio)}
          </div>
          <div class="report-kpi-sub">Points earned: <strong>${fmt(repData.salesPoints)}</strong> / ${fmt(repData.targetPoints)} pts</div>
        </div>

        <div class="report-kpi-card" style="border-left: 3px solid var(--gold); background:linear-gradient(135deg, var(--surface), rgba(245, 158, 11, 0.04));">
          <div class="report-kpi-title">
            <span>Q4 Performance & Targets</span>
            <span>🚀</span>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin:2px 0 5px 0;">
            <span style="font-size:11.5px; font-weight:700; color:var(--text-secondary);">Q4 So Far:</span>
            <div style="display:flex; align-items:center; gap:6px;">
              <span class="ratio-badge ${ratioClass(repData.actualQ4Ratio)}" style="font-size:13px; font-weight:800; padding:1px 6px;">${fmtPct(repData.actualQ4Ratio)}</span>
              <span style="font-size:11px; color:var(--text-muted); font-weight:600;">(${fmt(repData.salesValueQ4)} EGP)</span>
            </div>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:baseline; margin:4px 0 6px 0; border-top:1px dashed var(--border); padding-top:4px;">
            <div><span style="font-size:11px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Req 100%:</span> <span style="color:var(--gold); font-size:16px; font-weight:800; margin-left:3px;">${fmtPct(repData.requiredQ4Ratio)}</span></div>
            <div><span style="font-size:11px; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Req 120%:</span> <span style="color:#10b981; font-size:16px; font-weight:800; margin-left:3px;">${fmtPct(repData.requiredQ4Ratio_120)}</span></div>
          </div>
          <div class="report-kpi-sub">Needed: <strong>${fmt(repData.neededPointsQ4)}</strong> pts (100%) &bull; <strong>${fmt(repData.neededPointsQ4_120)}</strong> pts (120%)</div>
        </div>
      </div>

      <!-- SECTION: PER-MEDICINE SHORTAGE BREAKDOWN TABLE -->
      <div class="report-section-title">
        <span>💊 Per-Medicine Shortage Breakdown</span>
        ${currentUser && !currentUser.repKey ? `<button onclick="openDeficitReport('team')" style="background:#f1f5f9; border:1px solid var(--border); padding:4px 10px; border-radius:6px; font-size:11px; font-weight:700; cursor:pointer;">← Back to Team Report</button>` : ''}
      </div>

      <div class="report-table-box">
        <table class="report-table medicine-table">
          <thead>
            <tr>
              <th>Medicine / Insulin Product</th>
              <th>Code</th>
              <th>Target Units</th>
              <th>Actual Units Sold</th>
              <th>Unit Deficit / Shortage (Units)</th>
              <th>Points Achievement %</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
    `;

    repData.products.forEach(prod => {
      const isDeficit = prod.deficitUnits > 0;
      const statusBadge = isDeficit
        ? (prod.ratio < 70 
            ? `<span class="priority-tag priority-critical">⚠️ High Deficit (-${fmt(prod.deficitUnits)} u)</span>`
            : `<span class="priority-tag priority-warning">📉 Deficit (-${fmt(prod.deficitUnits)} u)</span>`)
        : `<span class="priority-tag priority-success">✅ Met (+${fmt(Math.abs(prod.deficitUnits))} u)</span>`;

      html += `
        <tr>
          <td><strong>${prod.name}</strong></td>
          <td><span style="font-size:11px; background:#f1f5f9; padding:2px 6px; border-radius:4px; font-weight:700;">#${prod.pid}</span></td>
          <td>${fmt(prod.targetUnits)} units</td>
          <td><strong>${fmt(prod.salesUnits)}</strong> units</td>
          <td>${renderUnitDeficitBadge(prod.targetUnits, prod.salesUnits)}</td>
          <td>
            <div style="font-weight:800; color:${prod.ratio >= 100 ? '#16a34a' : prod.ratio >= 70 ? '#d97706' : '#dc2626'};">
              ${fmtPct(prod.ratio)}
            </div>
          </td>
          <td>${statusBadge}</td>
        </tr>
      `;
    });

    html += `
          <tr class="total-row">
            <td colspan="2">TOTAL ANNUAL QUOTA</td>
            <td>${fmt(repData.targetUnits)} units</td>
            <td>${fmt(repData.salesUnits)} units</td>
            <td>${renderUnitDeficitBadge(repData.targetUnits, repData.salesUnits)}</td>
            <td style="color:${repData.ratio >= 100 ? '#16a34a' : '#b45309'}; font-size:14px;">${fmtPct(repData.ratio)}</td>
            <td>${repData.deficitUnits > 0 ? '<span class="priority-tag priority-warning">Net Shortage</span>' : '<span class="priority-tag priority-success">Surplus</span>'}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ACTIONABLE INSIGHTS BOX -->
    <div class="report-insight-box">
      <strong>💡 Personalized Shortage Insights:</strong><br>
      To achieve <strong>100%</strong> of your annual quota, you need to achieve <strong>${fmtPct(repData.requiredQ4Ratio)}</strong> of your Q4 target (<strong>${fmt(repData.neededPointsQ4)} pts</strong>).
      To reach <strong>120%</strong> super-achievement, you need <strong>${fmtPct(repData.requiredQ4Ratio_120)}</strong> of Q4 (<strong>${fmt(repData.neededPointsQ4_120)} pts</strong>).
      ${repData.deficitUnits > 0 ? `Your primary product volume focus is <strong>${topDeficit.name}</strong> where you have a shortage of <strong>${fmt(topDeficit.deficitUnits)} units</strong>.` : ''}
    </div>
    `;

    bodyEl.innerHTML = html;
  }

  modal.classList.add('active');
}

function closeDeficitReport() {
  const modal = document.getElementById('deficitModal');
  if (modal) modal.classList.remove('active');
}

function printDeficitReport() {
  const modal = document.getElementById('deficitModal');
  if (!modal || !modal.classList.contains('active')) {
    openDeficitReport(currentReportScope || currentActiveRepKey || 'team');
  }
  document.body.classList.add('printing-report');
  window.onafterprint = () => {
    document.body.classList.remove('printing-report');
  };
  setTimeout(() => {
    window.print();
  }, 120);
}

function downloadDeficitExcel(targetType) {
  targetType = targetType || currentReportScope || 'team';
  if (currentUser && currentUser.repKey) targetType = currentUser.repKey;

  const isTeam = targetType === 'team';
  const wb = XLSX.utils.book_new();

  function fmtDeficitExcel(diff, isUnit) {
    if (diff === null || diff === undefined || isNaN(diff)) return "—";
    const suffix = isUnit ? " u" : "";
    if (diff > 0.001) {
      return `-${Math.round(diff).toLocaleString()}${suffix}`;
    } else if (diff < -0.001) {
      return `+${Math.round(Math.abs(diff)).toLocaleString()}${suffix} (Surplus)`;
    } else {
      return "Met (0)";
    }
  }

  function fmtTotalDeficitExcel(diff) {
    if (diff === null || diff === undefined || isNaN(diff)) return "—";
    if (diff > 0.001) {
      return `-${Math.round(diff).toLocaleString()} units`;
    } else if (diff < -0.001) {
      return `+${Math.round(Math.abs(diff)).toLocaleString()} surplus`;
    } else {
      return "Target Met (0)";
    }
  }

  if (isTeam) {
    const teamData = computeTeamDeficit();

    // ── SHEET 1: MANAGER MATRIX (UNIT DEFICIT PER REP & MEDICINE) ──
    const repRows = [
      ["EVA PHARMA - DELTA REGION SALES DASHBOARD"],
      ["MANAGER MATRIX: ANNUAL UNIT SHORTAGE PER REPRESENTATIVE & MEDICINE 2026"],
      ["Scope: Delta Region Aggregate | Medical Reps: 9 | Generated: " + new Date().toLocaleString()],
      [],
      [
        "Medical Representative",
        "Territory / Area",
        "Humaxin Mix 70/30 (Units Deficit)",
        "Humaxin Rapid (Units Deficit)",
        "Glargivin UPA (Units Deficit)",
        "Glargivin 100IU (Units Deficit)",
        "Total Unit Shortage (Units)",
        "Total Achievement % (Points)",
        "Q4 So Far % (Points)",
        "Req. Q4 % for 100% Year",
        "Req. Q4 % for 120% Year",
        "Operational Status"
      ]
    ];

    teamData.reps.forEach(r => {
      const status = r.deficitUnits > 0 ? (r.ratio < 70 ? "Critical Deficit" : "Deficit") : "Target Met";
      repRows.push([
        r.name,
        r.note,
        fmtDeficitExcel(r.prodDeficits[1260], true),
        fmtDeficitExcel(r.prodDeficits[1259], true),
        fmtDeficitExcel(r.prodDeficits[1251], true),
        fmtDeficitExcel(r.prodDeficits[1110], true),
        fmtTotalDeficitExcel(r.deficitUnits),
        (r.ratio || 0).toFixed(2) + "%",
        (r.actualQ4Ratio || 0).toFixed(2) + "% (" + Math.round(r.salesValueQ4 || 0).toLocaleString() + " EGP)",
        (r.requiredQ4Ratio || 0).toFixed(2) + "%",
        (r.requiredQ4Ratio_120 || 0).toFixed(2) + "%",
        status
      ]);
    });

    repRows.push([
      "DELTA TEAM TOTAL SHORTAGE",
      "All Territories (9 Reps)",
      fmtDeficitExcel(teamData.products[1260].deficitUnits, true),
      fmtDeficitExcel(teamData.products[1259].deficitUnits, true),
      fmtDeficitExcel(teamData.products[1251].deficitUnits, true),
      fmtDeficitExcel(teamData.products[1110].deficitUnits, true),
      fmtTotalDeficitExcel(teamData.deficitUnits),
      (teamData.ratio || 0).toFixed(2) + "%",
      (teamData.actualQ4Ratio || 0).toFixed(2) + "% (" + Math.round(teamData.salesValueQ4 || 0).toLocaleString() + " EGP)",
      (teamData.requiredQ4Ratio || 0).toFixed(2) + "%",
      (teamData.requiredQ4Ratio_120 || 0).toFixed(2) + "%",
      teamData.deficitUnits > 0 ? "Net Team Deficit" : "Net Team Surplus"
    ]);

    const wsReps = XLSX.utils.aoa_to_sheet(repRows);
    wsReps['!cols'] = [
      { wch: 26 }, // Medical Representative
      { wch: 22 }, // Territory / Area
      { wch: 28 }, // Humaxin Mix 70/30 (Units Deficit)
      { wch: 28 }, // Humaxin Rapid (Units Deficit)
      { wch: 26 }, // Glargivin UPA (Units Deficit)
      { wch: 26 }, // Glargivin 100IU (Units Deficit)
      { wch: 28 }, // Total Unit Shortage (Units)
      { wch: 26 }, // Total Achievement % (Points)
      { wch: 28 }, // Q4 So Far % (Points)
      { wch: 26 }, // Req. Q4 % for 100% Year
      { wch: 26 }, // Req. Q4 % for 120% Year
      { wch: 20 }  // Operational Status
    ];
    wsReps['!merges'] = [
      { s: { r: 0, c: 0 }, e: { r: 0, c: 11 } },
      { s: { r: 1, c: 0 }, e: { r: 1, c: 11 } },
      { s: { r: 2, c: 0 }, e: { r: 2, c: 11 } }
    ];
    wsReps['!rows'] = [
      { hpt: 26 },
      { hpt: 22 },
      { hpt: 18 },
      { hpt: 10 },
      { hpt: 28 }
    ];
    XLSX.utils.book_append_sheet(wb, wsReps, "Manager Matrix - Unit Shortage");

    // ── SHEET 2: MEDICINE SHORTAGE BREAKDOWN ──
    const medRows = [
      ["EVA PHARMA - DELTA REGION SALES DASHBOARD"],
      ["PER-MEDICINE UNIT SHORTAGE BREAKDOWN 2026"],
      ["Scope: Delta Team Aggregate | Total Insulin Products: 4 | Generated: " + new Date().toLocaleString()],
      [],
      [
        "Product Code",
        "Medicine Name",
        "Target Quota (Units)",
        "Actual Units Sold",
        "Net Unit Deficit / Shortage",
        "Points Achievement %",
        "Volume Fulfillment %",
        "Operational Status"
      ]
    ];

    PRODUCTS.forEach(p => {
      const prod = teamData.products[p.id];
      const isDeficit = prod.deficitUnits > 0;
      const status = isDeficit ? (prod.ratio < 70 ? "Critical Deficit" : "Deficit") : "Target Met";
      const volPct = prod.targetUnits > 0 ? ((prod.salesUnits / prod.targetUnits) * 100).toFixed(2) + "%" : "0%";
      medRows.push([
        "#" + prod.pid,
        prod.name,
        Math.round(prod.targetUnits).toLocaleString() + " units",
        Math.round(prod.salesUnits).toLocaleString() + " units",
        fmtTotalDeficitExcel(prod.deficitUnits),
        (prod.ratio || 0).toFixed(2) + "%",
        volPct,
        status
      ]);
    });

    const totalVolPct = teamData.targetUnits > 0 ? ((teamData.salesUnits / teamData.targetUnits) * 100).toFixed(2) + "%" : "0%";
    medRows.push([
      "TOTAL",
      "ALL 4 INSULIN PRODUCTS",
      Math.round(teamData.targetUnits).toLocaleString() + " units",
      Math.round(teamData.salesUnits).toLocaleString() + " units",
      fmtTotalDeficitExcel(teamData.deficitUnits),
      (teamData.ratio || 0).toFixed(2) + "%",
      totalVolPct,
      teamData.deficitUnits > 0 ? "Net Team Shortage" : "Surplus"
    ]);

    const wsMed = XLSX.utils.aoa_to_sheet(medRows);
    wsMed['!cols'] = [
      { wch: 16 }, // Product Code
      { wch: 38 }, // Medicine Name
      { wch: 24 }, // Target Quota (Units)
      { wch: 24 }, // Actual Units Sold
      { wch: 28 }, // Net Unit Deficit / Shortage
      { wch: 24 }, // Points Achievement %
      { wch: 24 }, // Volume Fulfillment %
      { wch: 22 }  // Operational Status
    ];
    wsMed['!merges'] = [
      { s: { r: 0, c: 0 }, e: { r: 0, c: 7 } },
      { s: { r: 1, c: 0 }, e: { r: 1, c: 7 } },
      { s: { r: 2, c: 0 }, e: { r: 2, c: 7 } }
    ];
    wsMed['!rows'] = [
      { hpt: 26 },
      { hpt: 22 },
      { hpt: 18 },
      { hpt: 10 },
      { hpt: 28 }
    ];
    XLSX.utils.book_append_sheet(wb, wsMed, "Team Medicine Breakdown");

    // ── SHEET 3: EXECUTIVE KPI SUMMARY ──
    const kpiRows = [
      ["EVA PHARMA - DELTA REGION SALES DASHBOARD"],
      ["ANNUAL EXECUTIVE KPI SUMMARY 2026"],
      ["Scope: Delta Team Aggregate | Medical Reps: 9 | Generated: " + new Date().toLocaleString()],
      [],
      [
        "Executive KPI Metric",
        "Actual Achieved YTD",
        "Target Quota 2026",
        "Net Deficit / Variance",
        "Achievement Rate %",
        "Strategic Status"
      ],
      [
        "Physical Volume (Units)",
        Math.round(teamData.salesUnits).toLocaleString() + " units",
        Math.round(teamData.targetUnits).toLocaleString() + " units",
        fmtTotalDeficitExcel(teamData.deficitUnits),
        totalVolPct + " (Units)",
        teamData.deficitUnits > 0 ? "Volume Shortage" : "Volume Surpassed"
      ],
      [
        "Achievement Currency (Points)",
        Math.round(teamData.salesPoints).toLocaleString() + " pts",
        Math.round(teamData.targetPoints).toLocaleString() + " pts",
        "-" + Math.round(teamData.deficitPoints).toLocaleString() + " pts",
        (teamData.ratio || 0).toFixed(2) + "% (Points)",
        teamData.ratio >= 100 ? "Quota Met" : (teamData.ratio >= 80 ? "On Track" : "Action Needed")
      ],
      [
        "Sales Revenue Value (EGP)",
        Math.round(teamData.salesValue).toLocaleString() + " EGP",
        Math.round(teamData.targetValue).toLocaleString() + " EGP",
        "-" + Math.round(teamData.deficitValue).toLocaleString() + " EGP",
        (teamData.targetValue > 0 ? ((teamData.salesValue / teamData.targetValue) * 100).toFixed(2) : "0") + "% (EGP)",
        teamData.salesValue >= teamData.targetValue ? "Surpassed" : "Under Target"
      ],
      [
        "Q4 Performance Achieved So Far",
        Math.round(teamData.salesPointsQ4).toLocaleString() + " pts (" + Math.round(teamData.salesValueQ4).toLocaleString() + " EGP)",
        Math.round(teamData.targetPointsQ4).toLocaleString() + " pts (" + Math.round(teamData.targetValueQ4).toLocaleString() + " EGP)",
        "-" + Math.round((teamData.targetPointsQ4 - teamData.salesPointsQ4)).toLocaleString() + " pts remaining in Q4",
        (teamData.actualQ4Ratio || 0).toFixed(2) + "% Achieved in Q4",
        teamData.actualQ4Ratio >= 100 ? "Q4 Target Met" : "Q4 In Progress"
      ],
      [
        "Required Q4 Target for 100% Year",
        Math.round(teamData.neededPointsQ4).toLocaleString() + " pts (Needed in Q4)",
        Math.round(teamData.targetPointsQ4).toLocaleString() + " pts (Q4 Target Quota)",
        "Remaining: " + Math.round(teamData.neededPointsQ4).toLocaleString() + " pts",
        (teamData.requiredQ4Ratio || 0).toFixed(2) + "% Required in Q4",
        teamData.requiredQ4Ratio > 100 ? "High Deficit" : "Achievable Target"
      ],
      [
        "Required Q4 Target for 120% Year",
        Math.round(teamData.neededPointsQ4_120).toLocaleString() + " pts (Needed in Q4)",
        Math.round(teamData.targetPointsQ4).toLocaleString() + " pts (Q4 Target Quota)",
        "Remaining: " + Math.round(teamData.neededPointsQ4_120).toLocaleString() + " pts",
        (teamData.requiredQ4Ratio_120 || 0).toFixed(2) + "% Required in Q4",
        teamData.requiredQ4Ratio_120 > 120 ? "High Challenge" : "Achievable Target"
      ]
    ];

    const wsKpi = XLSX.utils.aoa_to_sheet(kpiRows);
    wsKpi['!cols'] = [
      { wch: 34 },
      { wch: 26 },
      { wch: 26 },
      { wch: 28 },
      { wch: 26 },
      { wch: 24 }
    ];
    wsKpi['!merges'] = [
      { s: { r: 0, c: 0 }, e: { r: 0, c: 5 } },
      { s: { r: 1, c: 0 }, e: { r: 1, c: 5 } },
      { s: { r: 2, c: 0 }, e: { r: 2, c: 5 } }
    ];
    wsKpi['!rows'] = [
      { hpt: 26 },
      { hpt: 22 },
      { hpt: 18 },
      { hpt: 10 },
      { hpt: 28 }
    ];
    XLSX.utils.book_append_sheet(wb, wsKpi, "Executive KPI Summary");

    XLSX.writeFile(wb, "EVA_Delta_Team_Unit_Deficit_Report_2026.xlsx");
  } else {
    // SINGLE REP SCOPE
    const repData = computeSingleRepDeficit(targetType);
    if (!repData) return;
    const rep = repData.rep;

    // Sheet 1: Per-Medicine Shortage Breakdown
    const medRows = [
      ["EVA PHARMA - DELTA REGION SALES DASHBOARD"],
      ["PERSONAL ANNUAL UNIT DEFICIT REPORT 2026"],
      ["Representative: " + rep.name, "Territory: " + rep.note, "", "Generated: " + new Date().toLocaleString()],
      [],
      [
        "Product Code",
        "Medicine Name",
        "Target Quota (Units)",
        "Actual Units Sold",
        "Net Unit Deficit / Shortage",
        "Points Achievement %",
        "Volume Fulfillment %",
        "Operational Status"
      ]
    ];

    repData.products.forEach(prod => {
      const isDeficit = prod.deficitUnits > 0;
      const status = isDeficit ? (prod.ratio < 70 ? "Critical Deficit" : "Deficit") : "Target Met";
      const volPct = prod.targetUnits > 0 ? ((prod.salesUnits / prod.targetUnits) * 100).toFixed(2) + "%" : "0%";
      medRows.push([
        "#" + prod.pid,
        prod.name,
        Math.round(prod.targetUnits).toLocaleString() + " units",
        Math.round(prod.salesUnits).toLocaleString() + " units",
        fmtTotalDeficitExcel(prod.deficitUnits),
        (prod.ratio || 0).toFixed(2) + "%",
        volPct,
        status
      ]);
    });

    const totalVolPct = repData.targetUnits > 0 ? ((repData.salesUnits / repData.targetUnits) * 100).toFixed(2) + "%" : "0%";
    medRows.push([
      "TOTAL",
      "ALL 4 INSULIN PRODUCTS",
      Math.round(repData.targetUnits).toLocaleString() + " units",
      Math.round(repData.salesUnits).toLocaleString() + " units",
      fmtTotalDeficitExcel(repData.deficitUnits),
      (repData.ratio || 0).toFixed(2) + "%",
      totalVolPct,
      repData.deficitUnits > 0 ? "Net Unit Shortage" : "Surplus"
    ]);

    const wsMed = XLSX.utils.aoa_to_sheet(medRows);
    wsMed['!cols'] = [
      { wch: 16 },
      { wch: 38 },
      { wch: 24 },
      { wch: 24 },
      { wch: 28 },
      { wch: 24 },
      { wch: 24 },
      { wch: 22 }
    ];
    wsMed['!merges'] = [
      { s: { r: 0, c: 0 }, e: { r: 0, c: 7 } },
      { s: { r: 1, c: 0 }, e: { r: 1, c: 7 } },
      { s: { r: 2, c: 0 }, e: { r: 2, c: 7 } }
    ];
    wsMed['!rows'] = [
      { hpt: 26 },
      { hpt: 22 },
      { hpt: 18 },
      { hpt: 10 },
      { hpt: 28 }
    ];
    XLSX.utils.book_append_sheet(wb, wsMed, "Medicine Shortage Breakdown");

    // Sheet 2: Personal KPI Summary
    const kpiRows = [
      ["EVA PHARMA - DELTA REGION SALES DASHBOARD"],
      ["PERSONAL PERFORMANCE & QUOTA SUMMARY 2026"],
      ["Representative: " + rep.name, "Territory: " + rep.note, "", "Generated: " + new Date().toLocaleString()],
      [],
      [
        "Performance Metric",
        "Actual Achieved YTD",
        "Target Quota 2026",
        "Net Deficit / Variance",
        "Achievement Rate %",
        "Status"
      ],
      [
        "Physical Volume (Units)",
        Math.round(repData.salesUnits).toLocaleString() + " units",
        Math.round(repData.targetUnits).toLocaleString() + " units",
        fmtTotalDeficitExcel(repData.deficitUnits),
        totalVolPct + " (Units)",
        repData.deficitUnits > 0 ? "Volume Deficit" : "Volume Surpassed"
      ],
      [
        "Achievement Currency (Points)",
        Math.round(repData.salesPoints).toLocaleString() + " pts",
        Math.round(repData.targetPoints).toLocaleString() + " pts",
        "-" + Math.round(repData.deficitPoints).toLocaleString() + " pts",
        (repData.ratio || 0).toFixed(2) + "% (Points)",
        repData.ratio >= 100 ? "Target Met" : (repData.ratio >= 80 ? "On Track" : "Needs Push")
      ],
      [
        "Sales Revenue Value (EGP)",
        Math.round(repData.salesValue).toLocaleString() + " EGP",
        Math.round(repData.targetValue).toLocaleString() + " EGP",
        "-" + Math.round(repData.deficitValue).toLocaleString() + " EGP",
        (repData.targetValue > 0 ? ((repData.salesValue / repData.targetValue) * 100).toFixed(2) : "0") + "% (EGP)",
        repData.salesValue >= repData.targetValue ? "Surpassed" : "Under Target"
      ],
      [
        "Q4 Performance Achieved So Far",
        Math.round(repData.salesPointsQ4).toLocaleString() + " pts (" + Math.round(repData.salesValueQ4).toLocaleString() + " EGP)",
        Math.round(repData.targetPointsQ4).toLocaleString() + " pts (" + Math.round(repData.targetValueQ4).toLocaleString() + " EGP)",
        "-" + Math.round((repData.targetPointsQ4 - repData.salesPointsQ4)).toLocaleString() + " pts remaining in Q4",
        (repData.actualQ4Ratio || 0).toFixed(2) + "% Achieved in Q4",
        repData.actualQ4Ratio >= 100 ? "Q4 Target Met" : "Q4 In Progress"
      ],
      [
        "Required Q4 Target for 100% Year",
        Math.round(repData.neededPointsQ4).toLocaleString() + " pts (Needed in Q4)",
        Math.round(repData.targetPointsQ4).toLocaleString() + " pts (Q4 Target Quota)",
        "Remaining: " + Math.round(repData.neededPointsQ4).toLocaleString() + " pts",
        (repData.requiredQ4Ratio || 0).toFixed(2) + "% Required in Q4",
        repData.requiredQ4Ratio > 100 ? "Critical Deficit" : "Achievable Target"
      ],
      [
        "Required Q4 Target for 120% Year",
        Math.round(repData.neededPointsQ4_120).toLocaleString() + " pts (Needed in Q4)",
        Math.round(repData.targetPointsQ4).toLocaleString() + " pts (Q4 Target Quota)",
        "Remaining: " + Math.round(repData.neededPointsQ4_120).toLocaleString() + " pts",
        (repData.requiredQ4Ratio_120 || 0).toFixed(2) + "% Required in Q4",
        repData.requiredQ4Ratio_120 > 120 ? "High Challenge" : "Achievable Target"
      ]
    ];

    const wsKpi = XLSX.utils.aoa_to_sheet(kpiRows);
    wsKpi['!cols'] = [
      { wch: 34 },
      { wch: 26 },
      { wch: 26 },
      { wch: 28 },
      { wch: 26 },
      { wch: 24 }
    ];
    wsKpi['!merges'] = [
      { s: { r: 0, c: 0 }, e: { r: 0, c: 5 } },
      { s: { r: 1, c: 0 }, e: { r: 1, c: 5 } },
      { s: { r: 2, c: 0 }, e: { r: 2, c: 5 } }
    ];
    wsKpi['!rows'] = [
      { hpt: 26 },
      { hpt: 22 },
      { hpt: 18 },
      { hpt: 10 },
      { hpt: 28 }
    ];
    XLSX.utils.book_append_sheet(wb, wsKpi, "Personal KPI Summary");

    const cleanName = rep.name.replace(/[^a-zA-Z0-9]/g, "_");
    XLSX.writeFile(wb, `EVA_Unit_Deficit_Report_${cleanName}_2026.xlsx`);
  }

  showToast("📊 Excel report downloaded with clean, structured formatting!");
}

function copyDeficitSummary(targetType) {
  targetType = targetType || currentReportScope || 'team';
  if (currentUser && currentUser.repKey) targetType = currentUser.repKey;

  const isTeam = targetType === 'team';
  let text = '';

  if (isTeam) {
    const d = computeTeamDeficit();
    const unitDeficitStr = d.deficitUnits > 0 ? `Deficit (-${fmt(d.deficitUnits)} units)` : `Surplus (+${fmt(Math.abs(d.deficitUnits))} units)`;

    text = `📊 *EVA PHARMA - DELTA TEAM*
*Annual Unit Deficit & Points Achievement Report 2026*
━━━━━━━━━━━━━━━━━━━━
🎯 *Delta Team Overall Status:*
• Target Quota (Units): ${fmt(d.targetUnits)} units
• Actual Units Sold: ${fmt(d.salesUnits)} units
• Net Unit Deficit: ${unitDeficitStr}
• Total Achievement Rate (Points): ${fmtPct(d.ratio)}
  (Sales Points: ${fmt(d.salesPoints)} pts | Target Points: ${fmt(d.targetPoints)} pts)
• Q4 Actual Achieved So Far: ${fmtPct(d.actualQ4Ratio)}
  (Sales: ${fmt(d.salesValueQ4)} EGP | ${fmt(d.salesPointsQ4)} pts of ${fmt(d.targetPointsQ4)} Q4 target pts)
• Required in Q4 to Hit 100% Annual Quota: ${fmtPct(d.requiredQ4Ratio)}
  (Needs ${fmt(d.neededPointsQ4)} pts of ${fmt(d.targetPointsQ4)} Q4 target pts)
• Required in Q4 to Hit 120% Annual Super-Achievement: ${fmtPct(d.requiredQ4Ratio_120)}
  (Needs ${fmt(d.neededPointsQ4_120)} pts of ${fmt(d.targetPointsQ4)} Q4 target pts)

━━━━━━━━━━━━━━━━━━━━
💊 *Per-Medicine Unit Shortage & Points Achievement:*
`;

    PRODUCTS.forEach((p, idx) => {
      const prod = d.products[p.id];
      const uDef = prod.deficitUnits > 0 ? `Deficit -${fmt(prod.deficitUnits)} units` : `Target Met (+${fmt(Math.abs(prod.deficitUnits))} units)`;
      text += `${idx + 1}️⃣ *${prod.name}* (#${prod.pid}): ${uDef} | Points Ach.: ${fmtPct(prod.ratio)}\n`;
    });

    text += `\n━━━━━━━━━━━━━━━━━━━━\n👥 *Manager's Matrix (Unit Shortage per Rep & Quota Fulfillment):*\n`;

    d.reps.forEach(r => {
      const defMix = r.prodDeficits[1260] > 0 ? `-${fmt(r.prodDeficits[1260])}` : `+${fmt(Math.abs(r.prodDeficits[1260]))}`;
      const defRap = r.prodDeficits[1259] > 0 ? `-${fmt(r.prodDeficits[1259])}` : `+${fmt(Math.abs(r.prodDeficits[1259]))}`;
      const defUPA = r.prodDeficits[1251] > 0 ? `-${fmt(r.prodDeficits[1251])}` : `+${fmt(Math.abs(r.prodDeficits[1251]))}`;
      const def100 = r.prodDeficits[1110] > 0 ? `-${fmt(r.prodDeficits[1110])}` : `+${fmt(Math.abs(r.prodDeficits[1110]))}`;
      const totDef = r.deficitUnits > 0 ? `Deficit (-${fmt(r.deficitUnits)} u)` : `Surplus (+${fmt(Math.abs(r.deficitUnits))} u)`;
      text += `• *${r.name}* (${r.note}):\n  - Mix: ${defMix} | Rapid: ${defRap} | UPA: ${defUPA} | 100IU: ${def100}\n  - Total: ${totDef} | YTD Ach: ${fmtPct(r.ratio)} | Q4 So Far: ${fmtPct(r.actualQ4Ratio)} | Req 100%: ${fmtPct(r.requiredQ4Ratio)} | Req 120%: ${fmtPct(r.requiredQ4Ratio_120)}\n`;
    });

    const topDeficit = Object.values(d.products).reduce((max, cur) => cur.deficitUnits > max.deficitUnits ? cur : max);
    if (topDeficit && topDeficit.deficitUnits > 0) {
      text += `\n━━━━━━━━━━━━━━━━━━━━\n⚠️ *Top Priority Deficit SKU:* ${topDeficit.name} (-${fmt(topDeficit.deficitUnits)} units)`;
    }

    text += `\n━━━━━━━━━━━━━━━━━━━━\n📅 Report Date: ${new Date().toLocaleDateString('en-GB')}`;
  } else {
    const repData = computeSingleRepDeficit(targetType);
    if (!repData) return;
    const rep = repData.rep;
    const unitDeficitStr = repData.deficitUnits > 0 ? `Deficit (-${fmt(repData.deficitUnits)} units)` : `Surplus (+${fmt(Math.abs(repData.deficitUnits))} units)`;

    text = `📊 *EVA PHARMA - DELTA TEAM*
*Personal Unit Deficit & Points Achievement Report 2026*
👤 *Representative:* ${rep.name} (${rep.note})
━━━━━━━━━━━━━━━━━━━━
🎯 *Personal Overall Performance:*
• Target Quota (Units): ${fmt(repData.targetUnits)} units
• Actual Units Sold: ${fmt(repData.salesUnits)} units
• Net Unit Deficit: ${unitDeficitStr}
• Total Achievement Rate (Points): ${fmtPct(repData.ratio)}
  (Sales Points: ${fmt(repData.salesPoints)} pts | Target Points: ${fmt(repData.targetPoints)} pts)
• Q4 Actual Achieved So Far: ${fmtPct(repData.actualQ4Ratio)}
  (Sales: ${fmt(repData.salesValueQ4)} EGP | ${fmt(repData.salesPointsQ4)} pts of ${fmt(repData.targetPointsQ4)} Q4 target pts)
• Required in Q4 to Hit 100% Annual Quota: ${fmtPct(repData.requiredQ4Ratio)}
  (Needs ${fmt(repData.neededPointsQ4)} pts of ${fmt(repData.targetPointsQ4)} Q4 target pts)
• Required in Q4 to Hit 120% Annual Super-Achievement: ${fmtPct(repData.requiredQ4Ratio_120)}
  (Needs ${fmt(repData.neededPointsQ4_120)} pts of ${fmt(repData.targetPointsQ4)} Q4 target pts)

━━━━━━━━━━━━━━━━━━━━
💊 *Per-Medicine Shortage & Points Achievement:*
`;

    repData.products.forEach((prod, idx) => {
      const uDef = prod.deficitUnits > 0 ? `Deficit -${fmt(prod.deficitUnits)} units` : `Target Met (+${fmt(Math.abs(prod.deficitUnits))} units)`;
      text += `${idx + 1}️⃣ *${prod.name}* (#${prod.pid}): ${uDef} | Points Ach.: ${fmtPct(prod.ratio)}\n`;
    });

    const topDeficit = repData.products.reduce((max, cur) => cur.deficitUnits > max.deficitUnits ? cur : max);
    if (topDeficit && topDeficit.deficitUnits > 0) {
      text += `\n━━━━━━━━━━━━━━━━━━━━\n⚠️ *Top Priority SKU to Focus:* ${topDeficit.name} (-${fmt(topDeficit.deficitUnits)} units)`;
    }

    text += `\n━━━━━━━━━━━━━━━━━━━━\n📅 Report Date: ${new Date().toLocaleDateString('en-GB')}`;
  }

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      showToast("📋 Report summary copied! Ready to paste into WhatsApp.");
    }).catch(() => {
      fallbackCopy(text);
    });
  } else {
    fallbackCopy(text);
  }
}

function fallbackCopy(text) {
  const ta = document.createElement("textarea");
  ta.value = text;
  document.body.appendChild(ta);
  ta.select();
  document.execCommand("copy");
  document.body.removeChild(ta);
  showToast("📋 Report summary copied! Ready to paste into WhatsApp.");
}

function showToast(msg) {
  const toast = document.getElementById('toastNotification');
  if (!toast) return;
  toast.innerHTML = `<span>${msg}</span>`;
  toast.classList.add('visible');
  setTimeout(() => {
    toast.classList.remove('visible');
  }, 3500);
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeDeficitReport();
});

/* ── INIT ── */
document.addEventListener('DOMContentLoaded', () => {
  const now = new Date();
  document.getElementById('topbar-date').textContent =
    now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  
  checkAuthStatus();
});

/* ── Q4 PRODUCT UNITS FORECAST & GLARGIVIN UPA DUAL SIMULATOR ── */

const SIM_PROD_META = {
  1260: { 
    id: 1260, 
    name: 'Humaxin Mix 70/30', 
    short: 'Mix 70/30', 
    pack: '5 Cartridges (OFP-CD-0284.02)', 
    icon: '📦', 
    price: 232.128, 
    ptsPerUnit: 464.256, 
    color: '#3b82f6', 
    isUpa: false 
  },
  1259: { 
    id: 1259, 
    name: 'Humaxin Rapid', 
    short: 'Rapid', 
    pack: '5 Cartridges (OFP-CD-0284)', 
    icon: '⚡', 
    price: 232.128, 
    ptsPerUnit: 464.256, 
    color: '#10b981', 
    isUpa: false 
  },
  1110: { 
    id: 1110, 
    name: 'Glargivin 100IU', 
    short: 'Glargivin 100IU', 
    pack: '5 Cartridges (Commercial Retail)', 
    icon: '💉', 
    price: 669.60, 
    ptsPerUnit: 1339.20, 
    color: '#8b5cf6', 
    isUpa: false 
  },
  1251: { 
    id: 1251, 
    name: 'Glargivin UPA', 
    short: 'Glargivin UPA', 
    pack: '5 Cartridges (Institutional Tender)', 
    icon: '🏛️', 
    price: 603.25, 
    ptsPerUnit: 1206.50, 
    color: '#f59e0b', 
    isUpa: true 
  }
};

// Global state for product units forecasting
let prodForecastUnits = {}; // { [pid]: number of units }
let currentUpaSimMode = 'target'; // 'target' (rebalancing target = sales/X) or 'sales' (direct units credit)
let currentUpaRepFilter = 'all';
let repUnitOverrides = {}; // { [repKey]: { [pid]: number of units } }
let activeEditingRepKey = null; // for rep units edit modal

// Compute baseline team stats for Q4 products from current REPS data
function getTeamProductStats() {
  const stats = {
    1260: { targetUnits: 0, actualUnits: 0, targetPoints: 0, actualPoints: 0, targetValue: 0, actualValue: 0 },
    1259: { targetUnits: 0, actualUnits: 0, targetPoints: 0, actualPoints: 0, targetValue: 0, actualValue: 0 },
    1110: { targetUnits: 0, actualUnits: 0, targetPoints: 0, actualPoints: 0, targetValue: 0, actualValue: 0 },
    1251: { targetUnits: 0, actualUnits: 0, targetPoints: 0, actualPoints: 0, targetValue: 0, actualValue: 0 }
  };

  REPS.forEach(r => {
    if (r.noData) return;
    const q4 = r.quarters && r.quarters['Q4'];
    if (!q4 || !q4.products) return;
    q4.products.forEach(p => {
      const pid = p.pid;
      if (stats[pid]) {
        stats[pid].targetUnits += Number(p.targetUnits || 0);
        stats[pid].actualUnits += Number(p.salesUnits || 0);
        const sv = Number(p.salesValue || 0);
        const sp = (p.salesPoints !== null && p.salesPoints !== undefined) ? Number(p.salesPoints) : (sv * 2);
        const tp = (p.targetPoints !== null && p.targetPoints !== undefined) ? Number(p.targetPoints) : (Number(p.targetValue || 0) * 2);
        stats[pid].actualPoints += sp;
        stats[pid].targetPoints += tp;
        stats[pid].targetValue += Number(p.targetValue || 0);
        stats[pid].actualValue += sv;
      }
    });
  });

  return stats;
}

// Initialize default units (85% commercial, 100% UPA)
function initDefaultUnits() {
  const stats = getTeamProductStats();
  prodForecastUnits = {
    1260: stats[1260].targetUnits * 0.85,
    1259: stats[1259].targetUnits * 0.85,
    1110: stats[1110].targetUnits * 0.85,
    1251: stats[1251].targetUnits * 1.00
  };
}

// Master preset setter
function setMasterTeamPreset(type) {
  const stats = getTeamProductStats();
  if (type === 'actual') {
    Object.keys(SIM_PROD_META).forEach(pid => {
      prodForecastUnits[pid] = stats[pid].actualUnits;
    });
  } else if (type === '85comm_100upa') {
    prodForecastUnits[1260] = stats[1260].targetUnits * 0.85;
    prodForecastUnits[1259] = stats[1259].targetUnits * 0.85;
    prodForecastUnits[1110] = stats[1110].targetUnits * 0.85;
    prodForecastUnits[1251] = stats[1251].targetUnits * 1.00;
  } else {
    const pct = parseFloat(type) / 100.0;
    Object.keys(SIM_PROD_META).forEach(pid => {
      prodForecastUnits[pid] = stats[pid].targetUnits * pct;
    });
  }
  renderUpaSimulator(true);
}

// Individual product preset chip setter
function setProductPresetChip(pid, type) {
  const stats = getTeamProductStats();
  if (type === 'actual') {
    prodForecastUnits[pid] = stats[pid].actualUnits;
  } else {
    const pct = parseFloat(type) / 100.0;
    prodForecastUnits[pid] = stats[pid].targetUnits * pct;
  }
  renderUpaSimulator(true);
}

// Individual product unit input handler
function onProductUnitChange(pid, val) {
  let num = parseFloat(val);
  if (isNaN(num) || num < 0) num = 0;
  prodForecastUnits[pid] = num;
  renderUpaSimulator(false);
}

// Individual product slider handler
function onProductSliderChange(pid, val) {
  let num = parseFloat(val);
  if (isNaN(num) || num < 0) num = 0;
  prodForecastUnits[pid] = num;
  const inputEl = document.getElementById(`prodUnitInput_${pid}`);
  if (inputEl) inputEl.value = Math.round(num);
  renderUpaSimulator(false);
}

function setUpaEqualizationMode(mode) {
  currentUpaSimMode = mode;
  renderUpaSimulator(true);
}

function setUpaRepFilter(filter) {
  currentUpaRepFilter = filter;
  renderUpaSimulator(false);
}

function openUpaSimulator(repKey) {
  currentUpaRepFilter = repKey || 'all';
  if (!prodForecastUnits[1260]) {
    initDefaultUnits();
  }
  const modal = document.getElementById('upaSimModal');
  if (!modal) return;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
  renderUpaSimulator(true);
}

function closeUpaSimulator() {
  const modal = document.getElementById('upaSimModal');
  if (!modal) return;
  modal.classList.remove('active');
  document.body.style.overflow = '';
}

// Rep unit overrides management
function openRepUnitEditor(repKey) {
  activeEditingRepKey = repKey;
  renderUpaSimulator(false);
}

function closeRepUnitEditor() {
  activeEditingRepKey = null;
  renderUpaSimulator(false);
}

function onRepCustomUnitChange(repKey, pid, val) {
  let num = parseFloat(val);
  if (isNaN(num) || num < 0) num = 0;
  if (!repUnitOverrides[repKey]) repUnitOverrides[repKey] = {};
  repUnitOverrides[repKey][pid] = num;
  renderUpaSimulator(false);
}

function resetSingleRepUnitOverrides(repKey) {
  delete repUnitOverrides[repKey];
  renderUpaSimulator(false);
}

function resetAllRepUnitOverrides() {
  repUnitOverrides = {};
  renderUpaSimulator(false);
}

/* ── SIMULATION ENGINE: UNITS TO ACHIEVEMENT % ── */
function computeUnitsSimulation(unitsDict, upaMode, repOverrides) {
  const stats = getTeamProductStats();
  unitsDict = unitsDict || prodForecastUnits;
  repOverrides = repOverrides || repUnitOverrides;

  // Glargivin UPA Line rate derived directly from its forecast units
  const upaTgtUnits = stats[1251].targetUnits;
  const upaFcUnits = unitsDict[1251] !== undefined ? unitsDict[1251] : stats[1251].actualUnits;
  const upaAchPct = upaTgtUnits > 0 ? (upaFcUnits / upaTgtUnits * 100) : 100.0;
  const F_upa = upaAchPct / 100.0;

  // Product-level simulated aggregates
  const prodSim = {};
  Object.keys(SIM_PROD_META).forEach(pid => {
    const meta = SIM_PROD_META[pid];
    const s = stats[pid];
    const fcUnits = unitsDict[pid] !== undefined ? unitsDict[pid] : s.actualUnits;
    const fcPoints = fcUnits * meta.ptsPerUnit;
    const fcValue = fcUnits * meta.price;
    const achPct = s.targetUnits > 0 ? (fcUnits / s.targetUnits * 100) : 0;
    prodSim[pid] = {
      meta,
      targetUnits: s.targetUnits,
      actualUnits: s.actualUnits,
      forecastUnits: fcUnits,
      forecastPoints: fcPoints,
      forecastValue: fcValue,
      achPct,
      ptsPerUnit: meta.ptsPerUnit,
      unitPrice: meta.price
    };
  });

  let team = {
    origQ4Sp: 0, origQ4Tp: 0, origQ4Sv: 0,
    simQ4Sp: 0, simQ4Tp: 0, simQ4Sv: 0,
    spQ1Q3: 0, tpQ1Q3: 0,
    origYtdSp: 0, origYtdTp: 0,
    simYtdSp: 0, simYtdTp: 0,
    totalForecastUnits: 0,
    totalTargetUnits: 0,
    totalActualUnits: 0
  };

  const repsSim = [];

  REPS.forEach(r => {
    if (r.noData) return;
    const q4 = r.quarters && r.quarters['Q4'];
    const q4Prods = q4 && q4.products ? q4.products : [];
    if (!q4Prods.length) return;

    let repOrigQ4Sp = 0, repOrigQ4Tp = 0, repOrigQ4Sv = 0;
    let repSimQ4Sp = 0, repSimQ4Tp = 0, repSimQ4Sv = 0;
    const repProdsMap = {};
    const hasOverrides = !!(repOverrides[r.key] && Object.keys(repOverrides[r.key]).length > 0);

    // Q1-Q3 points
    let spQ1Q3 = 0, tpQ1Q3 = 0;
    ['Q1', 'Q2', 'Q3'].forEach(q => {
      const qd = r.quarters && r.quarters[q];
      if (qd && qd.products) {
        qd.products.forEach(p => {
          const sv = (p.salesValue !== null && p.salesValue !== undefined) ? Number(p.salesValue) : 0;
          const sp = (p.salesPoints !== null && p.salesPoints !== undefined) ? Number(p.salesPoints) : (sv * 2);
          const tp = (p.targetPoints !== null && p.targetPoints !== undefined) ? Number(p.targetPoints) : ((p.targetValue || 0) * 2);
          spQ1Q3 += sp;
          tpQ1Q3 += tp;
        });
      }
    });

    q4Prods.forEach(p => {
      const pid = p.pid;
      const meta = SIM_PROD_META[pid];
      if (!meta) return;

      const actU = Number(p.salesUnits || 0);
      const tgtU = Number(p.targetUnits || 0);
      const sv = (p.salesValue !== null && p.salesValue !== undefined) ? Number(p.salesValue) : 0;
      const actSp = (p.salesPoints !== null && p.salesPoints !== undefined) ? Number(p.salesPoints) : (sv * 2);
      const tgtSp = (p.targetPoints !== null && p.targetPoints !== undefined) ? Number(p.targetPoints) : ((p.targetValue || 0) * 2);

      repOrigQ4Sp += actSp;
      repOrigQ4Tp += tgtSp;
      repOrigQ4Sv += sv;

      // Determine rep's forecast units for this product
      let repFcUnits = 0;
      const isPidOverridden = (repOverrides[r.key] && repOverrides[r.key][pid] !== undefined);

      if (isPidOverridden) {
        repFcUnits = Number(repOverrides[r.key][pid]);
      } else {
        const teamTgt = stats[pid].targetUnits;
        const teamFc = unitsDict[pid] !== undefined ? unitsDict[pid] : stats[pid].actualUnits;
        const ratio = teamTgt > 0 ? (teamFc / teamTgt) : 1.0;
        repFcUnits = Math.max(actU, tgtU * ratio);
      }

      const repFcPoints = repFcUnits * meta.ptsPerUnit;
      const repFcValue = repFcUnits * meta.price;

      // Glargivin UPA Equalization calculation
      if (pid === 1251) {
        if (upaMode === 'target') {
          // Target Rebalancing: Target adjusts so sales / target = upaAchPct
          const simUpaTp = F_upa > 0 ? (actSp / F_upa) : tgtSp;
          repSimQ4Tp += simUpaTp;
          repSimQ4Sp += actSp;
          repSimQ4Sv += (actSp / 2);
          repProdsMap[pid] = {
            units: actU,
            points: actSp,
            targetUnits: tgtU,
            actualUnits: actU,
            simTargetPoints: simUpaTp,
            isOverridden: isPidOverridden
          };
        } else {
          // Direct units / sales credit
          repSimQ4Tp += tgtSp;
          repSimQ4Sp += repFcPoints;
          repSimQ4Sv += repFcValue;
          repProdsMap[pid] = {
            units: repFcUnits,
            points: repFcPoints,
            targetUnits: tgtU,
            actualUnits: actU,
            simTargetPoints: tgtSp,
            isOverridden: isPidOverridden
          };
        }
      } else {
        // Commercial products
        repSimQ4Tp += tgtSp;
        repSimQ4Sp += repFcPoints;
        repSimQ4Sv += repFcValue;
        repProdsMap[pid] = {
          units: repFcUnits,
          points: repFcPoints,
          targetUnits: tgtU,
          actualUnits: actU,
          simTargetPoints: tgtSp,
          isOverridden: isPidOverridden
        };
      }
    });

    const origQ4Ratio = repOrigQ4Tp > 0 ? (repOrigQ4Sp / repOrigQ4Tp) * 100 : 0;
    const simQ4Ratio = repSimQ4Tp > 0 ? (repSimQ4Sp / repSimQ4Tp) * 100 : 0;

    const origYtdSp = spQ1Q3 + repOrigQ4Sp;
    const origYtdTp = tpQ1Q3 + repOrigQ4Tp;
    const origYtdRatio = origYtdTp > 0 ? (origYtdSp / origYtdTp) * 100 : 0;

    const simYtdSp = spQ1Q3 + repSimQ4Sp;
    const simYtdTp = tpQ1Q3 + repSimQ4Tp;
    const simYtdRatio = simYtdTp > 0 ? (simYtdSp / simYtdTp) * 100 : 0;

    team.origQ4Sp += repOrigQ4Sp;
    team.origQ4Tp += repOrigQ4Tp;
    team.origQ4Sv += repOrigQ4Sv;
    team.simQ4Sp += repSimQ4Sp;
    team.simQ4Tp += repSimQ4Tp;
    team.simQ4Sv += repSimQ4Sv;
    team.spQ1Q3 += spQ1Q3;
    team.tpQ1Q3 += tpQ1Q3;
    team.origYtdSp += origYtdSp;
    team.origYtdTp += origYtdTp;
    team.simYtdSp += simYtdSp;
    team.simYtdTp += simYtdTp;

    repsSim.push({
      rep: r,
      key: r.key,
      name: r.name,
      area: r.area || 'Delta Region',
      hasOverrides,
      prodsMap: repProdsMap,
      origQ4Sp: repOrigQ4Sp, 
      origQ4Tp: repOrigQ4Tp, 
      origQ4Ratio, 
      origQ4Sv: repOrigQ4Sv,
      simQ4Sp: repSimQ4Sp, 
      simQ4Tp: repSimQ4Tp, 
      simQ4Ratio, 
      simQ4Sv: repSimQ4Sv,
      origYtdSp, origYtdTp, origYtdRatio,
      simYtdSp, simYtdTp, simYtdRatio,
      q4RatioDiff: simQ4Ratio - origQ4Ratio,
      ytdRatioDiff: simYtdRatio - origYtdRatio,
      ptsDiff: simYtdSp - origYtdSp,
      is100Met: simYtdRatio >= 100,
      is120Met: simYtdRatio >= 120
    });
  });

  team.origQ4Ratio = team.origQ4Tp > 0 ? (team.origQ4Sp / team.origQ4Tp) * 100 : 0;
  team.simQ4Ratio = team.simQ4Tp > 0 ? (team.simQ4Sp / team.simQ4Tp) * 100 : 0;
  team.origYtdRatio = team.origYtdTp > 0 ? (team.origYtdSp / team.origYtdTp) * 100 : 0;
  team.simYtdRatio = team.simYtdTp > 0 ? (team.simYtdSp / team.simYtdTp) * 100 : 0;
  team.q4RatioDiff = team.simQ4Ratio - team.origQ4Ratio;
  team.ytdRatioDiff = team.simYtdRatio - team.origYtdRatio;
  team.ptsDiff = team.simYtdSp - team.origYtdSp;

  // Milestone checks
  team.is100Met = team.simYtdRatio >= 100;
  team.is120Met = team.simYtdRatio >= 120;
  team.gap100Pts = team.is100Met ? (team.simYtdSp - team.simYtdTp) : (team.simYtdTp - team.simYtdSp);
  const target120Pts = team.simYtdTp * 1.20;
  team.gap120Pts = team.is120Met ? (team.simYtdSp - target120Pts) : (target120Pts - team.simYtdSp);

  return {
    team,
    reps: repsSim,
    prodSim,
    upaAchPct,
    upaMode
  };
}

/* ── RENDER SIMULATOR UI ── */
function renderUpaSimulator(rebuildControls = true) {
  const bodyEl = document.getElementById('upaSimModalBody');
  if (!bodyEl) return;

  if (!prodForecastUnits[1260]) {
    initDefaultUnits();
  }

  const sim = computeUnitsSimulation(prodForecastUnits, currentUpaSimMode, repUnitOverrides);
  const team = sim.team;
  const prodSim = sim.prodSim;

  const overrideKeys = Object.keys(repUnitOverrides);
  const hasOverrides = overrideKeys.length > 0;
  const overrideCount = overrideKeys.length;

  const masterPresets = [
    { label: '33.1% (Actual Units)', val: 'actual' },
    { label: '75% Target', val: '75' },
    { label: '80% Target', val: '80' },
    { label: '85% Target', val: '85' },
    { label: '90% Target', val: '90' },
    { label: '95% Target', val: '95' },
    { label: '100% Target (Quota)', val: '100' },
    { label: '110% Target', val: '110' },
    { label: '120% (Incentive)', val: '120' },
    { label: '85% Comm + 100% UPA', val: '85comm_100upa' }
  ];

  let html = `
    <!-- TOP EXECUTIVE KPI CARDS -->
    <div class="report-kpi-grid" style="margin-bottom: 20px;">
      <div class="report-kpi-card" style="border-top: 4px solid #3b82f6;">
        <div class="report-kpi-title">
          <span>FORECASTED Q4 TOTAL ACH %</span>
          <span style="font-size:16px;">🎯</span>
        </div>
        <div class="report-kpi-val" style="color: ${team.simQ4Ratio >= 100 ? '#10b981' : (team.simQ4Ratio >= 85 ? '#3b82f6' : '#f59e0b')};">
          ${team.simQ4Ratio.toFixed(2)}%
          <span class="ratio-badge ${team.q4RatioDiff >= 0 ? 'ratio-green' : 'ratio-red'}" style="font-size:11px; margin-left:6px;">
            ${team.q4RatioDiff >= 0 ? '+' : ''}${team.q4RatioDiff.toFixed(2)}%
          </span>
        </div>
        <div class="report-kpi-sub">
          <strong>${fmt(team.simQ4Sp)} pts</strong> • ${fmt(team.simQ4Sv)} EGP
          <br><span style="color:#64748b;">Current Actual: ${team.origQ4Ratio.toFixed(2)}% (${fmt(team.origQ4Sp)} pts)</span>
        </div>
      </div>

      <div class="report-kpi-card kpi-surplus" style="border-top: 4px solid #10b981;">
        <div class="report-kpi-title">
          <span>FORECASTED FULL-YEAR (YTD) ACH %</span>
          <span style="font-size:16px;">🏆</span>
        </div>
        <div class="report-kpi-val" style="color: ${team.simYtdRatio >= 100 ? '#10b981' : (team.simYtdRatio >= 90 ? '#3b82f6' : '#f59e0b')};">
          ${team.simYtdRatio.toFixed(2)}%
          <span class="ratio-badge ${team.ytdRatioDiff >= 0 ? 'ratio-green' : 'ratio-red'}" style="font-size:11px; margin-left:6px;">
            ${team.ytdRatioDiff >= 0 ? '+' : ''}${team.ytdRatioDiff.toFixed(2)}%
          </span>
        </div>
        <div class="report-kpi-sub">
          Current Baseline YTD: <strong>${team.origYtdRatio.toFixed(2)}%</strong>
          <br>${team.is100Met ? '<span style="color:#10b981; font-weight:700;">100% Annual Milestone Surpassed! 🎉</span>' : '<span style="color:#f59e0b; font-weight:700;">Within striking distance of 100%</span>'}
        </div>
      </div>

      <div class="report-kpi-card" style="border-top: 4px solid ${team.is100Met ? '#10b981' : '#f59e0b'};">
        <div class="report-kpi-title">
          <span>100% ANNUAL MILESTONE STATUS</span>
          <span style="font-size:16px;">⭐</span>
        </div>
        <div class="report-kpi-val" style="font-size: 20px; color: ${team.is100Met ? '#10b981' : '#f59e0b'};">
          ${team.is100Met ? 'MET & SURPASSED' : 'DEFICIT / IN PROGRESS'}
        </div>
        <div class="report-kpi-sub">
          ${team.is100Met 
            ? `Surplus: <strong style="color:#10b981;">+${fmt(team.gap100Pts)} pts</strong> ahead of quota` 
            : `Remaining to 100%: <strong style="color:#f59e0b;">${fmt(team.gap100Pts)} pts</strong>`}
        </div>
      </div>

      <div class="report-kpi-card" style="border-top: 4px solid ${team.is120Met ? '#8b5cf6' : '#64748b'};">
        <div class="report-kpi-title">
          <span>120% INCENTIVE MILESTONE</span>
          <span style="font-size:16px;">🚀</span>
        </div>
        <div class="report-kpi-val" style="font-size: 20px; color: ${team.is120Met ? '#8b5cf6' : '#64748b'};">
          ${team.is120Met ? 'MET & QUALIFIED' : 'IN PROGRESS'}
        </div>
        <div class="report-kpi-sub">
          ${team.is120Met 
            ? `Surplus: <strong style="color:#8b5cf6;">+${fmt(team.gap120Pts)} pts</strong> above 120%` 
            : `Gap to 120%: <strong>${fmt(team.gap120Pts)} pts</strong>`}
        </div>
      </div>
    </div>

    <!-- MASTER SCENARIO PRESETS BAR -->
    <div class="master-preset-strip">
      <span class="master-preset-label">
        <span style="font-size:15px;">⚡</span> Quick Line Scenarios:
      </span>
      ${masterPresets.map(p => `
        <button class="master-preset-btn" onclick="setMasterTeamPreset('${p.val}')">
          ${p.label}
        </button>
      `).join('')}

      <div style="margin-left:auto; display:flex; align-items:center; gap:8px;">
        <span style="font-size:11px; color:#64748b; font-weight:700;">UPA Mode:</span>
        <button class="upa-mode-btn ${currentUpaSimMode === 'target' ? 'active' : ''}" style="padding:4px 9px; font-size:10.5px;" onclick="setUpaEqualizationMode('target')" title="Rebalances UPA target so sales/target = equalized line rate">
          Target Rebalancing
        </button>
        <button class="upa-mode-btn ${currentUpaSimMode === 'sales' ? 'active' : ''}" style="padding:4px 9px; font-size:10.5px;" onclick="setUpaEqualizationMode('sales')" title="Credits points directly from forecast units">
          Sales Credit
        </button>
      </div>
    </div>

    <!-- 4 PRODUCT UNITS FORECAST CARDS -->
    <div class="prod-deck-grid">
      ${Object.keys(SIM_PROD_META).map(pid => {
        const ps = prodSim[pid];
        const meta = ps.meta;
        const curUnits = ps.forecastUnits;
        const tgtUnits = ps.targetUnits;
        const actUnits = ps.actualUnits;
        const maxSlider = Math.max(tgtUnits * 1.5, curUnits * 1.1, 100);

        return `
          <div class="prod-forecast-card" style="border-top: 4px solid ${meta.color};">
            <div class="prod-card-header">
              <div class="prod-card-title-wrap">
                <div class="prod-card-icon" style="color:${meta.color};">
                  ${meta.icon}
                </div>
                <div>
                  <div class="prod-card-name">${meta.name}</div>
                  <div class="prod-card-pack">${meta.pack}</div>
                </div>
              </div>
            </div>

            <div class="prod-baseline-pills">
              <div class="prod-baseline-row">
                <span>Q4 Target:</span>
                <span class="prod-baseline-val">${fmt(tgtUnits)} units</span>
              </div>
              <div class="prod-baseline-row">
                <span>Sold to Date:</span>
                <span class="prod-baseline-val" style="color:#0284c7;">${fmt(actUnits)} units (${(tgtUnits > 0 ? (actUnits/tgtUnits*100).toFixed(1) : 0)}%)</span>
              </div>
            </div>

            <div class="prod-input-group">
              <div class="prod-input-label">
                <span>Forecast Closing Units</span>
                <span style="color:${meta.color}; font-weight:800;">${ps.achPct.toFixed(1)}% Ach</span>
              </div>
              <div class="prod-input-row">
                <input type="number" id="prodUnitInput_${pid}" class="prod-unit-input" step="10" min="0" value="${Math.round(curUnits)}" oninput="onProductUnitChange(${pid}, this.value)">
                <span class="prod-unit-suffix">units</span>
              </div>
            </div>

            <div class="prod-slider-wrap">
              <input type="range" class="prod-slider" style="accent-color:${meta.color};" min="0" max="${maxSlider}" step="10" value="${curUnits}" oninput="onProductSliderChange(${pid}, this.value)">
            </div>

            <div class="prod-presets-row">
              <button class="prod-preset-chip" onclick="setProductPresetChip(${pid}, 'actual')">Actual</button>
              <button class="prod-preset-chip" onclick="setProductPresetChip(${pid}, 75)">75%</button>
              <button class="prod-preset-chip" onclick="setProductPresetChip(${pid}, 85)">85%</button>
              <button class="prod-preset-chip" onclick="setProductPresetChip(${pid}, 100)">100%</button>
              <button class="prod-preset-chip" onclick="setProductPresetChip(${pid}, 110)">110%</button>
              <button class="prod-preset-chip" onclick="setProductPresetChip(${pid}, 120)">120%</button>
            </div>

            <div class="prod-card-metrics">
              <div class="prod-metric-row">
                <span class="prod-metric-label">Forecast Points:</span>
                <span class="prod-metric-val">${fmt(ps.forecastPoints)} pts</span>
              </div>
              <div class="prod-metric-row">
                <span class="prod-metric-label">Forecast Revenue:</span>
                <span class="prod-metric-val">${fmt(ps.forecastValue)} EGP</span>
              </div>
              <div class="prod-metric-row">
                <span class="prod-metric-label">Product Ach %:</span>
                <span class="prod-ach-badge" style="background:${ps.achPct >= 100 ? '#dcfce7' : (ps.achPct >= 80 ? '#dbeafe' : '#fef3c7')}; color:${ps.achPct >= 100 ? '#15803d' : (ps.achPct >= 80 ? '#1d4ed8' : '#b45309')};">
                  ${ps.achPct.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        `;
      }).join('')}
    </div>

    <!-- REPRESENTATIVES BREAKDOWN TABLE -->
    <div style="background:#ffffff; border-radius:14px; border:1px solid #e2e8f0; padding:18px; margin-bottom:20px; box-shadow:0 4px 14px rgba(15,23,42,0.04);">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:14px;">
        <div>
          <div style="font-size:14.5px; font-weight:800; color:#0f172a;">
            Representatives Performance & Q4 Unit Forecast Breakdown
          </div>
          <div style="font-size:11px; color:#64748b; margin-top:2px;">
            Units distributed proportionally to quota with protection of actual sales. Customize individual reps if needed.
          </div>
        </div>
        <div style="display:flex; align-items:center; gap:10px;">
          ${hasOverrides ? `
            <button class="btn-reset-overrides" onclick="resetAllRepUnitOverrides()">
              Reset All ${overrideCount} Rep Overrides
            </button>
          ` : ''}
          <div style="display:flex; align-items:center; gap:6px;">
            <span style="font-size:11px; font-weight:700; color:#64748b;">Filter:</span>
            <select class="upa-rep-select" onchange="setUpaRepFilter(this.value)">
              <option value="all" ${currentUpaRepFilter === 'all' ? 'selected' : ''}>All Reps</option>
              ${sim.reps.map(r => `<option value="${r.key}" ${currentUpaRepFilter === r.key ? 'selected' : ''}>${r.name}</option>`).join('')}
            </select>
          </div>
        </div>
      </div>

      <div style="overflow-x:auto;">
        <table class="report-table" style="font-size:12px; width:100%;">
          <thead>
            <tr>
              <th style="min-width:140px;">Medical Rep</th>
              <th style="text-align:right; min-width:90px;">Mix 70/30 (u)</th>
              <th style="text-align:right; min-width:90px;">Rapid (u)</th>
              <th style="text-align:right; min-width:95px;">Glargivin 100 (u)</th>
              <th style="text-align:right; min-width:95px;">Glargivin UPA (u)</th>
              <th style="text-align:right; min-width:115px;">Sim Q4 Pts</th>
              <th style="text-align:right; min-width:110px;">Forecast Q4 %</th>
              <th style="text-align:right; min-width:110px;">Forecast YTD %</th>
              <th style="text-align:center; min-width:85px;">100% Year</th>
              <th style="text-align:center; min-width:85px;">120% Year</th>
              <th style="text-align:center; min-width:70px;">Action</th>
            </tr>
          </thead>
          <tbody>
            ${sim.reps
              .filter(r => currentUpaRepFilter === 'all' || currentUpaRepFilter === r.key)
              .map(r => {
                const isOverridden = r.hasOverrides;
                return `
                  <tr style="${isOverridden ? 'background: #fffbeb;' : ''}">
                    <td>
                      <div style="display:flex; align-items:center; gap:8px;">
                        <span class="rep-avatar" style="width:28px; height:28px; font-size:11px; border-radius:6px; flex-shrink:0;">${r.name.slice(0, 2).toUpperCase()}</span>
                        <div>
                          <div style="font-weight:800; color:#0f172a;">${r.name}</div>
                          <div style="font-size:10px; color:#64748b;">${r.area} ${isOverridden ? '<span style="color:#d97706; font-weight:800;">• Custom</span>' : ''}</div>
                        </div>
                      </div>
                    </td>
                    <td style="text-align:right;">
                      <div class="rep-unit-pill">${fmt(r.prodsMap[1260].units)}</div>
                      <div class="rep-unit-sub">Sold: ${fmt(r.prodsMap[1260].actualUnits)}</div>
                    </td>
                    <td style="text-align:right;">
                      <div class="rep-unit-pill">${fmt(r.prodsMap[1259].units)}</div>
                      <div class="rep-unit-sub">Sold: ${fmt(r.prodsMap[1259].actualUnits)}</div>
                    </td>
                    <td style="text-align:right;">
                      <div class="rep-unit-pill">${fmt(r.prodsMap[1110].units)}</div>
                      <div class="rep-unit-sub">Sold: ${fmt(r.prodsMap[1110].actualUnits)}</div>
                    </td>
                    <td style="text-align:right;">
                      <div class="rep-unit-pill">${fmt(r.prodsMap[1251].units)}</div>
                      <div class="rep-unit-sub">Sold: ${fmt(r.prodsMap[1251].actualUnits)}</div>
                    </td>
                    <td style="text-align:right; font-weight:700; color:#334155;">
                      ${fmt(r.simQ4Sp)}
                      <div style="font-size:10px; color:#94a3b8;">was ${fmt(r.origQ4Sp)}</div>
                    </td>
                    <td style="text-align:right;">
                      <span class="ratio-badge ${r.simQ4Ratio >= 100 ? 'ratio-green' : (r.simQ4Ratio >= 80 ? 'ratio-blue' : 'ratio-yellow')}">
                        ${r.simQ4Ratio.toFixed(2)}%
                      </span>
                      <div style="font-size:10px; color:${r.q4RatioDiff >= 0 ? '#10b981' : '#ef4444'}; font-weight:700; margin-top:2px;">
                        (${r.q4RatioDiff >= 0 ? '+' : ''}${r.q4RatioDiff.toFixed(1)}%)
                      </div>
                    </td>
                    <td style="text-align:right;">
                      <span class="ratio-badge ${r.simYtdRatio >= 100 ? 'ratio-green' : (r.simYtdRatio >= 90 ? 'ratio-blue' : 'ratio-yellow')}" style="font-weight:900;">
                        ${r.simYtdRatio.toFixed(2)}%
                      </span>
                      <div style="font-size:10px; color:#64748b; margin-top:2px;">
                        was ${r.origYtdRatio.toFixed(1)}% (${r.ytdRatioDiff >= 0 ? '+' : ''}${r.ytdRatioDiff.toFixed(1)}%)
                      </div>
                    </td>
                    <td style="text-align:center;">
                      ${r.is100Met ? '<span style="color:#10b981; font-weight:800; font-size:12px;">✓ YES</span>' : `<span style="color:#64748b; font-size:11px;">✗ ${r.simYtdRatio.toFixed(1)}%</span>`}
                    </td>
                    <td style="text-align:center;">
                      ${r.is120Met ? '<span style="color:#8b5cf6; font-weight:800; font-size:12px;">✓ 120%</span>' : `<span style="color:#94a3b8; font-size:11px;">✗</span>`}
                    </td>
                    <td style="text-align:center;">
                      <div style="display:flex; justify-content:center; align-items:center; gap:4px;">
                        <button class="rep-unit-edit-btn" onclick="openRepUnitEditor('${r.key}')" title="Customize units for ${r.name}">
                          ✏️
                        </button>
                        ${isOverridden ? `
                          <button class="rep-reset-btn" onclick="resetSingleRepUnitOverrides('${r.key}')" title="Reset to line ratio">
                            ↺
                          </button>
                        ` : ''}
                      </div>
                    </td>
                  </tr>

                  ${activeEditingRepKey === r.key ? `
                    <tr style="background:#f1f5f9;">
                      <td colspan="11" style="padding:14px 18px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                          <div style="font-weight:800; color:#0f172a; font-size:13px;">
                            ✏️ Custom Q4 Units for ${r.name} (${r.area})
                          </div>
                          <button class="rep-unit-edit-btn" onclick="closeRepUnitEditor()" style="background:#e2e8f0;">
                            Done / Close
                          </button>
                        </div>
                        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px;">
                          ${Object.keys(SIM_PROD_META).map(pid => {
                            const pm = SIM_PROD_META[pid];
                            const curRepU = r.prodsMap[pid].units;
                            return `
                              <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:8px; padding:8px 10px;">
                                <div style="font-size:10.5px; font-weight:800; color:#475569; margin-bottom:4px;">
                                  ${pm.icon} ${pm.short}
                                </div>
                                <div style="display:flex; align-items:center; gap:4px;">
                                  <input type="number" step="5" style="width:100%; border:1px solid #94a3b8; border-radius:6px; padding:4px 6px; font-size:13px; font-weight:800;" value="${Math.round(curRepU)}" onchange="onRepCustomUnitChange('${r.key}', ${pid}, this.value)">
                                  <span style="font-size:10px; color:#64748b;">u</span>
                                </div>
                              </div>
                            `;
                          }).join('')}
                        </div>
                      </td>
                    </tr>
                  ` : ''}
                `;
              }).join('')}
          </tbody>
          <tfoot>
            <tr style="background:#f8fafc; font-weight:800; border-top:2px solid #cbd5e1;">
              <td>
                <div style="color:#0f172a; font-size:12.5px;">DELTA REGION TEAM</div>
                <div style="font-size:10px; color:#64748b;">Dr. Sherif (9 Representatives)</div>
              </td>
              <td style="text-align:right; font-weight:900;">${fmt(prodSim[1260].forecastUnits)} u</td>
              <td style="text-align:right; font-weight:900;">${fmt(prodSim[1259].forecastUnits)} u</td>
              <td style="text-align:right; font-weight:900;">${fmt(prodSim[1110].forecastUnits)} u</td>
              <td style="text-align:right; font-weight:900;">${fmt(prodSim[1251].forecastUnits)} u</td>
              <td style="text-align:right; font-weight:900; color:#0f172a;">${fmt(team.simQ4Sp)}</td>
              <td style="text-align:right;">
                <span class="ratio-badge ratio-green" style="font-size:12px;">${team.simQ4Ratio.toFixed(2)}%</span>
                <div style="font-size:10px; color:#10b981; margin-top:2px;">(+${team.q4RatioDiff.toFixed(2)}%)</div>
              </td>
              <td style="text-align:right;">
                <span class="ratio-badge ${team.simYtdRatio >= 100 ? 'ratio-green' : 'ratio-blue'}" style="font-size:12.5px;">
                  ${team.simYtdRatio.toFixed(2)}%
                </span>
                <div style="font-size:10px; color:#64748b; margin-top:2px;">was ${team.origYtdRatio.toFixed(2)}% (+${team.ytdRatioDiff.toFixed(2)}%)</div>
              </td>
              <td style="text-align:center;">
                ${team.is100Met ? '<span style="color:#10b981; font-weight:900;">✓ 100% MET</span>' : '<span style="color:#f59e0b;">IN PROGRESS</span>'}
              </td>
              <td style="text-align:center;">
                ${team.is120Met ? '<span style="color:#8b5cf6; font-weight:900;">✓ 120% MET</span>' : '<span style="color:#94a3b8;">✗</span>'}
              </td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- RATIONALE / EXPLANATORY NOTE -->
    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:12px 16px; font-size:11.5px; color:#166534; display:flex; gap:10px; align-items:flex-start;">
      <span style="font-size:16px;">💡</span>
      <div style="line-height:1.5;">
        <strong>Unit-Based Closing Forecast Rationale:</strong>
        This simulator enables management to forecast exact physical unit closures per medicine across the portfolio. 
        Each representative's forecast units are derived from their quota share, guaranteeing that total expected points, quarterly achievement percentage (<strong>${team.simQ4Ratio.toFixed(2)}%</strong>), and annual cumulative performance (<strong>${team.simYtdRatio.toFixed(2)}%</strong>) directly reflect market reality and commercial agreements.
      </div>
    </div>
  `;

  bodyEl.innerHTML = html;
}

/* ── EXCEL EXPORT WITH PRODUCT UNITS & REPS ── */
function downloadUpaSimExcel() {
  if (typeof XLSX === 'undefined') {
    alert('Excel export library is loading, please try again in a moment.');
    return;
  }

  const sim = computeUnitsSimulation(prodForecastUnits, currentUpaSimMode, repUnitOverrides);
  const team = sim.team;
  const prodSim = sim.prodSim;

  const wb = XLSX.utils.book_new();

  // 1. Products Forecast Sheet
  const prodRows = [
    ['EVA PHARMA — DELTA REGION SALES DASHBOARD 2026'],
    ['Q4 PRODUCT UNITS CLOSING FORECAST & TARGET EQUALIZATION REPORT'],
    ['Generated On:', new Date().toLocaleString()],
    [''],
    ['Product ID', 'Product Name', 'Package', 'Q4 Target Units', 'Sold Units', 'Ach % So Far', 'Forecast Units', 'Unit Price (EGP)', 'Pts / Unit', 'Forecast Points', 'Forecast Revenue (EGP)', 'Forecast Ach %']
  ];

  Object.keys(SIM_PROD_META).forEach(pid => {
    const ps = prodSim[pid];
    prodRows.push([
      pid,
      ps.meta.name,
      ps.meta.pack,
      ps.targetUnits,
      ps.actualUnits,
      ps.targetUnits > 0 ? (ps.actualUnits / ps.targetUnits * 100) : 0,
      ps.forecastUnits,
      ps.unitPrice,
      ps.ptsPerUnit,
      ps.forecastPoints,
      ps.forecastValue,
      ps.achPct
    ]);
  });

  prodRows.push(['']);
  prodRows.push(['TEAM TOTALS', '', '', '', '', '', '', '', '', team.simQ4Sp, team.simQ4Sv, team.simQ4Ratio]);
  prodRows.push(['FULL-YEAR (YTD) FORECAST %', '', '', '', '', '', '', '', '', team.simYtdSp, team.simYtdTp, team.simYtdRatio]);
  prodRows.push(['100% MILESTONE STATUS', team.is100Met ? 'MET & SURPASSED' : 'IN PROGRESS', '', 'Surplus/Gap Pts:', team.gap100Pts]);
  prodRows.push(['120% MILESTONE STATUS', team.is120Met ? 'MET & SURPASSED' : 'IN PROGRESS', '', 'Surplus/Gap Pts:', team.gap120Pts]);

  const wsProd = XLSX.utils.aoa_to_sheet(prodRows);
  XLSX.utils.book_append_sheet(wb, wsProd, 'Product Forecast');

  // 2. Representatives Sheet
  const repRows = [
    ['EVA PHARMA — DELTA REGION SALES DASHBOARD 2026'],
    ['REPRESENTATIVES Q4 UNIT FORECAST & FULL-YEAR PROJECTION BREAKDOWN'],
    ['Generated On:', new Date().toLocaleString()],
    [''],
    [
      'Medical Rep', 'Area', 
      'Mix 70/30 (Units)', 'Rapid (Units)', 'Glargivin 100IU (Units)', 'Glargivin UPA (Units)',
      'Actual Q4 Pts', 'Forecast Q4 Pts', 'Actual Q4 Ach %', 'Forecast Q4 Ach %',
      'Actual YTD Ach %', 'Forecast YTD Ach %', '100% Year Status', '120% Year Status', 'Custom Overrides'
    ]
  ];

  sim.reps.forEach(r => {
    repRows.push([
      r.name,
      r.area,
      r.prodsMap[1260].units,
      r.prodsMap[1259].units,
      r.prodsMap[1110].units,
      r.prodsMap[1251].units,
      r.origQ4Sp,
      r.simQ4Sp,
      r.origQ4Ratio,
      r.simQ4Ratio,
      r.origYtdRatio,
      r.simYtdRatio,
      r.is100Met ? 'YES' : 'NO',
      r.is120Met ? 'YES' : 'NO',
      r.hasOverrides ? 'YES' : 'NO'
    ]);
  });

  repRows.push(['']);
  repRows.push([
    'DELTA REGION TEAM (Dr. Sherif)', 'Grand Aggregate',
    prodSim[1260].forecastUnits, prodSim[1259].forecastUnits, prodSim[1110].forecastUnits, prodSim[1251].forecastUnits,
    team.origQ4Sp, team.simQ4Sp, team.origQ4Ratio, team.simQ4Ratio,
    team.origYtdRatio, team.simYtdRatio, team.is100Met ? 'YES' : 'NO', team.is120Met ? 'YES' : 'NO', ''
  ]);

  const wsReps = XLSX.utils.aoa_to_sheet(repRows);
  XLSX.utils.book_append_sheet(wb, wsReps, 'Reps Breakdown');

  const filename = `EVA_Delta_Q4_Unit_Forecast_Simulation_${new Date().toISOString().slice(0, 10)}.xlsx`;
  XLSX.writeFile(wb, filename);
}

function printUpaSimReport() {
  window.print();
}
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
