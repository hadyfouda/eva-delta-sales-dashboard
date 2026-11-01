import os, json, zipfile, xml.etree.ElementTree as ET
import shutil

DELTA_DIR = r'C:\Users\ALMadina\Downloads\EVA Insulin Line Sales\Delta Team'
PRICES = {1260: 232.125, 1259: 232.125, 1251: 603.25, 1110: 669.60}

PRODUCTS = [
    {'id': 1260, 'code': 'OFP-CD-0284.02', 'name': 'Humaxin Mix 70/30', 'fullName': 'Humaxin Mix 70/30 5 Carts'},
    {'id': 1259, 'code': 'OFP-CD-0284', 'name': 'Humaxin Rapid', 'fullName': 'Humaxin Rapid 5 Carts'},
    {'id': 1251, 'code': 'OFP-CD-0326.05', 'name': 'Glargivin UPA', 'fullName': 'Glargivin 100U/ML 3ML X5CART UPA'},
    {'id': 1110, 'code': 'OFP-CD-0326.03', 'name': 'Glargivin 100IU', 'fullName': 'GLARGIVIN -100 IU 3 ML 5 CARTRIDGES'}
]

REPS_CONFIG = [
    {'key': 'amany',   'name': 'Amany',   'nameAr': 'أماني',   'folder': 'Amany',   'av': 'av-1', 'startQ': 1},
    {'key': 'hady',    'name': 'Hady',    'nameAr': 'هادي',    'folder': 'Hady',    'av': 'av-2', 'startQ': 1},
    {'key': 'ibrahim', 'name': 'Ibrahim', 'nameAr': 'إبراهيم', 'folder': 'Ibrahim', 'av': 'av-3', 'startQ': 2, 'note': 'Joined the team in Q2 — No Q1 records available'},
    {'key': 'radwa',   'name': 'Radwa',   'nameAr': 'رضوى',   'folder': 'Radwa',   'av': 'av-4', 'startQ': 1},
    {'key': 'hassan',  'name': 'Hassan',  'nameAr': 'حسن',    'folder': 'Hassan',  'av': 'av-5', 'startQ': 3, 'note': 'Joined the team in Q3 — No Q1 or Q2 records available'},
    {'key': 'nadeem',  'name': 'Nadeem',  'nameAr': 'نديم',    'folder': 'Nadeem',  'av': 'av-6', 'startQ': 1},
    {'key': 'sabah',   'name': 'Sabah',   'nameAr': 'صباح',   'folder': 'Sabah',   'av': 'av-7', 'startQ': 1},
    {'key': 'tawfik',  'name': 'Tawfik',  'nameAr': 'توفيق',  'folder': 'Tawfik',  'av': 'av-8', 'startQ': 1},
    {'key': 'wedad',   'name': 'Wedad',   'nameAr': 'وداد',    'folder': 'Wedad',   'av': 'av-9', 'startQ': 1}
]

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
                    if idx < len(sst):
                        val = sst[idx]
                cell_dict[col_letter] = val
            rows.append(cell_dict)
        return rows

def clean_f(val):
    if val is None or val == '':
        return None
    s = str(val).replace(',', '').strip()
    try:
        return float(s)
    except:
        return None

reps_data = []

