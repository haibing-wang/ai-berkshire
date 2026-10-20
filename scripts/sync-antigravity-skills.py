#!/usr/bin/env python3
"""Generate Antigravity skills from AI Berkshire Claude command files.

Transforms skills/*.md into standard Antigravity skill directories:
skills_antigravity/<skill_name>/skill.md with YAML frontmatter,
adapter notes, and associated scripts in skills_antigravity/<skill_name>/scripts/.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAUDE_SKILLS = ROOT / "skills"
ANTIGRAVITY_SKILLS = ROOT / "skills_antigravity"
TOOLS_DIR = ROOT / "tools"

# Specific descriptions for core skills to provide optimal prompt trigger context
SKILL_DESCRIPTIONS: dict[str, str] = {
    "investment-research": "四大师综合分析框架：巴菲特-芒格-段永平-李录。对指定公司进行系统化投资研究与双源财务验算。",
    "investment-team": "投研团队：四角色并行分析框架。商业模式/财务估值/行业竞争/管理层四视角并行研判，最终汇总决策报告。",
    "investment-checklist": "巴菲特价值投资买入前 Checklist：逐项排查护城河、商业模式、管理层诚信及安全边际。",
    "industry-research": "行业投资研究：产业链全景扫描 + 四大师个股分析框架，全景剖析行业生命周期与竞争格局。",
    "industry-funnel": "行业漏斗筛选：从全市场初筛到 3 家终选标的的价值投资精选流程。",
    "private-company-research": "未上市公司研究：多Agent并行深度研究框架，信息稀缺下还原公司真实商业本质与估值。",
    "earnings-review": "财报精读：一手财报资料深度解读与核心业务经营数据拆解。",
    "earnings-team": "财报精读团队：四大师并行解读 + 编辑润色 + 读者评审把关质量，产出高质量财报复盘。",
    "management-deep-dive": "管理层纵深研究：买股票就是买人。评估创始人及管理团队资本配置能力与诚信度。",
    "news-pulse": "公司新闻脉搏：股价异动时快速归因。侦察公司事件、监管政策与情绪，判断是否触发论文重审。",
    "portfolio-review": "组合管理：从“研究公司”到“管理组合”。投资组合审视、仓位再平衡与风险回报优化。",
    "quality-screen": "去劣筛选：7条核心指标快速排除非一流公司，提高选股信噪比。",
    "thesis-tracker": "投资论文追踪：买入后的纪律系统，持续检验投资假设是否依然成立。",
    "thesis-drift": "投资论文漂移检测：分清事实变化与措辞变化，防范持有偏误与逻辑自我强化。",
    "income-investment": "股息收益投资：可持续与机会型现金流分红深度评估分析。",
    "bottleneck-hunter": "供应链瓶颈猎手：AI驱动的全球产业链瓶颈套利与卡脖子环节扫描。",
    "deep-company-series": "看懂XX公司（深度公司系列）：3-8篇深度长文拆解一家公司的商业底层逻辑与核心壁垒。",
    "dyp-ask": "段永平问答：以本分、平常心、做对的事情与把事情做对的方式思考商业与投资。",
    "financial-data": "财务数据获取与交叉验证规范：美股/港股/A股双独立信源核对标准。",
    "wechat-article": "微信公众号文章：作者-编辑-读者三Agent协作，产出高传播深度投研长文。",
}

# Specific report path guidelines for each skill
SKILL_REPORT_PATHS: dict[str, str] = {
    "investment-research": "reports/{公司名}/{公司名}-research-{YYYYMMDD}.md",
    "investment-team": "reports/{公司名}/最终报告.md",
    "investment-checklist": "reports/{公司名}/{公司名}-checklist-{YYYYMMDD}.md",
    "industry-research": "reports/{行业名}-industry-{YYYYMMDD}.md",
    "industry-funnel": "reports/{行业名}-funnel-{YYYYMMDD}.md",
    "private-company-research": "reports/{公司名}/{公司名}-private-{YYYYMMDD}.md",
    "earnings-review": "reports/{公司名}/{公司名}-earnings-{期间}.md",
    "earnings-team": "reports/{公司名}/{公司名}-earnings-{期间}.md",
    "management-deep-dive": "reports/{公司名}/{公司名}-management-{YYYYMMDD}.md",
    "news-pulse": "reports/{公司名}/{公司名}-pulse-{YYYYMMDD}.md",
    "portfolio-review": "reports/portfolio-latest.md",
    "quality-screen": "reports/quality-screen-{YYYYMMDD}.md",
    "thesis-tracker": "reports/{公司名}/{公司名}-thesis.md",
    "thesis-drift": "reports/{公司名}/{公司名}-drift-{YYYYMMDD}.md",
    "income-investment": "reports/{公司名}/{公司名}-income-{YYYYMMDD}.md",
    "bottleneck-hunter": "reports/bottleneck-map/{赛道名}-bottleneck-{YYYYMMDD}.md",
    "deep-company-series": "reports/{公司名}/《看懂{公司名}》/第X篇.md",
    "wechat-article": "reports/wechat/{主题}-{YYYYMMDD}.md",
}

# Association of specific shared tools to skill packages
SKILL_SCRIPTS: dict[str, list[str]] = {
    "bottleneck-hunter": ["twstock_data.py"],
    "financial-data": ["twstock_data.py", "ashare_data.py", "morningstar_fair_value.py"],
    "investment-research": ["financial_rigor.py", "terminal_value.py", "report_audit.py"],
    "earnings-review": ["financial_rigor.py", "report_audit.py", "twstock_data.py"],
    "investment-checklist": ["financial_rigor.py"],
    "quality-screen": ["stock_screener.py"],
    "news-pulse": ["xueqiu_scraper.py"],
    "dyp-ask": ["xueqiu_scraper.py"],
    "portfolio-review": ["financial_rigor.py", "momentum_backtest.py"],
    "thesis-drift": ["financial_rigor.py"],
    "thesis-tracker": ["financial_rigor.py"],
    "income-investment": ["financial_rigor.py", "report_audit.py"],
    "industry-research": ["report_audit.py"],
}


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Split existing YAML frontmatter if present."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 5 :].lstrip("\n")


def first_heading(text: str, fallback: str) -> str:
    """Extract first top-level Markdown heading as title fallback."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def yaml_quote(value: str) -> str:
    """Safely quote string for YAML format."""
    value = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{value}"'


