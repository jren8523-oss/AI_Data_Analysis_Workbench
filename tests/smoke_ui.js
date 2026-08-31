// 冒烟测试：加载 index.html 内联脚本（mock DOM），验证
// 1) 十示例可解析、可被推荐分析运行、render 产出完整 HTML
// 2) 关键数值自洽（指数体系 / 回归 R² / 置信区间 / 描述统计）
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync('index.html', 'utf8');
const code = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function makeEl() {
  const el = {
    style: {}, dataset: {}, innerHTML: '', textContent: '', value: '',
    classList: { add(){}, remove(){}, toggle(){}, contains(){ return false; } },
    addEventListener(){}, querySelectorAll(){ return []; }, querySelector(){ return null; },
    scrollIntoView(){}, remove(){}, appendChild(){}, removeChild(){}, closest(){ return null; }, click(){}
  };
  return el;
}
const els = {};
const documentMock = {
  getElementById(id){ return els[id] || (els[id] = makeEl()); },
  createElement(){ return makeEl(); },
  body: { appendChild(){}, removeChild(){} },
  querySelector(){ return makeEl(); },
  querySelectorAll(){ return []; }
};

const ctx = {
  console,
  window: { scrollTo(){} },
  document: documentMock,
  navigator: { clipboard: null },
  setTimeout, clearTimeout,
  requestAnimationFrame(fn){ return fn(); },
  URL: { createObjectURL(){ return 'blob:mock'; }, revokeObjectURL(){} },
  Blob: function(){}, FileReader: function(){}
};
vm.createContext(ctx);
vm.runInContext(code, ctx, { filename: 'index-inline.js' });

const AN = ctx.ANALYSES, SM = ctx.SAMPLES;
let fail = 0;
const ok = (cond, msg) => { if (cond) console.log('  PASS', msg); else { console.error('  FAIL', msg); fail++; } };

console.log('== 1. 分析类型完整性 ==');
ok(Object.keys(AN).length === 8, 'ANALYSES 8 项');
Object.keys(AN).forEach(k => {
  const a = AN[k];
  ok(typeof a.detect === 'function' && typeof a.config === 'function' &&
     typeof a.run === 'function' && typeof a.render === 'function', k + ' 四件套齐全');
});

console.log('== 2. 示例库加载 + 推荐分析运行 ==');
Object.keys(SM).forEach(k => {
  const s = SM[k];
  if (s.placeholder) { console.log('  SKIP', k, '(placeholder)'); return; }
  const ds = ctx.parseCSV(s.csv);
  ok(ds.headers.length >= 2 && ds.rows.length >= (k === 'task06' ? 3 : 5), k + ' 解析 ' + ds.rows.length + ' 行 x ' + ds.headers.length + ' 列');
  const reco = s.analysis || Object.keys(AN).find(kk => AN[kk].detect(ds));
  ok(!!reco, k + ' 推荐分析: ' + reco);
  const a = AN[reco];
  const cfgEls = a.config(ds).match(/id="cfg_[a-z0-9_]+"/g) || [];
  const cfg = {};
  cfgEls.forEach(m => { const id = m.slice(4, -1); cfg[id.slice(4)] = '0'; });
  const res = a.run(ds, cfg);
  const out = a.render(ds, cfg, res);
  ok(out.indexOf('res-block') >= 0 && out.length > 500, k + ' render 产出 ' + out.length + ' 字符');
});

console.log('== 3. 关键数值自洽 ==');
// 描述统计：task04 电费
const t4 = ctx.parseCSV(SM.task04.csv);
const d4 = ctx.describe(ctx.colValues(t4.rows, 1));
ok(d4.variance >= 0 && d4.std >= 0 && d4.range === d4.max - d4.min, 'task04 描述统计自洽 (var/std/range)');
// 指数体系自洽：task06
const t6 = ctx.parseCSV(SM.task06.csv);
const ia = ctx.indexAnalysis(
  ctx.colValues(t6.rows, 1), ctx.colValues(t6.rows, 2),
  ctx.colValues(t6.rows, 3), ctx.colValues(t6.rows, 4));
const relErr = Math.abs(ia.kTotal - ia.kqL * ia.kpP) / ia.kTotal;
ok(relErr < 1e-9, 'task06 指数体系 K总=Kq拉*Kp帕 (err=' + relErr.toExponential(2) + ')');
ok(Math.abs(ia.eTotal - (ia.eQ + ia.eP)) < 1e-6, 'task06 绝对额 eQ+eP=eTotal');
// 回归：task07
const t7 = ctx.parseCSV(SM.task07.csv);
const lg = ctx.linreg(ctx.colValues(t7.rows, 1), ctx.colValues(t7.rows, 2));
ok(lg.r2 >= 0 && lg.r2 <= 1.000001 && Math.abs(lg.r) <= 1.000001, 'task07 R²∈[0,1], |r|≤1 (r=' + lg.r.toFixed(4) + ')');
// 抽样：task05 均值区间下限<上限
const t5 = ctx.parseCSV(SM.task05.csv);
const mi = ctx.meanInterval(ctx.colValues(t5.rows, 1));
ok(mi.lower < mi.upper && mi.se > 0, 'task05 置信区间 lower<upper, SE>0');
// 时序：task08 几何平均速度 0<x<2
const t8 = ctx.parseCSV(SM.task08.csv);
const ta = ctx.tsAnalysis(ctx.colValues(t8.rows, 1));
ok(ta.geoMean > 0 && ta.avgGrowth === (ta.last - ta.first) / (ta.n - 1), 'task08 几何速度>0 且平均增长量口径一致');
// 清洗：task03 必发现问题
const t3 = ctx.parseCSV(SM.task03.csv);
const cd = ctx.cleanDiagnose(t3);
ok(cd.issues.length >= 4, 'task03 清洗诊断发现问题 ' + cd.issues.length + ' 项 (缺失/文本数字/异常值/重复行 4 类命中)');

console.log('== 4. 图表函数 ==');
ok(ctx.svgBar(['A','B'], [1,2]).indexOf('<svg') === 0, 'svgBar');
ok(ctx.svgLine(['A','B'], [{name:'s', values:[1,2]}]).indexOf('<svg') === 0, 'svgLine');
ok(ctx.svgPie(['A','B'], [1,2]).indexOf('<svg') === 0, 'svgPie');
ok(ctx.svgHist([1,2,3,4,5], {}).indexOf('<svg') === 0, 'svgHist');
ok(ctx.svgBox([1,2,3,4,5], {}).indexOf('<svg') === 0, 'svgBox');
ok(ctx.svgScatter([1,2,3],[4,5,6], {}).indexOf('<svg') === 0, 'svgScatter');
ok(ctx.svgLineForecast(['a','b'],[1,2], {trend:{predict:(t)=>1+t*0.5}, forecastVals:[2.5], forecastN:1}).indexOf('<svg') === 0, 'svgLineForecast');
ok(ctx.svgGroupedBar(['a','b'],[{name:'x',values:[1,2]}], {}).indexOf('<svg') === 0, 'svgGroupedBar');

console.log('\n' + (fail === 0 ? 'ALL PASS ✔' : fail + ' FAILURES ✘'));
process.exit(fail === 0 ? 0 : 1);
