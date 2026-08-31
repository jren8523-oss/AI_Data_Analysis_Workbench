# GitHub 同步操作手册（自己来版）

> 准备工作已完成：`.gitignore` 已就位（挡住了 `__pycache__` 等垃圾），
> README / 验收报告无本地路径泄漏，代码无敏感信息。

## 第 1 步：GitHub 网页上建仓库

1. 打开 https://github.com/new
2. Repository name 填：`AI-Data-Analysis-Workbench`（或你喜欢的名字）
3. 可见性自己选：Public（学生/同事可见）/ Private（仅自己）
4. **不要勾选** README、.gitignore、license（本地已有 README，别重复）
5. 点 Create repository
6. 创建后会看到一行推送命令，先别急着复制，用下面的

## 第 2 步：本地推送（在 Git Bash 里）

```bash
cd "C:/Users/lenovo/Desktop/AI_Data_Analysis_Workbench"

git init
git add .
git commit -m "AI 数据分析工作台：10 任务 + 交互式三步向导 + 双引擎 + 验收报告"
git branch -M main
git remote add origin https://github.com/<你的用户名>/AI-Data-Analysis-Workbench.git
git push -u origin main
```

把 `<你的用户名>` 换成你的 GitHub 用户名（git 全局配置里是 jren8523-oss，如果一致就直接用这个）。

## 第 3 步：认证（会弹浏览器）

第一次 push 时，Git Credential Manager 会自动弹出浏览器窗口让你登录 GitHub。
点允许授权即可，**之后就不会再弹了**。
如果没弹窗，说明之前试过一次失败了，重跑 `git push -u origin main` 即可。

## 可选：不想提交 output/（生成物）

如果不想把 9 份 HTML 报告 + PPTX 传上去（想让别人 clone 后自己跑脚本生成），
编辑 `.gitignore`，把最后一行 `# output/` 的注释符去掉（变成 `output/`），
再执行第 2 步。

## 验证

推送完成后打开 https://github.com/<你的用户名>/AI-Data-Analysis-Workbench 检查。

之后更新代码只需要：
```bash
git add .
git commit -m "改了什么"
git push
```
