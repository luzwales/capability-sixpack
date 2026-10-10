"""
generate_dmaic_excel_templates.py
=================================
Generates 5 comprehensive, production-ready Excel template workbooks corresponding to DMAIC:
1. DMAIC_01_Define_Template.xlsx
   - Sheet 'Project_Charter': Business case, problem statement, scope, goals, team, milestones
   - Sheet 'SIPOC': Supplier, Input, Process, Output, Customer
   - Sheet 'VOC_to_CTQ': Voice of customer, customer need, key quality requirement (CTQ), spec limit
   - Sheet 'Defect_Pareto': Defect category, occurrences, cost, notes

2. DMAIC_02_Measure_Template.xlsx
   - Sheet 'Process_Data': Baseline CTQ continuous sample measurements
   - Sheet 'MSA_Gage_RR': Standard 10 parts, 3 operators, 2-3 trials measurement data
   - Sheet 'Attribute_Agreement': Attribute pass/fail agreement study data (50 samples, 3 appraisers)
   - Sheet 'Specs_and_Targets': Upper spec limit (USL), Lower spec limit (LSL), Target, Subgroup size

3. DMAIC_03_Analyze_Template.xlsx
   - Sheet 'Process_Factors': Continuous variables (Temp, Pressure, Speed, Humidity, etc.) vs CTQ Y
   - Sheet 'Multi_Vari_Data': Three-level hierarchical variation (Within-piece, Piece-to-Piece, Time-to-Time)
   - Sheet 'Hypothesis_2Sample': Two sample comparison data (e.g. Shift A vs Shift B, Vendor 1 vs Vendor 2)
   - Sheet 'ANOVA_Data': Multi-group categorical factor levels (e.g. Machine 1, 2, 3, 4) vs Performance Y
   - Sheet 'FMEA': Failure mode, potential effect, severity (S), potential cause, occurrence (O), current control, detection (D), RPN

4. DMAIC_04_Improve_Template.xlsx
   - Sheet 'DOE_2k_Factorial': Standard 2^3 full factorial design with replicates (Standard order, Run order, Factor A, B, C, Response Y)
   - Sheet 'DOE_Fill_Height_Case': Flex reference case (Carbonation, Pressure, Line Speed, Replicates 1 & 2, Deviation)
   - Sheet 'Optimization_Verification': Trial verification runs before vs after parameter optimization
   - Sheet 'Implementation_Plan': Action item, root cause addressed, owner, due date, validation metric

5. DMAIC_05_Control_Template.xlsx
   - Sheet 'SPC_Monitoring_Data': Post-improvement sequential batch/sample measurements for I-MR / Xbar-R charts
   - Sheet 'Control_Plan': Process step, parameter, spec limit, measurement method, sample size, frequency, owner, OCAP
   - Sheet 'Poka_Yoke_Register': Mistake proofing mechanism, failure mode eliminated, inspection type, status
   - Sheet 'Project_Signoff': Financial savings, Cpk achievement, sponsor & process owner signoff checklist
"""
import os
import numpy as np
import pandas as pd

TEMPLATE_DIR = "SigmaFlow/templates"
os.makedirs(TEMPLATE_DIR, exist_ok=True)
np.random.seed(42)

