# 扩能任务提示词（4 个统计方法 · 精简版）

你能直接读到 `index.html`（单文件统计工作台）。所有方法定义在 `var ANALYSES = {...}` 对象里，每个方法含 4 个钩子：`detect` / `config` / `run` / `render`。动笔前先读这 3 处作参照：① `corr` 方法（多选列 + 矩阵计算）；② `cluster` 方法（多选列 + 自定义算法）；③ 文件中部那一大段辅助函数区。

## 铁律（GPT 最容易翻车的 5 点，逐条自检）

1. **严格 ES5**：用 `var`、`function` 表达式；不用 `let/const`、箭头函数、模板字符串、`Array.fill`。
2. **多选列的值是字符串数组**：`<select multiple>` 读出来是 `["0","1","2"]`，必须 `[].concat(cfg.cols||[]).map(function(x){return parseInt(x,10);})` 转数字——照抄 `corr.run` 开头那行。
3. **图标格式**：`icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">...</svg>'`，抄任意现有方法。
4. **用户数据进 HTML 必须 `escXML()` 转义**；数值用 `fmtNum(v, 位)` / `fmtPct(v, 位)`。
5. **结果区只用现成组件**：`resBlock(标题, html)`、`metricCard(标签,值,单位,高亮)`、`formulaCard(标签,公式,代入,结果)`、`finding(层级,标题,文字)`、`preTable(表头,行)`；finding 层级 = `fact`/`anl`/`sug`/`warn`。

## 有现成、直接复用（文件里搜得到，勿重写）

`fDistP(f,df1,df2)`、`tDist2tail(t,df)`、`tDist1tail`、`normCdf`、`chi2P`、`betaInc`、`gammaincP/Q`、`pearson`、`spearman`、`rankAll`、`variance`(样本方差 ddof=1)、`mean`、`sum`、`describe`、`linreg`、`colOptions`、`colValues`、`parseNum`、`isNumCol`、`levelCount`、`multiSelHtml`、`customSel`、`selHtml`、`svgHist`、`svgBox`、`svgScatter`、`svgLine`、`svgPie`、`svgClusterScatter`。

## 没有现成、必须自己写

- 矩阵运算（乘法、**高斯消元求逆**）
- **特征值分解**（对称矩阵，用 Jacobi 旋转迭代）
- 逻辑回归的 **IRLS 迭代**
- **Shapiro-Wilk 系数**（Royston 1992 近似）与 p 值近似

---

## 任务 1 · 多元线性回归（key: `mregress`）

**做什么**：1 个因变量 y + ≥2 个自变量 x₁…xₖ，拟合 ŷ = b₀ + b₁x₁ + … + bₖxₖ。

- `detect`：数值列 ≥ 3
- `config`：因变量单选（`selHtml`）+ 自变量多选（`multiSelHtml`，默认选除 y 外的前 2~4 个数值列，上限 5）
- `run` 返回：`{yName, xNames, b:[b0..bk], se, t, p, r2, adjR2, F, pF, n, df}`
- `render`：① 回归方程 + R²/调整 R² → ② 系数表（系数/标准误/t/p，preTable）→ ③ 整体 F 检验 → ④ 分层解读（整体是否显著、哪些系数显著、解释力度、共线性/外推警示）

**算法**：listwise 成对剔除 → 设计矩阵 X=[1,x₁…xₖ] → b=(XᵀX)⁻¹Xᵀy（高斯消元求逆）→ σ̂²=SSE/(n−k−1) → se(bⱼ)=σ̂√((XᵀX)⁻¹ⱼⱼ) → t=b/se、p=`tDist2tail(|t|, n−k−1)` → R²=1−SSE/SST、调整 R²=1−(1−R²)(n−1)/(n−k−1) → F=(R²/k)/((1−R²)/(n−k−1))、p=`fDistP(F,k,n−k−1)`。