for cfg in REPS_CONFIG:
    rep_obj = {
        'key': cfg['key'],
        'name': cfg['name'],
        'nameAr': cfg['nameAr'],
        'av': cfg['av'],
        'startQ': cfg['startQ'],
        'quarters': {'Q1': None, 'Q2': None, 'Q3': None, 'Q4': None}
    }
    if 'note' in cfg:
        rep_obj['note'] = cfg['note']

    fpath = os.path.join(DELTA_DIR, cfg['folder'])
    if not os.path.exists(fpath):
        print(f"Warning: Folder not found {fpath}")
        reps_data.append(rep_obj)
        continue

    files_in_folder = os.listdir(fpath)

    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        # Check startQ restriction
        if cfg['startQ'] == 2 and q == 'Q1':
            continue
        if cfg['startQ'] == 3 and (q == 'Q1' or q == 'Q2'):
            continue

        q_match = [f for f in files_in_folder if q.lower() in f.lower() and f.endswith('.xlsx')]
        if not q_match:
            print(f"  {cfg['name']} has no file for {q}")
            continue

        file_path = os.path.join(fpath, q_match[0])
        rows = parse_sheet(file_path)

        prods = []
        tot_sv = 0.0
        tot_tv = 0.0
        tot_su = 0.0
        tot_tu = 0.0

        for p_def in PRODUCTS:
            pid = p_def['id']
            price = PRICES[pid]
            row_found = next((r for r in rows if r.get('A', '').strip() == str(pid)), None)

            if row_found:
                su = clean_f(row_found.get('D'))
                sv = clean_f(row_found.get('E'))
                tu = clean_f(row_found.get('F'))
                tv = clean_f(row_found.get('G'))

                if su is None and sv is not None: su = round(sv / price, 2)
                if sv is None and su is not None: sv = round(su * price, 2)
                if tu is None and tv is not None: tu = round(tv / price, 2)
                if tv is None and tu is not None: tv = round(tu * price, 2)

                sp = clean_f(row_found.get('I')) or (round(sv * 2, 2) if sv else 0.0)
                tp = clean_f(row_found.get('J')) or (round(tv * 2, 2) if tv else 0.0)
                ratio = round((sp / tp) * 100, 2) if (tp and tp > 0 and sp is not None) else (round((sv / tv) * 100, 2) if (tv and tv > 0 and sv is not None) else (100.0 if sv else 0.0))

                if sv is not None: tot_sv += sv
                if tv is not None: tot_tv += tv
                if su is not None: tot_su += su
                if tu is not None: tot_tu += tu

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
            else:
                prods.append({
                    'pid': pid,
                    'salesUnits': None,
                    'salesValue': None,
                    'targetUnits': None,
                    'targetValue': None,
                    'ratio': None,
                    'salesPoints': None,
                    'targetPoints': None
                })

        tot_sp = sum(p['salesPoints'] for p in prods if p['salesPoints'] is not None)
        tot_tp = sum(p['targetPoints'] for p in prods if p['targetPoints'] is not None)
        tot_ratio = round((tot_sp / tot_tp) * 100, 2) if tot_tp > 0 else (round((tot_sv / tot_tv) * 100, 2) if tot_tv > 0 else 0.0)
        rep_obj['quarters'][q] = {
            'products': prods,
            'total': {
                'salesUnits': round(tot_su, 2),
                'salesValue': round(tot_sv, 2),
                'targetUnits': round(tot_tu, 2),
                'targetValue': round(tot_tv, 2),
                'ratio': tot_ratio,
                'salesPoints': round(tot_sp, 2),
                'targetPoints': round(tot_tp, 2)
            }
        }
        print(f"  Processed {cfg['name']} - {q}: Sales={tot_sv:,.2f} EGP, Target={tot_tv:,.2f} EGP")

    reps_data.append(rep_obj)

# Output data.py
dashboard_dir = r"C:\Users\ALMadina\.gemini\antigravity\scratch\delta-team-dashboard"
data_py_path = os.path.join(dashboard_dir, "data.py")
with open(data_py_path, "w", encoding="utf-8") as f:
    f.write("# Product definitions\n")
    f.write(f"PRODUCTS = {repr(PRODUCTS)}\n\n")
    f.write(f"REPS_DATA = {repr(reps_data)}\n\n")
    f.write("print('Loaded data.py with all 9 reps and Q1-Q4 records!')\n")

print(f"Successfully updated {data_py_path}!")

# Output data.json
data_json_path = os.path.join(dashboard_dir, "data.json")
with open(data_json_path, "w", encoding="utf-8") as f:
    json.dump({'products': PRODUCTS, 'reps': reps_data}, f, ensure_ascii=False, indent=2)

print(f"Successfully updated {data_json_path}!")
