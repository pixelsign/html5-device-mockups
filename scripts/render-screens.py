"""Generate optional, original demo illustrations; never applied by the embed CSS."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'screens'
OUT.mkdir(exist_ok=True)
PALETTES = {
    'macOS': ('#ffc49b','#da795e','#943f50','#443d58'),
    'Windows': ('#bedde9','#68b0ca','#3d83a5','#204567'),
    'ChromeOS': ('#ece5ae','#adbd72','#648863','#345e58'),
    'Tizen': ('#fae7bd','#d2ad79','#ab7857','#684e4a'),
    'webOS': ('#edcab6','#cb8c80','#9f585c','#623f54'),
    'Google TV': ('#d0e5da','#8db7a9','#53887e','#315858'),
    'Smart TV': ('#cee1ee','#85a7c0','#607f99','#364f67'),
}

def box(x,y,w,h,color,r=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{color}"/>'

def text(x,y,size,value,color='white',weight=500):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}">{value}</text>'

def disc(x,y,r,color):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'

def landscape(p):
    sky,far,mid,near=p
    return (box(0,0,800,450,sky)+disc(583,134,54,'#fff1d0')+
            f'<path d="M0 255 Q124 120 249 217 T520 221 T800 164V450H0Z" fill="{far}"/>'+
            f'<path d="M0 291 Q149 322 324 228 T650 242 T800 206V450H0Z" fill="{mid}"/>'+
            f'<path d="M0 390 Q146 256 322 306 T625 303 T800 280V450H0Z" fill="{near}"/>')

def dock(x,y):
    colors=['#4587bd','#c5694c','#64997b','#9475a8','#d7a04b']; paths=['M5 10h6l2 2h6v6H5Z','M5 7l14 5-14 5 3-5Z','M8 5v12a3 3 0 1 1-2-3V7l10-2v9a3 3 0 1 1-2-3V6Z','M5 6h14v10H9l-4 3Z','M6 6h12v13H6Z']; out=''
    for i,(c,d) in enumerate(zip(colors,paths)):
        out+=box(x+i*36,y,28,28,c,7)+f'<path transform="translate({x+2+i*36} {y+2})" d="{d}" fill="white"/>'
    return out

def desktop(os,p):
    if os=='macOS':
        return (box(0,0,800,27,'#47394b')+text(18,19,14,'Finder　 File　 Edit　 View')+text(719,19,14,'09:41')+
                box(305,402,190,44,'#efdddb',14)+dock(314,410))
    if os=='Windows':
        return (box(0,406,800,44,'#e7eff4')+box(202,418,19,19,'#2872ad')+box(210,418,2,19,'#e7eff4')+box(202,426,19,2,'#e7eff4')+
                box(234,414,135,29,'white',14)+text(250,434,14,'Search','#485568')+dock(382,414)+text(742,432,13,'09:41','#364454'))
    return box(10,402,780,40,'#324a43',20)+disc(33,422,10,'#dae9dc')+dock(312,408)+text(730,427,14,'09:41')

def tv_home(os):
    dark='#20262b'; rail=os=='Tizen'; google=os=='Google TV'; x=124 if rail else 36
    s=(box(0,0,97,450,dark)+text(12,43,18,'Home')+text(12,92,14,'Art')+text(12,124,14,'Media')) if rail else ''
    if google:s+=box(0,0,800,46,dark)+text(36,30,18,'For you　　 Live　　 Apps　　 Library')
    s+=box(x,145,265,86,dark,5)+text(x+16,174,14,'ART COLLECTION' if rail else 'FEATURED FILM')+text(x+16,211,32,'Still Country',weight=650)
    y=327 if os=='webOS' else 342
    s+=box(0 if not rail else 97,y-31,800,160,dark)+text(x,y-7,16,{'Tizen':'Smart Hub','webOS':'webOS  /  Quick Cards','Google TV':'Continue watching','Smart TV':'Channels'}[os])
    names={'Tizen':['Gallery','Live TV','Sources'],'webOS':['Home office','Games','Music'],'Google TV':['Field Notes','Night Train','Coastlines'],'Smart TV':['Live TV','Guide','Inputs']}[os]
    for i,(n,c) in enumerate(zip(names,['#42665c','#86554b','#4d627a'])):
        dx=x+210*i;s+=box(dx,y,198,77,c,14 if os=='webOS' else 5)+text(dx+14,y+49,21,n)
    return s

for os,p in PALETTES.items():
    tv=os in ('Tizen','webOS','Google TV','Smart TV')
    for mode in ('app','lock'):
        s=landscape(p)
        if mode=='app': s+=tv_home(os) if tv else desktop(os,p)
        elif tv:s+=text(32,383,15,os+'  /  Ambient')+text(32,419,31,'Still Country',weight=600)
        else:
            x={'macOS':318,'Windows':48,'ChromeOS':72}[os];s+=text(x,175,64,'09:41','#202d38',650)+text(x+4,204,18,'Friday, November 20','#202d38')+text(30,414,16,os+'  /  Locked')
        name=os.replace(' ','-')+'-'+mode
        (OUT/(name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" preserveAspectRatio="none" font-family="system-ui, sans-serif"><title>{os} preview</title><desc>Original illustration, MIT (LICENSE.txt). Not a vendor screenshot.</desc>{s}</svg>\n')
