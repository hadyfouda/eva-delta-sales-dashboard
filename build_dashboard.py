# Generate the complete index.html for Delta Team Sales Dashboard
import json
from data import PRODUCTS, REPS_DATA

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>لوحة مبيعات فريق دلتا | Delta Team Sales Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --primary:     #122b54;
    --primary-lt:  #1e427b;
    --primary-accent: #2563eb;
    --teal:        #0284c7;
    --green:       #16a34a;
    --green-bg:    #dcfce7;
    --green-text:  #15803d;
    --orange:      #ea580c;
    --orange-bg:   #ffedd5;
    --orange-text: #c2410c;
    --red:         #dc2626;
    --red-bg:      #fee2e2;
    --red-text:    #b91c1c;
    --bg:          #f1f5f9;
    --surface:     #ffffff;
    --border:      #e2e8f0;
    --border-dark: #cbd5e1;
    --text:        #0f172a;
    --muted:       #64748b;
    --header-h:    68px;
  }

  body {
    font-family: 'Cairo', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    font-size: 14px;
    direction: rtl;
    line-height: 1.5;
  }

  /* ── TOPBAR ── */
  #topbar {
    position: sticky; top: 0; z-index: 100;
    height: var(--header-h);
    background: linear-gradient(135deg, #09172e 0%, var(--primary) 50%, var(--primary-lt) 100%);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.18);
    border-bottom: 1px solid rgba(255,255,255,0.1);
  }
  .brand { display: flex; align-items: center; gap: 14px; cursor: pointer; }
  .brand-logo {
    width: 44px; height: 44px; border-radius: 12px;
    background: linear-gradient(135deg, #38bdf8, #2563eb);
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; color: #fff; font-weight: 900;
    box-shadow: 0 4px 12px rgba(37,99,235,0.35);
  }
  .brand-name { color: #fff; font-weight: 800; font-size: 20px; line-height: 1.1; }
  .brand-sub  { color: #94a3b8; font-size: 11.5px; font-weight: 500; }
  .topbar-right { display: flex; align-items: center; gap: 14px; }
  .topbar-date {
    color: #cbd5e1; font-size: 12.5px; font-weight: 600;
    background: rgba(255,255,255,0.08); padding: 6px 14px; border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.12);
  }
  #back-btn {
    display: none; align-items: center; gap: 8px;
    background: #ffffff; color: var(--primary);
    padding: 8px 18px; border-radius: 10px; border: none;
    cursor: pointer; font-family: 'Cairo', sans-serif; font-size: 13.5px;
    font-weight: 700; transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  }
  #back-btn:hover { background: #f8fafc; transform: translateY(-1px); }
  #back-btn.visible { display: flex; }

  /* ── MAIN CONTAINER ── */
  #main { padding: 28px 24px; max-width: 1440px; margin: 0 auto; width: 100%; }

  .view { display: none; }
  .view.active { display: block; animation: fadeIn 0.25s ease; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

  /* ── PAGE TITLE ── */
  .page-title {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 24px; flex-wrap: wrap; gap: 14px;
  }
  .title-content { display: flex; align-items: center; gap: 14px; }
  .title-icon {
    width: 48px; height: 48px; border-radius: 14px;
    background: linear-gradient(135deg, var(--primary), var(--primary-accent));
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; color: #fff; box-shadow: 0 4px 14px rgba(37,99,235,0.25);
  }
  .page-title h1 { font-size: 23px; font-weight: 800; color: var(--primary); }
  .page-title .subtitle { font-size: 13px; color: var(--muted); font-weight: 500; }

  /* ── STAT CARDS ── */
  .stat-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px; margin-bottom: 28px;
  }
  .stat-card {
    background: var(--surface); border-radius: 16px;
    padding: 18px 20px; border: 1px solid var(--border);
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    display: flex; flex-direction: column; justify-content: space-between;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .stat-card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.08); }
  .stat-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .stat-label { font-size: 12px; color: var(--muted); font-weight: 600; }
  .stat-icon { font-size: 18px; }
  .stat-val { font-size: 22px; font-weight: 800; color: var(--primary); }
  .stat-sub { font-size: 11.5px; color: var(--muted); margin-top: 4px; display: flex; gap: 6px; align-items: center; }

  /* ── TEAM GRID ── */
  .team-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
    gap: 20px;
  }
  .rep-card {
    background: var(--surface); border-radius: 18px;
    padding: 22px; cursor: pointer;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border: 1px solid var(--border);
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative; overflow: hidden;
    display: flex; flex-direction: column; justify-content: space-between;
  }
  .rep-card::before {
    content: ''; position: absolute; top: 0; right: 0; left: 0; height: 4px;
    background: linear-gradient(90deg, var(--primary-accent), #38bdf8);
    border-radius: 18px 18px 0 0;
  }
  .rep-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(0,0,0,0.1);
    border-color: var(--primary-accent);
  }
  .rep-card.no-data { cursor: default; opacity: 0.8; }
  .rep-card.no-data::before { background: #cbd5e1; }
  .rep-card.no-data:hover { transform: none; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-color: var(--border); }

  .rep-card-header { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
  .rep-avatar {
    width: 48px; height: 48px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 19px; font-weight: 800; color: #fff; flex-shrink: 0;
    box-shadow: 0 3px 10px rgba(0,0,0,0.12);
  }
  .rep-card-title { font-size: 17px; font-weight: 800; color: var(--primary); }
  .rep-card-badge {
    display: inline-block; font-size: 10.5px; font-weight: 700;
    padding: 2px 9px; border-radius: 20px; margin-top: 3px;
  }
  .badge-active { background: var(--green-bg); color: var(--green-text); }
  .badge-nodata { background: #f1f5f9; color: #94a3b8; }
  .badge-q2start { background: #e0f2fe; color: #0369a1; }

  .rep-card-kpi {
    background: #f8fafc; border-radius: 12px; padding: 12px 14px;
    margin-bottom: 14px; border: 1px solid #f1f5f9;
  }
  .kpi-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
  .kpi-row:last-child { margin-bottom: 0; }
  .kpi-label { font-size: 11.5px; color: var(--muted); font-weight: 500; }
  .kpi-value { font-size: 14px; font-weight: 700; color: var(--primary); }

  .progress-wrap { margin-bottom: 14px; }
  .progress-label { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; font-weight: 600; }
  .progress-bar { height: 9px; background: #e2e8f0; border-radius: 6px; overflow: hidden; }
  .progress-fill { height: 100%; border-radius: 6px; transition: width 0.6s ease; }

  .rep-card-footer {
    display: flex; justify-content: space-between; align-items: center;
    padding-top: 12px; border-top: 1px solid var(--border);
  }
  .quarters-pills { display: flex; gap: 5px; }
  .q-pill {
    font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 6px;
  }
  .q-pill.available { background: #e0f2fe; color: #0369a1; }
  .q-pill.missing   { background: #f1f5f9; color: #94a3b8; }
  .q-pill.entered   { background: var(--green-bg); color: var(--green-text); }
  .rep-card-arrow   { color: var(--primary-accent); font-size: 18px; font-weight: 700; }

  /* ── AVATARS GRADIENTS ── */
  .av-1 { background: linear-gradient(135deg, #4f46e5, #06b6d4); }
  .av-2 { background: linear-gradient(135deg, #059669, #10b981); }
  .av-3 { background: linear-gradient(135deg, #d97706, #fbbf24); }
  .av-4 { background: linear-gradient(135deg, #db2777, #f472b6); }
  .av-5 { background: linear-gradient(135deg, #7c3aed, #a78bfa); }
  .av-6 { background: linear-gradient(135deg, #2563eb, #60a5fa); }
  .av-7 { background: linear-gradient(135deg, #0d9488, #2dd4bf); }
  .av-8 { background: linear-gradient(135deg, #ea580c, #f97316); }
  .av-9 { background: linear-gradient(135deg, #475569, #94a3b8); }

  /* ── REP VIEW STYLING ── */
  .rep-header-bar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 20px; flex-wrap: wrap; gap: 16px;
  }
  .rep-profile { display: flex; align-items: center; gap: 16px; }
  .rep-profile-name { font-size: 24px; font-weight: 900; color: var(--primary); line-height: 1.1; }
  .rep-profile-note { font-size: 13px; color: var(--muted); margin-top: 4px; }

  /* YTD STRIP */
  .ytd-strip {
    background: linear-gradient(135deg, #09172e 0%, var(--primary) 60%, var(--primary-lt) 100%);
    border-radius: 18px; padding: 22px 28px; margin-bottom: 24px; color: #fff;
    display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)) auto;
    gap: 20px; align-items: center;
    box-shadow: 0 6px 20px rgba(18,43,84,0.25);
    border: 1px solid rgba(255,255,255,0.1);
  }
  .ytd-item .ytd-label { font-size: 12px; color: #94a3b8; font-weight: 600; margin-bottom: 4px; }
  .ytd-item .ytd-val   { font-size: 21px; font-weight: 800; color: #ffffff; }
  .ytd-item .ytd-unit  { font-size: 11px; color: #64748b; margin-top: 2px; }
  .ytd-badge-box {
    text-align: center; background: rgba(255,255,255,0.1); padding: 12px 24px;
    border-radius: 14px; border: 1px solid rgba(255,255,255,0.18);
  }
  .ytd-badge-label { font-size: 11.5px; color: #cbd5e1; font-weight: 600; margin-bottom: 4px; }
  .ytd-badge-val   { font-size: 28px; font-weight: 900; }

  /* TABS */
  .tabs-nav {
    display: flex; gap: 8px; margin-bottom: 22px; flex-wrap: wrap;
    background: var(--surface); padding: 6px; border-radius: 14px;
    border: 1px solid var(--border); width: fit-content;
  }
  .tab-btn {
    padding: 9px 22px; border-radius: 10px; border: none;
    background: transparent; cursor: pointer; font-family: 'Cairo', sans-serif;
    font-size: 13.5px; font-weight: 700; color: var(--muted);
    transition: all 0.2s; display: flex; align-items: center; gap: 8px;
  }
  .tab-btn:hover { color: var(--primary); background: #f8fafc; }
  .tab-btn.active {
    background: var(--primary); color: #fff;
    box-shadow: 0 2px 10px rgba(18,43,84,0.25);
  }
  .tab-btn.q4-tab { color: var(--orange-text); background: #fff7ed; }
  .tab-btn.q4-tab.active { background: var(--orange); color: #fff; }
  .tab-btn.disabled { opacity: 0.45; cursor: not-allowed; pointer-events: none; }

  .tab-panel { display: none; }
  .tab-panel.active { display: block; animation: fadeIn 0.2s ease; }

  /* ── TABLES ── */
  .card {
    background: var(--surface); border-radius: 18px;
    border: 1px solid var(--border); box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    overflow: hidden; margin-bottom: 24px;
  }
  .card-header {
    padding: 16px 22px; background: #f8fafc;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
  }
  .card-header h3 { font-size: 16px; font-weight: 800; color: var(--primary); display: flex; align-items: center; gap: 8px; }
  .card-header-sub { font-size: 12px; color: var(--muted); font-weight: 500; }

  .table-scroll { overflow-x: auto; width: 100%; }
  table.data-table {
    width: 100%; border-collapse: separate; border-spacing: 0;
    font-size: 12.5px; text-align: right; min-width: 980px;
  }
  table.data-table th {
    background: #0f2342; color: #ffffff; font-weight: 700;
    padding: 12px 14px; font-size: 11.5px; white-space: nowrap;
    border-bottom: 2px solid #09172e;
  }
  table.data-table th.th-grp-unit  { background: #1e3a8a; }
  table.data-table th.th-grp-val   { background: #0f2342; }
  table.data-table th.th-grp-pts   { background: #134e4a; }
  table.data-table th.th-grp-ratio { background: #042f2e; text-align: center; }

  table.data-table td {
    padding: 12px 14px; border-bottom: 1px solid var(--border);
    white-space: nowrap; vertical-align: middle;
  }
  table.data-table tbody tr:hover td { background: #f8fafc; }

  /* ROW TYPES */
  .prod-title { font-weight: 800; color: var(--primary); font-size: 13px; line-height: 1.3; }
  .prod-code  { font-size: 10.5px; color: var(--muted); font-weight: 600; }
  .prod-tag   { font-size: 10px; padding: 1px 7px; border-radius: 4px; font-weight: 700; display: inline-block; margin-top: 3px; }
  .tag-est    { background: #fef3c7; color: #92400e; }
  .tag-partial{ background: #e0f2fe; color: #0369a1; }

  /* BADGES & DEFICIT */
  .deficit-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 9px; border-radius: 6px; font-size: 11.5px; font-weight: 700;
  }
  .deficit-red {
    background: var(--red-bg); color: var(--red-text);
  }
  .deficit-green {
    background: var(--green-bg); color: var(--green-text);
  }
  .ratio-badge {
    display: inline-block; padding: 4px 11px; border-radius: 20px;
    font-size: 11.5px; font-weight: 800; text-align: center;
  }
  .ratio-green  { background: var(--green-bg); color: var(--green-text); }
  .ratio-orange { background: var(--orange-bg); color: var(--orange-text); }
  .ratio-red    { background: var(--red-bg); color: var(--red-text); }

  /* TOTAL ROW */
  tr.row-total td {
    background: #e2e8f0 !important; font-weight: 800;
    color: var(--primary); font-size: 13px;
    border-top: 2px solid #94a3b8; border-bottom: none;
  }

  /* ── CHARTS ROW ── */
  .charts-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
    gap: 20px; margin-bottom: 24px;
  }
  .chart-box { padding: 18px; height: 320px; position: relative; }

  /* ── Q4 FORM ── */
  .q4-wrapper { padding: 24px; }
  .q4-alert {
    background: #fff7ed; border: 1px solid #fdba74; border-radius: 12px;
    padding: 14px 18px; margin-bottom: 22px; display: flex; align-items: center; gap: 12px;
  }
  .q4-alert-text { font-size: 13px; color: #9a3412; font-weight: 600; }
  .q4-prod-card {
    background: #f8fafc; border: 1px solid var(--border); border-radius: 14px;
    margin-bottom: 18px; overflow: hidden;
  }
  .q4-prod-header {
    background: #e2e8f0; padding: 10px 18px; font-weight: 800;
    font-size: 13.5px; color: var(--primary); display: flex; justify-content: space-between; align-items: center;
  }
  .q4-inputs-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 14px; padding: 16px 18px;
  }
  .q4-field label {
    display: block; font-size: 11.5px; font-weight: 700; color: var(--muted); margin-bottom: 5px;
  }
  .q4-field input {
    width: 100%; padding: 8px 12px; border: 1px solid var(--border-dark);
    border-radius: 8px; font-family: 'Cairo', sans-serif; font-size: 13px;
    font-weight: 600; color: var(--primary); background: #ffffff;
    transition: all 0.2s;
  }
  .q4-field input:focus {
    outline: none; border-color: var(--primary-accent);
    box-shadow: 0 0 0 3px rgba(37,99,235,0.15);
  }
  .q4-actions {
    display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin-top: 22px;
  }
  .btn {
    padding: 10px 24px; border-radius: 10px; border: none; cursor: pointer;
    font-family: 'Cairo', sans-serif; font-size: 14px; font-weight: 700;
    display: flex; align-items: center; gap: 8px; transition: all 0.2s;
  }
  .btn-save {
    background: var(--green); color: #fff;
    box-shadow: 0 4px 14px rgba(22,163,74,0.3);
  }
  .btn-save:hover { background: #15803d; transform: translateY(-1px); }
  .btn-clear {
    background: #fff; color: var(--red); border: 1px solid var(--red);
  }
  .btn-clear:hover { background: var(--red-bg); }
  .save-toast {
    display: none; padding: 10px 18px; border-radius: 8px; font-size: 13px;
    font-weight: 700; background: var(--green-bg); color: var(--green-text);
    border: 1px solid #86efac; align-items: center; gap: 8px;
  }
  .save-toast.visible { display: flex; animation: fadeIn 0.2s; }

  /* RESPONSIVE */
  @media (max-width: 768px) {
    #topbar { padding: 0 16px; }
    #main { padding: 18px 12px; }
    .page-title h1 { font-size: 20px; }
    .ytd-strip { grid-template-columns: 1fr 1fr; }
    .charts-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<!-- TOPBAR -->
<header id="topbar">
  <div class="brand" onclick="showHome()">
    <div class="brand-logo">Δ</div>
    <div>
      <div class="brand-name">Delta Team Sales</div>
      <div class="brand-sub">نظام متابعة المبيعات والعجز وتحقيق الأهداف 2026</div>
    </div>
  </div>
  <div class="topbar-right">
    <div class="topbar-date" id="topbar-date"></div>
    <button id="back-btn" onclick="showHome()">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
      لوحة الفريق الرئيسية
    </button>
  </div>
</header>

<main id="main">

  <!-- VIEW: TEAM OVERVIEW -->
  <div id="view-home" class="view active">
    <div class="page-title">
      <div class="title-content">
        <div class="title-icon">📊</div>
        <div>
          <h1>لوحة متابعة أداء الفريق السنوية (YTD 2026)</h1>
          <div class="subtitle">تجميع مبيعات الربع الأول والثاني والثالث، مع متابعة العجز والفائض بالوحدات والقيمة والنقاط</div>
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
        <div id="rep-avatar-large" class="rep-avatar" style="width:58px;height:58px;font-size:24px;border-radius:16px;"></div>
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
          <h3>📊 مقارنة المبيعات مقابل الهدف حسب الصنف</h3>
          <div class="card-header-sub">القيمة بالجنيه المصري (EGP)</div>
        </div>
        <div class="chart-box"><canvas id="repBarChart"></canvas></div>
      </div>
      <div class="card">
        <div class="card-header">
          <h3>📈 تطور المبيعات والهدف عبر الكوارتارات</h3>
          <div class="card-header-sub">التتبع الربعي التراكمي</div>
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
// If Target > Sales => Deficit (عجز) => RED
// If Sales >= Target => Surplus (فائض / محقق) => GREEN
function renderDeficitUnit(targetUnits, salesUnits) {
  if (targetUnits === null || salesUnits === null || targetUnits === undefined || salesUnits === undefined) {
    return '—';
  }
  const diff = targetUnits - salesUnits;
  if (diff > 0.001) {
    return `<span class="deficit-badge deficit-red">عجز -${fmt(diff)}</span>`;
  } else if (diff <= -0.001) {
    return `<span class="deficit-badge deficit-green">فائض +${fmt(Math.abs(diff))}</span>`;
  } else {
    return `<span class="deficit-badge deficit-green">محقق 100%</span>`;
  }
}

function renderDeficitVal(targetVal, salesVal) {
  if (targetVal === null || salesVal === null || targetVal === undefined || salesVal === undefined) {
    return '—';
  }
  const diff = targetVal - salesVal;
  if (diff > 0.01) {
    return `<span class="deficit-badge deficit-red">عجز -${fmt(diff)} EGP</span>`;
  } else if (diff <= -0.01) {
    return `<span class="deficit-badge deficit-green">فائض +${fmt(Math.abs(diff))} EGP</span>`;
  } else {
    return `<span class="deficit-badge deficit-green">محقق 100%</span>`;
  }
}

function renderDeficitPts(targetPts, salesPts) {
  if (targetPts === null || salesPts === null || targetPts === undefined || salesPts === undefined) {
    return '—';
  }
  const diff = targetPts - salesPts;
  if (diff > 0.01) {
    return `<span class="deficit-badge deficit-red">عجز -${fmt(diff)}</span>`;
  } else if (diff <= -0.01) {
    return `<span class="deficit-badge deficit-green">فائض +${fmt(Math.abs(diff))}</span>`;
  } else {
    return `<span class="deficit-badge deficit-green">محقق</span>`;
  }
}

/* ── LOCAL STORAGE Q4 ── */
function getQ4Key(repKey) { return 'delta_sales_q4_' + repKey; }
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

  // Team-wide aggregation
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
        <span class="stat-label">إجمالي مبيعات الفريق (YTD)</span>
        <span class="stat-icon">💰</span>
      </div>
      <div class="stat-val">${fmt(totalSales)}</div>
      <div class="stat-sub">جنيه مصري (EGP)</div>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">إجمالي هدف الفريق (YTD)</span>
        <span class="stat-icon">🎯</span>
      </div>
      <div class="stat-val">${fmt(totalTarget)}</div>
      <div class="stat-sub">جنيه مصري (EGP)</div>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">عجز / فائض الفريق</span>
        <span class="stat-icon">⚖️</span>
      </div>
      <div class="stat-val ${teamDeficit <= 0 ? 'deficit-green' : 'deficit-red'}" style="font-size:18px;">
        ${teamDeficit <= 0 ? 'فائض +' + fmt(Math.abs(teamDeficit)) : 'عجز -' + fmt(teamDeficit)} EGP
      </div>
      <div class="stat-sub">${teamDeficit <= 0 ? 'تم تجاوز الهدف المطلوب' : 'متبقي لتحقيق الهدف الكلي'}</div>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">نسبة التحقق الكلية</span>
        <span class="stat-icon">📈</span>
      </div>
      <div class="stat-val"><span class="ratio-badge ${ratioClass(teamRatio)}" style="font-size:17px;">${fmtPct(teamRatio)}</span></div>
      <div class="stat-sub">المجموع التراكمي للفريق</div>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">إجمالي نقاط البيع</span>
        <span class="stat-icon">⭐</span>
      </div>
      <div class="stat-val">${fmt(totalPoints)}</div>
      <div class="stat-sub">نقاط مبيعات محققة</div>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-label">أعضاء الفريق</span>
        <span class="stat-icon">👥</span>
      </div>
      <div class="stat-val">${REPS.length} مندوبين</div>
      <div class="stat-sub">${activeCount} لديهم بيانات مسجلة</div>
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
            <div class="rep-avatar ${rep.av}">${rep.name[0]}</div>
            <div>
              <div class="rep-card-title">${rep.name} — ${rep.nameAr}</div>
              <span class="rep-card-badge badge-nodata">لا توجد بيانات</span>
            </div>
          </div>
          <div style="text-align:center;padding:24px 0;color:var(--muted);">
            <div style="font-size:32px;margin-bottom:8px;">📁</div>
            <div style="font-weight:700;font-size:14px;">لم يتم إدراج ملفات بعد</div>
            <div style="font-size:11.5px;color:#94a3b8;margin-top:4px;">فولدر المندوب فارغ في شيتات الشركة</div>
          </div>
        </div>
        <div class="rep-card-footer">
          <div class="quarters-pills">
            <span class="q-pill missing">Q1</span>
            <span class="q-pill missing">Q2</span>
            <span class="q-pill missing">Q3</span>
            <span class="q-pill missing">Q4</span>
          </div>
          <span style="font-size:11.5px;color:#94a3b8;">غير متاح</span>
        </div>
      `;
    } else {
      const ytd = computeRepYTD(rep);
      const q4saved = loadQ4(rep.key);
      const ratio = ytd ? ytd.ratio : 0;
      const progressWidth = ratio ? Math.min(ratio, 130) / 130 * 100 : 0;
      const progressColor = ratio >= 100 ? 'background:var(--green);' : ratio >= 70 ? 'background:var(--orange);' : 'background:var(--red);';
      const badgeClass = rep.startQ === 2 ? 'badge-q2start' : 'badge-active';
      const badgeText  = rep.startQ === 2 ? 'انضم Q2' : 'نشط (Q1 - Q3)';

      const qPills = ['Q1', 'Q2', 'Q3', 'Q4'].map(q => {
        if (q === 'Q4') {
          return q4saved ? `<span class="q-pill entered">Q4: تم الإدخال</span>` : `<span class="q-pill missing">Q4: متاح للإدخال</span>`;
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
            <div class="rep-avatar ${rep.av}">${rep.name[0]}</div>
            <div>
              <div class="rep-card-title">${rep.name} — ${rep.nameAr}</div>
              <span class="rep-card-badge ${badgeClass}">${badgeText}</span>
            </div>
          </div>

          <div class="rep-card-kpi">
            <div class="kpi-row">
              <span class="kpi-label">المبيعات الفعلية (YTD):</span>
              <span class="kpi-value">${ytd ? fmt(ytd.salesValue) : '—'} EGP</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-label">الهدف المطلوب (YTD):</span>
              <span class="kpi-value">${ytd ? fmt(ytd.targetValue) : '—'} EGP</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-label">العجز / الفائض:</span>
              <span>${ytd ? renderDeficitVal(ytd.targetValue, ytd.salesValue) : '—'}</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-label">الوحدات المباعة:</span>
              <span class="kpi-value">${ytd ? fmt(ytd.salesUnits) : '—'} وحدة</span>
            </div>
          </div>

          <div class="progress-wrap">
            <div class="progress-label">
              <span>نسبة تحقيق الهدف:</span>
              <span class="ratio-badge ${ratioClass(ratio)}">${fmtPct(ratio)}</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width:${progressWidth}%;${progressColor}"></div>
            </div>
          </div>
        </div>

        <div class="rep-card-footer">
          <div class="quarters-pills">${qPills}</div>
          <span class="rep-card-arrow">عرض التفاصيل ›</span>
        </div>
      `;
    }
    grid.appendChild(card);
  });
}

/* ── BUILD TABLE HTML FOR A QUARTER OR YTD ── */
function buildProductsTable(title, sub, productsList, totalData) {
  const rows = productsList.map(p => {
    const prod = PRODUCTS.find(pr => pr.id === p.pid) || { name: 'صنف ' + p.pid, code: '' };
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
        <td><strong>${fmt(p.salesValue)}</strong> EGP</td>
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
              <th rowspan="2" style="min-width:180px;">الصنف الدوائي</th>
              <th colspan="3" class="th-grp-unit">الوحدات (Units)</th>
              <th colspan="3" class="th-grp-val">القيمة بالجنيه (Sales & Target Value EGP)</th>
              <th colspan="3" class="th-grp-pts">النقاط (Sales & Target Points)</th>
              <th rowspan="2" class="th-grp-ratio">نسبة التحقق %</th>
            </tr>
            <tr>
              <th class="th-grp-unit">وحدات مبيعات</th>
              <th class="th-grp-unit">وحدات هدف</th>
              <th class="th-grp-unit">عجز / فائض الوحدات</th>
              <th class="th-grp-val">قيمة مبيعات</th>
              <th class="th-grp-val">قيمة هدف</th>
              <th class="th-grp-val">عجز / فائض القيمة</th>
              <th class="th-grp-pts">نقاط مبيعات</th>
              <th class="th-grp-pts">نقاط هدف</th>
              <th class="th-grp-pts">عجز / فائض النقاط</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
            <tr class="row-total">
              <td>الإجمالي الكلي (Total)</td>
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
          <span style="font-size:11px;color:var(--muted);">${prod.code}</span>
        </div>
        <div class="q4-inputs-grid">
          <div class="q4-field">
            <label>وحدات المبيعات (Sales Units)</label>
            <input type="number" step="any" id="q4_su_${idx}_${rep.key}" placeholder="0" value="${saved && saved.salesUnits !== null ? saved.salesUnits : ''}">
          </div>
          <div class="q4-field">
            <label>قيمة المبيعات EGP (Sales Value)</label>
            <input type="number" step="any" id="q4_sv_${idx}_${rep.key}" placeholder="0.00" value="${saved && saved.salesValue !== null ? saved.salesValue : ''}" oninput="autoPoints(${idx}, '${rep.key}')">
          </div>
          <div class="q4-field">
            <label>نقاط المبيعات (Sales Points)</label>
            <input type="number" step="any" id="q4_sp_${idx}_${rep.key}" placeholder="0.00" value="${saved && saved.salesPoints !== null ? saved.salesPoints : ''}">
          </div>
          <div class="q4-field">
            <label>وحدات الهدف (Target Units)</label>
            <input type="number" step="any" id="q4_tu_${idx}_${rep.key}" placeholder="0" value="${saved && saved.targetUnits !== null ? saved.targetUnits : ''}">
          </div>
          <div class="q4-field">
            <label>قيمة الهدف EGP (Target Value)</label>
            <input type="number" step="any" id="q4_tv_${idx}_${rep.key}" placeholder="0.00" value="${saved && saved.targetValue !== null ? saved.targetValue : ''}" oninput="autoPoints(${idx}, '${rep.key}')">
          </div>
          <div class="q4-field">
            <label>نقاط الهدف (Target Points)</label>
            <input type="number" step="any" id="q4_tp_${idx}_${rep.key}" placeholder="0.00" value="${saved && saved.targetPoints !== null ? saved.targetPoints : ''}">
          </div>
        </div>
      </div>
    `;
  }).join('');

  let savedTableHtml = '';
  if (q4saved && q4saved.products) {
    savedTableHtml = buildProductsTable('بيانات Q4 المحفوظة حالياً للمندوب', 'نتائج الربع الرابع بعد حفظها', q4saved.products, q4saved.total);
  }

  return `
    <div class="card">
      <div class="card-header">
        <h3>✍️ شاشة إدخال بيانات الربع الرابع (Q4 2026) للمندوب</h3>
        <div class="card-header-sub">كل مندوب يمكنه رفع بياناته الخاصة بـ Q4 وحفظها مباشرة</div>
      </div>
      <div class="q4-wrapper">
        <div class="q4-alert">
          <span style="font-size:22px;">ℹ️</span>
          <div class="q4-alert-text">
            أدخل وحدات وقيم وأهداف الربع الرابع (Q4). سيتم حساب العجز والفائض أوتوماتيكياً وتحديث إجمالي السنة (YTD) والشارتات في الحال.
          </div>
        </div>
        ${prodCards}
        <div class="q4-actions">
          <button class="btn btn-save" onclick="saveQ4Data('${rep.key}')">
            💾 حفظ واعتماد بيانات Q4
          </button>
          <button class="btn btn-clear" onclick="clearQ4Data('${rep.key}')">
            🗑️ مسح بيانات Q4
          </button>
          <div class="save-toast" id="toast-${rep.key}">
            ✅ تم حفظ وتحديث بيانات Q4 بنجاح!
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
  // In company formula: points = value * 2
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

  // Show Toast
  const toast = document.getElementById(`toast-${repKey}`);
  if (toast) {
    toast.classList.add('visible');
    setTimeout(() => toast.classList.remove('visible'), 3500);
  }

  // Reload current view
  showRep(repKey, 'tab-Q4');
}

function clearQ4Data(repKey) {
  if (!confirm('هل تريد بالتأكيد مسح جميع بيانات Q4 المسجلة لهذا المندوب؟')) return;
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
  av.className = 'rep-avatar ' + rep.av;
  av.textContent = rep.name[0];
  document.getElementById('rep-profile-name').textContent = rep.name + ' — ' + rep.nameAr;
  document.getElementById('rep-profile-note').textContent = rep.note || 'ميديكال ريب في Delta Team — متابعة المبيعات 2026';

  // YTD Strip
  const ytd = computeRepYTD(rep);
  const strip = document.getElementById('rep-ytd-strip');
  if (ytd) {
    strip.innerHTML = `
      <div class="ytd-item">
        <div class="ytd-label">إجمالي المبيعات الفعلية (YTD)</div>
        <div class="ytd-val">${fmt(ytd.salesValue)} EGP</div>
        <div class="ytd-unit">${fmt(ytd.salesUnits)} وحدة مباعة</div>
      </div>
      <div class="ytd-item">
        <div class="ytd-label">إجمالي الهدف المطلوب (YTD)</div>
        <div class="ytd-val">${fmt(ytd.targetValue)} EGP</div>
        <div class="ytd-unit">${fmt(ytd.targetUnits)} وحدة مطلوبة</div>
      </div>
      <div class="ytd-item">
        <div class="ytd-label">عجز / فائض القيمة</div>
        <div class="ytd-val">${renderDeficitVal(ytd.targetValue, ytd.salesValue)}</div>
        <div class="ytd-unit">الفارق الإجمالي للعام</div>
      </div>
      <div class="ytd-item">
        <div class="ytd-label">عجز / فائض الوحدات</div>
        <div class="ytd-val">${renderDeficitUnit(ytd.targetUnits, ytd.salesUnits)}</div>
        <div class="ytd-unit">صافي فارق الوحدات</div>
      </div>
      <div class="ytd-item">
        <div class="ytd-label">نقاط المبيعات المحققة</div>
        <div class="ytd-val">${fmt(ytd.salesPoints)} pts</div>
        <div class="ytd-unit">هدف النقاط: ${fmt(ytd.targetPoints)}</div>
      </div>
      <div class="ytd-badge-box">
        <div class="ytd-badge-label">نسبة التحقق (YTD)</div>
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
    { id: 'tab-YTD', label: '📊 إجمالي السنة التراكمي (YTD)', isYTD: true },
    { id: 'tab-Q1',  label: 'الربع الأول (Q1)', q: 'Q1' },
    { id: 'tab-Q2',  label: 'الربع الثاني (Q2)', q: 'Q2' },
    { id: 'tab-Q3',  label: 'الربع الثالث (Q3)', q: 'Q3' },
    { id: 'tab-Q4',  label: 'الربع الرابع Q4 (إدخال البيانات)', isQ4: true }
  ];

  tabs.forEach(t => {
    const isQ1Disabled = rep.startQ === 2 && t.q === 'Q1';
    const btn = document.createElement('button');
    btn.className = 'tab-btn' + (t.isQ4 ? ' q4-tab' : '') + (isQ1Disabled ? ' disabled' : '');
    btn.innerHTML = isQ1Disabled ? 'Q1 (لم ينضم بعد)' : t.label;
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
          'ملخص مبيعات الأصناف التراكمي للسنة (YTD 2026)',
          'مجموع الكوارتارات متضمناً العجز والفائض لكل صنف دواء',
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
          <div class="card" style="padding:40px;text-align:center;color:var(--muted);">
            <div style="font-size:40px;margin-bottom:12px;">📅</div>
            <div style="font-size:16px;font-weight:700;">المندوب لم يكن موجوداً بالشركة في Q1</div>
            <div style="font-size:13px;margin-top:6px;">تاريخ بدء العمل بالفريق من الربع الثاني Q2</div>
          </div>
        `;
      } else if (qData) {
        panel.innerHTML = buildProductsTable(
          `تفاصيل بيع الأصناف وحساب العجز — ${t.q} 2026`,
          `المبيعات والأهداف والعجز بالوحدات والقيمة والنقاط للربع ${t.q}`,
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

  // Render Charts
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
          label: 'المبيعات المحققة (EGP)',
          data: salesVals,
          backgroundColor: '#1e427b',
          borderRadius: 8,
          borderSkipped: false
        },
        {
          label: 'الهدف المطلوب (EGP)',
          data: targetVals,
          backgroundColor: '#22c55e',
          borderRadius: 8,
          borderSkipped: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { font: { family: 'Cairo', weight: '700' } } },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${fmt(ctx.parsed.y)} EGP`
          }
        }
      },
      scales: {
        y: {
          ticks: { font: { family: 'Cairo' }, callback: v => fmt(v) },
          grid: { color: '#f1f5f9' }
        },
        x: {
          ticks: { font: { family: 'Cairo', weight: '600' } },
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
        lineLabels.push('Q4 (مدخل)');
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
          label: 'مبيعات الكوارتر (EGP)',
          data: lineSales,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37,99,235,0.08)',
          tension: 0.35,
          borderWidth: 3,
          pointRadius: 6,
          pointBackgroundColor: '#2563eb',
          fill: true
        },
        {
          label: 'تارجت الكوارتر (EGP)',
          data: lineTargets,
          borderColor: '#16a34a',
          backgroundColor: 'transparent',
          borderDash: [6, 4],
          borderWidth: 2.5,
          pointRadius: 6,
          pointBackgroundColor: '#16a34a',
          tension: 0.35
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { font: { family: 'Cairo', weight: '700' } } },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${fmt(ctx.parsed.y)} EGP`
          }
        }
      },
      scales: {
        y: {
          ticks: { font: { family: 'Cairo' }, callback: v => fmt(v) },
          grid: { color: '#f1f5f9' }
        },
        x: {
          ticks: { font: { family: 'Cairo', weight: '600' } },
          grid: { color: '#f1f5f9' }
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
    now.toLocaleDateString('ar-EG', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  renderHome();
});
</script>
</body>
</html>
'''

# Substitute the JSON data directly into the HTML
full_html = HTML_TEMPLATE.replace('__PRODUCTS_JSON__', json.dumps(PRODUCTS, ensure_ascii=False, indent=2))
full_html = full_html.replace('__REPS_JSON__', json.dumps(REPS_DATA, ensure_ascii=False, indent=2))

output_path = r"C:\Users\ALMadina\.gemini\antigravity\scratch\delta-team-dashboard\index.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Dashboard built successfully! Output size:", len(full_html), "bytes")
