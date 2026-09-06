# Antigravity 技能同步转换方案设计与实现 (`sync-antigravity-skills.py`)

> **设计日期**：2026-09-06  
> **设计目标**：构建 AI Berkshire 投研技能从 Claude Code (`skills/*.md`) 到 Antigravity (`skills_antigravity/*.md`) 的自动化转换机制  
> **核心工具**：[scripts/sync-antigravity-skills.py](file:///Users/wanghaibing/code/ai/ai-berkshire/scripts/sync-antigravity-skills.py)  
> **产物路径**：`skills_antigravity/*.md`  

---

## 1. 背景与核心动机

AI Berkshire 是基于价值投资体系（巴菲特、芒格、段永平、李录）的专业投研技能合集。原本的工作流源文件定义于 `skills/*.md`，最初面向 Claude Code 的 slash-command 体系设计。

随着多环境协同演进，项目已经建立了生成 Codex 技能的同步机制（`scripts/sync-codex-skills.py`）。然而在 **Google Antigravity IDE / Agent Runtime** 环境下，原有格式存在以下关键阻碍：

1. **元数据缺失与无法自动发现**：  
   Antigravity 的自定义能力体系（基于 `agy-customizations`）依赖渐进式披露（Progressive Disclosure）。未携带 YAML frontmatter（`name`、`description`）的单文件 Markdown 无法被 Antigravity 作为标准化 Skill 自动识别并呈现给模型。
2. **命令参数占位符不兼容**：  
   原文件依赖 Claude Code 的 `$ARGUMENTS` 命令行宏替换机制，在 Antigravity 的对话交互与多轮推理中需显式定义其上下文语义。
3. **工具生态调用映射差异**：  
   原文件中大量提及 Claude 特有的“`Task 工具启动后台 Agent`”以及“`使用 Bash`”，需要映射为 Antigravity 的原生能力（`search_web`、`read_url_content`、`browser_subagent` 以及 `run_command`）。
4. **工作区安全边界与输出路径冲突**：  
   部分原始技能（如 `skills/investment-research.md` 第 268 行）要求写入用户家目录 `~/[公司名]投资研究报告.md`，这严重违背了 Antigravity 工作区安全沙箱原则（禁止写 `~`），且与仓库现行的报告分目录归档规范冲突。

为解决上述问题，我们参考 `sync-codex-skills.py` 的设计思路，实现了全新的 `scripts/sync-antigravity-skills.py` 自动化生成工具。

---

## 2. 总体架构与设计原则

```
              ┌──────────────────────────────────────────────┐
              │ Canonical Source (唯一真实源)                 │
              │ skills/*.md                                  │
              └──────────────────────┬───────────────────────┘
                                     │
                    python3 scripts/sync-antigravity-skills.py
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
│ 1. Frontmatter 智能提取与定制    │                 │ 2. Antigravity 适配器层注入     │
│ name: <skill-name>              │                 │ ## Antigravity Adapter Note     │
│ description: 精炼高辨识度投研描述│                 │ - $ARGUMENTS 上下文解析声明     │
└─────────────────────────────────┘                 │ - 工具映射 (search_web/subagent)│
                                                    │ - 严格隔离至 reports_antigravity│
                                                    │ - date 确认数据基准             │
                                                    └─────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 3. 正文清洗与路径收敛 (Transform Body)                                                │
│ - 消除 ~/[公司名]*.md 等非法路径，转换为规范的 reports_antigravity/{公司名}/...       │
│ - 自动适配 20 个子技能的专项报告路径规范                                            │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │ Antigravity Ready Skills 产物                │
              │ skills_antigravity/*.md                      │
              └──────────────────────────────────────────────┘
```

### 核心设计原则

- **单一事实源（Single Source of Truth, SSOT）**：  
  严格以 `skills/*.md` 为唯一维护源，禁止手动修改生成的目标文件；改动源文件后通过脚本一键重新同步。
- **业务语义零损耗（Zero Semantic Loss）**：  
  完整继承四大师思维模型、前置 AI 偏见自觉、财务双源交叉验证、十年折现永续模型以及 15% 抽检准出流程。
- **沙箱安全与路径隔离（Sandbox Security）**：  
  独立创建专用报告归档空间 `reports_antigravity/`，杜绝任何逃逸出 workspace 写入用户系统家目录的隐患。
- **双模式运行（Build & Check）**：  
  支持常规文件生成模式和 `--check` 纯只读校验模式，可直接嵌入 CI/CD 流水线。

---

## 3. 关键实现细节

### 3.1 YAML Frontmatter 生成

每个 Skill 均配备合法的 YAML Frontmatter。为了让 Antigravity 模型在看到技能列表时能精准识别何时激活技能，脚本内置了 `SKILL_DESCRIPTIONS` 映射字典：

```yaml
---
name: investment-research
description: "四大师综合分析框架：巴菲特-芒格-段永平-李录。对指定公司进行系统化投资研究与双源财务验算。"
---
```

若新增技能未在字典中预定义，脚本会自动提取文档的首个一级标题作为降级描述：
`"AI Berkshire 投研技能：{title}。来源：skills/{source_name}。"`

### 3.2 Antigravity 专用适配器声明（Adapter Note）

在正文之前统一注入 `## Antigravity Adapter Note`，为 Agent 提供精准的执行上下文：

```markdown
## Antigravity Adapter Note
- 将 $ARGUMENTS 视为用户在当前对话中指定的分析标的（如公司名称、美股/港股/A股代码）。
- 网络数据收集时，优先使用 `search_web` 和 `read_url_content`，如遇到复杂页面可调用 `browser_subagent`。
- 校验工具调用：使用 `run_command` 在工作区根目录下执行 `python3 tools/...`。
- 报告产出路径：严格保存至 `{report_path}`，严禁写入 `~`。
- 投研前务必使用 `date` 确认今日基准日期。
```

其中 `{report_path}` 会根据技能类型动态映射至合规路径，例如：
- 个股综合投研：`reports_antigravity/{公司名}/{公司名}-research-{YYYYMMDD}.md`
- 团队分析报告：`reports_antigravity/{公司名}/最终报告.md`
- 行业研究报告：`reports_antigravity/{行业名}-industry-{YYYYMMDD}.md`
- 财报精读报告：`reports_antigravity/{公司名}/{公司名}-earnings-{期间}.md`

### 3.3 正文清洗与路径安全性重定向

在 `transform_body` 函数中，对正文进行正则替换：
1. **替换危险的家目录写入**：将形如 `~/[公司名]投资研究报告.md` 自动重写为指定的合规路径 `reports_antigravity/{公司名}/{公司名}-research-{YYYYMMDD}.md`。
2. **归档目录命名空间隔离**：将历史示例中的 `reports/` 规范化映射到 `reports_antigravity/`。

### 3.4 一致性检查机制 (`--check`)

脚本内置 `--check` 参数，按内容逐字节比对源文件转换后的内容与磁盘现有文件：
- 若完全同步：打印 `Checked 20 Antigravity skills in skills_antigravity`，退出码为 `0`；
- 若出现滞后或丢失：打印过期文件列表，退出码为 `1`。

---

## 4. 验证与测试结果

执行生成与验证命令：

```bash
# 1. 执行转换与生成
python3 scripts/sync-antigravity-skills.py

# 输出:
# Generated 20 Antigravity skills in skills_antigravity

# 2. 执行只读一致性校验
python3 scripts/sync-antigravity-skills.py --check

# 输出:
# Checked 20 Antigravity skills in skills_antigravity (exit code 0)
```

### 转换成果清单 (共 20 项)

| 源文件 (`skills/`) | 生成文件 (`skills_antigravity/`) | 报告输出规范 (`reports_antigravity/`) |
| :--- | :--- | :--- |
| `investment-research.md` | `investment-research.md` | `{公司名}/{公司名}-research-{YYYYMMDD}.md` |
| `investment-team.md` | `investment-team.md` | `{公司名}/最终报告.md` |
| `investment-checklist.md` | `investment-checklist.md` | `{公司名}/{公司名}-checklist-{YYYYMMDD}.md` |
| `industry-research.md` | `industry-research.md` | `{行业名}-industry-{YYYYMMDD}.md` |
| `industry-funnel.md` | `industry-funnel.md` | `{行业名}-funnel-{YYYYMMDD}.md` |
| `private-company-research.md` | `private-company-research.md` | `{公司名}/{公司名}-private-{YYYYMMDD}.md` |
| `earnings-review.md` | `earnings-review.md` | `{公司名}/{公司名}-earnings-{期间}.md` |
| `earnings-team.md` | `earnings-team.md` | `{公司名}/{公司名}-earnings-{期间}.md` |
| `management-deep-dive.md` | `management-deep-dive.md` | `{公司名}/{公司名}-management-{YYYYMMDD}.md` |
| `news-pulse.md` | `news-pulse.md` | `{公司名}/{公司名}-pulse-{YYYYMMDD}.md` |
| `portfolio-review.md` | `portfolio-review.md` | `portfolio-latest.md` |
| `quality-screen.md` | `quality-screen.md` | `quality-screen-{YYYYMMDD}.md` |
| `thesis-tracker.md` | `thesis-tracker.md` | `{公司名}/{公司名}-thesis.md` |
| `thesis-drift.md` | `thesis-drift.md` | `{公司名}/{公司名}-drift-{YYYYMMDD}.md` |
| `income-investment.md` | `income-investment.md` | `{公司名}/{公司名}-income-{YYYYMMDD}.md` |
| `bottleneck-hunter.md` | `bottleneck-hunter.md` | `{赛道名}-bottleneck-{YYYYMMDD}.md` |
| `deep-company-series.md` | `deep-company-series.md` | `{公司名}/《看懂{公司名}》/第X篇.md` |
| `dyp-ask.md` | `dyp-ask.md` | 对话式问答输出 |
| `financial-data.md` | `financial-data.md` | 投研双源数据规范基准 |
| `wechat-article.md` | `wechat-article.md` | `wechat/{主题}-{YYYYMMDD}.md` |

---

## 5. 日常使用与工作流整合

在日常开发与维护过程中，请遵循以下规范：

1. **编辑规则**：
   - 任何技能流程的修改均应在 `skills/*.md` 中进行。
   - 修改完成后，同步运行：
     ```bash
     # 同时刷新 Codex 与 Antigravity 技能
     python3 scripts/sync-codex-skills.py
     python3 scripts/sync-antigravity-skills.py
     ```
2. **提交前自检**：
   ```bash
   python3 scripts/sync-antigravity-skills.py --check
   ```
3. **在 Antigravity 中使用技能**：
   在 Antigravity 对话中，Agent 可直接读取 `skills_antigravity/<name>.md` 中的完整指令，根据其中的 Adapter Note 规范驱动本地 Python 严谨性工具链和网络工具，安全输出报告至 `reports_antigravity/`。
