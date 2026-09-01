// 交互冒烟（平台壳 v2）：在增强 DOM mock 中驱动完整用户流程
// 流程：平台壳结构 → 路由切换 → loadSampleAndRun 链 → 三栏切换 → 导出 → 壳子预览
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync('index.html', 'utf8');
const code = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function makeEl(tag) {
  const el = {
    tagName: tag || 'div', style: {}, dataset: {}, innerHTML: '', textContent: '', value: '',
    _classes: [], _clicked: false,
    classList: {
      add(c){ if (el._classes.indexOf(c) < 0) el._classes.push(c); },
      remove(c){ const i = el._classes.indexOf(c); if (i >= 0) el._classes.splice(i, 1); },
      toggle(c, f){ const has = el._classes.indexOf(c) >= 0; if (f === undefined ? !has : f) el.classList.add(c); else el.classList.remove(c); },
      contains(c){ return el._classes.indexOf(c) >= 0; }
    },
    addEventListener(){}, removeEventListener(){},
    querySelectorAll(sel){
      if (sel === '.pb-copy') return [{ remove(){ pbRemoved = true; } }];
      return [];
    },
    querySelector(){ return null; },
    scrollIntoView(){}, remove(){}, appendChild(){}, removeChild(){}, closest(){ return null; },
    click(){ el._clicked = true; }
  };
  return el;
}
const els = {};
const clickedEls = [];
let pbRemoved = false;
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
let blobCaptured = null;
const _realSetTimeout = setTimeout;
// 让 loadSampleAndRun 内部的 60/100ms 链式 setTimeout 同步执行；3s 延迟保留异步
function mockSetTimeout(fn, t){
  if (typeof t === 'number' && t < 500){ try { fn(); } catch(e){} return 0; }
  return _realSetTimeout(fn, t);
}
const ctx = {
  console,
  window: { scrollTo(){} },
  document: doc,
  navigator: { clipboard: null },
  setTimeout: mockSetTimeout, clearTimeout,
  requestAnimationFrame(fn){ return fn(); },
  URL: { createObjectURL(b){ blobCaptured = b; return 'blob:mock'; }, revokeObjectURL(){} },
  Blob: function(parts, opts){ this.parts = parts; this.opts = opts; },
  FileReader: function(){}
};
vm.createContext(ctx);
vm.runInContext(code, ctx, { filename: 'index-inline.js' });

let fail = 0;
const ok = (c, m) => { if (c) console.log('  PASS', m); else { console.error('  FAIL', m); fail++; } };

// 初始化在 vm.runInContext 末尾已自动跑：renderSidenav + renderHomeView + renderWorkspace + bindAppEvents + navigate('home')

console.log('== 1. 平台壳结构 ==');
ok(html.includes('class="appbar"') && html.includes('appbar-l') && html.includes('appbar-c') && html.includes('appbar-r'), 'appbar 顶栏（品牌/搜索/操作）在 HTML 中');
ok(els.sidenav && els.sidenav.innerHTML.length > 200, 'sidenav 侧栏已渲染（含菜单）');
ok(html.includes('id="mainArea"') && html.includes('id="menuMask"'), 'main-area + menu-mask 在 HTML 中');
ok(html.includes('appbar-foot') && html.includes('系统状态') && html.includes('v2.2.0'), '底部状态栏在 HTML 中（系统状态/版本号）');
const viewIds = ['view-home','view-workspace','view-knowledge','view-training','view-output'];
ok(viewIds.every(id => els[id]), '5 个 view 容器全部存在（home/workspace/knowledge/training/output）');
ok(els['view-home'].classList.contains('on'), '初始：view-home.on');
ok(viewIds.slice(1).every(id => !els[id].classList.contains('on')), '初始：其余 4 个 view 隐藏');

