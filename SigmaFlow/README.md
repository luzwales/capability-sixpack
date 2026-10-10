# SigmaFlow — 六西格玛 DMAIC 统计工程与 Minitab 图形分析体系

> **基于 Python + Matplotlib + Statsmodels 的专业级精益六西格玛（Lean Six Sigma）全流程统计分析框架与 Minitab 高保真出图系统。**

---

## 📌 项目概述

**SigmaFlow** 是一套开箱即用的六西格玛黑带（Black Belt）实战统计分析体系。项目完整覆盖 DMAIC（定义 Define、测量 Measure、分析 Analyze、改进 Improve、控制 Control）五大阶段，严格对齐 Minitab 官方算法与视觉规范（灰框白底、标准配色、统计窗格、外边界控制限），彻底摆脱对商业统计软件授权的依赖。

所有分析过程均配有标准 Excel 工程数据模板、可交互 Jupyter Notebook，并一键生成高管汇报演示文稿（PPTX）与高清矢量级统计图表卡片。

---

## 🏗️ 核心架构与目录结构

```text
SigmaFlow/
├── minitab_dmaic_visuals.py       # 核心绘图引擎：完整复刻 Minitab Graph 与 Quality Tools 全谱系
├── notebooks/                     # DMAIC 五大阶段交互式 Jupyter Notebook
│   ├── 01_define_phase.ipynb      # Phase 1: 定义阶段 (SIPOC, CTQ, 帕累托)
│   ├── 02_measure_phase.ipynb     # Phase 2: 测量阶段 (Sixpack, Gage R&R, Kappa)
│   ├── 03_analyze_phase.ipynb     # Phase 3: 分析阶段 (Graph全谱系, 假设检验, 方差分析, 鱼骨图)
│   ├── 04_improve_phase.ipynb     # Phase 4: 改进阶段 (DOE试验设计, 回归, 最佳窗口)
│   ├── 05_control_phase.ipynb     # Phase 5: 控制阶段 (SPC控制图矩阵, 控制计划, 防错)
│   └── sixpack_report.py          # 过程能力六合一与 Gage R&R 辅助模块
├── templates/                     # 真实工业场景配套 Excel 数据源模板 (XLSX)
│   ├── DMAIC_01_Define_Template.xlsx
│   ├── DMAIC_02_Measure_Template.xlsx
│   ├── DMAIC_03_Analyze_Template.xlsx
│   ├── DMAIC_04_Improve_Template.xlsx
│   └── DMAIC_05_Control_Template.xlsx
├── reports/                       # 交付物与自动化汇报
│   ├── Six_Sigma_DMAIC_Project_Report.pptx   # 11 页高管实战汇报幻灯片
│   └── figures/                   # 自动渲染输出的全套 Minitab 统计图表及数据表卡片 (PNG)
├── input/datasets/                # 历史参考工序数据集
├── examples/                      # 基础示例脚本
└── requirements.txt               # 环境依赖清单
```

---

## 📊 DMAIC 五大阶段 Notebook 详解

### 1. Phase 1: Define (定义阶段) — `01_define_phase.ipynb`
- **项目立项卡片 (Project Charter)**: 业务背景、问题陈述、目标指标、团队角色与阶段里程碑。
- **高阶流程图 (SIPOC Flow)**: 供方 (S)、输入 (I)、流程步骤 (P)、输出 (O)、客户 (C) 端到端梳理。
- **客户声音转化 (VOC to CTQ)**: 客户诉求逐级解构至关键工程技术规范与公差要求。
- **缺陷帕累托分析 (Pareto Chart)**: 80/20 原则锁定核心主要质量缺陷分类。

### 2. Phase 2: Measure (测量阶段) — `02_measure_phase.ipynb`
- **基线过程能力六合一 (Process Capability Sixpack)**:
  - 运行图 / I-MR 控制图、能力直方图（组内 vs 整体正态曲线对比）
  - 正态概率图 (Probability Plot)、最后 25 点散点图
  - 工序能力指数计算卡片 ($C_p, C_{pk}, P_p, P_{pk}, C_{pm}$) 与 PPM 不合格品预估
