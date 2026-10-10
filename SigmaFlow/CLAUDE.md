# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目简介

**SigmaFlow** 是一个 Python 开源库，用于自动化执行 Lean Six Sigma (LSS) 项目。接受 CSV/Excel 原始过程数据，自动运行完整 DMAIC（定义→测量→分析→改善→控制）分析管道，生成统计图表、根因分析和 HTML/PDF 报告，输出结果无需任何手动配置。

---

## 常用命令

### 环境安装

```bash
pip install -e .                          # 开发模式安装（推荐）
pip install -r requirements.txt           # 仅安装依赖
pip install -e ".[dev]"                   # 含开发工具（pytest、ruff、mypy）
pip install -e ".[latex]"                 # 含 LaTeX PDF 报告支持（需系统安装 TeX）
```

### 运行分析

```bash
python main.py                               # 零参数运行，处理 input/datasets/ 下所有文件
sigmaflow run dataset.xlsx                   # CLI 单文件完整分析
sigmaflow dmaic dataset.xlsx                 # DMAIC 分阶段管道
sigmaflow demo                               # 使用合成数据演示
sigmaflow list                               # 列出已注册的分析器
```

### 测试

```bash
pytest tests/ -v                                             # 运行全部测试
pytest tests/ -v --cov=sigmaflow --cov-report=term-missing   # 含覆盖率报告
pytest tests/test_capability.py -v                           # 运行单个测试文件
```

### 代码检查

```bash
ruff check sigmaflow/     # Lint（行长限制 100，目标 Python 3.9）
mypy sigmaflow/           # 类型检查
```

### 示例脚本

```bash
python examples/basic_dmaic.py
python examples/manufacturing_example.py
python examples/statistical_analysis.py
```

---

## SigmaFlow 做什么

SigmaFlow 将一个包含过程测量数据的 CSV/Excel 文件，经过全自动管道处理后，输出：

- **统计指标**：Cp、Cpk、DPMO、西格玛水平、均值、标准差、偏度
- **过程控制图**：XmR 个值图、CUSUM、EWMA、X-bar/R 图（含 UCL/LCL）
- **根因排序**：Pearson 相关矩阵 + 变量重要性排名
- **高级分析**：多变量 OLS 回归、DOE/ANOVA、MSA 量具 R&R、FMEA/RPN
- **统计检验**：Shapiro-Wilk / Anderson-Darling / KS 正态性检验、t 检验、ANOVA、Mann-Whitney U
- **结构化洞察**：基于 Western Electric 规则和 Cpk 阈值，按 critical / warning / info 分级
- **HTML 仪表盘**：`output/dashboard/report.html`，可直接浏览器打开
- **LaTeX/PDF 报告**：`output/reports/`（需安装 LaTeX）
- **JSON 导出**：`output/insights.json`，所有洞察的结构化输出

---

## 架构概览

### 六层处理管道（每个文件独立处理）

```text
Dataset (CSV/XLSX)
  → [1]  DataProfiler       — 形状、数据类型、缺失值、描述统计、主要目标列识别
  → [2]  ProblemDetector    — 统计问题类型识别（SPC/能力/DOE/回归...）
  → [3]  DatasetRegistry    — 按 priority 排序调用 detect()，选择最合适的分析器
  → [4]  Statistics Engine  — 主分析 + 智能分发高级分析（MSA/FMEA/DOE/回归）+ 统计检验
  → [5]  RulesEngine        — Western Electric、Cpk 阈值、DPMO 分级，生成 Insight 对象
  → [6]  Report Generator   — HTML 仪表盘 (Jinja2) + LaTeX/PDF + insights.json 导出
```

### 核心编排层（`sigmaflow/core/`）

| 文件 | 职责 |
| --- | --- |
| `engine.py` | 主编排器，10 步 `_process_file` 管道，每步独立 try/except（失败不中断后续步骤） |
| `dmaic_engine.py` | DMAIC 分阶段执行，顺序调用 Define→Measure→Analyze→Improve→Control |
| `dataset_registry.py` | `pkgutil + importlib + inspect` 自动发现 `sigmaflow/datasets/` 中所有 `BaseDataset` 子类 |
| `data_profiler.py` | 数据集元信息提取，驱动下游所有检测逻辑 |
| `problem_detector.py` | 根据 profile 输出识别统计问题类型，生成 `DetectionResult` |
| `analysis_selector.py` | 根据 `DetectionResult` 选择对应 DMAIC 分析方案 |
| `logger.py` | 结构化日志，输出至 `output/logs/` |

### 数据集分析器自动发现机制

`DatasetRegistry` 使用 `pkgutil + importlib + inspect` 扫描 `sigmaflow/datasets/` 包，自动注册所有继承 `BaseDataset` 的子类，按 `priority`（降序）排列，依次调用 `detect(df)` 直到匹配。

