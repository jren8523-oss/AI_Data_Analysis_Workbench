import fs from 'node:fs';
import path from 'node:path';

const project = 'C:/Users/lenovo/Desktop/AI_Data_Analysis_Workbench/ppt_master_build/workbench_process_deck_20260902';
const outDir = path.join(project, 'svg_output');
fs.mkdirSync(outDir, { recursive: true });

const C = {
  bg: '#F7F6F2', panel: '#EEF1F2', ink: '#171717', muted: '#6E7476',
  blue: '#1F6EA8', orange: '#C76D3A', green: '#5C7A72', line: '#D4D7D8', white: '#FFFFFF'
};
const font = 'Microsoft YaHei, Arial, sans-serif';

function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
function t(x, y, text, size=24, fill=C.ink, weight=400, anchor='start', extra='') {
  return `<text x="${x}" y="${y}" font-family="${font}" font-size="${size}px" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}" ${extra}>${esc(text)}</text>`;
}
function lines(x, y, arr, size=24, fill=C.ink, weight=400, gap=34, anchor='start') {
  return `<text x="${x}" y="${y}" font-family="${font}" font-size="${size}px" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}">${arr.map((s,i)=>`<tspan x="${x}" dy="${i===0?0:gap}">${esc(s)}</tspan>`).join('')}</text>`;
}
function rect(x,y,w,h,fill='none',stroke='none',sw=1,rx=0,extra='') { return `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" rx="${rx}" ${extra}/>`; }
function line(x1,y1,x2,y2,stroke=C.line,sw=1,dash='') { return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${stroke}" stroke-width="${sw}" ${dash?`stroke-dasharray="${dash}"`:''}/>`; }
function circle(cx,cy,r,fill=C.blue,stroke='none',sw=1) { return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`; }
function img(file,x,y,w,h,mode='meet',id='image') { return `<image id="${id}" href="../images/${file}" x="${x}" y="${y}" width="${w}" height="${h}" preserveAspectRatio="xMidYMid ${mode}"/>`; }
function label(x,y,textv,fill=C.blue) { return `${rect(x,y-24,150,30,fill,'none',0,15)}${t(x+75,y-3,textv,16,C.white,700,'middle')}`; }
function header(kicker, title, page, dark=false) {
  const fg = dark ? C.white : C.ink, sub = dark ? '#D9E5EB' : C.muted, rule = dark ? '#557386' : C.line;
  return `${t(64,44,kicker.toUpperCase(),14,dark?C.orange:C.blue,700)}${t(1180,44,String(page).padStart(2,'0'),14,sub,700,'end')}${line(64,62,1216,62,rule,1)}${t(64,122,title,54,fg,800)}`;
}
function base(content, role='content', dark=false) {
  return `<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" data-pptx-page-role="${role}">${rect(0,0,1280,720,dark?'#18262D':C.bg)}${content}</svg>`;
}
function save(n, svg) { fs.writeFileSync(path.join(outDir, `slide-${String(n).padStart(2,'0')}.svg`), svg, 'utf8'); }

// P01 Cover
save(1, base(`${rect(64,64,8,8,C.blue)}${t(88,70,'AI DATA ANALYSIS WORKBENCH',14,C.muted,700)}${t(64,206,'我如何做出一个',58,C.ink,800)}${t(64,276,'数据分析工作台',76,C.ink,800)}${lines(68,350,['从课程材料、需求对齐到界面实现与功能验收'],28,C.muted,400,38)}${line(64,438,1216,438,C.line,1)}${t(64,504,'制作过程复盘',20,C.blue,700)}${t(1216,504,'Part 1 / Part 2',18,C.muted,400,'end')}${rect(774,146,398,330,C.panel,C.line,1,12)}${rect(808,180,330,34,C.blue,'none',0,8)}${t(826,203,'DATA ANALYSIS WORKBENCH',15,C.white,700)}${rect(808,242,156,190,C.white,C.line,1,8)}${rect(982,242,156,190,C.white,C.line,1,8)}${circle(838,274,9,C.orange)}${t(858,280,'输入数据',16,C.ink,700)}${circle(838,318,9,C.green)}${t(858,324,'选择分析',16,C.ink,700)}${circle(838,362,9,C.blue)}${t(858,368,'查看交付',16,C.ink,700)}${t(1002,280,'分析结果',16,C.ink,700)}${line(1008,330,1110,330,C.blue,5)}${line(1008,360,1090,360,C.green,5)}${line(1008,390,1120,390,C.orange,5)}${t(64,660,'01 / WORKBENCH PROCESS',14,C.muted,700)}`,'cover',false));

// P02 Material to requirement
save(2, base(`${header('01 / 起点','先让 AI 读懂课程材料',2)}${t(70,186,'我先把老师上课用的 10 个课程 PPT 交给 AI。',30,C.ink,700)}${t(70,232,'先理解课程内容，再决定要做什么工具。',24,C.muted)}${line(70,300,1150,300,C.line,2)}${circle(118,410,36,C.blue)}${t(118,420,'01',20,C.white,800,'middle')}${t(180,390,'输入',18,C.muted,700)}${t(180,424,'10 个课程 PPT',32,C.ink,700)}${line(380,410,490,410,C.blue,2)}${circle(540,410,36,C.green)}${t(540,420,'02',20,C.white,800,'middle')}${t(602,390,'理解',18,C.muted,700)}${t(602,424,'让 AI 总结课程任务',32,C.ink,700)}${line(830,410,940,410,C.blue,2)}${circle(990,410,36,C.orange)}${t(990,420,'03',20,C.white,800,'middle')}${t(1052,390,'需求',18,C.muted,700)}${t(1052,424,'做一个工作台',32,C.ink,700)}${rect(70,550,1140,74,C.panel,'none',0,8)}${t(96,598,'课程材料  →  AI 理解  →  清晰需求',30,C.ink,800)}${t(1210,682,'先把问题说清楚，再开始制作',16,C.muted,400,'end')}`));

// P03 Experts and skills
save(3, base(`${header('02 / 配置','给 AI 配上合适的角色和能力',3)}${lines(70,188,['WorkBuddy 里有很多专家和技能。','我选择“工作台搭建师”，再按需要挂载 Skill。'],28,C.ink,700,42)}${rect(70,312,504,292,C.panel,'none',0,12)}${t(96,356,'Expert',20,C.blue,800)}${t(96,396,'决定 AI 怎么想',36,C.ink,800)}${lines(96,448,['工作台搭建师','负责从产品角度拆解需求、规划结构。'],22,C.muted,400,34)}${rect(610,312,600,292,C.white,C.line,1,12)}${img('workbuddy-experts-skills.png',626,328,568,260,'meet','workbuddy-experts')}${label(626,572,'工作台搭建师',C.blue)}${t(804,568,'选择合适的协作角色',18,C.muted,400)}`));

// P04 Grill-me
save(4, base(`${header('03 / 对齐','先把需求问清楚',4)}${t(70,184,'工具：grill-me',34,C.ink,800)}${t(70,226,'它会通过多轮提问，把“大概想法”问成可以开始设计的方案。',24,C.muted)}${rect(70,282,1140,144,C.white,C.line,1,10)}${img('grill-me-guide.png',92,302,1096,102,'meet','grill-me')}${line(70,486,1210,486,C.line,1)}${circle(116,558,30,C.blue)}${t(116,566,'1',20,C.white,800,'middle')}${t(170,566,'提出大致想法',24,C.ink,700)}${circle(496,558,30,C.green)}${t(496,566,'2',20,C.white,800,'middle')}${t(550,566,'多轮追问',24,C.ink,700)}${circle(832,558,30,C.orange)}${t(832,566,'3',20,C.white,800,'middle')}${t(886,566,'形成清晰构思',24,C.ink,700)}${t(1210,680,'需求越具体，后面越少返工',16,C.muted,400,'end')}`));

// P05 Design skills comparison
save(5, base(`${header('04 / 设计','先设计界面，再开始实现',5)}${t(70,180,'可以先构思界面，再让不同的设计 Skill 给出视觉参考。',28,C.ink,700)}${t(70,222,'效果会不同，但目的都是减少试错。',22,C.muted)}${line(70,270,1210,270,C.line,1)}${rect(70,304,260,300,C.white,C.line,1,10)}${img('taste-skill-example.png',82,316,236,252,'meet','taste-skill')}${t(200,594,'taste-skill',18,C.ink,700,'middle')}${rect(360,304,260,300,C.white,C.line,1,10)}${img('ui-ux-pro-max-example.png',372,316,236,252,'meet','ui-ux')}${t(490,594,'UI-UX-PRO-MAX',18,C.ink,700,'middle')}${rect(650,304,260,300,C.white,C.line,1,10)}${img('frontend-design-example.png',662,316,236,252,'meet','frontend-design')}${t(780,594,'frontend-design',18,C.ink,700,'middle')}${rect(940,304,270,300,C.panel,C.line,1,10)}${img('skill-comparison.png',952,316,246,252,'meet','skill-comparison')}${t(1075,594,'不同审美方向',18,C.ink,700,'middle')}`));

// P06 Build
save(6, base(`${header('05 / 实现','先搭骨架，再填功能',6)}${t(70,184,'有了界面参考以后，我把制作拆成三件事。',30,C.ink,700)}${line(112,300,112,572,C.blue,4)}${circle(112,316,18,C.blue)}${t(156,326,'规划功能',26,C.ink,800)}${t(156,360,'写说明文档，或边讨论边确定功能范围。',22,C.muted)}${circle(112,418,18,C.green)}${t(156,428,'搭好 UI',26,C.ink,800)}${t(156,462,'在 Codex 里持续微调界面结构。',22,C.muted)}${circle(112,520,18,C.orange)}${t(156,530,'填入功能',26,C.ink,800)}${t(156,564,'让 AI 补上数据处理和交付逻辑。',22,C.muted)}${rect(760,264,430,300,C.panel,'none',0,12)}${t(800,320,'最后再做质量检查',28,C.blue,800)}${lines(800,380,['karpathy','检查代码是否简单、可靠','superpower','检查功能是否完整、可用'],24,C.ink,700,42)}${line(800,528,1120,528,C.line,1)}${t(800,560,'先骨架，后细节，再验收',22,C.muted,400)}`));

// P07 Summary process
save(7, base(`${header('RECAP','我的做法：把一次任务做成可复用工具',7)}${t(70,194,'不是让 AI 一键生成，而是让 AI 在每一步承担具体工作。',32,C.ink,800)}${line(70,246,1210,246,C.line,1)}${['读材料','定角色','做对齐','画界面','写功能','做检查'].map((s,i)=>{const y=318+i*50; return `${t(76,y,String(i+1).padStart(2,'0'),18,i===5?C.orange:C.blue,800)}${t(142,y,s,26,C.ink,700)}${t(360,y,['建立课程背景','选择 Expert + Skill','把想法问具体','先看结构和审美','从 UI 进入可运行工具','确认功能能用、结果可交付'][i],21,C.muted)}`;}).join('')}${rect(70,642,1140,36,C.blue,'none',0,4)}${t(640,667,'制作逻辑 = 理解问题 + 组织能力 + 分步验证',22,C.white,800,'middle')}`));

// P08 Whole workbench
save(8, base(`${header('PART 2 / 使用','做出来以后，怎么用？',8)}${rect(70,160,850,438,C.white,C.line,1,10)}${img('workbench-full.png',84,174,822,410,'meet','workbench-full')}${t(956,212,'数据',18,C.blue,800)}${t(956,250,'放左边',32,C.ink,800)}${lines(956,290,['上传数据或切换数据源。'],20,C.muted,400,30)}${line(956,350,1178,350,C.line,1)}${t(956,392,'任务',18,C.green,800)}${t(956,430,'选中间',32,C.ink,800)}${lines(956,470,['选择想做的分析。'],20,C.muted,400,30)}${line(956,530,1178,530,C.line,1)}${t(956,572,'交付',18,C.orange,800)}${t(956,610,'看右边',32,C.ink,800)}${t(956,650,'查看结果并导出 HTML。',20,C.muted,400)}`));

// P09 Data sources and delivery
save(9, base(`${header('PART 2 / 功能','三种数据入口，一个交付出口',9)}${rect(64,160,250,198,C.white,C.line,1,10)}${img('upload-data.png',78,174,222,168,'meet','upload-data')}${t(189,390,'上传数据',22,C.ink,800,'middle')}${t(189,420,'拖入 CSV',18,C.muted,400,'middle')}${rect(332,160,250,198,C.white,C.line,1,10)}${img('public-datasets.png',346,174,222,168,'meet','public-datasets')}${t(457,390,'公开数据库',22,C.ink,800,'middle')}${t(457,420,'直接跳转数据源',18,C.muted,400,'middle')}${rect(600,160,250,198,C.white,C.line,1,10)}${img('bazhuayu-guide.png',614,174,222,168,'meet','bazhuayu')}${t(725,390,'八爪鱼采集',22,C.ink,800,'middle')}${t(725,420,'采集后导出 CSV',18,C.muted,400,'middle')}${rect(900,160,300,408,C.panel,'none',0,10)}${t(936,222,'最后的交付',18,C.orange,800)}${t(936,276,'HTML',48,C.ink,800)}${lines(936,334,['根据需要选择交付形式。','分析结果可以直接查看，','也可以导出成 HTML。'],24,C.ink,400,38)}${line(936,466,1162,466,C.line,1)}${t(936,516,'入口可以不同',22,C.blue,800)}${t(936,552,'分析流程保持一致',22,C.green,800)}`));

// P10 Closing
save(10, base(`${header('CLOSING','最后，我把 AI 组织成了一条制作流程',10)}${t(70,196,'先理解问题，再选择能力。',32,C.ink,800)}${t(70,248,'先设计结构，再实现功能。',32,C.ink,800)}${t(70,300,'最后用结果验证工具。',32,C.ink,800)}${line(70,370,1210,370,C.line,1)}${t(70,438,'制作',18,C.blue,800)}${t(70,480,'读材料 → 定需求 → 选专家和技能 → 设计 → 实现 → 检查',25,C.ink,700)}${t(70,548,'使用',18,C.green,800)}${t(70,590,'放入数据 → 选择分析 → 查看并导出结果',25,C.ink,700)}${rect(70,650,1140,30,C.orange,'none',0,4)}${t(640,672,'这就是我做数据分析工作台的基本逻辑。',22,C.white,800,'middle')}`,'ending',false));

console.log(`Wrote ${10} SVG slides to ${outDir}`);
