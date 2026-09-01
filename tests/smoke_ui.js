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
ok(Object.keys(AN).length === 12, 'ANALYSES 12 项（9 已实现 + 3 待接入壳子）');
Object.keys(AN).forEach(k => {
  const a = AN[k];
  ok(typeof a.detect === 'function' && typeof a.config === 'function' &&
     typeof a.run === 'function' && typeof a.render === 'function', k + ' 四件套齐全');
});

console.log('== 1.5 待接入能力壳子（ANOVA / 卡方 / 非参数）==');
// task09：数值列=访客数，分类列=日期、商品类目 —— 三个壳子都能覆盖
const t9 = ctx.parseCSV(SM.task09.csv);
const c9 = ctx.colOptions(t9);
const n9 = c9.filter(o => o.num).map(o => o.idx);    // 访客数
const k9 = c9.filter(o => !o.num).map(o => o.idx);   // 日期, 商品类目

// --- ANOVA 壳子 ---
const an = AN.anova;
ok(an.detect(t9), 'anova detect 命中 task09（数值列 + 分类列）');
const anCfg = { y: String(n9[0]), grp: String(k9[1]), posthoc: 'tukey', alpha: '0.05', levene: '1', effsize: 'both' };
const anRes = an.run(t9, anCfg);
ok(anRes.__shell === true && !!anRes.spec, 'anova run 返回 __shell 标记（算法未接入）');
ok(anRes.pre.k >= 3, 'anova 数据体检：分出 ' + anRes.pre.k + ' 组');
ok(anRes.spec.todos.length >= 5, 'anova 待接入清单 ' + anRes.spec.todos.length + ' 项');
const anOut = an.render(t9, anCfg, anRes);
ok(anOut.includes('shell-flag') && anOut.includes('数据体检') && anOut.includes('待接入'), 'anova render 产出三段式规格预览');
ok(anOut.includes('F 统计量') && anOut.includes('Tukey HSD'), 'anova 规格含 F 统计量与 Tukey HSD');
ok(anOut.includes('SS组间') && anOut.includes('SS组内') && anOut.includes('Levene'), 'anova 规格含平方和分解与 Levene 检验');
// 数据不适配时应抛出明确错误（因变量误选文本列 → 有效组为 0）
let anThrew = '';
try { an.run(t9, { y: String(k9[0]), grp: String(n9[0]) }); } catch (e) { anThrew = String(e); }
ok(anThrew.indexOf('有效组') >= 0, 'anova 数据不适配时抛出明确错误：' + anThrew.slice(0, 24));

// --- 卡方壳子 ---
const ch = AN.chi2;
ok(ch.detect(t9), 'chi2 detect 命中 task09（含分类列）');
const chCfg = { type: 'ind', row: String(k9[0]), col2: String(k9[1]), yates: 'auto', eff: 'v' };
const chRes = ch.run(t9, chCfg);
ok(chRes.__shell === true, 'chi2 run 返回 __shell 标记');
ok(chRes.pre.mode === 'ind' && chRes.pre.rKeys.length >= 2 && chRes.pre.cKeys.length >= 2,
   'chi2 列联表 ' + chRes.pre.rKeys.length + ' 行 × ' + chRes.pre.cKeys.length + ' 列');
const chOut = ch.render(t9, chCfg, chRes);
ok(chOut.includes('列联表') && chOut.includes('实际观测频数'), 'chi2 render 产出列联表预览');
ok(chOut.includes('Cram') && chOut.includes('Yates'), 'chi2 规格含 Cramér V 与 Yates 校正');
// 拟合优度分支
const chFit = ch.run(t9, { type: 'fit', cat: String(k9[1]), ratio: '等比例' });
ok(chFit.pre.mode === 'fit' && chFit.pre.keys.length >= 2, 'chi2 拟合优度体检：' + chFit.pre.keys.length + ' 个类别');

// --- 非参数壳子 ---
const np = AN.nonparam;
ok(np.detect(t9), 'nonparam detect 命中 task09');
const npCfg = { type: 'mw', y: String(n9[0]), grp: String(k9[1]), alt: 'two', pmeth: 'auto', cc: '1' };
const npRes = np.run(t9, npCfg);
ok(npRes.__shell === true, 'nonparam run 返回 __shell 标记');
ok(npRes.pre.k >= 2, 'nonparam 数据体检：' + npRes.pre.k + ' 组');
const npOut = np.render(t9, npCfg, npRes);
ok(npOut.includes('Mann-Whitney') && npOut.includes('Kruskal-Wallis') &&
   npOut.includes('Wilcoxon') && npOut.includes('Friedman'), 'nonparam 规格覆盖四种检验');