def metadata_for(name: str, source_name: str, source_text: str) -> str:
    """Generate YAML frontmatter for Antigravity skill."""
    existing, body = split_frontmatter(source_text)
    custom_desc = SKILL_DESCRIPTIONS.get(name)

    if custom_desc:
        desc_str = custom_desc
    elif existing and (m := re.search(r'(?m)^description:\s*["\']?(.*?)["\']?$', existing)):
        desc_str = m.group(1).strip()
    else:
        title = first_heading(body if existing else source_text, name)
        desc_str = f"AI Berkshire 投研技能：{title}。来源：skills/{source_name}。"

    return (
        "---\n"
        f"name: {name}\n"
        f"description: {yaml_quote(desc_str)}\n"
        "---\n\n"
    )


def antigravity_adapter_note(name: str) -> str:
    """Generate Antigravity Adapter Note tailored for this skill."""
    report_path = SKILL_REPORT_PATHS.get(
        name,
        "reports/{公司名}/{公司名}-research-{YYYYMMDD}.md",
    )
    tools = SKILL_SCRIPTS.get(name, [])
    if tools:
        tool_desc = f"使用 `run_command` 执行本 Skill 专属脚本 `python3 skills_antigravity/{name}/scripts/...` 或根目录 `python3 tools/...`。"
    else:
        tool_desc = "使用 `run_command` 在工作区根目录下执行 `python3 tools/...`。"

    return (
        "## Antigravity Adapter Note\n"
        "- 将 $ARGUMENTS 视为用户在当前对话中指定的分析标的（如公司名称、美股/港股/A股代码）。\n"
        "- 网络数据收集时，优先使用 `search_web` 和 `read_url_content`，如遇到复杂页面可调用 `browser_subagent`。\n"
        f"- 校验工具调用：{tool_desc}\n"
        f"- 报告产出路径：严格保存至 `{report_path}`，严禁写入 `~`。\n"
        "- 投研前务必使用 `date` 确认今日基准日期。\n\n"
    )


def transform_body(name: str, body: str) -> str:
    """Sanitize body text to align with Antigravity environment and directory layout."""
    report_path = SKILL_REPORT_PATHS.get(
        name,
        "reports/{公司名}/{公司名}-research-{YYYYMMDD}.md",
    )
    # Fix dangerous home directory writes (e.g. ~/[公司名]投资研究报告.md)
    body = re.sub(
        r"~/[^\s`]+\.md",
        report_path,
        body,
    )
    # Ensure reports/ output paths are standard reports/
    body = re.sub(r"\breports_antigravity/", "reports/", body)
    return body.rstrip() + "\n"


def main() -> None:
    check = "--check" in sys.argv[1:]
    unknown_args = [arg for arg in sys.argv[1:] if arg != "--check"]
    if unknown_args:
        joined = ", ".join(unknown_args)
        raise SystemExit(f"Unknown argument(s): {joined}")

    if not check:
        ANTIGRAVITY_SKILLS.mkdir(exist_ok=True)

    count = 0
    stale: list[str] = []
    for source in sorted(CLAUDE_SKILLS.glob("*.md")):
        name = source.stem
        source_text = source.read_text(encoding="utf-8")
        _, body = split_frontmatter(source_text)

        target_dir = ANTIGRAVITY_SKILLS / name
        target = target_dir / "skill.md"

        content = (
            metadata_for(name, source.name, source_text)
            + antigravity_adapter_note(name)
            + transform_body(name, body)
        )

        if check:
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                stale.append(str(target.relative_to(ROOT)))
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

            # Setup scripts directory and copy related tools if configured
            scripts = SKILL_SCRIPTS.get(name, [])
            if scripts:
                scripts_dir = target_dir / "scripts"
                scripts_dir.mkdir(parents=True, exist_ok=True)
                for tool_name in scripts:
                    tool_src = TOOLS_DIR / tool_name
                    tool_dst = scripts_dir / tool_name
                    if tool_src.exists() and not tool_dst.exists():
                        shutil.copy2(tool_src, tool_dst)

        count += 1

    if check:
        if stale:
            print("Antigravity skills are out of date:")
            for path in stale:
                print(f"  {path}")
            raise SystemExit(1)
        print(f"Checked {count} Antigravity skills in {ANTIGRAVITY_SKILLS.relative_to(ROOT)}")
        return

    print(f"Generated {count} Antigravity skills in {ANTIGRAVITY_SKILLS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
