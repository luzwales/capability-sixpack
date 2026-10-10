"""
generate_dmaic_presentation.py
==============================
Builds a professional 16:9 Six Sigma DMAIC executive PPT report using python-pptx,
incorporating generated figures, key statistical metrics, and findings from the 5 Notebooks.
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# 16:9 Standard widescreen dimensions
WIDTH = Inches(13.333)
HEIGHT = Inches(7.5)

prs = Presentation()
prs.slide_width = WIDTH
prs.slide_height = HEIGHT

# Professional Theme Colors
BG_DARK = RGBColor(16, 37, 66)       # Deep Corporate Navy #102542
BG_LIGHT = RGBColor(245, 247, 250)   # Clean Off-White #F5F7FA
PRIMARY = RGBColor(27, 85, 155)      # Lean Six Sigma Blue #1B559B
ACCENT_GREEN = RGBColor(44, 160, 44) # Six Sigma Green #2CA02C
ACCENT_RED = RGBColor(214, 39, 40)   # Warning Red #D62728
TEXT_DARK = RGBColor(33, 37, 41)     # Primary Charcoal
TEXT_MUTED = RGBColor(108, 117, 125) # Muted Gray
WHITE = RGBColor(255, 255, 255)

BLANK_LAYOUT = prs.slide_layouts[6]
FIG_DIR = Path("SigmaFlow/reports/figures")

def add_header(slide, phase_tag, title_text, subtitle_text):
    """Adds standard corporate DMAIC header."""
    # Top banner line
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), WIDTH, Inches(0.1))
    shape.fill.solid()
    shape.fill.fore_color.rgb = PRIMARY
    shape.line.fill.background()

    # Phase badge
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(2.2), Inches(0.45))
    badge.fill.solid()
    badge.fill.fore_color.rgb = PRIMARY
    badge.line.fill.background()
    tf_b = badge.text_frame
    tf_b.word_wrap = True
    p_b = tf_b.paragraphs[0]
    p_b.text = phase_tag
    p_b.font.size = Pt(13)
    p_b.font.bold = True
    p_b.font.color.rgb = WHITE
    p_b.alignment = PP_ALIGN.CENTER

    # Title box
    txBox = slide.shapes.add_textbox(Inches(3.2), Inches(0.35), Inches(9.3), Inches(0.8))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_DARK
    
    p2 = tf.add_paragraph()
    p2.text = subtitle_text
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_MUTED

# =============================================================================
# SLIDE 1: Title Slide (Cover)
# =============================================================================
s1 = prs.slides.add_slide(BLANK_LAYOUT)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, WIDTH, HEIGHT)
bg1.fill.solid()
bg1.fill.fore_color.rgb = BG_DARK
bg1.line.fill.background()

# Title text
tx_title = s1.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(11), Inches(3.2))
tf1 = tx_title.text_frame
tf1.word_wrap = True

p_main = tf1.paragraphs[0]
p_main.text = "精益六西格玛 (Lean Six Sigma) DMAIC 改善报告"
p_main.font.size = Pt(36)
p_main.font.bold = True
p_main.font.color.rgb = WHITE

p_sub = tf1.add_paragraph()
p_sub.text = "Python 数据驱动全流程替代 Minitab — 精密机械加工尺寸 CTQ 能力提升项目"
p_sub.font.size = Pt(19)
p_sub.font.color.rgb = RGBColor(180, 205, 237)
p_sub.space_before = Pt(16)

p_meta = tf1.add_paragraph()
p_meta.text = "项目周期: 2026 Q1 - Q2  |  带级: Six Sigma Black Belt  |  工具架构: SigmaFlow + Minitab-Style Engine"
p_meta.font.size = Pt(13)
p_meta.font.color.rgb = RGBColor(140, 160, 185)
p_meta.space_before = Pt(30)

# =============================================================================
# SLIDE 2: Executive Summary (项目执行总览)
# =============================================================================
s2 = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s2, "EXECUTIVE SUMMARY", "项目核心成果与经济效益总结", "基于 DMAIC 严谨方法论的量化前后对比与价值交付")

def add_kpi_card(slide, left, top, width, height, title, value_before, value_after, delta_text, is_positive=True):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = WHITE
    card.line.color.rgb = RGBColor(220, 224, 230)
    card.line.width = Pt(1)
    
    tf = card.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = TEXT_DARK
    
    p1 = tf.add_paragraph()
    p1.text = f"改善前: {value_before}  ➔  改善后: {value_after}"
    p1.font.size = Pt(12)
    p1.font.color.rgb = TEXT_MUTED
    p1.space_before = Pt(10)

    p2 = tf.add_paragraph()
    p2.text = delta_text
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_GREEN if is_positive else ACCENT_RED
    p2.space_before = Pt(8)

add_kpi_card(s2, Inches(0.8), Inches(1.5), Inches(5.6), Inches(2.2), "制程能力指数 (Cpk)", "1.000 (警戒)", "1.632 (卓越)", "Cpk 提升 +63.2% (跨入世界级制程)", True)
add_kpi_card(s2, Inches(6.8), Inches(1.5), Inches(5.6), Inches(2.2), "预期缺陷率 (DPMO)", "2,700 PPM", "< 1 PPM", "不良率下降 99.9% (消除超差隐患)", True)
add_kpi_card(s2, Inches(0.8), Inches(4.1), Inches(5.6), Inches(2.2), "制程标准差 (Sigma Level)", "0.4087 mm (3.0σ)", "0.2450 mm (4.9σ)", "波动方差收窄 40.1% (稳定性倍增)", True)
add_kpi_card(s2, Inches(6.8), Inches(4.1), Inches(5.6), Inches(2.2), "工具架构迁移", "Minitab 单机许可依赖", "Python SigmaFlow 自动化", "代码化、可复现、企业级开源部署", True)

# =============================================================================
# SLIDE 3: Phase 1 - Define (定义阶段: Charter & Pareto)
# =============================================================================
s3 = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s3, "PHASE 1 : DEFINE", "项目界定、SIPOC 流程图与缺陷帕累托分析", "识别关键顾客需求 (CTQ)，依据 80/20 法则聚焦首要尺寸缺陷")

# Add Pareto image
pareto_img = FIG_DIR / "phase1_define_pareto.png"
if pareto_img.exists():
    s3.shapes.add_picture(str(pareto_img), Inches(0.8), Inches(1.5), Inches(6.6), Inches(4.9))

# Right text block
card_r = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.7), Inches(1.5), Inches(4.8), Inches(4.9))
card_r.fill.solid()
card_r.fill.fore_color.rgb = WHITE
card_r.line.color.rgb = RGBColor(220, 224, 230)
tf_r = card_r.text_frame
tf_r.word_wrap = True

p_r0 = tf_r.paragraphs[0]
p_r0.text = "Define 阶段关键发现与交付物:"
p_r0.font.size = Pt(14)
p_r0.font.bold = True
p_r0.font.color.rgb = TEXT_DARK

points_d = [
    "【CTQ 明确】: 客户终检尺寸需求锁定于 50.00 ± 1.20 mm，公差要求高精密配合。",
    "【帕累托关键少数】: 外径超差占质量投诉的 54%，连同粗糙度合计贡献 80% 以上不良，确定首要攻关方向。",
    "【SIPOC 范围】: 边界涵盖毛坯定位装夹至在线测量终检全链路 5 道核心工序。",
    "【立项收益】: 消除批次返工，年预计节约质量报废成本超 35 万元。"
]
for pt in points_d:
    p_cur = tf_r.add_paragraph()
    p_cur.text = pt
    p_cur.font.size = Pt(11)
    p_cur.font.color.rgb = TEXT_DARK
    p_cur.space_before = Pt(14)

# =============================================================================
# SLIDE 4: Phase 2 - Measure Part 1 (测量系统分析 MSA: 计量型 Gage R&R 与 计数型 Kappa)
# =============================================================================
s4a = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s4a, "PHASE 2 : MEASURE (MSA)", "测量系统分析 (Gage R&R 图表、ANOVA 数据表与计数型研究)", "计量型 ANOVA Gage R&R 验证测量精度，配合 Minitab 风格数据表卡片与计数型 Kappa")

grr_img = FIG_DIR / "phase2_gage_rr_report.png"
tables_img = FIG_DIR / "phase2_gage_rr_report_tables.png"
attr_img = FIG_DIR / "phase2_attribute_agreement_chart.png"
if grr_img.exists():
    s4a.shapes.add_picture(str(grr_img), Inches(0.6), Inches(1.5), Inches(4.3), Inches(5.1))
if tables_img.exists():
    s4a.shapes.add_picture(str(tables_img), Inches(5.0), Inches(1.5), Inches(3.8), Inches(5.1))
if attr_img.exists():
    s4a.shapes.add_picture(str(attr_img), Inches(8.9), Inches(1.5), Inches(3.8), Inches(5.1))

# =============================================================================
# SLIDE 5: Phase 2 - Measure Part 2 (基线能力量化与正态评估)
# =============================================================================
s4 = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s4, "PHASE 2 : MEASURE (能力基准)", "工序能力基准量化 (Cpk) 与正态分布检验", "双正态分布曲线叠加验证: 组内短期变异 vs 整体长期变异")

cap_img = FIG_DIR / "phase2_capability_histogram.png"
if cap_img.exists():
    s4.shapes.add_picture(str(cap_img), Inches(0.8), Inches(1.5), Inches(7.2), Inches(4.9))

card_m = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.3), Inches(1.5), Inches(4.2), Inches(4.9))
card_m.fill.solid()
card_m.fill.fore_color.rgb = WHITE
card_m.line.color.rgb = RGBColor(220, 224, 230)
tf_m = card_m.text_frame
tf_m.word_wrap = True

p_m0 = tf_m.paragraphs[0]
p_m0.text = "Measure 阶段关键度量指标:"
p_m0.font.size = Pt(14)
p_m0.font.bold = True
p_m0.font.color.rgb = TEXT_DARK

points_m = [
    "【正态性假定】: Shapiro-Wilk (p=0.610 > 0.05) 与 Anderson-Darling 检验双重证实数据高度服从正态分布。",
    "【能力不足】: 基线 Cpk = 1.000，Ppk = 0.970，低于行业及格线 1.33，制程处于濒临失控边缘。",
    "【MSA 可信度】: 计量型 Gage R&R %Study Var = 6.57% (<10%)，ndc = 21 (>=5)；计数型 Kappa 平均达 0.726，数据高度可信。",
    "【缺陷预估】: 预计不合格品达 2,700 PPM，需要深入 Analyze 探查参数根因。"
]
for pt in points_m:
    p_cur = tf_m.add_paragraph()
    p_cur.text = pt
    p_cur.font.size = Pt(11)
    p_cur.font.color.rgb = TEXT_DARK
    p_cur.space_before = Pt(12)

# =============================================================================
# SLIDE 5B: Phase 3 - Analyze Part 0 (单变量与多列数据分布形态对比)
# =============================================================================
s5_0 = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s5_0, "PHASE 3 : ANALYZE (分布对比)", "图形化汇总报告 (Summary Report) 与多列数据对比", "展示 Minitab 经典 Graphical Summary Report (含偏度、峰度与 95% CI)，以及多班次并排箱线图和分面直方图")

summary_img = FIG_DIR / "phase3_graphical_summary_dimension.png"
m_box_img = FIG_DIR / "phase3_multi_column_boxplot.png"
m_hist_img = FIG_DIR / "phase3_multi_column_histogram_paneled.png"

if summary_img.exists():
    s5_0.shapes.add_picture(str(summary_img), Inches(0.6), Inches(1.5), Inches(4.5), Inches(5.1))
if m_box_img.exists():
    s5_0.shapes.add_picture(str(m_box_img), Inches(5.2), Inches(1.5), Inches(4.2), Inches(5.1))
if m_hist_img.exists():
    s5_0.shapes.add_picture(str(m_hist_img), Inches(9.5), Inches(1.5), Inches(3.3), Inches(5.1))

# =============================================================================
# SLIDE 5C: Phase 3 - Analyze Part 0B (特性要因图 / 鱼骨图原因排查)
# =============================================================================
s5_fish = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s5_fish, "PHASE 3 : ANALYZE (鱼骨图因果分析)", "特性要因图 (Cause-and-Effect / Fishbone Diagram)", "系统化按制造 6M 维度梳理潜在因子，初步锁定重点检验排查的根因路径")

fish_img = FIG_DIR / "phase3_fishbone_diagram.png"
if fish_img.exists():
    s5_fish.shapes.add_picture(str(fish_img), Inches(1.2), Inches(1.5), Inches(10.9), Inches(5.4))

# =============================================================================
# SLIDE 6: Phase 3 - Analyze Part 1 (假设检验、卡方分析与多变量分析)
# =============================================================================
s5a = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s5a, "PHASE 3 : ANALYZE (统计检验)", "假设检验体系、卡方独立性分析、水平区间图与 Means 表", "全面覆盖 1-Sample/2-Sample t检验、配对检验、Minitab 水平区间估计与列联表卡方分析")

chi_img = FIG_DIR / "phase3_chisquare_contingency_chart.png"
int_img = FIG_DIR / "phase3_interval_plot.png"
means_tab_img = FIG_DIR / "phase3_interval_means_table.png"
mv_img = FIG_DIR / "phase3_multi_vari_chart.png"

if chi_img.exists():
    s5a.shapes.add_picture(str(chi_img), Inches(0.6), Inches(1.5), Inches(3.9), Inches(5.1))
if int_img.exists():
    s5a.shapes.add_picture(str(int_img), Inches(4.6), Inches(1.5), Inches(4.3), Inches(2.6))
if means_tab_img.exists():
    s5a.shapes.add_picture(str(means_tab_img), Inches(4.6), Inches(4.2), Inches(4.3), Inches(2.4))
if mv_img.exists():
    s5a.shapes.add_picture(str(mv_img), Inches(9.0), Inches(1.5), Inches(3.9), Inches(5.1))

# =============================================================================
# SLIDE 7: Phase 3 - Analyze Part 2 (相关性热力图、回归与 FMEA 风险分析)
# =============================================================================
s5 = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s5, "PHASE 3 : ANALYZE (归因锁定)", "工艺自变量相关性、回归模型与 FMEA 风险排查", "辨析关键输入变量 (X) 对关键输出尺寸 (Y) 的敏感度，结合 FMEA 锁定根因")

corr_img = FIG_DIR / "phase3_factors_correlation.png"
reg_tab_img = FIG_DIR / "phase3_regression_table.png"
fmea_img = FIG_DIR / "phase3_fmea_table.png"

if corr_img.exists():
    s5.shapes.add_picture(str(corr_img), Inches(0.6), Inches(1.5), Inches(4.2), Inches(5.1))
if reg_tab_img.exists():
    s5.shapes.add_picture(str(reg_tab_img), Inches(4.9), Inches(1.5), Inches(3.6), Inches(5.1))
if fmea_img.exists():
    s5.shapes.add_picture(str(fmea_img), Inches(8.6), Inches(1.5), Inches(4.3), Inches(5.1))

# =============================================================================
# SLIDE 8: Phase 3 - Analyze Part 3 (根本原因统计验证: Root Cause Validation)
# =============================================================================
s5b = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s5b, "PHASE 3 : ANALYZE (根因统计验证)", "根本原因统计验证复合报告 (Root Cause Validation: Operator)", "ANOVA 验证操作员显著性 (P=0.048 < 0.05)，量化各工位均值散差与 95% 置信区间")

root_val_img = FIG_DIR / "phase3_root_cause_validation.png"
if root_val_img.exists():
    s5b.shapes.add_picture(str(root_val_img), Inches(1.0), Inches(1.4), Inches(11.3), Inches(5.6))

# =============================================================================
# SLIDE 8: Phase 4 - Improve Part 1 (回归优化、预测区间与残差诊断四合一)
# =============================================================================
s6a = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s6a, "PHASE 4 : IMPROVE (回归与诊断)", "预测区间、残差诊断四合一图与二次非线性回归极值优化", "移植 data-six-sigma 进阶分析：CI vs PI 预测带、残差 4-in-1 检验与抛物线驻点寻优")

fit_pi_img = FIG_DIR / "phase4_fitted_line_with_pi.png"
res4_img = FIG_DIR / "phase4_residuals_4in1.png"
quad_img = FIG_DIR / "phase4_quadratic_regression_chart.png"

if fit_pi_img.exists():
    s6a.shapes.add_picture(str(fit_pi_img), Inches(0.6), Inches(1.5), Inches(4.2), Inches(5.1))
if res4_img.exists():
    s6a.shapes.add_picture(str(res4_img), Inches(4.9), Inches(1.5), Inches(4.4), Inches(5.1))
if quad_img.exists():
    s6a.shapes.add_picture(str(quad_img), Inches(9.4), Inches(1.5), Inches(3.5), Inches(5.1))

# =============================================================================
# SLIDE 9: Phase 4 - Improve Part 2 (DOE 试验设计与因子效应评估)
# =============================================================================
s6 = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s6, "PHASE 4 : IMPROVE (DOE 试验)", "全因子试验设计 (2³ DOE)、效应帕累托图与模型精简", "采用全因子试验评估因子效应，输出 Minitab 效应帕累托图与 Flex 经典案例表")

me_img = FIG_DIR / "phase4_doe_main_effects.png"
pareto_eff_img = FIG_DIR / "phase4_pareto_standardized_effects.png"
flex_anova_img = FIG_DIR / "phase4_flex_anova_table.png"

if me_img.exists():
    s6.shapes.add_picture(str(me_img), Inches(0.6), Inches(1.5), Inches(4.3), Inches(5.1))
if pareto_eff_img.exists():
    s6.shapes.add_picture(str(pareto_eff_img), Inches(5.0), Inches(1.5), Inches(4.2), Inches(5.1))
if flex_anova_img.exists():
    s6.shapes.add_picture(str(flex_anova_img), Inches(9.3), Inches(1.5), Inches(3.5), Inches(5.1))

# =============================================================================
# SLIDE 10: Phase 4 - Improve Part 3 (参数优化窗口与效果验证)
# =============================================================================
s7 = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s7, "PHASE 4 : IMPROVE (优化验证)", "最佳工艺窗口推荐与改善前后能力对比 (Before vs After)", "基于 DOE 方差分析与响应优化拟合，验证变异收窄与 Cpk 大幅跃升")

comp_tab_img = FIG_DIR / "phase4_before_after_table.png"
imp_img = FIG_DIR / "phase4_improved_capability.png"
if comp_tab_img.exists():
    s7.shapes.add_picture(str(comp_tab_img), Inches(0.8), Inches(1.5), Inches(5.6), Inches(4.9))
if imp_img.exists():
    s7.shapes.add_picture(str(imp_img), Inches(6.7), Inches(1.5), Inches(5.8), Inches(4.9))

# =============================================================================
# SLIDE 11: Phase 5 - Control (控制阶段: I-MR 控制图与 SPC 控制计划)
# =============================================================================
s8 = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s8, "PHASE 5 : CONTROL", "统计过程控制 (I-MR)、失控反应计划 (OCAP) 与控制计划表", "落实 Western Electric 准则在线预警，防范改进成果回潮，固化控制计划与防错")

imr_img = FIG_DIR / "phase5_imr_control_chart.png"
cplan_tab_img = FIG_DIR / "phase5_control_plan_table.png"

if imr_img.exists():
    s8.shapes.add_picture(str(imr_img), Inches(0.8), Inches(1.5), Inches(6.2), Inches(5.0))
if cplan_tab_img.exists():
    s8.shapes.add_picture(str(cplan_tab_img), Inches(7.2), Inches(1.5), Inches(5.5), Inches(5.0))

# =============================================================================
# SLIDE 11B: Phase 5 - Control Part 2 (SPC 计量型与计数型控制图矩阵)
# =============================================================================
s8_b = prs.slides.add_slide(BLANK_LAYOUT)
add_header(s8_b, "PHASE 5 : CONTROL (控制图矩阵)", "计量型子组 (Xbar-R) 与计数型 (P, NP, C, U) 控制图体系", "覆盖连续批量子组抽样及不合格品率、缺陷数在线统计过程控制与 Test 1 失控报警")

xbar_img = FIG_DIR / "phase5_xbar_r_control_chart.png"
p_img = FIG_DIR / "phase5_p_chart.png"
c_img = FIG_DIR / "phase5_c_chart.png"

if xbar_img.exists():
    s8_b.shapes.add_picture(str(xbar_img), Inches(0.6), Inches(1.5), Inches(5.8), Inches(5.1))
if p_img.exists():
    s8_b.shapes.add_picture(str(p_img), Inches(6.6), Inches(1.5), Inches(6.1), Inches(2.5))
if c_img.exists():
    s8_b.shapes.add_picture(str(c_img), Inches(6.6), Inches(4.1), Inches(6.1), Inches(2.5))

# Save Presentation
ppt_out = Path("SigmaFlow/reports/Six_Sigma_DMAIC_Project_Report.pptx")
ppt_out.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(ppt_out))
print(f"Professional 11-slide DMAIC Presentation successfully generated at: {ppt_out}")
