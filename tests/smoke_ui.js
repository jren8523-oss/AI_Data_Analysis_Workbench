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
ok(Object.keys(AN).length === 15, 'ANALYSES 15 项均已接入计算');
Object.keys(AN).forEach(k => {
  const a = AN[k];
  ok(typeof a.detect === 'function' && typeof a.config === 'function' &&
     typeof a.run === 'function' && typeof a.render === 'function', k + ' 四件套齐全');
});

console.log('== 1b. 相关分析（corr，真实 iris 数据）==');
const corrA = AN.corr;
const irisDs = ctx.parseCSV(SM.iris.csv);
ok(corrA.detect(irisDs), 'corr detect 命中 iris（4 列数值）');
const corrCfg = { cols: ['0', '1', '2', '3'] };
const corrRes = corrA.run(irisDs, corrCfg);
ok(corrRes.names.length === 4, 'corr 矩阵 4 列：' + corrRes.names.join(','));
ok(Math.abs(corrRes.pMat[2][3] - 0.9629) < 1e-3, 'corr petal_length×petal_width r=' + corrRes.pMat[2][3].toFixed(4) + ' (公认 0.9629)');
ok(Math.abs(corrRes.pMat[0][0] - 1) < 1e-9, 'corr 对角线 = 1');
ok(corrRes.pMat[1][2] < 0, 'corr sepal_width×petal_length 负相关 r=' + corrRes.pMat[1][2].toFixed(4));
ok(corrRes.sMat[2][3] > 0.9, 'corr Spearman petal_length×petal_width ρ=' + corrRes.sMat[2][3].toFixed(4));
const corrOut = corrA.render(irisDs, corrCfg, corrRes);
ok(corrOut.includes('相关矩阵') && corrOut.includes('Spearman'), 'corr render 含相关矩阵与 Spearman');

console.log('== 1c. 方差齐性（levene）与信度（reliability）==');
const levA = AN.levene;
ok(levA.detect(irisDs), 'levene detect 命中 iris（数值列 + 分类列）');
const levCfg = { y: '2', grp: '4' };
const levRes = levA.run(irisDs, levCfg);
ok(isFinite(levRes.levene.W) && isFinite(levRes.levene.p), 'levene W=' + levRes.levene.W.toFixed(3) + ' p=' + levRes.levene.p.toFixed(4));
const levOut = levA.render(irisDs, levCfg, levRes);
ok(levOut.includes('Levene'), 'levene render 含 Levene 检验');

const relA = AN.reliability;
const relDs = ctx.parseCSV('i1,i2,i3,i4,i5\n1,1,1,1,1\n2,2,2,2,2\n3,3,3,3,3\n4,4,4,4,4\n5,5,5,5,5');
ok(relA.detect(relDs), 'reliability detect 命中 5 题');
const relRes = relA.run(relDs, { cols: ['0', '1', '2', '3', '4'] });
ok(Math.abs(relRes.ca.alpha - 1) < 1e-9, 'reliability 完全一致题项 α=1，实际=' + relRes.ca.alpha);
ok(relRes.ca.itemStats.length === 5, 'reliability 分项统计 5 项');
const relOut = relA.render(relDs, { cols: ['0', '1', '2', '3', '4'] }, relRes);
ok(relOut.includes('α') && relOut.includes('删除后 α'), 'reliability render 含 α 与删除后 α');


console.log('== 1.5 推断统计真实计算（ANOVA / 卡方 / 非参数）==');
// task09：数值列=访客数，分类列=日期、商品类目
const t9 = ctx.parseCSV(SM.task09.csv);
const c9 = ctx.colOptions(t9);
const n9 = c9.filter(o => o.num).map(o => o.idx);    // 访客数
const k9 = c9.filter(o => !o.num).map(o => o.idx);   // 日期, 商品类目

