# Six Sigma DMAIC & Capability Sixpack Toolkit

> **基于 Python + Matplotlib 的专业级精益六西格玛（Lean Six Sigma）统计分析、Minitab 经典出图引擎与过程能力六合一报告系统。**

---

## 🌟 核心组成模块

本仓库由两大核心模块构成：

### 1. [SigmaFlow](./SigmaFlow/) — 六西格玛 DMAIC 统计工程全流程系统
专为六西格玛黑带（Black Belt）与绿带（Green Belt）实战项目打造，包含完整的 DMAIC 五阶段分析体系、Minitab 经典出图引擎与工业级数据模板：
- **`SigmaFlow/notebooks/`**: 5 个按阶段编排的交互式 Jupyter Notebook（`01_define` 至 `05_control`），涵盖 SIPOC、Sixpack、Gage R&R、假设检验、方差分析、多元回归、DOE 试验设计、SPC 控制图矩阵等。
- **`SigmaFlow/minitab_dmaic_visuals.py`**: 原生 Minitab 统计绘图引擎，实现包括**Graph 菜单全谱系**（散点图、边际图、矩阵散点图、气泡图、茎叶图、概率图、经验 CDF、单值图、折线图等）、**6M 特性要因图（鱼骨图）**、**图形化汇总报告 (Summary Report)** 以及 **全套 SPC 控制图（I-MR, Xbar-R, P, NP, C, U）**。
- **`SigmaFlow/templates/`**: 配套 5 套真实制造工程情境的 Excel 数据源模板。
- **`SigmaFlow/reports/`**: 包含已渲染的高清统计图表与 11 页高管实战汇报演示文稿（`Six_Sigma_DMAIC_Project_Report.pptx`）。

👉 **详细功能与使用指南请参阅 [SigmaFlow/README.md](./SigmaFlow/README.md)**。

---

### 2. [Capability Sixpack](./notebooks/capability_reports.ipynb) — 独立过程能力六合一与 Gage R&R
专注工序能力评价与测量系统分析，支持直接通过 Python 脚本或交互式 Notebook 快速生成：
- **Capability Sixpack (六合一报告)**: 整合 I/MR 控制图、能力直方图、正态概率图、散点运行图与完整工序能力指数 ($C_p, C_{pk}, P_p, P_{pk}, C_{pm}$)
- **Capability Analysis (正态能力分析)**: 带规格限公差、整体与组内正态拟合曲线、PPM 不合格品预估
- **Gage R&R Study (双因素方差分析法)**: 评价人与部件变异分量表、%Study Var 及可区分类别数 $ndc$
- **MSA Assistant (测量系统评定仪表盘)**: 依据 AIAG MSA 指南自动判定合格性并提供改进建议

---

## 📁 项目目录结构

```text
.
├── SigmaFlow/                                # 六西格玛 DMAIC 统计工程核心体系
│   ├── minitab_dmaic_visuals.py             # 核心绘图库 (全套 Minitab 统计图表与 SPC 图)
│   ├── notebooks/                           # 01_define 到 05_control 五大阶段 Notebook
│   ├── templates/                           # DMAIC 01 至 05 配套 Excel 数据模板
│   ├── reports/                             # 包含汇报 PPTX 与已渲染图表 figures/
│   └── README.md                            # SigmaFlow 详细中文技术文档
├── notebooks/
│   └── capability_reports.ipynb             # 过程能力六合一与 Gage R&R 交互式 Notebook
├── src/
│   └── sixpack_report.py                    # 独立过程能力分析底层代码
├── output/                                  # 根目录示例输出图像
├── generate_dmaic_excel_templates.py        # 模板生成与数据刷新脚本
├── generate_dmaic_notebooks.py              # Notebook 代码生成与批量重构流水线
├── generate_dmaic_presentation.py           # 自动化生成高管汇报 PPTX 脚本
└── requirements.txt                         # 项目依赖清单
```

---

## 🚀 快速上手

### 1. 安装依赖
```bash
pip install numpy pandas matplotlib scipy statsmodels openpyxl python-pptx
```

### 2. 运行 DMAIC 阶段分析
进入 `SigmaFlow/notebooks/` 目录并启动 Jupyter：
```bash
cd SigmaFlow/notebooks
jupyter notebook
```
依次执行 `01_define_phase.ipynb` 至 `05_control_phase.ipynb` 即可体验全套统计检验与图表输出。

### 3. 生成过程能力六合一报告
```bash
python src/sixpack_report.py --download-fonts
```

---

## 📄 许可证

本项目遵循 MIT 开源许可证。
