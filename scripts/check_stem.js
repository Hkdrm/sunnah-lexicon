// Vérifie que le radical JS (web/index.html) == radical Python (scripts/arabic.py) sur tout le corpus.
const fs=require('fs'),cp=require('child_process'),path=require('path');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(root+'/web/index.html','utf8');
const m=html.match(/const arNorm[\s\S]*?function stem\(w\)\{[\s\S]*?\n\}/)[0];
const {arTokens,stem}=new Function(m+';return {arTokens,stem}')();
const data=JSON.parse(fs.readFileSync(root+'/web/data.json','utf8'));
const texts=data.hadiths.map(h=>h.arabic);
const js=texts.map(t=>arTokens(t).map(stem).join(' '));
const py=JSON.parse(cp.execFileSync('python3',['-c',`
import json,sys; sys.path.insert(0,'${root}/scripts')
from arabic import tokens,stem
d=json.load(open('${root}/web/data.json'))
print(json.dumps([' '.join(stem(t) for t in tokens(h['arabic'])) for h in d['hadiths']],ensure_ascii=False))`],{maxBuffer:1<<28}).toString());
let bad=0; js.forEach((x,i)=>{if(x!==py[i]){bad++; if(bad<3)console.log('DIFF',i)}});
console.log(bad?`${bad} divergences`:`OK : ${texts.length} hadiths identiques JS/Python`);
process.exit(bad?1:0);
