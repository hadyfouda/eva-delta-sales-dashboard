/**
 * ============================================================================
 * EVA INSULIN — DELTA TEAM SALES DASHBOARD BACKEND
 * Google Apps Script (Code.gs)
 * ============================================================================
 * 
 * Instructions:
 * 1. Open Google Sheets (https://sheets.new) or your Delta_Team_Database
 * 2. Click: Extensions -> Apps Script
 * 3. Paste this entire code into Code.gs
 * 4. (Optional) Set your DRIVE_FOLDER_ID below, or name your Drive folder "Delta Team Sales"
 * 5. Click Deploy -> New Deployment -> Select "Web app"
 * 6. Set "Execute as": Me
 * 7. Set "Who has access": Anyone
 * 8. Click Deploy and copy the Web App URL!
 * 9. Paste that URL into your Dashboard settings!
 * ============================================================================
 */

// ============================================================================
// 📁 GOOGLE DRIVE FOLDER CONFIGURATION
// If you have a specific Google Drive folder ID, paste it below.
// Example: If URL is drive.google.com/drive/folders/1ABC_xyz123, use "1ABC_xyz123"
// If left empty, it will automatically search for a folder named "Delta Team Sales" or "EVA Insulin Line Sales"
// ============================================================================
const DRIVE_FOLDER_ID = "";

const SHEET_SALES = "Sales_Database";
const SHEET_REPS  = "Reps_List";

const PRODUCTS_MAP = {
  1260: { code: "OFP-CD-0284.02", name: "Humaxin Mix 70/30" },
  1259: { code: "OFP-CD-0284",    name: "Humaxin Rapid" },
  1251: { code: "OFP-CD-0326.05", name: "Glargivin UPA" },
  1110: { code: "OFP-CD-0326.03", name: "Glargivin 100IU" }
};

// Aliases for matching Representatives (English & Arabic)
const REPS_IDENTIFIERS = [
  { key: "amany",   name: "Amany",   aliases: ["amany", "أماني", "اماني"] },
  { key: "hady",    name: "Hady",    aliases: ["hady", "هادي", "هادى"] },
  { key: "ibrahim", name: "Ibrahim", aliases: ["ibrahim", "إبراهيم", "ابراهيم"] },
  { key: "radwa",   name: "Radwa",   aliases: ["radwa", "رضوى", "رضوي"] },
  { key: "hassan",  name: "Hassan",  aliases: ["hassan", "hasan", "حسن"] },
  { key: "nadeem",  name: "Nadeem",  aliases: ["nadeem", "nadim", "نديم"] },
  { key: "sabah",   name: "Sabah",   aliases: ["sabah", "صباح"] },
  { key: "tawfik",  name: "Tawfik",  aliases: ["tawfik", "tawfeek", "توفيق"] },
  { key: "wedad",   name: "Wedad",   aliases: ["wedad", "widad", "وداد"] }
];

/**
 * Handle GET Requests (Read data, or sync Google Drive folder on demand)
 */
function doGet(e) {
  try {
    const action = (e && e.parameter && e.parameter.action) ? e.parameter.action : "getData";

    // 1. Sync Drive Folder on demand (e.g. from Dashboard "Sync Google Drive" button)
    if (action === "syncDrive") {
      syncDriveFolder();
      return getSalesData();
    }

    // 2. Direct quarter save fallback
    if ((action === "saveQuarter" || action === "saveQ4") && e.parameter.payload) {
      const payload = JSON.parse(decodeURIComponent(e.parameter.payload));
      saveQuarterData(payload);
      return getSalesData();
    }

    return getSalesData();
  } catch (err) {
    return createJsonResponse({ status: "error", message: err.toString() });
  }
}

/**
 * Handle POST Requests
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
 * ============================================================================
 * 📁 GOOGLE DRIVE FOLDER SCANNER
 * Recursively scans Google Drive folder for .xlsx reports and syncs to Sheets
 * ============================================================================
 */