console.log('== 2. 侧栏多级菜单 ==');
const navHtml = els.sidenav.innerHTML;
ok(navHtml.includes('data-key="home"') && navHtml.includes('data-key="workspace"'), '顶级：首页 + 工作台');
ok(navHtml.includes('data-key="knowledge"') && navHtml.includes('data-key="training"'), '知识库 + 实训中心');
ok(navHtml.includes('data-key="datasrc"') && navHtml.includes('data-key="output"'), '数据工作台 + 输出中心');
ok(navHtml.includes('数据分析知识体系') && navHtml.includes('案例库') && !navHtml.includes('undefined'), '知识库 4 子项渲染（无 undefined）');
const trainingChildren = (navHtml.match(/data-key="training\/task/g) || []).length;
ok(trainingChildren === 10, '实训中心动态生成 ' + trainingChildren + ' 子项（期望 10）');

console.log('== 3. 首页动态渲染 ==');
ok(els.homeQuick && els.homeQuick.innerHTML.includes('qc'), 'home-quick 4 卡渲染（qc-icon/text）');
ok(els.homeProjects && els.homeProjects.innerHTML.includes('pc'), 'home-projects 4 卡渲染（pc-top/title）');
ok(els.homeStats && els.homeStats.innerHTML.includes('sc-num'), 'home-stats 6 指标卡渲染（含数字）');
ok(els.homeStats.innerHTML.includes('12') && els.homeStats.innerHTML.includes('28') && els.homeStats.innerHTML.includes('89'), '指标卡含数据集/分析/图表统计数字');

console.log('== 4. 路由切换 ==');
ctx.navigate('workspace');
ok(els['view-workspace'].classList.contains('on'), 'navigate("workspace") → view-workspace.on');
ok(!els['view-home'].classList.contains('on'), 'navigate("workspace") → view-home 隐藏');
// 侧栏 nav-item 的 .on 高亮由 navigate 内部对真实 DOM 元素 classList.toggle 设置，
// mock 的 querySelectorAll 返回 []，故从 innerHTML 串读不到——此断言改在浏览器 e2e 验证
ctx.navigate('home');
ok(els['view-home'].classList.contains('on'), 'navigate("home") → view-home.on');
ctx.navigate('workspace');

console.log('== 5. loadSampleAndRun(task06) 链：load → renderWSConfig → runWSAnalysis ==');
ctx.loadSampleAndRun('task06');
ok(ctx.state.ds && ctx.state.ds.rows.length === 3, 'task06 数据集 3 行');
ok(ctx.state.reco === 'index', 'task06 推荐 = index（自动检测）');
ok(ctx.state.analysis === 'index', 'loadSampleAndRun 自动选中推荐 = index');
ok(els['view-workspace'].classList.contains('on'), 'loadSampleAndRun 后路由切到 workspace');
ok(els.wsSrc && els.wsSrc.innerHTML.includes('示例库'), '工作台左栏显示数据源');
ok(els.wsVars && els.wsVars.innerHTML.includes('ws-var'), '工作台左栏变量列表');
ok(els.wsAnList && els.wsAnList.innerHTML.includes('ws-abtn'), '工作台中栏分析能力按钮');
ok(els.wsCfgWrap && !els.wsCfgWrap.classList.contains('hidden'), '工作台配置区自动展开');
ok(els.wsCfgFields && els.wsCfgFields.innerHTML.includes('cfg_'), '工作台配置表单已渲染');
ok(els.wsResult && els.wsResult.innerHTML.includes('res-block') && ctx.state.lastHtml.includes('res-block'), '工作台运行结果已渲染（含 res-block）');
ok(ctx.state.lastHtml.includes('指数体系成立') || ctx.state.lastHtml.includes('自洽'), '指数自洽验证块出现');

console.log('== 6. 三栏切换分析能力 ==');
ctx.renderWSConfig('desc');
ok(ctx.state.analysis === 'desc', 'renderWSConfig("desc") → state.analysis=desc');
ok(els.wsCfgFields.innerHTML.includes('cfg_'), 'desc 配置表单重新渲染');
// 中栏 .sel 高亮：mock querySelectorAll 返回 []，状态切换由真实 DOM 完成——跳过 mock 验证

console.log('== 7. 导出独立报告 ==');
ctx.exportReport();
ok(clickedEls.length >= 1, '导出触发 a.click()');
ok(clickedEls.some(a => a.download && /\.html$/.test(a.download)), '导出文件名 .html');
ok(blobCaptured && blobCaptured.parts.length === 1, 'Blob 单 part');
ok(blobCaptured && blobCaptured.parts[0].includes('AI DATA ANALYSIS'), '导出 HTML 含报告头');
ok(blobCaptured && blobCaptured.parts[0].includes('res-block'), '导出 HTML 含结果编号块');
ok(pbRemoved, '导出前移除 .pb-copy 按钮');

console.log('== 8. 壳子预览（task09 + anova/chi2/nonparam）==');
ctx.loadSampleAndRun('task09');
ok(ctx.state.ds && ctx.state.ds.rows.length > 0, 'task09 数据加载');
ok(els.wsAnList.innerHTML.includes('anova') && els.wsAnList.innerHTML.includes('chi2') && els.wsAnList.innerHTML.includes('nonparam'), '三栏中栏列出 3 个待接入壳子');
ctx.renderWSConfig('anova');
ok(ctx.state.analysis === 'anova', '选中 anova 壳子');
ctx.runWSAnalysis();
ok(els.wsResult.innerHTML.includes('shell-flag') && els.wsResult.innerHTML.includes('待接入'), 'anova 壳子 → 规格预览（数据体检 + 待接入）');
ctx.renderWSConfig('chi2');
ctx.runWSAnalysis();
ok(els.wsResult.innerHTML.includes('列联表') && els.wsResult.innerHTML.includes('Cram'), 'chi2 壳子 → 列联表 + Cramér V');
ctx.renderWSConfig('nonparam');
ctx.runWSAnalysis();
ok(els.wsResult.innerHTML.includes('Mann-Whitney') && els.wsResult.innerHTML.includes('Friedman'), 'nonparam 壳子 → 四种检验规格');

console.log('== 9. 重置空态（loadFile 不可 mock FileReader；用 applyDS(null) 等价）==');
ctx.applyDS(null, '', '', null);
ok(els.wsSrc.innerHTML.includes('尚未加载数据'), 'applyDS(null) 后左栏空态');
ok(els.wsVars.innerHTML === '', 'applyDS(null) 后变量列表空');
ok(els.wsCfgFields.innerHTML === '', 'applyDS(null) 后配置区空');
ok(els.wsAnHint && !els.wsAnHint.classList.contains('hidden'), '空态提示可见');
ok(els.wsCfgWrap.classList.contains('hidden'), '空态时配置区隐藏');

console.log('\n' + (fail === 0 ? 'ALL INTERACT PASS ✔' : fail + ' FAILURES ✘'));
process.exit(fail === 0 ? 0 : 1);
