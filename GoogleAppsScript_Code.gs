/**
 * ============================================================================
 * EVA INSULIN — DELTA TEAM SALES DASHBOARD BACKEND
 * Google Apps Script (Code.gs)
 * ============================================================================
 * 
 * Instructions:
 * 1. Open Google Sheets (https://sheets.new)
 * 2. Click: Extensions -> Apps Script
 * 3. Paste this entire code into Code.gs
 * 4. Click Deploy -> New Deployment -> Select "Web app"
 * 5. Set "Execute as": Me
 * 6. Set "Who has access": Anyone (even anonymous)
 * 7. Click Deploy, authorize, and copy the Web App URL!
 * 8. Paste that URL into your Dashboard settings!
 * ============================================================================
 */

const SHEET_SALES = "Sales_Database";
const SHEET_REPS  = "Reps_List";

const PRODUCTS_MAP = {
  1260: { code: "OFP-CD-0284.02", name: "Humaxin Mix 70/30" },
  1259: { code: "OFP-CD-0284",    name: "Humaxin Rapid" },
  1251: { code: "OFP-CD-0326.05", name: "Glargivin UPA" },
  1110: { code: "OFP-CD-0326.03", name: "Glargivin 100IU" }
};

/**
 * Handle GET Requests (Read data or GET fallback for saving)
 */
function doGet(e) {
  try {
    const action = e.parameter.action || "getData";

    if ((action === "saveQuarter" || action === "saveQ4") && e.parameter.payload) {
      const payload = JSON.parse(decodeURIComponent(e.parameter.payload));
      return saveQuarterData(payload);
    }

    return getSalesData();
  } catch (err) {
    return createJsonResponse({ status: "error", message: err.toString() });
  }
}

/**
 * Handle POST Requests (Save Quarter records)
 */
function doPost(e) {
  try {
    let payload = null;
    if (e.postData && e.postData.contents) {
      payload = JSON.parse(e.postData.contents);
    } else if (e.parameter && e.parameter.payload) {
      payload = JSON.parse(e.parameter.payload);
    }
    
    if (!payload) {
      return createJsonResponse({ status: "error", message: "No data payload provided" });
    }

    return saveQuarterData(payload);
  } catch (err) {
    return createJsonResponse({ status: "error", message: err.toString() });
  }
}

/**
 * Read Sales & Reps data from Sheets and output clean JSON
 */