# =============================================================================
# 1. DEFINE TEMPLATE
# =============================================================================
def make_define_template():
    path = os.path.join(TEMPLATE_DIR, "DMAIC_01_Define_Template.xlsx")
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        # Sheet 1: Project Charter
        df_charter = pd.DataFrame([
            {"Section": "1. 项目名称 (Project Title)", "Detail": "精密轴承套加工核心尺寸 (dimension_mm) 过程能力提升项目", "Remarks": "依据公司年度质量攻坚要求立项"},
            {"Section": "2. 商业论证 (Business Case)", "Detail": "外径尺寸超差导致装配线返工与报废率高，影响主机厂客户交付准时率", "Remarks": "直接质量损失超 35 万元/年"},
            {"Section": "3. 问题陈述 (Problem Statement)", "Detail": "在 2025Q4 期间，外径核心尺寸 Cpk 仅为 1.00，超出客户 Cpk>=1.33 质量基准，次品率达 2,700 PPM", "Remarks": "数据统计区间: 2025-10-01 至 2025-12-31"},
            {"Section": "4. 改善目标 (Goal Statement)", "Detail": "将外径尺寸过程能力 Cpk 从 1.00 提升至 >= 1.60，不良率降至 50 PPM 以下", "Remarks": "目标达成期限: 2026 Q2"},
            {"Section": "5. 项目范围 (Project Scope)", "Detail": "包括 CNC 粗车、精车及切削冷却全工序；不含原材料熔炼与铸造工序", "Remarks": "专注于产线受控工艺参数"},
            {"Section": "6. 关键成员 (Team Members)", "Detail": "Champion: 制造总监 | Black Belt: 质量主管 | Process Owner: 机械加工主管 | Member: 设备工程师、工艺员", "Remarks": "跨职能核心攻坚组"},
            {"Section": "7. 里程碑进度 (Milestones)", "Detail": "D: W4 | M: W8 | A: W12 | I: W16 | C: W20", "Remarks": "项目预期周期为 20 周"}
        ])
        df_charter.to_excel(writer, sheet_name="Project_Charter", index=False)

        # Sheet 2: SIPOC
        df_sipoc = pd.DataFrame({
            "Supplier (供应商)": ["合金圆钢原料商", "刀具五金供应商", "主轴冷却油供应商", "切削液配制房", "数控机床原厂"],
            "Input (输入)": ["合格锻件圆棒料 (45#钢)", "超硬涂层数控刀片", "专用主轴循环降温油", "恒压高浓冷却水乳液", "精准G代码加工程序"],
            "Process (5大核心步骤)": ["1. 棒料上料自定心卡盘夹紧", "2. 外圆粗车高速剥皮去余量", "3. 精密切削车削至最终尺寸", "4. 气动量规在线自动外径检测", "5. 超声波清洗除毛刺入库"],
            "Output (输出)": ["粗车半成品", "外圆切削成品零件", "稳定机床加工热平衡", "在线100%全检尺寸数据", "合格装配轴套组件"],
            "Customer (客户)": ["精加工车削班组", "质量在线检验科", "设备运转巡检员", "汽车差速器总成总装线", "终端主机厂整车质保部"]
        })
        df_sipoc.to_excel(writer, sheet_name="SIPOC", index=False)

        # Sheet 3: VOC to CTQ
        df_voc = pd.DataFrame([
            {"Customer Voice (VOC)": "轴套经常压装卡滞，装不到位", "Issue / Need (质量需求)": "严控外径上限，杜绝大尺寸工件流入总装", "CTQ Metric (指标名称)": "外径核心尺寸 (dimension_mm)", "Target (目标值)": 50.00, "LSL (下限)": 48.80, "USL (上限)": 51.20, "Unit": "mm"},
            {"Customer Voice (VOC)": "配合面偶见拉伤漏油", "Issue / Need (质量需求)": "表面光洁平整，粗糙度达到镜面级别", "CTQ Metric (指标名称)": "表面粗糙度 (Ra)", "Target (目标值)": 0.80, "LSL (下限)": 0.00, "USL (上限)": 1.60, "Unit": "μm"},
            {"Customer Voice (VOC)": "高速旋转时轴系轻微跳动", "Issue / Need (质量需求)": "严格控制内外径同轴偏差", "CTQ Metric (指标名称)": "外圆径向跳动量 (Runout)", "Target (目标值)": 0.00, "LSL (下限)": 0.00, "USL (上限)": 0.03, "Unit": "mm"}
        ])
        df_voc.to_excel(writer, sheet_name="VOC_to_CTQ", index=False)

        # Sheet 4: Defect Pareto
        df_pareto = pd.DataFrame([
            {"Defect_Category": "外径尺寸超差 (Dimension Out of Spec)", "Count": 156, "Unit_Cost_RMB": 85.0, "Total_Cost_RMB": 13260.0, "Root_Category": "尺寸精度"},
            {"Defect_Category": "表面光洁度粗糙 (Surface Roughness High)", "Count": 78, "Unit_Cost_RMB": 40.0, "Total_Cost_RMB": 3120.0, "Root_Category": "外观质量"},
            {"Defect_Category": "同轴度与圆度超差 (Coaxiality / Roundness)", "Count": 32, "Unit_Cost_RMB": 85.0, "Total_Cost_RMB": 2720.0, "Root_Category": "形位公差"},
            {"Defect_Category": "局部切削热灼伤 (Surface Heat Burn)", "Count": 16, "Unit_Cost_RMB": 65.0, "Total_Cost_RMB": 1040.0, "Root_Category": "热变形"},
            {"Defect_Category": "端面毛刺未去净 (Burr Remains)", "Count": 9, "Unit_Cost_RMB": 15.0, "Total_Cost_RMB": 135.0, "Root_Category": "后处理"},
            {"Defect_Category": "装夹磕碰压痕 (Handling Dents)", "Count": 4, "Unit_Cost_RMB": 85.0, "Total_Cost_RMB": 340.0, "Root_Category": "转运磕碰"}
        ])
        df_pareto.to_excel(writer, sheet_name="Defect_Pareto", index=False)
    print("Created:", path)

