// preview.py の HTML を、consulting-pptx-skill の Playwright で 1 枚の画像にする。
//   node shot.mjs <consulting-pptx-skill のフォルダ> <html> <png> <ページの幅 px>
import { createRequire } from 'module';
import path from 'path';

const [,, skill, html, out, vw] = process.argv;
const require = createRequire(path.join(skill, 'package.json'));
const { chromium } = require('playwright');
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: Number(vw), height: 600 }, deviceScaleFactor: 2 });
await p.goto('file://' + html);
await p.screenshot({ path: out, fullPage: true });
await b.close();
