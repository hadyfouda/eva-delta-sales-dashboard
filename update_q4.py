import os, json, zipfile, xml.etree.ElementTree as ET
import openpyxl
from data import REPS_DATA, PRODUCTS

DELTA_DIR = r'C:\Users\ALMadina\Downloads\EVA Insulin Line Sales\Delta Team'
PRICES = {1260: 232.125, 1259: 232.125, 1251: 603.25, 1110: 669.60}

def parse_sheet(path):
    with zipfile.ZipFile(path) as z:
        sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        sst = []
        if 'xl/sharedStrings.xml' in z.namelist():
            tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                texts = [t.text for t in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if t.text]
                sst.append(''.join(texts))
        rows = []
        for r in sheet.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            cell_dict = {}
            for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                r_ref = c.get('r')
                col_letter = ''.join([ch for ch in r_ref if ch.isalpha()])
                t_attr = c.get('t')
                v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                val = v.text if v is not None else ''
                if t_attr == 's' and val.isdigit():
                    idx = int(val)
                    if idx < len(sst): val = sst[idx]
                cell_dict[col_letter] = val
            rows.append(cell_dict)
        return rows

def clean_f(val):
    if not val: return None
    s = str(val).replace(',', '').strip()
    try: return float(s)
    except: return None

folder_map = {
    'amany': 'Amany',
    'hady': 'Hady',
    'hassan': 'Hassan',
    'ibrahim': 'Ibrahim',
    'radwa': 'Radwa',
    'sabah': 'Sabah',
    'tawfik': 'Tawfik'
}

for r in REPS_DATA:
    key = r['key']
    if key in folder_map:
        folder = folder_map[key]
        fpath = os.path.join(DELTA_DIR, folder)
        q4_files = [f for f in os.listdir(fpath) if 'Q4' in f and f.endswith('.xlsx')]
        if q4_files:
            file_path = os.path.join(fpath, q4_files[0])
            rows = parse_sheet(file_path)
            prods = []
            tot_sv = 0.0
            tot_tv = 0.0
            tot_su = 0.0
            tot_tu = 0.0
            for row in rows:
                pid_str = row.get('A', '')
                if pid_str in ['1260', '1259', '1251', '1110']:
                    pid = int(pid_str)
                    price = PRICES[pid]
                    su = clean_f(row.get('D'))
                    sv = clean_f(row.get('E'))
                    tu = clean_f(row.get('F'))
                    tv = clean_f(row.get('G'))
                    
                    if su is None and sv is not None: su = round(sv / price, 2)
                    if sv is None and su is not None: sv = round(su * price, 2)
                    if tu is None and tv is not None: tu = round(tv / price, 2)
                    if tv is None and tu is not None: tv = round(tu * price, 2)
                    
                    ratio = round((sv / tv) * 100, 2) if tv and tv > 0 else (100.0 if sv else 0.0)
                    sp = clean_f(row.get('I')) or (round(sv * 2, 2) if sv else 0.0)
                    tp = clean_f(row.get('J')) or (round(tv * 2, 2) if tv else 0.0)
                    
                    if sv: tot_sv += sv
                    if tv: tot_tv += tv
                    if su: tot_su += su
                    if tu: tot_tu += tu
                    prods.append({
                        'pid': pid,
                        'salesUnits': su,
                        'salesValue': sv,
                        'targetUnits': tu,
                        'targetValue': tv,
                        'ratio': ratio,
                        'salesPoints': sp,
                        'targetPoints': tp
                    })
            tot_ratio = round((tot_sv / tot_tv) * 100, 2) if tot_tv > 0 else 0.0
            r['quarters']['Q4'] = {
                'products': prods,
                'total': {
                    'salesUnits': round(tot_su, 2),
                    'salesValue': round(tot_sv, 2),
                    'targetUnits': round(tot_tu, 2),
                    'targetValue': round(tot_tv, 2),
                    'ratio': tot_ratio,
                    'salesPoints': round(tot_sv * 2, 2),
                    'targetPoints': round(tot_tv * 2, 2)
                }
            }
            print(f"Updated {r['name']} Q4: Sales={tot_sv:,.2f}, Target={tot_tv:,.2f}, Ratio={tot_ratio}%")

# Save updated data.py
with open(r'C:\Users\ALMadina\.gemini\antigravity\scratch\delta-team-dashboard\data.py', 'w', encoding='utf-8') as f:
    f.write('# Product definitions\n')
    f.write('PRODUCTS = ' + repr(PRODUCTS) + '\n\n')
    f.write('REPS_DATA = ' + repr(REPS_DATA) + '\n\n')
    f.write('print("Loaded data.py with all 9 reps and Q1-Q4 records!")\n')

# Save updated data.json
with open(r'C:\Users\ALMadina\.gemini\antigravity\scratch\delta-team-dashboard\data.json', 'w', encoding='utf-8') as f:
    json.dump({'status': 'success', 'reps': REPS_DATA}, f, ensure_ascii=False, indent=2)

print("Saved updated data.py and data.json!")
