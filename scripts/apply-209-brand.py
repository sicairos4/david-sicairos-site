import html
import os
from pathlib import Path
import re

root = Path('.').resolve()
excluded = {'.git', '.github', 'node_modules', 'android', 'worker', 'workers', 'tests', 'output'}
anchor = re.compile(r'''(<a\b[^>]*\bclass\s*=\s*["'][^"']*\bbrand\b[^"']*["'][^>]*>)(.*?)(</a>)''', re.I | re.S)
icon = re.compile(r'''<link\b(?=[^>]*\brel\s*=\s*["'](?:shortcut\s+)?icon["'])[^>]*>''', re.I)
for path in sorted(root.rglob('*.html')):
    relative = path.relative_to(root)
    if any(part in excluded for part in relative.parts):
        continue
    source = path.read_text(encoding='utf-8')
    logo = os.path.relpath(root / 'assets/209-wordmark.svg', path.parent).replace(os.sep, '/')
    favicon = os.path.relpath(root / 'favicon.svg', path.parent).replace(os.sep, '/')
    def replace_brand(match):
        text = html.unescape(re.sub('<[^>]+>', '', match.group(2))).strip()
        if text not in {'209', '209.'}:
            return match.group(0)
        image = '<img src="' + logo + '" alt="209." width="96" height="44" style="display:block;width:96px;height:44px;object-fit:contain;border-radius:8px">'
        return match.group(1) + image + match.group(3)
    updated = anchor.sub(replace_brand, source)
    if re.search(r'</head\s*>', updated, re.I):
        updated = icon.sub('', updated)
        updated = re.sub(r'</head\s*>', '<link rel="icon" type="image/svg+xml" href="' + favicon + '\">\n</head>', updated, count=1, flags=re.I)
    if updated != source:
        path.write_text(updated, encoding='utf-8')

path = root / 'assets/topbar.js'
source = path.read_text(encoding='utf-8')
marker = '/* 209. outlined brand rollout */'
if marker not in source:
    source += r'''
/* 209. outlined brand rollout */
(()=>{'use strict';const base=new URL('../',document.currentScript.src);function mount(){for(const brand of document.querySelectorAll('header .brand')){if(!['209','209.'].includes(brand.textContent.trim())&&!brand.querySelector('img[alt="209."]'))continue;const image=document.createElement('img');image.src=new URL('assets/209-wordmark.svg',base).href;image.alt='209.';image.width=96;image.height=44;image.style.cssText='display:block;width:96px;height:44px;object-fit:contain;border-radius:8px';image.onerror=()=>{brand.textContent='209.';};brand.replaceChildren(image);brand.setAttribute('aria-label','209. home');brand.style.cssText+=';display:inline-flex;align-items:center;flex:0 0 auto;line-height:1';}const icons=[...document.querySelectorAll('link[rel]')].filter(link=>link.rel.split(/\s+/).includes('icon'));let icon=icons.shift();icons.forEach(link=>link.remove());if(!icon){icon=document.createElement('link');document.head.append(icon);}icon.rel='icon';icon.type='image/svg+xml';icon.href=new URL('favicon.svg',base).href;}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});else mount();})();
'''
    path.write_text(source, encoding='utf-8')
