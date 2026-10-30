import os
from playwright.sync_api import sync_playwright
from PIL import Image
K={'k1_wide':1.3,'k2_perch':4.45,'k3_close':6.65}
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto('file://'+os.path.abspath('index.html')+'?render');pg.evaluate('window.ready')
    pg.evaluate('window.NOFADE=true;window.NOFLY=true')
    for n,t in K.items():
        pg.evaluate(f'seek({t})');pg.screenshot(path=f'keys/{n}.png')
        Image.open(f'keys/{n}.png').convert('RGB').resize((720,1280),Image.LANCZOS).save(f'keys/{n}.jpg',quality=92)
    pg.evaluate('window.NOFLY=false');pg.evaluate('seek(11.0)');pg.screenshot(path='keys/k4_logo.png')
    Image.open('keys/k4_logo.png').convert('RGB').resize((720,1280),Image.LANCZOS).save('keys/k4_logo.jpg',quality=92)
