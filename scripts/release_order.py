"""Release order and human-readable date precision for the downloadable galleries."""
import calendar
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'catalog'
YEARS=json.loads((ROOT/'release-years.json').read_text())
DATES={key:value for p in sorted((ROOT/'release-dates').glob('*.json')) for key,value in json.loads(p.read_text()).items()}
def family(d):
    if d['brand']=='Apple':return {'phone':'iPhone','tablet':'iPad'}.get(d.get('type','phone'),'Mac')
    return d['brand']
def date(d):return DATES.get(d['id'],{}).get('date') or str(YEARS[d['id']] or '')
def release_order(d):
    group=family(d);first=['iPhone','iPad','Mac','Samsung']; key=tuple((0,int(s)) if s.isdigit() else (1,s) for s in re.split(r'(\d+)',d['label'].casefold()))
    return (first.index(group) if group in first else len(first),group,-int(date(d).replace('-','').ljust(8,'0')),key,d['id'])
def release_label(d):
    parts=date(d).split('-');y=parts[0];m=calendar.month_abbr[int(parts[1])] if len(parts)>1 else '';day=str(int(parts[2])) if len(parts)>2 else ''
    return ' '.join(filter(None,[day,m,y])) or 'Release date unknown'