- **计量型测量系统分析 (Gage R&R - ANOVA 法)**:
  - 双因素交叉方差分析（部件、评价人、部件×评价人交互项）
  - 变异分量表与研究变异占比（%Study Var < 10% 评估与可区分组数 $ndc \ge 5$ 判定）
  - MSA Assistant 自动化合格评级仪表盘
- **计数型测量系统分析 (Attribute Agreement Analysis)**:
  - 评价人自身重复性、评价人间再现性与标准基准符合率
  - Fleiss / Cohen Kappa 一致性统计量检验与判定

### 3. Phase 3: Analyze (分析阶段) — `03_analyze_phase.ipynb`
- **抽样与分布理论**: 中心极限定理 (CLT) 模拟（偏态总体 vs $N=5, 30$ 均值收敛）。
- **Minitab 经典单变量分布探索**:
  - 点图 (Dotplot)
  - 正态拟合直方图 (Histogram with Normal Fit & Parameter Sidebar)
  - 单变量箱线图 (Boxplot with 5-Number Summary & Mean Marker $\oplus$)
  - **图形化汇总报告 (Summary Report for Data)**: 复刻 Minitab 招牌汇总图（直方图+水平箱线图+95% CI 图+AD 正态性检验+偏度 Skewness+峰度 Kurtosis）
- **多列数据横向对比**:
  - 多列并排箱线图 (Multiple Columns Boxplot with Mean Trends)
  - 多列同刻度分面直方图 (Paneled Histogram - Same X-Scale)
  - 多列同图叠加直方图 (Overlay Histogram with Normal Fits)
- **Minitab Graph 菜单全谱系工具**:
  - 散点图 (Scatterplot with Linear Fit & $R^2$)
  - 矩阵散点图 (Matrix Plot)
  - 三维气泡图 (Bubble Plot)
  - 边际分布图 (Marginal Plot with Top/Right Histograms)
  - 茎叶图 (Stem-and-Leaf Card)
  - 正态概率图 (Probability Plot on Normal Paper with 95% CI Bands)
  - 经验累积分布图 (Empirical CDF vs Normal CDF)
  - 理论分布图 (Probability Distribution Plot with $\alpha=0.05$ Rejection Regions)
  - 单值散点图 (Individual Value Plot)
  - 时序折线图 (Line Plot)
- **特性要因分析 (Cause-and-Effect / 鱼骨图)**:
  - 经典 6M 制造分类骨架（人、机、料、法、测、环）
  - 根本原因红色虚线方框突出高亮标注
- **全套假设检验与因果验证**:
  - 单样本 1-Sample t-Test 与 1-Variance $\chi^2$ 检验
  - 双样本 2-Sample t-Test（等方差/异方差）、方差齐性 F-Test、配对 t 检验 (Paired t-Test)
  - 2-Proportions 比例检验与列联表卡方独立性检验 ($\chi^2$ Contingency Analysis)
  - 多变量分析图 (Multi-Vari Chart: 件内、件间、时变三分量分析)
  - 单因素方差分析 (ANOVA) 与分组箱线图
  - 过程因子相关系数矩阵热力图与多元线性回归模型
  - 过程 FMEA 风险优先数 (RPN) 排查分析
  - 根本原因黑带实战复合验证面板 (Root Cause Validation Report)

### 4. Phase 4: Improve (改进阶段) — `04_improve_phase.ipynb`
- **回归诊断深度建模**:
  - 多元线性回归模型与回归系数表
  - 回归预测区间与置信区间 (CI vs PI)
  - Minitab 经典残差诊断四合一图 (4-in-1: 正态概率图、拟合值图、直方图、顺序图)
  - 二次非线性抛物线回归 (Quadratic Regression) 与导数极值驻点 $X^*$ 优化求解