function getSalesData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let wsSales = ss.getSheetByName(SHEET_SALES);
  let wsReps  = ss.getSheetByName(SHEET_REPS);

  // If sheets do not exist, run auto-initialization
  if (!wsSales || !wsReps) {
    initDatabase();
    wsSales = ss.getSheetByName(SHEET_SALES);
    wsReps  = ss.getSheetByName(SHEET_REPS);
  }

  // 1. Read Reps List
  const repsData = wsReps.getDataRange().getValues();
  const repsList = [];
  for (let i = 1; i < repsData.length; i++) {
    const row = repsData[i];
    if (row[0]) {
      repsList.push({
        key: row[0].toString().toLowerCase().trim(),
        name: row[1],
        startQ: row[2] === "Q2" ? 2 : 1,
        noData: row[3] === "Pending Data"
      });
    }
  }

  // 2. Read Sales Database
  const salesRows = wsSales.getDataRange().getValues();
  const salesMap = {};

  for (let i = 1; i < salesRows.length; i++) {
    const r = salesRows[i];
    const repKey = (r[0] || "").toString().toLowerCase().trim();
    const repName = r[1] || "";
    const quarter = r[2] || "";
    const pid     = parseInt(r[3]) || 0;
    const su      = r[6] !== "" && r[6] !== null ? parseFloat(r[6]) : null;
    const tu      = r[7] !== "" && r[7] !== null ? parseFloat(r[7]) : null;
    const sv      = r[9] !== "" && r[9] !== null ? parseFloat(r[9]) : null;
    const tv      = r[10] !== "" && r[10] !== null ? parseFloat(r[10]) : null;
    const sp      = r[12] !== "" && r[12] !== null ? parseFloat(r[12]) : null;
    const tp      = r[13] !== "" && r[13] !== null ? parseFloat(r[13]) : null;
    const ratio   = r[15] !== "" && r[15] !== null ? parseFloat(r[15]) : (tv > 0 ? (sv / tv) * 100 : null);

    if (!repKey || !quarter || !pid) continue;

    if (!salesMap[repKey]) salesMap[repKey] = {};
    if (!salesMap[repKey][quarter]) salesMap[repKey][quarter] = [];

    salesMap[repKey][quarter].push({
      pid: pid,
      salesUnits: su,
      targetUnits: tu,
      salesValue: sv,
      targetValue: tv,
      salesPoints: sp,
      targetPoints: tp,
      ratio: ratio
    });
  }

  // Assemble response
  const repsStructured = repsList.map(rep => {
    const quartersObj = { Q1: null, Q2: null, Q3: null, Q4: null };
    const repSales = salesMap[rep.key] || {};

    ["Q1", "Q2", "Q3", "Q4"].forEach(q => {
      const prods = repSales[q];
      if (prods && prods.length > 0) {
        let totSu = 0, totTu = 0, totSv = 0, totTv = 0, totSp = 0, totTp = 0;
        prods.forEach(p => {
          if (p.salesUnits !== null) totSu += p.salesUnits;
          if (p.targetUnits !== null) totTu += p.targetUnits;
          if (p.salesValue !== null) totSv += p.salesValue;
          if (p.targetValue !== null) totTv += p.targetValue;
          if (p.salesPoints !== null) totSp += p.salesPoints;
          if (p.targetPoints !== null) totTp += p.targetPoints;
        });
        const totRatio = totTv > 0 ? (totSv / totTv) * 100 : null;

        quartersObj[q] = {
          products: prods,
          total: {
            salesUnits: totSu, targetUnits: totTu,
            salesValue: totSv, targetValue: totTv,
            salesPoints: totSp, targetPoints: totTp,
            ratio: totRatio
          }
        };
      }
    });

    return {
      key: rep.key,
      name: rep.name,
      startQ: rep.startQ,
      noData: rep.noData,
      quarters: quartersObj
    };
  });

  return createJsonResponse({
    status: "success",
    timestamp: new Date().toISOString(),
    reps: repsStructured
  });
}

/**
 * Save quarterly records to the Sales_Database sheet (Supports Q1, Q2, Q3, Q4)
 */