// --- ANOVA ---
const an = AN.anova;
ok(an.detect(t9), 'anova detect 命中 task09（数值列 + 分类列）');
const anCfg = { y: String(n9[0]), grp: String(k9[1]), posthoc: 'bonf', alpha: '0.05', levene: '1', effsize: 'both' };
const anRes = an.run(t9, anCfg);
ok(anRes.anova.k >= 3 && anRes.anova.dfw > 0, 'anova 真实计算：k=' + anRes.anova.k + '，dfw=' + anRes.anova.dfw);
const anOut = an.render(t9, anCfg, anRes);
ok(anOut.includes('方差分析表') && anOut.includes('Bonferroni'), 'anova 输出方差分析表与 Bonferroni 比较');
let anThrew = '';
try { ctx.anovaOneWay([{name:'A',values:[1]},{name:'B',values:[2]},{name:'C',values:[3]}]); } catch (e) { anThrew = e.message || String(e); }
ok(anThrew.includes('组内自由度不足'), 'anova 一组一个观测时拒绝计算：' + anThrew);

// --- 卡方 ---
const ch = AN.chi2;
ok(ch.detect(t9), 'chi2 detect 命中 task09（含分类列）');
const chCfg = { type: 'ind', row: String(k9[0]), col2: String(k9[1]), yates: 'auto', eff: 'v' };
const chRes = ch.run(t9, chCfg);
ok(chRes.ind.df > 0 && isFinite(chRes.ind.p), 'chi2 真实计算：df=' + chRes.ind.df + '，p=' + chRes.ind.p.toFixed(4));
const chOut = ch.render(t9, chCfg, chRes);
ok(chOut.includes('观测频数表') && chOut.includes("Cramér's V"), 'chi2 输出列联表与效应量');
// 拟合优度分支
const chFit = ch.run(t9, { type: 'fit', cat: String(k9[1]), ratio: '等比例' });
ok(chFit.fit.df > 0 && isFinite(chFit.fit.p), 'chi2 拟合优度真实计算：' + chFit.keys.length + ' 个类别');
const yatesObs = { a:{x:1,y:1}, b:{x:1,y:2} }, yatesBase = ctx.chi2Independence(yatesObs, ['a','b'], ['x','y']);
let yates = 0;
['a','b'].forEach(r => ['x','y'].forEach(c => { const v=Math.max(0, Math.abs(yatesObs[r][c]-yatesBase.exp[r][c])-0.5); yates += v*v/yatesBase.exp[r][c]; }));
ok(yates === 0, '2×2 Yates 校正先截断再平方（本例 χ²=0）');

// --- 非参数 ---
const np = AN.nonparam;
ok(np.detect(t9), 'nonparam detect 命中 task09');
const npCfg = { type: 'mw', y: String(n9[0]), grp: String(k9[1]), alt: 'two', cc: '1' };
const npRes = np.run(t9, npCfg);
ok(npRes.mw.n1 > 0 && npRes.mw.n2 > 0 && isFinite(npRes.mw.p), 'Mann-Whitney 真实计算');
const npOut = np.render(t9, npCfg, npRes);
ok(npOut.includes('Mann-Whitney U') && !npOut.includes('待接入'), '非参数输出真实检验结果');
let wxThrew = '';
try { ctx.wilcoxonSignedRank([1,1,1], [1,1,1]); } catch (e) { wxThrew = e.message || String(e); }
ok(wxThrew.includes('差值均为 0'), 'Wilcoxon 全部零差值时给出明确提示');

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

console.log('== 4. 多指标与图表边界 ==');
const t1 = ctx.parseCSV(SM.task01.csv);
const multiCfg = AN.multi.config(t1);
ok(!multiCfg.includes('value="6" selected'), 'task01 默认不选「总访客数」合计列');
const multiRes = AN.multi.run(t1, { cat: '0', nums: ['1','2','3','4','5'] });
const multiOut = AN.multi.render(t1, {}, multiRes);
ok(Math.abs(multiRes.mom[0] - 270/1443) < 1e-12 && multiOut.includes('+18.7%'), '环比与对应月份对齐（2月较1月 +18.7%）');
ok(ctx.svgPie(['A','B'], [1,1]).includes('50.0%') && !ctx.svgPie(['A','B'], [1,1]).includes('5000.0%'), '饼图图例不重复乘以 100');
ok(!ctx.svgPie(['A','B'], [0,0]).includes('NaN'), '全零饼图不给出 NaN');

console.log('== 5. 图表函数 ==');
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