- **全因子试验设计 (DOE 2^k Factorial)**:
  - $2^3$ 经典全因子设计矩阵（温度 $\times$ 转速 $\times$ 压力）
  - 主效应图 (Main Effects Plot) 与 交互作用图 (Interaction Plot)
  - 标准化效应帕累托图 (Pareto Chart of Standardized Effects with $t_{\text{crit}}$ 参考线)
  - 模型精简 (Model Reduction) 与最优多元回归预测方程
  - Flex 官方教材灌装高度经典案例 (Fill Height Case Study) 复现
- **工艺窗口推荐与能力提升对比**:
  - 最佳工艺推荐参数公差窗口卡片
  - 改善前后工序能力显著性对比验证（$C_{pk}$ 从 0.898 跃升至 1.714，超差率清零）

### 5. Phase 5: Control (控制阶段) — `05_control_phase.ipynb`
- **SPC 统计过程控制全矩阵**:
  - **I-MR 控制图**: 单件连续在线监控与移动极差分析
  - **Xbar-R 控制图**: 计量型子组抽样监控（子组大小 $n=5$，自动查验 $A_2, D_3, D_4$ 常数表，外边界限值标注）
  - **P 控制图**: 计数型不合格品率监控（支持可变与恒定样本量的阶梯控制限）
  - **NP 控制图**: 计数型不合格品数监控（恒定样本量 $n$）
  - **C 控制图**: 计数型缺陷数监控（固定检验单元，泊松分布）
  - **U 控制图**: 计数型单位缺陷数监控（可变检验单元）
  - **失控判定**: 自动检测 Western Electric Rule 1（超出 3σ 限）并以红方块标注 `"1"`
- **闭环维持与标准化**:
  - 过程控制计划与失控反应计划 (Control Plan & OCAP Card)
  - 防错技术措施台账 (Poka-Yoke Register Card)
  - 六西格玛项目审计结案与财务效益签署清单 (Sign-Off Checklist Card)

---

## 🎨 Minitab 风格绘图引擎 (`minitab_dmaic_visuals.py`)

`minitab_dmaic_visuals.py` 是整个可视化系统的核心底座，无需配置即可直接调用：