**验口径（必须过）**：构造 `y = 5 + 2x₁ − 3x₂` 精确线性（10 组无噪声）。应还原 b₀=5、b₁=2、b₂=−3（误差<1e-6）、R²=1、p≈0。附实测结果。

## 任务 2 · 逻辑回归（key: `logit`）

**做什么**：二分类 y∈{0,1}，拟合 P(y=1)=1/(1+e^(−(b₀+b₁x₁+…+bₖxₖ)))。

- `detect`：存在 1 个「只有两个取值」的列 + ≥1 数值列
- `config`：二分类因变量下拉 + 自变量多选
- `run` 返回：`{yName, xNames, b, se, z, p, oddsRatio, nll, accuracy}`
- `render`：① 方程（logit 形式 + 概率形式）→ ② 系数表（系数/标准误/z/p/OR=e^b）→ ③ 模型拟合（负对数似然 + 准确率）→ ④ 分层解读（显著变量、OR 含义、分离/样本量警示）

**算法**：二分类列编码 0/1（最小类=0）→ listwise 剔除 → **IRLS** 或梯度下降估计（收敛 1e-6、最大 100 次）→ se=Hessian 逆对角开方（H=XᵀWX，W=diag(p̂ᵢ(1−p̂ᵢ))）→ z=b/se、p=2*(1−`normCdf(|z|)`) → OR=e^b → 准确率=0.5 阈值正确率。

**验口径**：x=1..10，y=1 当 x>5.5。应方向为正且明显、准确率=100%。

## 任务 3 · 探索性因子分析（key: `factor`）

**做什么**：多题项主成分法因子分析，输出载荷矩阵 + 方差解释率。

- `detect`：数值列 ≥ 3
- `config`：题项多选（上限 8）+ 因子数（`customSel` 1~5，默认 2）
- `run` 返回：`{names, corrMat, eigenvalues, loadings, communalities, varExplained}`
- `render`：① 相关矩阵 → ② 特征值 + 方差贡献/累计% 表 → ③ 因子载荷矩阵 → ④ 分层解读（因子含义、累计解释率是否达标、载荷<0.4 视为弱）

**算法**：`pearson` 算相关矩阵 → **Jacobi 旋转**求特征值（降序）与特征向量 → 载荷 = 特征向量 × √λ → 共同度 = 行载荷平方和 → 方差解释率 = λᵢ/Σλ。

**验口径**：6 题，前 3 题强相关、后 3 题强相关、两组近乎无关。应前 2 特征值显著大，载荷呈「前 3 题挂因子1、后 3 题挂因子2」的块状。附说明。

## 任务 4 · Shapiro-Wilk 正态性检验（key: `swilk`）

**做什么**：单列数值的 Shapiro-Wilk 检验，输出 W 与 p。

- `detect`：数值列 ≥ 1
- `config`：数值列单选
- `run` 返回：`{col, n, W, p, skew, kurt}`
- `render`：① W + p → ② 偏度/峰度 → ③ 直方图（`svgHist`）→ ④ 分层解读（p<0.05 拒绝、改非参数；小样本功效不足警示）

**算法**：排序 x(1)≤…≤x(n) → 用 **Royston (1992) 近似**算正态顺序统计量系数 aᵢ（不查表）→ W=(Σaᵢx(i))²/Σ(x−x̄)² → p 用 Royston 变换近似。若系数近似太难，可用 **Shapiro-Francia**（正态分位数相关系数）替代，但必须在注释里明确标注。

**验口径**：均匀分布或明显偏态 → p 显著<0.05；正态随机样本（30 个）→ p>0.05。说明与 scipy.stats.shapiro 的「拒绝/不拒绝」结论一致。

---

## 每个任务结尾都要求 GPT 这样输出

只返回**一段可直接插入 `ANALYSES` 的完整代码块**（含 name/short/desc/fit/icon/detect/config/run/render 全部字段），代码块后用 3~5 行说明：① 验口径实测结果；② 复用了哪些现成函数、新写了哪些。不要寒暄。