function syncDriveFolder() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let wsSales = ss.getSheetByName(SHEET_SALES);
  let wsReps  = ss.getSheetByName(SHEET_REPS);
  if (!wsSales || !wsReps) {
    initDatabase();
    wsSales = ss.getSheetByName(SHEET_SALES);
    wsReps  = ss.getSheetByName(SHEET_REPS);
  }

  // 1. Resolve Drive Folder
  let folder = null;
  if (DRIVE_FOLDER_ID && DRIVE_FOLDER_ID.trim() !== "") {
    try {
      folder = DriveApp.getFolderById(DRIVE_FOLDER_ID.trim());
    } catch (err) {
      Logger.log("Notice: folder by ID not found: " + err.message);
    }
  }

  if (!folder) {
    const candidateNames = ["Delta Team Sales", "EVA Insulin Line Sales", "Delta Team", "Delta sales"];
    for (let i = 0; i < candidateNames.length; i++) {
      const it = DriveApp.getFoldersByName(candidateNames[i]);
      if (it.hasNext()) {
        folder = it.next();
        break;
      }
    }
  }

  if (!folder) {
    Logger.log("No Google Drive folder found. Set DRIVE_FOLDER_ID in Code.gs.");
    return { status: "warning", message: "Google Drive folder not found. Please set DRIVE_FOLDER_ID in Code.gs." };
  }

  // 2. Recursively gather all .xlsx files
  const filesList = [];
  collectFilesRecursively(folder, folder.getName(), filesList);
  Logger.log("Found " + filesList.length + " Excel file(s) in Drive folder.");

  // 3. Process each file
  let processed = 0;
  for (let i = 0; i < filesList.length; i++) {
    const item = filesList[i];
    const ok = processDriveExcelFile(item.file, item.parentFolderName, wsSales, wsReps);
    if (ok) processed++;
  }

  return {
    status: "success",
    message: "Synced " + processed + " file(s) from Google Drive folder successfully.",
    totalFiles: filesList.length
  };
}

function collectFilesRecursively(folder, parentName, list) {
  const files = folder.getFiles();
  while (files.hasNext()) {
    const f = files.next();
    const name = f.getName().toLowerCase();
    if (name.endsWith(".xlsx") && !name.startsWith("~$")) {
      list.push({ file: f, parentFolderName: parentName });
    }
  }

  const subfolders = folder.getFolders();
  while (subfolders.hasNext()) {
    const sub = subfolders.next();
    collectFilesRecursively(sub, sub.getName(), list);
  }
}