# =============================================================================
# 2. MEASURE TEMPLATE
# =============================================================================
def make_measure_template():
    path = os.path.join(TEMPLATE_DIR, "DMAIC_02_Measure_Template.xlsx")
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        # Sheet 1: Process Data (Baseline)
        n = 300
        dates = pd.date_range("2026-01-05 08:00", periods=n, freq="15min")
        temp = np.random.normal(79.8, 2.5, n)
        press = np.random.normal(10.9, 0.6, n)
        speed = np.random.normal(1485, 90, n)
        humidity = np.random.normal(50.0, 8.0, n)
        dim = np.random.normal(49.98, 0.40, n)
        df_proc = pd.DataFrame({
            "Timestamp": dates,
            "Part_ID": [f"SN-{i+1:04d}" for i in range(n)],
            "dimension_mm": np.round(dim, 3),
            "temperature_C": np.round(temp, 2),
            "pressure_bar": np.round(press, 2),
            "machine_speed_rpm": np.round(speed, 1),
            "humidity_pct": np.round(humidity, 1)
        })
        df_proc.to_excel(writer, sheet_name="Process_Data", index=False)

        # Sheet 2: Specs and Targets
        df_specs = pd.DataFrame([
            {"Parameter": "dimension_mm", "LSL": 48.80, "Target": 50.00, "USL": 51.20, "Unit": "mm", "Subgroup_Size": 1, "Historical_Mean": 49.98, "Historical_StDev": 0.40}
        ])
        df_specs.to_excel(writer, sheet_name="Specs_and_Targets", index=False)

        # Sheet 3: Gage R&R (10 parts x 3 operators x 3 trials)
        parts = [f"Part_{i+1}" for i in range(10)]
        operators = ["Operator_A", "Operator_B", "Operator_C"]
        part_true = np.linspace(49.4, 50.6, 10)
        grr_rows = []
        for trial in [1, 2, 3]:
            for p_idx, p_name in enumerate(parts):
                for op_idx, op_name in enumerate(operators):
                    # Part true + op bias + random error
                    op_bias = (op_idx - 1) * 0.015
                    noise = np.random.normal(0, 0.025)
                    meas = part_true[p_idx] + op_bias + noise
                    grr_rows.append({
                        "Part": p_name,
                        "Operator": op_name,
                        "Trial": trial,
                        "Measurement": round(meas, 4)
                    })
        df_grr = pd.DataFrame(grr_rows)
        df_grr.to_excel(writer, sheet_name="MSA_Gage_RR", index=False)

        # Sheet 4: Attribute Agreement Analysis (30 samples x 3 appraisers x 2 trials)
        sample_standards = ["Pass"]*18 + ["Fail"]*12
        np.random.shuffle(sample_standards)
        attr_rows = []
        for appraiser in ["Inspector_1", "Inspector_2", "Inspector_3"]:
            for rep in [1, 2]:
                for s_id, std in enumerate(sample_standards):
                    # 90% accuracy
                    if np.random.rand() < 0.92:
                        assessment = std
                    else:
                        assessment = "Fail" if std == "Pass" else "Pass"
                    attr_rows.append({
                        "Sample_ID": f"S_{s_id+1:02d}",
                        "Appraiser": appraiser,
                        "Trial": rep,
                        "Standard": std,
                        "Assessment": assessment
                    })
        pd.DataFrame(attr_rows).to_excel(writer, sheet_name="Attribute_Agreement", index=False)
    print("Created:", path)

