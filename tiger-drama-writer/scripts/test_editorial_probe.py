from editorial_probe import probe
from pathlib import Path
import tempfile
s='''## EP01｜测试\n### SC01｜室内\n唐予：我不签这张纸，除非你说明白。\n唐越：你又想拖到什么时候？\n唐予握住纸，撕掉封条。\n### SC02｜门外\n唐予：你先走。\n唐越：我不走。\n### SC03｜大厅\n唐予：我留下。\n唐越：你决定好了？\n'''
with tempfile.TemporaryDirectory() as t:
 p=Path(t)/'a.md'; p.write_text(s,encoding='utf8'); r=probe(p)
 assert len(r['episodes'])==1
 e=r['episodes'][0];assert e['episode']==1 and e['scenes']==3 and e['spoken_han']>0
 assert e['timed_readthrough'] is False and r['quality_certified'] is False
 assert {x['name'] for x in e['speakers']}=={'唐予','唐越'}
 print('editorial probe 5 assertions passed')
