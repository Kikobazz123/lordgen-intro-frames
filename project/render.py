import os,subprocess
from playwright.sync_api import sync_playwright
FPS=30;DUR=12
ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','image2pipe','-framerate',str(FPS),'-c:v','mjpeg','-i','-',
  '-i','score.wav','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-shortest','-movflags','+faststart','tmp_out.mp4'],stdin=subprocess.PIPE)
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto('file://'+os.path.abspath('index.html')+'?render');pg.evaluate('window.ready')
    for f in range(FPS*DUR):
        pg.evaluate(f'seek({f/FPS})');ff.stdin.write(pg.screenshot(type='jpeg',quality=95))
ff.stdin.close();rc=ff.wait()
if rc==0: os.replace('tmp_out.mp4','LordGen_Intro.mp4')
print('rc',rc)