# =============================================================================
# 3. ANALYZE TEMPLATE (Comprehensive Hypothesis, Chi-Square, CLT, ANOVA, FMEA)
# =============================================================================
def make_analyze_template():
    path = os.path.join(TEMPLATE_DIR, "DMAIC_03_Analyze_Template.xlsx")
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        # Sheet 1: Process Factors Correlation & Regression
        n = 120
        temp = np.random.uniform(74, 86, n)
        press = np.random.uniform(10.0, 12.5, n)
        speed = np.random.uniform(1350, 1650, n)
        coolant = np.random.uniform(7.5, 9.5, n)
        dim = 49.20 + 0.0085 * temp + 0.045 * press - 0.00012 * speed + np.random.normal(0, 0.12, n)
        df_factors = pd.DataFrame({
            "Sample_Index": range(1, n + 1),
            "temperature_C": np.round(temp, 2),
            "pressure_bar": np.round(press, 2),
            "machine_speed_rpm": np.round(speed, 1),
            "coolant_ph": np.round(coolant, 2),
            "dimension_mm": np.round(dim, 3)
        })
        df_factors.to_excel(writer, sheet_name="Process_Factors", index=False)

        # Sheet 2: CLT & Sampling Simulation Data
        pop_data = np.random.exponential(scale=2.0, size=500)
        means_n5 = [np.mean(np.random.choice(pop_data, size=5)) for _ in range(200)]
        means_n30 = [np.mean(np.random.choice(pop_data, size=30)) for _ in range(200)]
        df_clt = pd.DataFrame({
            "Population_Raw": np.round(pop_data[:200], 3),
            "Sample_Means_N5": np.round(means_n5, 3),
            "Sample_Means_N30": np.round(means_n30, 3)
        })
        df_clt.to_excel(writer, sheet_name="Sampling_CLT_Data", index=False)

        # Sheet 3: 1-Sample Hypothesis Test & Univariate Distributions
        s1_vals = np.random.normal(50.04, 0.38, 50)
        s1_weight = np.random.normal(125.20, 1.15, 50)
        s1_hardness = np.random.normal(58.45, 0.65, 50)
        pd.DataFrame({
            "Sample_ID": range(1, 51),
            "Dimension_mm": np.round(s1_vals, 3),
            "Weight_g": np.round(s1_weight, 2),
            "Hardness_HRC": np.round(s1_hardness, 2)
        }).to_excel(writer, sheet_name="Hypothesis_1Sample", index=False)

        # Sheet 4: Multi-Column Comparison & 2-Sample Test (Shift 1, Shift 2, Shift 3)
        s1 = np.random.normal(50.05, 0.35, 50)
        s2 = np.random.normal(50.40, 0.42, 50)
        s3 = np.random.normal(49.83, 0.31, 50)
        df_2sample = pd.DataFrame({
            "Shift_1_Dimension": np.round(s1, 3),
            "Shift_2_Dimension": np.round(s2, 3),
            "Shift_3_Dimension": np.round(s3, 3)
        })
        df_2sample.to_excel(writer, sheet_name="Hypothesis_2Sample", index=False)

        # Sheet 5: Paired t-Test (Online Gage vs Lab CMM on same 25 pieces)
        base_pieces = np.random.normal(50.00, 0.30, 25)
        online_meas = base_pieces + np.random.normal(0.015, 0.02, 25)
        cmm_meas = base_pieces + np.random.normal(0.0, 0.01, 25)
        pd.DataFrame({
            "Piece_ID": [f"Piece_{i+1:02d}" for i in range(25)],
            "Online_Gage_mm": np.round(online_meas, 4),
            "Lab_CMM_mm": np.round(cmm_meas, 4),
            "Difference_mm": np.round(online_meas - cmm_meas, 4)
        }).to_excel(writer, sheet_name="Hypothesis_Paired", index=False)

        # Sheet 6: 2-Proportions Test Data
        df_prop = pd.DataFrame([
            {"Line": "Line_A (标准线)", "Inspected_Count": 500, "Defective_Count": 24, "Defect_Rate": "4.8%"},
            {"Line": "Line_B (对比线)", "Inspected_Count": 500, "Defective_Count": 46, "Defect_Rate": "9.2%"}
        ])
        df_prop.to_excel(writer, sheet_name="Hypothesis_2Proportion", index=False)

        # Sheet 7: Chi-Square Contingency Table (Machine vs Defect Classification)
        df_chi = pd.DataFrame([
            {"Machine": "Machine_1", "Defect_Oversize": 8, "Defect_Undersize": 12, "Defect_Roughness": 6},
            {"Machine": "Machine_2", "Defect_Oversize": 18, "Defect_Undersize": 4, "Defect_Roughness": 14},
            {"Machine": "Machine_3", "Defect_Oversize": 5, "Defect_Undersize": 19, "Defect_Roughness": 7},
            {"Machine": "Machine_4", "Defect_Oversize": 14, "Defect_Undersize": 9, "Defect_Roughness": 15}
        ])
        df_chi.to_excel(writer, sheet_name="ChiSquare_Contingency", index=False)

        # Sheet 8: ANOVA Data (4 Machines x 30 observations)
        anova_rows = []
        for m_id, mean_val in [("Machine_1", 50.02), ("Machine_2", 49.91), ("Machine_3", 50.18), ("Machine_4", 49.85)]:
            vals = np.random.normal(mean_val, 0.28, 30)
            for v in vals:
                anova_rows.append({"Machine": m_id, "Dimension_mm": round(v, 3)})
        pd.DataFrame(anova_rows).to_excel(writer, sheet_name="ANOVA_Data", index=False)

        # Sheet 9: Multi-Vari Data (Within-piece, Piece-to-piece, Time-to-time)
        mvari_rows = []
        times = ["Morning (08:00)", "Noon (13:00)", "Evening (18:00)"]
        for t in times:
            for piece in range(1, 4):
                piece_base = 50.0 + (0.1 if "Noon" in t else (-0.05 if "Morning" in t else 0.02)) + np.random.normal(0, 0.04)
                for pos in ["Top", "Middle", "Bottom"]:
                    mvari_rows.append({
                        "Time_Period": t,
                        "Piece_ID": f"P_{piece}",
                        "Position": pos,
                        "Dimension_mm": round(piece_base + np.random.normal(0, 0.015), 3)
                    })
        pd.DataFrame(mvari_rows).to_excel(writer, sheet_name="Multi_Vari_Data", index=False)

        # Sheet 10: FMEA
        df_fmea = pd.DataFrame([
            {"Process_Step": "精密切削", "Failure_Mode": "主轴发热热膨胀伸长", "Effect": "成品轴套外径超出上限尺寸", "Severity_S": 8, "Potential_Cause": "冷却油散热器滤网堵塞，换热受阻", "Occurrence_O": 6, "Current_Control": "操作工班后手动手感测温", "Detection_D": 5, "Action_Plan": "安装数字热电偶温度闭环继电器，油温联锁停机", "Action_Owner": "设备科李工"},
            {"Process_Step": "工件装夹", "Failure_Mode": "三爪自定心卡盘夹持力衰减", "Effect": "车削振刀出现微棱圆度失真", "Severity_S": 7, "Potential_Cause": "液压站调压阀内泄压力不稳", "Occurrence_O": 5, "Current_Control": "每班首件百分表巡检", "Detection_D": 4, "Action_Plan": "增加数显压力变送器低压报警", "Action_Owner": "维修班王组长"},
            {"Process_Step": "刀具走刀", "Failure_Mode": "硬质合金刀片后刀面急剧磨损", "Effect": "表面粗糙度Ra升高并产生毛刺", "Severity_S": 6, "Potential_Cause": "切削线速度偏高超过刀具寿命上限", "Occurrence_O": 7, "Current_Control": "定数换刀卡片控制", "Detection_D": 4, "Action_Plan": "优化数控主轴转速转为恒线速切削", "Action_Owner": "工艺室张工"}
        ])
        df_fmea["RPN"] = df_fmea["Severity_S"] * df_fmea["Occurrence_O"] * df_fmea["Detection_D"]
        df_fmea.to_excel(writer, sheet_name="FMEA", index=False)

        # Sheet 11: Root Cause Validation - Operator vs Accuracy % (152 observations matching ANOVA F=2.30, p=0.048)
        ops_info = [
            ("Alex", 36, 52.795, 2.463),
            ("Grace", 22, 52.407, 2.308),
            ("Janet", 16, 53.215, 2.171),
            ("Luke", 16, 53.909, 2.419),
            ("Patricia", 37, 51.952, 1.779),
            ("Wilson", 25, 52.150, 2.200)
        ]
        np.random.seed(101)
        all_res = [np.random.normal(0, 1, n) - np.mean(np.random.normal(0, 1, n)) for _, n, _, _ in ops_info]
        scale = np.sqrt(712.75 / np.sum(np.concatenate(all_res)**2))
        root_rows = []
        for (op, n, m, s), raw in zip(ops_info, all_res):
            vals = m + raw * scale
            if op == "Patricia":
                vals[0] = 56.8
            for idx_v, v in enumerate(vals):
                root_rows.append({"Sample_ID": f"{op}_{idx_v+1:02d}", "Operator": op, "Accuracy_Pct": round(float(v), 3)})
        pd.DataFrame(root_rows).to_excel(writer, sheet_name="Root_Cause_Operator", index=False)
    print("Created:", path)

