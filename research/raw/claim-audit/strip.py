import sys,re,html
for f in sys.argv[1:]:
    t=open(f,encoding='utf-8',errors='replace').read()
    t=re.sub(r'(?s)<(script|style|math)[^>]*>.*?</\1>',' ',t)
    t=html.unescape(re.sub(r'<[^>]+>',' ',t)); t=re.sub(r'\s+',' ',t)
    open(f.rsplit('.',1)[0]+'.txt','w').write(t)