function processDriveExcelFile(file, parentFolder, wsSales, wsReps) {
  const fileName = file.getName();
  const lowerFile = fileName.toLowerCase();
  const lowerFolder = (parentFolder || "").toLowerCase();

  // Match Rep
  let matchedRep = null;
  // 1. check parent folder name
  for (let i = 0; i < REPS_IDENTIFIERS.length; i++) {
    const r = REPS_IDENTIFIERS[i];
    for (let a = 0; a < r.aliases.length; a++) {
      if (lowerFolder.indexOf(r.aliases[a]) !== -1) {
        matchedRep = r;
        break;
      }
    }
    if (matchedRep) break;
  }

  // 2. check file name
  if (!matchedRep) {
    for (let i = 0; i < REPS_IDENTIFIERS.length; i++) {
      const r = REPS_IDENTIFIERS[i];
      for (let a = 0; a < r.aliases.length; a++) {
        if (lowerFile.indexOf(r.aliases[a]) !== -1) {
          matchedRep = r;
          break;
        }
      }
      if (matchedRep) break;
    }
  }

  if (!matchedRep) {
    Logger.log("Could not identify representative for file: " + fileName);
    return false;
  }

  // Match Quarter
  let matchedQuarter = null;
  if (/q4|الرابع/i.test(lowerFile)) matchedQuarter = "Q4";
  else if (/q3|الثالث|التالت/i.test(lowerFile)) matchedQuarter = "Q3";
  else if (/q2|الثاني|التاني/i.test(lowerFile)) matchedQuarter = "Q2";
  else if (/q1|الاول|الأول/i.test(lowerFile)) matchedQuarter = "Q1";

  if (!matchedQuarter) {
    Logger.log("Could not identify quarter for file: " + fileName);
    return false;
  }

  // Unzip .xlsx and parse sheet1.xml
  try {
    const blob = file.getBlob();
    const unzipped = Utilities.unzip(blob);
    let sheetXml = null;
    for (let i = 0; i < unzipped.length; i++) {
      if (unzipped[i].getName() === "xl/worksheets/sheet1.xml") {
        sheetXml = unzipped[i].getDataAsString();
        break;
      }
    }

    if (!sheetXml) {
      Logger.log("No sheet1.xml in: " + fileName);
      return false;
    }

    // Extract cell values
    const cells = {};
    const cellRegex = /<c\s+[^>]*?r="([A-Z]+)(\d+)"[^>]*>(?:<v\s*>([^<]*)<\/v>)?/g;
    let match;
    while ((match = cellRegex.exec(sheetXml)) !== null) {
      const col = match[1];
      const row = match[2];
      const val = (match[3] !== undefined && match[3] !== "") ? parseFloat(match[3]) : null;
      if (!cells[row]) cells[row] = {};
      cells[row][col] = val;
    }

    const targetPids = [1260, 1259, 1251, 1110];
    const foundPids = {};

    for (let r in cells) {
      const colA = cells[r]["A"];
      if (colA !== undefined && colA !== null) {
        const pidNum = Math.round(colA);
        if (targetPids.indexOf(pidNum) !== -1) {
          const su = cells[r]["D"] !== undefined ? cells[r]["D"] : null;
          const sv = cells[r]["E"] !== undefined ? cells[r]["E"] : null;
          const tu = cells[r]["F"] !== undefined ? cells[r]["F"] : null;
          const tv = cells[r]["G"] !== undefined ? cells[r]["G"] : null;
          const sp = cells[r]["I"] !== undefined ? cells[r]["I"] : (sv !== null ? sv * 2 : null);
          const tp = cells[r]["J"] !== undefined ? cells[r]["J"] : (tv !== null ? tv * 2 : null);
          const ratio = (tv && tv > 0 && sv !== null) ? (sv / tv) * 100 : (cells[r]["H"] !== undefined ? cells[r]["H"] : null);

          foundPids[pidNum] = {
            pid: pidNum,
            salesUnits: su,
            targetUnits: tu,
            salesValue: sv,
            targetValue: tv,
            salesPoints: sp,
            targetPoints: tp,
            ratio: ratio
          };
        }
      }
    }

    const productsData = [];
    targetPids.forEach(pid => {
      if (foundPids[pid]) {
        productsData.push(foundPids[pid]);
      } else {
        productsData.push({
          pid: pid,
          salesUnits: null, targetUnits: null,
          salesValue: null, targetValue: null,
          salesPoints: null, targetPoints: null,
          ratio: null
        });
      }
    });

    const payload = {
      repKey: matchedRep.key,
      repName: matchedRep.name,
      quarter: matchedQuarter,
      products: productsData
    };

    saveQuarterData(payload);
    Logger.log("Successfully synced from Drive: " + matchedRep.name + " (" + matchedQuarter + ")");
    return true;

  } catch (err) {
    Logger.log("Error processing " + fileName + ": " + err.toString());
    return false;
  }
}

/**
 * ============================================================================
 * ⏰ TIME-DRIVEN AUTO-SYNC TRIGGER
 * Run this function once in Apps Script to automatically scan Google Drive every 15 minutes!
 * ============================================================================
 */
function setupAutoSyncTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  for (let i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "syncDriveFolder") {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }

  ScriptApp.newTrigger("syncDriveFolder")
    .timeBased()
    .everyMinutes(15)
    .create();

  Logger.log("✅ Auto-sync trigger established: Google Drive will be monitored every 15 minutes!");
}

/**
 * Read Sales & Reps data from Sheets and output clean JSON
 */
function getSalesData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let wsSales = ss.getSheetByName(SHEET_SALES);
  let wsReps  = ss.getSheetByName(SHEET_REPS);

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
        startQ: row[2] === "Q2" ? 2 : (row[2] === "Q3" ? 3 : 1),
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
 * Save quarterly records to the Sales_Database sheet
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

  // Update Rep status in Reps_List
  const repsData = wsReps.getDataRange().getValues();
  let repFound = false;
  for (let i = 1; i < repsData.length; i++) {
    if ((repsData[i][0] || "").toString().toLowerCase().trim() === repKey) {
      repFound = true;
      if (repsData[i][3] === "Pending Data") {
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

  for (let i = 1; i < data.length; i++) {
    const rowRep = (data[i][0] || "").toString().toLowerCase().trim();
    const rowQ   = data[i][2] || "";
    const rowPid = parseInt(data[i][3]) || 0;
    if (rowRep === repKey && rowQ === quarter) {
      existingRows[rowPid] = i + 1;
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
      wsSales.getRange(existingRows[pid], 1, 1, rowValues.length).setValues([rowValues]);
    } else {
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

function createJsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Initialize fresh sheets if starting completely blank
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
      ["hassan", "Hassan", "Q3", "Active"],
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