# =============================================================================
# 4. IMPROVE TEMPLATE (Regression Suite, Quadratic, 4-in-1, DOE & Flex Case)
# =============================================================================
def make_improve_template():
    path = os.path.join(TEMPLATE_DIR, "DMAIC_04_Improve_Template.xlsx")
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        # Sheet 1: Linear Regression & Prediction Interval Data
        n_reg = 80
        temp_x = np.linspace(74.0, 86.0, n_reg)
        dim_y = 48.05 + 0.0245 * temp_x + np.random.normal(0, 0.14, n_reg)
        df_reg = pd.DataFrame({
            "Run_Index": range(1, n_reg + 1),
            "Temperature_C": np.round(temp_x, 2),
            "Dimension_mm": np.round(dim_y, 3)
        })
        df_reg.to_excel(writer, sheet_name="Linear_Regression_Data", index=False)

        # Sheet 2: Quadratic (Nonlinear) Regression Data (Speed vs Surface Roughness Ra)
        # Demonstrating parabolic optimum from data-six-sigma Module 6
        speed_x = np.linspace(1200, 1800, 60)
        # Minimum Ra around 1500 rpm: Ra = 0.40 + 0.000008 * (speed - 1500)^2
        ra_y = 0.42 + 0.0000075 * ((speed_x - 1490)**2) + np.random.normal(0, 0.05, 60)
        df_quad = pd.DataFrame({
            "Sample_ID": range(1, 61),
            "Machine_Speed_rpm": np.round(speed_x, 1),
            "Surface_Roughness_Ra": np.round(ra_y, 3)
        })
        df_quad.to_excel(writer, sheet_name="Quadratic_Regression_Data", index=False)

        # Sheet 3: 2^3 Factorial DOE (Temperature x Machine Speed x Pressure)
        doe_base = [
            (-1, -1, -1),
            ( 1, -1, -1),
            (-1,  1, -1),
            ( 1,  1, -1),
            (-1, -1,  1),
            ( 1, -1,  1),
            (-1,  1,  1),
            ( 1,  1,  1),
        ]
        doe_rows = []
        for rep in [1, 2]:
            for run_idx, (a, b, c) in enumerate(doe_base):
                y = 50.00 + 0.35 * a - 0.25 * b + 0.12 * c + 0.18 * (a * b) + np.random.normal(0, 0.05)
                doe_rows.append({
                    "Std_Order": run_idx + 1 + (rep - 1) * 8,
                    "Run_Order": (run_idx * 2 + rep) % 16 + 1,
                    "Replicate": rep,
                    "Temp_Code": a,
                    "Speed_Code": b,
                    "Press_Code": c,
                    "Temperature_C": 78.0 if a == -1 else 84.0,
                    "Machine_Speed_rpm": 1400 if b == -1 else 1600,
                    "Pressure_bar": 10.5 if c == -1 else 12.0,
                    "Dimension_mm": round(y, 3)
                })
        pd.DataFrame(doe_rows).to_excel(writer, sheet_name="DOE_2k_Factorial", index=False)

        # Sheet 4: DOE Flex Training Case Study (Carbonation, Pressure, Line Speed)
        flex_rows = [
            {"Run": 1, "Carbonation_Pct": 10, "Pressure_psi": 25, "LineSpeed_bpm": 200, "Fill_Height_Dev": -3.0},
            {"Run": 2, "Carbonation_Pct": 12, "Pressure_psi": 25, "LineSpeed_bpm": 200, "Fill_Height_Dev": 0.0},
            {"Run": 3, "Carbonation_Pct": 10, "Pressure_psi": 30, "LineSpeed_bpm": 200, "Fill_Height_Dev": -1.0},
            {"Run": 4, "Carbonation_Pct": 12, "Pressure_psi": 30, "LineSpeed_bpm": 200, "Fill_Height_Dev": 2.5},
            {"Run": 5, "Carbonation_Pct": 10, "Pressure_psi": 25, "LineSpeed_bpm": 250, "Fill_Height_Dev": -1.0},
            {"Run": 6, "Carbonation_Pct": 12, "Pressure_psi": 25, "LineSpeed_bpm": 250, "Fill_Height_Dev": 1.0},
            {"Run": 7, "Carbonation_Pct": 10, "Pressure_psi": 30, "LineSpeed_bpm": 250, "Fill_Height_Dev": 0.0},
            {"Run": 8, "Carbonation_Pct": 12, "Pressure_psi": 30, "LineSpeed_bpm": 250, "Fill_Height_Dev": 3.5},
            {"Run": 9, "Carbonation_Pct": 10, "Pressure_psi": 25, "LineSpeed_bpm": 200, "Fill_Height_Dev": -1.0},
            {"Run": 10, "Carbonation_Pct": 12, "Pressure_psi": 25, "LineSpeed_bpm": 200, "Fill_Height_Dev": 1.0},
            {"Run": 11, "Carbonation_Pct": 10, "Pressure_psi": 30, "LineSpeed_bpm": 200, "Fill_Height_Dev": 0.0},
            {"Run": 12, "Carbonation_Pct": 12, "Pressure_psi": 30, "LineSpeed_bpm": 200, "Fill_Height_Dev": 1.0},
            {"Run": 13, "Carbonation_Pct": 10, "Pressure_psi": 25, "LineSpeed_bpm": 250, "Fill_Height_Dev": 0.0},
            {"Run": 14, "Carbonation_Pct": 12, "Pressure_psi": 25, "LineSpeed_bpm": 250, "Fill_Height_Dev": 2.0},
            {"Run": 15, "Carbonation_Pct": 10, "Pressure_psi": 30, "LineSpeed_bpm": 250, "Fill_Height_Dev": 1.0},
            {"Run": 16, "Carbonation_Pct": 12, "Pressure_psi": 30, "LineSpeed_bpm": 250, "Fill_Height_Dev": 3.0},
        ]
        pd.DataFrame(flex_rows).to_excel(writer, sheet_name="DOE_Fill_Height_Case", index=False)

        # Sheet 5: Optimization Verification (Pilot Run post-DOE)
        n_pilot = 100
        before_data = np.random.normal(49.98, 0.40, n_pilot)
        after_data = np.random.normal(50.00, 0.22, n_pilot)
        df_pilot = pd.DataFrame({
            "Batch_ID": [f"Pilot_{i+1:03d}" for i in range(n_pilot)],
            "Before_Improvement_Dim": np.round(before_data, 3),
            "After_Improvement_Dim": np.round(after_data, 3)
        })
        df_pilot.to_excel(writer, sheet_name="Optimization_Verification", index=False)

        # Sheet 5: Optimization Verification (Pilot Run post-DOE)
        n_pilot = 100
        before_data = np.random.normal(49.98, 0.40, n_pilot)
        after_data = np.random.normal(50.00, 0.22, n_pilot)
        df_pilot = pd.DataFrame({
            "Batch_ID": [f"Pilot_{i+1:03d}" for i in range(n_pilot)],
            "Before_Improvement_Dim": np.round(before_data, 3),
            "After_Improvement_Dim": np.round(after_data, 3)
        })
        df_pilot.to_excel(writer, sheet_name="Optimization_Verification", index=False)

        # Sheet 6: Implementation Action Plan
        df_actions = pd.DataFrame([
            {"Item": 1, "Countermeasure": "加装主轴恒温冷却油机，闭环控制油温在 78.5±1.5℃", "Target_Cause": "热变形主轴轴向窜动", "Owner": "设备工程科", "Target_Date": "2026-03-15", "Status": "已完成", "Verification_Metric": "油温稳定性控制在 ±1.0℃ 内"},
            {"Item": 2, "Countermeasure": "CNC宏程序固化切削线速度为 1450 rpm", "Target_Cause": "转速偏高与振刀", "Owner": "数控工艺室", "Target_Date": "2026-03-20", "Status": "已完成", "Verification_Metric": "机床G代码密码锁定"},
            {"Item": 3, "Countermeasure": "更换高压恒压切削液调压阀至 11.2 bar", "Target_Cause": "冲屑不良与换热不稳", "Owner": "动力车间", "Target_Date": "2026-03-22", "Status": "已完成", "Verification_Metric": "压力波动降至 ±0.2 bar"}
        ])
        df_actions.to_excel(writer, sheet_name="Implementation_Plan", index=False)
    print("Created:", path)

