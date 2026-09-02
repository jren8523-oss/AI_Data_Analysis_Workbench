// 交互冒烟：验证当前单页三栏工作台的真实结构与动态配置。
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync('index.html', 'utf8');
const code = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function makeEl(tag) {
  const el = {
    tagName: tag || 'div', style: {}, dataset: {}, innerHTML: '', textContent: '', value: '',
    _classes: [],
    classList: {
      add(c){ if (!el._classes.includes(c)) el._classes.push(c); },
      remove(c){ el._classes = el._classes.filter(x => x !== c); },
      toggle(c, on){ if (on === undefined ? !el._classes.includes(c) : on) el.classList.add(c); else el.classList.remove(c); },
      contains(c){ return el._classes.includes(c); }
    },
    addEventListener(){}, removeEventListener(){},
    querySelectorAll(){ return []; }, querySelector(){ return null; },
    scrollIntoView(){}, remove(){}, appendChild(){}, removeChild(){}, closest(){ return null; }, click(){}
  };
  return el;
}

const els = {};
const documentMock = {
  getElementById(id){ return els[id] || (els[id] = makeEl('div')); },
  createElement(tag){ return makeEl(tag); },
  body: { appendChild(){}, removeChild(){} },
  querySelector(){ return makeEl(); }, querySelectorAll(){ return []; }
};
const ctx = {
  console, document: documentMock, window: { scrollTo(){} }, navigator: { clipboard: null },
  setTimeout, clearTimeout, requestAnimationFrame(fn){ return fn(); },
  URL: { createObjectURL(){ return 'blob:mock'; }, revokeObjectURL(){} }, Blob: function(){}, FileReader: function(){}
};
vm.createContext(ctx);
vm.runInContext(code, ctx, { filename: 'index-inline.js' });

let fail = 0;
const ok = (cond, msg) => { if (cond) console.log('  PASS', msg); else { console.error('  FAIL', msg); fail++; } };

console.log('== 1. 当前工作台结构 ==');
ok(html.includes('class="topbar"') && html.includes('class="workbench"'), '顶栏 + 三栏工作台存在');
ok((html.match(/<section class="col">/g) || []).length === 3 && html.includes('id="anGroups"') && html.includes('id="result"'), '数据、分析、结果三区存在');
ok(html.includes('教学版') && !html.includes('class="appbar"'), '测试的是当前工作台页面，而非旧 v2 平台壳');

console.log('== 2. 响应式与配置切换 ==');
ok(/@media \(max-width:768px\)[\s\S]*?\.workbench\{display:block/.test(html), '手机端三栏纵向堆叠');
ok(html.includes('function syncConfigFields') && html.includes('typeSel.addEventListener("change"'), '配置类型切换已绑定');
ok(html.includes('cfg_fitDiv') && html.includes('cfg_frDiv') && html.includes('cfg_pairedDiv'), '卡方、非参数与 t 检验的分支表单齐全');
ok(!html.includes('cfg_pmeth'), '未实现的精确 p 值选项已移除');

console.log('== 3. 动态配置渲染 ==');
ctx.state.ds = ctx.parseCSV(ctx.SAMPLES.task09.csv);
ctx.renderConfig('chi2');
ok(els.cfgFields.innerHTML.includes('cfg_fitDiv') && els.cfgFields.innerHTML.includes('cfg_yatesRow'), '卡方配置可渲染拟合优度和 Yates 选项');
ctx.renderConfig('nonparam');
ok(els.cfgFields.innerHTML.includes('cfg_mwDiv') && els.cfgFields.innerHTML.includes('cfg_frDiv'), '非参数四种检验配置可渲染');
ctx.renderConfig('ttest');
ok(els.cfgFields.innerHTML.includes('cfg_pairedDiv') && els.cfgFields.innerHTML.includes('cfg_oneDiv'), 't 检验三种模式配置可渲染');

console.log('\n' + (fail === 0 ? 'ALL INTERACT PASS ✔' : fail + ' FAILURES ✘'));
process.exit(fail === 0 ? 0 : 1);