function saveQuarterData(payload) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let wsSales = ss.getSheetByName(SHEET_SALES);
  let wsReps  = ss.getSheetByName(SHEET_REPS);
  if (!wsSales || !wsReps) {
    initDatabase();
    wsSales = ss.getSheetByName(SHEET_SALES);
    wsReps  = ss.getSheetByName(SHEET_REPS);
  }

  const repKey = (payload.repKey || "").toString().toLowerCase().trim();
  const repName = payload.repName || repKey.toUpperCase();
  const quarter = (payload.quarter || "Q4").toUpperCase().trim();
  const products = payload.products || [];

  if (!repKey || products.length === 0) {
    return createJsonResponse({ status: "error", message: "Invalid payload: missing repKey or products" });
  }

  // Update Rep status in Reps_List if needed
  const repsData = wsReps.getDataRange().getValues();
  let repFound = false;
  for (let i = 1; i < repsData.length; i++) {
    if ((repsData[i][0] || "").toString().toLowerCase().trim() === repKey) {
      repFound = true;
      if (repsData[i][3] === "Pending Data") {
        wsReps.getRange(i + 1, 3).setValue(quarter);
        wsReps.getRange(i + 1, 4).setValue("Active");
      }
      break;
    }
  }
  if (!repFound) {
    wsReps.appendRow([repKey, repName, quarter, "Active"]);
  }

  const data = wsSales.getDataRange().getValues();
  const existingRows = {};

  // Track existing rows for this rep and quarter
  for (let i = 1; i < data.length; i++) {
    const rowRep = (data[i][0] || "").toString().toLowerCase().trim();
    const rowQ   = data[i][2] || "";
    const rowPid = parseInt(data[i][3]) || 0;
    if (rowRep === repKey && rowQ === quarter) {
      existingRows[rowPid] = i + 1; // 1-based index
    }
  }

  products.forEach(p => {
    const pid = p.pid;
    const pMeta = PRODUCTS_MAP[pid] || { code: "", name: "Product " + pid };
    const su = p.salesUnits !== null && p.salesUnits !== undefined ? parseFloat(p.salesUnits) : null;
    const tu = p.targetUnits !== null && p.targetUnits !== undefined ? parseFloat(p.targetUnits) : null;
    const uDef = (tu !== null && su !== null) ? (tu - su) : null;

    const sv = p.salesValue !== null && p.salesValue !== undefined ? parseFloat(p.salesValue) : null;
    const tv = p.targetValue !== null && p.targetValue !== undefined ? parseFloat(p.targetValue) : null;
    const vDef = (tv !== null && sv !== null) ? (tv - sv) : null;

    const sp = p.salesPoints !== null && p.salesPoints !== undefined ? parseFloat(p.salesPoints) : (sv !== null ? sv * 2 : null);
    const tp = p.targetPoints !== null && p.targetPoints !== undefined ? parseFloat(p.targetPoints) : (tv !== null ? tv * 2 : null);
    const pDef = (tp !== null && sp !== null) ? (tp - sp) : null;

    const ratio = (tv && tv > 0 && sv !== null) ? (sv / tv) * 100 : null;

    const rowValues = [
      repKey, repName, quarter,
      pid, pMeta.code, pMeta.name,
      su, tu, uDef,
      sv, tv, vDef,
      sp, tp, pDef,
      ratio
    ];

    if (existingRows[pid]) {
      // Update existing row
      wsSales.getRange(existingRows[pid], 1, 1, rowValues.length).setValues([rowValues]);
    } else {
      // Append new row
      wsSales.appendRow(rowValues);
    }
  });

  return createJsonResponse({
    status: "success",
    message: quarter + " records successfully saved to Google Sheet for " + repName,
    repKey: repKey,
    quarter: quarter
  });
}

function saveQ4Data(payload) {
  payload.quarter = "Q4";
  return saveQuarterData(payload);
}

function createJsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Run this function once in Apps Script if creating a fresh sheet from scratch!
 */
function initDatabase() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  let wsReps = ss.getSheetByName(SHEET_REPS);
  if (!wsReps) {
    wsReps = ss.insertSheet(SHEET_REPS);
    wsReps.appendRow(["Rep Key", "Rep Name", "Start Quarter", "Status"]);
    const reps = [
      ["amany", "Amany", "Q1", "Active"],
      ["hady", "Hady", "Q1", "Active"],
      ["ibrahim", "Ibrahim", "Q2", "Active"],
      ["radwa", "Radwa", "Q1", "Active"],
      ["hassan", "Hassan", "Q1", "Active"],
      ["nadeem", "Nadeem", "Q1", "Active"],
      ["sabah", "Sabah", "Q1", "Active"],
      ["tawfik", "Tawfik", "Q1", "Active"],
      ["wedad", "Wedad", "Q1", "Pending Data"]
    ];
    reps.forEach(r => wsReps.appendRow(r));
    wsReps.getRange("A1:D1").setFontWeight("bold").setBackground("#0F172A").setFontColor("#FFFFFF");
  }

  let wsSales = ss.getSheetByName(SHEET_SALES);
  if (!wsSales) {
    wsSales = ss.insertSheet(SHEET_SALES);
    wsSales.appendRow([
      "Rep_Key", "Rep_Name", "Quarter",
      "Product_Id", "Product_Code", "Product_Name",
      "Sales_Units", "Target_Units", "Unit_Deficit",
      "Sales_Value_EGP", "Target_Value_EGP", "Value_Deficit_EGP",
      "Sales_Points", "Target_Points", "Points_Deficit",
      "Ratio_Pct"
    ]);
    wsSales.getRange("A1:P1").setFontWeight("bold").setBackground("#0F172A").setFontColor("#FFFFFF");
  }
}