# =============================================================================
# 5. CONTROL TEMPLATE
# =============================================================================
def make_control_template():
    path = os.path.join(TEMPLATE_DIR, "DMAIC_05_Control_Template.xlsx")
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        # Sheet 1: SPC Monitoring Data (50 consecutive batches, improved process)
        n_spc = 60
        spc_vals = np.random.normal(50.00, 0.22, n_spc)
        # Inject one special-cause shift around sample 45 for detection test
        spc_vals[44] += 0.75
        df_spc = pd.DataFrame({
            "Sample_ID": range(1, n_spc + 1),
            "Timestamp": pd.date_range("2026-04-01 08:00", periods=n_spc, freq="2h"),
            "Dimension_mm": np.round(spc_vals, 3),
            "Oil_Temp_C": np.round(np.random.normal(78.5, 0.8, n_spc), 1),
            "Pressure_bar": np.round(np.random.normal(11.2, 0.15, n_spc), 2)
        })
        df_spc.to_excel(writer, sheet_name="SPC_Monitoring_Data", index=False)

        # Sheet 2: Subgroup Data for Xbar-R Control Chart (25 subgroups of size n=5)
        np.random.seed(42)
        n_subgroups = 25
        subgroup_size = 5
        sub_raw = np.random.normal(50.00, 0.18, (n_subgroups, subgroup_size))
        # Inject one out-of-control signal in subgroup 18
        sub_raw[17] += 0.35
        sub_df = pd.DataFrame(np.round(sub_raw, 3), columns=[f"Sample_{i+1}" for i in range(subgroup_size)])
        sub_df.insert(0, "Subgroup_ID", range(1, n_subgroups + 1))
        sub_df["Subgroup_Mean"] = np.round(sub_raw.mean(axis=1), 3)
        sub_df["Subgroup_Range"] = np.round(np.ptp(sub_raw, axis=1), 3)
        sub_df.to_excel(writer, sheet_name="SPC_Subgroup_XbarR", index=False)

        # Sheet 3: Attributes Data for P-Chart and NP-Chart (30 inspection batches of n=100)
        n_batches = 30
        batch_sizes = np.full(n_batches, 100)
        # 2 batches with variable sample sizes (e.g. 120 and 80) to demonstrate variable control limits in p-chart
        batch_sizes[10] = 120
        batch_sizes[20] = 80
        defectives = np.random.binomial(batch_sizes, 0.035)
        # Inject special cause in batch 24
        defectives[23] = 11
        df_p_np = pd.DataFrame({
            "Batch_ID": range(1, n_batches + 1),
            "Sample_Size_n": batch_sizes,
            "Defective_Count_d": defectives,
            "Defective_Rate_p": np.round(defectives / batch_sizes, 4)
        })
        df_p_np.to_excel(writer, sheet_name="SPC_Attribute_P_NP", index=False)

        # Sheet 4: Attributes Data for C-Chart and U-Chart (30 inspection runs)
        units_inspected = np.full(n_batches, 5)  # 5 inspection units per run
        units_inspected[14] = 8
        units_inspected[25] = 4
        c_defects = np.random.poisson(units_inspected * 1.2)  # defect rate ~1.2 per unit
        c_defects[18] += 12  # Out of control spike
        df_c_u = pd.DataFrame({
            "Inspection_Run": range(1, n_batches + 1),
            "Units_Inspected_n": units_inspected,
            "Total_Defects_c": c_defects,
            "Defects_Per_Unit_u": np.round(c_defects / units_inspected, 3)
        })
        df_c_u.to_excel(writer, sheet_name="SPC_Attribute_C_U", index=False)

        # Sheet 5: Control Plan
        df_cplan = pd.DataFrame([
            {"Step_No": "OP-10", "Process_Name": "精车削工序", "Feature_Controlled": "零件核心外径 (dimension_mm)", "Spec_Tolerance": "50.00 ± 1.20 mm", "Control_Method": "I-MR 控制图 (SPC)", "Sample_Size": "每小时抽检 1 件", "Measurement_Technique": "数字气动量仪 (分辨率 0.001mm)", "Reaction_Plan_OCAP": "若单点超出 3σ 报警线，操机员立即按暂停键并挂黄牌，质检员介入复测，排查刀尖磨损及油温报警"},
            {"Step_No": "OP-10", "Process_Name": "主轴冷却单元", "Feature_Controlled": "主轴润滑油温 (temperature_C)", "Spec_Tolerance": "78.5 ± 1.5 °C", "Control_Method": "PLC连续数字闭环监测", "Sample_Size": "100% 实时传感器", "Measurement_Technique": "K型热电偶变送器", "Reaction_Plan_OCAP": "油温超 80℃ 系统自动闪烁报警，副散热风机强启；超 82℃ 联锁停机保护"},
            {"Step_No": "OP-10", "Process_Name": "切削液供给泵", "Feature_Controlled": "管路工作压力 (pressure_bar)", "Spec_Tolerance": "11.20 ± 0.40 bar", "Control_Method": "高低压电子压力开关", "Sample_Size": "100% 实时监测", "Measurement_Technique": "隔膜压力变送表", "Reaction_Plan_OCAP": "压力低于 10.5 bar 报警，班组长检查进液滤网清理铁屑"}
        ])
        df_cplan.to_excel(writer, sheet_name="Control_Plan", index=False)

        # Sheet 3: Poka-Yoke Register
        df_poka = pd.DataFrame([
            {"ID": "PY-01", "Process_Step": "主轴降温系统", "Risk_Failure_Mode": "冷却油耗尽干磨过热", "Poka_Yoke_Type": "关机型 (Shutdown)", "Device_Mechanism": "油箱浮球液位传感器 + PLC电气互锁，液位过低强制无法启动切削循环", "Effectiveness": "100% 消除无油运转隐患", "Responsible": "设备保全部"},
            {"ID": "PY-02", "Process_Step": "工件装夹就位", "Risk_Failure_Mode": "零件端面虚夹未贴紧基准面", "Poka_Yoke_Type": "报警型 (Warning)", "Device_Mechanism": "夹具定位面嵌入气隙微压传感器，贴合不严漏气时绿灯变红灯且机床不可合门", "Effectiveness": "防止尺寸轴向跳动超差", "Responsible": "工装模具科"}
        ])
        df_poka.to_excel(writer, sheet_name="Poka_Yoke_Register", index=False)

        # Sheet 4: Project Sign-Off Checklist
        df_signoff = pd.DataFrame([
            {"Audit_Item": "1. 过程能力目标达成", "Criteria": "Cpk 目标 >= 1.60", "Actual_Result": "Pilot 试运行 Cpk = 1.632", "Verdict": "Pass (合格)"},
            {"Audit_Item": "2. 缺陷率抑制情况", "Criteria": "DPMO < 50 PPM", "Actual_Result": "未出现超差品 (预估 DPMO < 1 PPM)", "Verdict": "Pass (合格)"},
            {"Audit_Item": "3. 财务收益核定", "Criteria": "年度节约报废返工成本 >= 30 万元", "Actual_Result": "财务复核年化质量成本节约 36.8 万元", "Verdict": "Pass (合格)"},
            {"Audit_Item": "4. 标准化与培训", "Criteria": "更新 SOP 与控制计划，完成操作员培训", "Actual_Result": "SOP-PR-2026-04 已发布，培训覆盖率 100%", "Verdict": "Pass (合格)"},
            {"Audit_Item": "5. 项目结案审批", "Criteria": "Champion / Process Owner 共同签字", "Actual_Result": "项目正式移交车间日常维持", "Verdict": "Approved (已核准)"}
        ])
        df_signoff.to_excel(writer, sheet_name="Project_Signoff", index=False)
    print("Created:", path)

if __name__ == "__main__":
    make_define_template()
    make_measure_template()
    make_analyze_template()
    make_improve_template()
    make_control_template()
    print("All 5 DMAIC Excel Templates successfully generated in SigmaFlow/templates/!")