// 配对分支（task07 两列数值）
const t7np = ctx.parseCSV(SM.task07.csv);
const c7np = ctx.colOptions(t7np).filter(o => o.num).map(o => o.idx);
const npW = np.run(t7np, { type: 'wilcoxon', a: String(c7np[0]), b: String(c7np[1]) });
ok(npW.pre.mode === 'wilcoxon' && npW.pre.n > 0, 'nonparam wilcoxon 体检：' + npW.pre.n + ' 对');
// Friedman 分支（task04 多列数值）
const t4np = ctx.parseCSV(SM.task04.csv);
const c4 = ctx.colOptions(t4np).filter(o => o.num).map(o => o.idx).slice(0, 3);
const npF = np.run(t4np, { type: 'friedman', multi: c4.map(String) });
ok(npF.pre.mode === 'friedman' && npF.pre.cols.length === 3, 'nonparam friedman 体检：' + npF.pre.cols.length + ' 个条件');

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

console.log('== 3.5 t 检验数值自洽 ==');
// t 分布临界值：t(18, 0.975) ≈ 2.1009（标准值，验证 tCritical 二分 + tDist2tail）
const tc18 = ctx.tCritical(18, 0.95);
ok(Math.abs(tc18 - 2.1009) < 0.001, 'tCritical(18,0.95)=' + tc18.toFixed(4) + ' ≈ 2.1009');
ok(Math.abs(ctx.tDist2tail(0, 10) - 1.0) < 1e-9, 'tDist2tail(0,10)=1.0（t=0 双尾 p=1）');
ok(Math.abs(ctx.tDist2tail(tc18, 18) - 0.05) < 1e-3, 'tDist2tail(tCritical,18)=0.05（临界值自洽）');
// 独立样本 Welch：两组明显不同的样本 → 显著
const grpA = [12,11,13,12.5,11.5,12,11.8,12.2], grpB = [9,9.5,8.8,9.2,9.6,9.0,8.9];
const indW = ctx.ttestIndependent(grpA, grpB, { welch: true });
ok(indW.kind === 'ind' && indW.welch === true && indW.df > 0, '独立 Welch：kind=ind, df=' + indW.df.toFixed(2));
ok(indW.p < 0.01 && indW.m1 > indW.m2, '独立 Welch：p=' + indW.p.toExponential(2) + ' < 0.01 且 m1>m2');
ok(indW.ciLower < indW.diff && indW.diff < indW.ciUpper, '独立 Welch：CI 覆盖均值差');
// 独立 Student（等方差）与 Welch 一致量级
const indS = ctx.ttestIndependent(grpA, grpB, { welch: false });
ok(indS.df === grpA.length + grpB.length - 2, '独立 Student：df=n1+n2-2=' + indS.df);
// 配对：前高后低 → t<0 且显著
const pre = [10,11,12,11,10,11,12,11,10,12,11,10], post = [9,9.5,10,10,9,9.8,10.5,9.7,9,10.2,9.5,9];
const pr = ctx.ttestPaired(pre, post);
ok(pr.kind === 'paired' && pr.df === pre.length - 1, '配对：kind=paired, df=' + pr.df);
ok(pr.t > 0 && pr.p < 0.001 && pr.diff > 0, '配对：t=' + pr.t.toFixed(2) + ' >0, p=' + pr.p.toExponential(2) + ' 且差值>0（前高于后）');
ok(Math.abs(pr.diff - (ctx.mean(pre) - ctx.mean(post))) < 1e-9, '配对：diff = mean(pre)-mean(post)');
// 单样本：均值显著高于 μ0
const smp = [5.1,5.0,4.9,5.2,5.1,5.0,5.3,4.8,5.1,5.0];
const one = ctx.ttestOneSample(smp, 4.5);
ok(one.kind === 'one' && one.df === smp.length - 1, '单样本：kind=one, df=' + one.df);
ok(one.t > 0 && one.p < 0.01, '单样本：t=' + one.t.toFixed(2) + ' >0, p=' + one.p.toExponential(2));
ok(Math.abs(one.mean - ctx.mean(smp)) < 1e-9 && one.mu0 === 4.5, '单样本：mean 与 μ0 正确');
// Cohen's d：paired 分支用差值数组
const dp = []; for (let i = 0; i < pre.length; i++) dp.push(pre[i] - post[i]);
ok(Math.abs(ctx.cohenD(dp, null, 'paired') - (ctx.mean(dp) / Math.sqrt(ctx.variance(dp)))) < 1e-9, 'cohenD paired = mean(d)/sd(d)');

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