**添加新分析器只需在该目录创建一个文件，无需修改任何现有代码。**

已注册分析器及优先级：

| 分析器 | priority | 自动触发条件 |
| --- | --- | --- |
| `doe_dataset.py` | 80 | DOE 结构（因子列含 {-1, +1} + 响应列） |
| `spc_dataset.py` | 70 | 时间序列 / 过程测量数据 |
| `capability_dataset.py` | 60 | 含规格限（USL/LSL）的数据 |
| `root_cause_dataset.py` | 50 | 多数值列，适合相关分析 |
| `logistics_dataset.py` | 45 | 物流 / 交期相关列 |
| `service_dataset.py` | 40 | 服务 / 等待时间相关列 |

### 智能高级分析分发逻辑（`Engine._dispatch_advanced`）

引擎在主分析完成后，根据数据集列名结构自动追加触发：

| 分析模块 | 触发条件 |
| --- | --- |
| **MSA（量具 R&R）** | 含 `Part`、`Operator`、`Measurement` 列（不区分大小写） |
| **FMEA（RPN）** | 含 `Severity`、`Occurrence`、`Detection` 列 |
| **回归分析（OLS）** | 数值列 ≥ 3 列 |
| **DOE（ANOVA）** | 至少 1 个分类/低基数列 + 1 个数值列 |
| **高级 SPC 图** | 数据集类型为 `spc`、`capability` 或 `service` 且数据点 ≥ 8 |

### DMAIC 各阶段产出

| 阶段 | 关键产出 |
| --- | --- |
| **Define** | `problem_statement`、`project_charter`、`sipoc` |
| **Measure** | `baseline_cpk`、`sigma_level`、`dpmo`、`gauge_rr`、`normality`、`xmr_chart` |
| **Analyze** | `correlation_matrix`、`ranked_variables`、`regression`、`hypothesis_tests`、`pareto`、`fmea`、`western_electric` |
| **Improve** | `doe_results`、`significant_factors`、`optimal_settings`、`interaction_plots` |
| **Control** | `updated_control_limits`、`cusum_chart`、`ewma_chart`、`control_plan`、`html_dashboard` |

### 关键度量阈值（`RulesEngine` 判定标准）

| 度量 | 阈值 | 含义 |
| --- | --- | --- |
| Cpk ≥ 1.67 | info | 过程能力优秀（世界级） |
| 1.33 ≤ Cpk < 1.67 | info | 过程能力可接受 |
| 1.00 ≤ Cpk < 1.33 | warning | 过程能力边缘，需改善 |
| Cpk < 1.00 | **critical** | 过程不合格，产生缺陷 |
| DPMO > 66,807 | **critical** | 低于 3σ 水平 |
| RPN > 200 | **critical** | FMEA 高优先级失效模式 |
| Gauge R&R < 10% | — | 测量系统可靠 |
| Gauge R&R > 30% | — | 测量系统不可接受 |

### 主要 API 入口

```python
# 完整管道
from sigmaflow.core.engine import Engine
results = Engine(input_dir="input/datasets", output_dir="output").run()

# DMAIC 分阶段
from sigmaflow.core.dmaic_engine import DMAICEngine
result = DMAICEngine(df).run_all()
# result["define"]["problem_statement"]
# result["measure"]["sigma_level"]
# result["analyze"]["significant_variables"]

# 单独能力分析
from sigmaflow.analysis.capability_analysis import compute_capability
result = compute_capability(series, usl=10.3, lsl=9.7)
# result["Cpk"], result["dpmo"], result["sigma_level"]

# 洞察规则引擎
from sigmaflow.insights.rules_engine import RulesEngine
insights = RulesEngine().evaluate(df, analysis_dict, dataset_type="capability")
# insight.severity → "info" | "warning" | "critical"
```

### 输出目录结构

```text
output/
├── figures/<dataset>/   ← PNG 图表（控制图、Pareto、回归、热力图...）
├── reports/             ← PDF + .tex 文件
├── dashboard/           ← report.html（浏览器打开）
├── logs/                ← 结构化日志
└── insights.json        ← 所有洞察的结构化 JSON 导出
```

### 输入约定

将 `.csv` 或 `.xlsx` 文件放入 `input/datasets/`，运行 `python main.py` 即可。CSV 分隔符自动检测（`,` / `;` / `\t`）。

---

## 依赖说明

| 类型 | 包 |
| --- | --- |
| 统计分析 | `pandas`、`numpy`、`scipy`、`scikit-learn`、`statsmodels` |
| 可视化 | `matplotlib`、`seaborn` |
| 报告生成 | `jinja2`（HTML）、`pylatex`（PDF，可选） |
| 文件读写 | `openpyxl`（Excel） |
| 开发工具 | `pytest`、`pytest-cov`、`ruff`、`mypy` |