| 分类 | 核心函数 | 说明 |
| :--- | :--- | :--- |
| **基础配置** | `apply_minitab_theme()` | 注入全局 rcParams（外边框 `#e0e0e0`，白色轴面，虚线网格，中英文字体回退） |
| **数据表卡片** | `render_table_card()` | 自适应列宽比例，将 Pandas DataFrame 转为紧凑精美的 Minitab 灰框数据卡片图片 |
| **单变量图形** | `plot_histogram()` | 浅蓝柱体 + 红色正态拟合曲线 + 右上角 Minitab 统计参数框 (Mean, StDev, N) |
| | `plot_single_boxplot()` | 浅蓝箱体 + 红色中位数线 + 黑圈十字 $\oplus$ 均值标记 + 五数概括窗格 |
| | `plot_dotplot()` | 垂直堆叠离散圆点与统计标注 |
| | `plot_graphical_summary()` | Minitab 经典图形化汇总报告（直方图+箱线图+95% CI+偏度峰度与检验数据表） |
| **多列对比图形** | `plot_multi_column_boxplot()` | 多个列同图横向并排箱线图，标出各列均值连线与汇总参数 |
| | `plot_multi_column_histogram_paneled()` | 多列上下分面直方图，严格共享统一 X 轴刻度，直观对比中心漂移与方差 |
| | `plot_multi_column_histogram_overlay()` | 多列半透明多色叠加直方图，对比分布重叠形态 |
| **Graph 菜单全套** | `plot_scatterplot()` | 散点图 + 最小二乘拟合线 + 回归方程与 $S, R^2$ 标注窗格 |
| | `plot_matrix_plot()` | 多变量成对散点图矩阵，对角线包含单变量直方图 |
| | `plot_bubble_plot()` | 散点大小按第三变量尺寸等比映射气泡图，带尺寸图例 |
| | `plot_marginal_plot()` | 核心散点图，顶部与右侧边际附着直方图/箱线图 |
| | `plot_stem_and_leaf()` | 经典三列式茎叶图卡片（Depth, Stem, Leaves） |
| | `plot_probability_plot()` | 正态概率纸百分比非线性纵坐标（0.1% ~ 99.9%）+ 95% 置信带 + AD 检验值 |
| | `plot_empirical_cdf()` | 阶梯式经验累积曲线叠加理论正态 CDF |
| | `plot_probability_distribution_plot()`| 钟形正态分布图，标出 $\alpha=0.05$ 双侧显著性拒绝域红色阴影与临界切点 |
| | `plot_individual_value_plot()` | 各组轻微横向 Jitter 真实散点 + 组均值实心菱形标记与连线 |
| | `plot_line_plot()` | 时序/顺位连续质量折线图 + 均值基准线 |
| **质量工具** | `plot_fishbone_diagram()` | 制造 6M 特性要因图（鱼骨图），支持根本原因红色虚线方框突出高亮 |
| | `plot_pareto_chart()` | 缺陷分类频数柱状图叠加累计百分比折线与 80% 辅助红线 |
| | `plot_interval_plot()` | 水平区间图（水平误差棒 + 垂直端点 Caps + 总体均值虚线基准） |
| | `plot_residuals_4in1()` | 经典残差诊断四合一（概率图、拟合值图、直方图、顺序图） |
| **SPC 控制图** | `plot_spc_xmr_chart()` | 单值-移动极差控制图 (I-MR)，外边距标注限值，标红 Test 1 报警 |
| | `plot_spc_xbar_r_chart()` | 计量型子组均值-极差控制图 (Xbar-R)，查表标准常数 $A_2, D_3, D_4$ |
| | `plot_spc_p_chart()` | 计数型不合格品率控制图 (P)，支持可变样本量阶梯式控制限 |
| | `plot_spc_np_chart()` | 计数型不合格品数控制图 (NP) |
| | `plot_spc_c_chart()` | 计数型缺陷数控制图 (C) |
| | `plot_spc_u_chart()` | 计数型单位缺陷数控制图 (U) |

---

## 🚀 快速上手与使用示例

### 1. 环境准备
项目仅依赖通用数据科学三方库：
```bash
pip install numpy pandas matplotlib scipy statsmodels openpyxl python-pptx
```

### 2. 交互式运行 Notebook
启动 Jupyter Lab 或在 VSCode / WorkBuddy 中打开 `SigmaFlow/notebooks/`：
- 按顺序从 `01_define_phase.ipynb` 运行至 `05_control_phase.ipynb`。
- 每个 Notebook 会自动检测路径并导入 `minitab_dmaic_visuals`，所有图表与数据表均内嵌高清渲染。

### 3. 在外部 Python 代码中调用 Minitab 图表
```python
import minitab_dmaic_visuals as mv
import numpy as np

# 生成示例数据
data = np.random.normal(50.04, 0.38, 50)

# 1. 生成 Minitab 经典图形化汇总报告 (Summary Report)
mv.plot_graphical_summary(
    data=data,
    var_name="Dimension_mm",
    output_path="my_summary_report.png"
)

# 2. 生成特性要因图 (鱼骨图)
mv.plot_fishbone_diagram(
    effect_text="Dimension\nVariation\n(尺寸偏差)",
    highlight_causes=["Shift Handover (交接班差异)", "Feed Rate High (进给量偏高)"],
    output_path="my_fishbone.png"
)

# 3. 生成 Xbar-R 控制图 (子组大小 n=5)
subgroups = data.reshape(10, 5)
mv.plot_spc_xbar_r_chart(
    data=subgroups,
    title_xbar="Xbar Chart of Dimension",
    title_r="R Chart of Dimension",
    output_path="my_xbar_r.png"
)
```

---

## 📄 许可证

本项目遵循 MIT 开源许可证。
