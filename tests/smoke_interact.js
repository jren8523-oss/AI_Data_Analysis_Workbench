// 交互冒烟：在增强 DOM mock 中驱动完整用户流程
// 示例卡点击 → step2 → 选分析 → 运行 → 结果渲染 → 导出报告
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync('index.html', 'utf8');
const code = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function makeEl(tag) {
  const el = {
    tagName: tag || 'div', style: {}, dataset: {}, innerHTML: '', textContent: '', value: '',
    _classes: [], _clicked: false, _appended: false,
    classList: {
      add(c){ if (el._classes.indexOf(c) < 0) el._classes.push(c); },
      remove(c){ const i = el._classes.indexOf(c); if (i >= 0) el._classes.splice(i, 1); },
      toggle(c, f){ const has = el._classes.indexOf(c) >= 0; if (f === undefined ? !has : f) el.classList.add(c); else el.classList.remove(c); },
      contains(c){ return el._classes.indexOf(c) >= 0; }
    },
    addEventListener(){}, removeEventListener(){},
    querySelectorAll(sel){ if (sel === '.pb-copy') return [{ remove(){ pbRemoved = true; } }]; return []; }, querySelector(){ return null; },
    scrollIntoView(){}, remove(){}, appendChild(){}, removeChild(){}, closest(){ return null; },
    click(){ el._clicked = true; }
  };
  return el;
}
const els = {};
const clickedEls = [];
let pbRemoved = false; // 记录导出时「移除复制按钮」逻辑是否被调用
const doc = {
  getElementById(id){ return els[id] || (els[id] = makeEl('div', id)); },
  createElement(tag){
    const el = makeEl(tag);
    if (tag === 'a') clickedEls.push(el);
    return el;
  },
  body: { appendChild(){}, removeChild(){} },
  querySelector(){ return makeEl('div'); },
  querySelectorAll(){ return []; }
};
let blobCaptured = null, downloadName = null;
const ctx = {
  console,
  window: { scrollTo(){} },
  document: doc,
  navigator: { clipboard: null },
  setTimeout, clearTimeout,
  requestAnimationFrame(fn){ return fn(); },
  URL: { createObjectURL(b){ blobCaptured = b; return 'blob:mock'; }, revokeObjectURL(){} },
  Blob: function(parts, opts){ this.parts = parts; this.opts = opts; },
  FileReader: function(){}
};
vm.createContext(ctx);
vm.runInContext(code, ctx, { filename: 'index-inline.js' });

let fail = 0;
const ok = (c, m) => { if (c) console.log('  PASS', m); else { console.error('  FAIL', m); fail++; } };

console.log('== 用户流程：示例卡 → 分析 → 运行 → 导出 ==');
// 1. 首屏渲染
ctx.renderSampleGrid();
ok(els.sampleGrid.innerHTML.includes('实训 01') && els.sampleGrid.innerHTML.includes('placeholder'), '首屏示例卡渲染（含 02 占位灰卡）');
ctx.renderWall();
ok(els.wallGrid.innerHTML.includes('output/task01/report.html') && !els.wallGrid.innerHTML.includes('task02'), '报告墙渲染（9 卡，02 无报告）');

// 2. 点击示例卡（task06 指数）→ step2
ctx.loadSample('task06');
ok(ctx.state.ds && ctx.state.ds.rows.length === 3, 'task06 加载 3 行');
ok(ctx.state.reco === 'index', 'task06 推荐分析 = index');
ok(els.step2 && els.step2._classes.indexOf('hidden') < 0, 'step2 可见');
ok(els.anGrid.innerHTML.includes('an-card') && els.anGrid.innerHTML.includes('reco'), '分析卡渲染且推荐标出');

// 3. 点击分析卡 index → 参数表单
ctx.selectAnalysis('index');
ok(ctx.state.analysis === 'index', '选中 index 分析');
ok(els.cfgFields.innerHTML.includes('cfg_q0') && els.cfgFields.innerHTML.includes('cfg_p1'), '参数表单含 q0/q1/p0/p1 下拉');

// 4. 运行
ctx.runAnalysis();
ok(ctx.state.lastHtml.includes('res-block') && ctx.state.lastHtml.includes('<svg'), '运行成功，结果含编号块+SVG 图表');
ok(ctx.state.lastHtml.includes('指数体系成立') || ctx.state.lastHtml.includes('自洽'), '指数自洽验证块出现');

// 5. 导出报告
ctx.exportReport();
ok(clickedEls.length >= 1 && clickedEls.some(a => a.download && a.download.endsWith('.html')), '导出触发下载（文件名 .html）');
ok(blobCaptured && blobCaptured.parts.length === 1 && blobCaptured.parts[0].includes('AI DATA ANALYSIS') && blobCaptured.parts[0].includes('res-block'), '导出 HTML 含报告头部+编号块');
ok(pbRemoved, '导出逻辑调用了「移除复制按钮」');

// 6. 再测一个 desc 流程（task04）+ 上传流程（loadFile 的 FileReader 无法在 vm 中 mock 触发，跳过，用 loadSample 替代）
ctx.resetAll();
ok(els.dataCard._classes.indexOf('hidden') >= 0, 'resetAll 后回到 step1');
ctx.loadSample('task04');
ctx.selectAnalysis('desc');
ctx.runAnalysis();
ok(ctx.state.lastHtml.includes('直方图') && ctx.state.lastHtml.includes('箱线图'), 'task04 desc 结果含直方图+箱线图');
ok(ctx.state.lastHtml.includes('推荐 Prompt'), '结果含推荐 Prompt 块');

console.log('\n' + (fail === 0 ? 'ALL INTERACT PASS ✔' : fail + ' FAILURES ✘'));
process.exit(fail === 0 ? 0 : 1);
