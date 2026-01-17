### **1.0 材料规格与来源**

**1.1 来源识别**
- `doi`: (数字对象标识符)
- `publication_year`: (例如：2023)
- `article_title`: (论文标题)
- `journal`: (例如：腐蚀科学、材料科学与工程A)

**1.2 材料等级与来源**
- `dss_class`: (例如：精益双相钢(LDSS)、标准双相钢、超级双相钢(SDSS)、超双相钢(HDSS))
- `grade_designation`: (例如：DSS_2205、SDSS_2507、UNS_S32205、EN_1.4462)
- `material_source`: (例如：商业供应商、实验室制备)
- `as_received_form`: (例如：热轧板、棒材、铸造锭、粉末、线材)

**1.3 化学成分 (wt% 或 at%)**
- `measurement_method`: (例如：OES、XRF、ICP-OES、EDS、燃烧分析)
- `composition_type`: (例如：标称值、测量体积、测量粉末、测量线材)
- `elements`:
  - `Cr`: (数值)
  - `Ni`: (数值)
  - `Mo`: (数值)
  - `N`: (数值)
  - `Mn`: (数值)
  - `Si`: (数值)
  - `C`: (数值)
  - `Cu`: (数值)
  - `W`: (数值)
  - `S`: (数值)
  - `P`: (数值)
  - `Fe`: (例如：余量、测量值)
- `calculated_indices`:
  - `pren_value`: (数值)
  - `pren_formula`: (例如：Cr + 3.3*Mo + 16*N)
  - `Creq_Nieq_ratio`: (数值)

**1.4 原料 (用于增材制造/焊接)**
- `feedstock_type`: (例如：粉末、线材)
- `feedstock_fab_method`: (例如：气体雾化(GA)、等离子旋转电极工艺(PREP))
- `feedstock_characteristics`: (例如：粒度分布(D10、D50、D90)、形貌)

---

### **2.0 材料加工与制造 (体材)**

**2.1 初级制造 (锻造/铸造)**
- `method`: (例如：热轧、冷轧、锻造、铸造)
- `parameters`: (例如：温度、总变形率、应变率)

**2.2 增材制造 (AM)**
- `am_method`: (例如：激光粉末床熔融(L-PBF)/选择性激光熔化(SLM)、定向能量沉积(DED)、电弧增材制造(WAAM))
- `am_parameters`:
  - `energy_source`: (例如：激光功率(W)、电弧电流(A))
  - `scan_speed`: (mm/s)
  - `hatch_spacing`: (mm)
  - `layer_thickness`: (mm)
  - `energy_density`: (J/mm³)
  - `shielding_gas`: (例如：氩气、氮气)
  - `build_orientation`: (例如：水平、垂直)

**2.3 连接与焊接**
- `weld_method`: (例如：钨极氩弧焊(GTAW)/TIG、熔化极氩弧焊(GMAW)/MIG、激光束焊接(LBW))
- `weld_parameters`:
  - `heat_input`: (kJ/mm)
  - `filler_metal`: (例如：ER2209、ER2594)
  - `shielding_gas`: (成分、流量)
- `zone_analyzed`: (例如：母材(BM)、热影响区(HAZ)、熔合区(FZ))

**2.4 后处理热处理 (PPHT)**
- `treatment_type`: (例如：固溶退火、时效、固溶处理(ST)、焊后热处理(PWHT)、应力消除、热等静压(HIP))
- `treatment_parameters`:
  - `temperature`: (°C 或 K)
  - `time`: (小时、分钟)
  - `cooling_method`: (例如：水淬(WQ)、炉冷(FC)、空冷(AC))

---

### **3.0 试样制备**

**3.1 力学试验试样**
- `standard`: (例如：ASTM_E8、ASTM_E23)
- `geometry`: (例如：狗骨形、夏比V型缺口)
- `dimensions`: (例如：标距长度、横截面)
- `orientation`: (例如：纵向(L)、横向(T)、短横向(ST)、构建方向(BD))

**3.2 腐蚀试验试样**
- `dimensions_area`: (例如：10x10x1mm、暴露面积1cm2)
- `surface_finish`: (例如：SiC砂纸打磨至1200目、金刚石抛光至1μm)
- `cleaning_method`: (例如：丙酮、乙醇、超声波清洗)
- `mounting`: (例如：冷固化环氧树脂、聚四氟乙烯夹具)

**3.3 金相样品制备**
- `polishing_routine`: (例如：最终步骤0.05μm胶体二氧化硅)
- `etching_reagent`: (例如：Beraha试剂、40% NaOH电解、10%草酸)
- `etching_parameters`: (例如：时间、电压)

---

### **4.0 表征与分析方法 (工具)**

**4.1 显微镜技术**
- `method`: (例如：光学显微镜(OM)、扫描电子显微镜(SEM)、透射电子显微镜(TEM))
- `instrument_details`: (例如：型号、电压(kV))
- `detectors_modes`: (例如：二次电子(SE)、背散射电子(BSE)、明场(BF)、暗场(DF))

**4.2 相与晶体学分析**
- `method`: (例如：X射线衍射(XRD)、电子背散射衍射(EBSD))
- `instrument_details`: (例如：XRD射线源(Cu_Kα)、EBSD步长(μm))

**4.3 成分分析 (微观)**
- `method`: (例如：能量色散X射线光谱(EDS)、波长色散光谱(WDS)、原子探针断层扫描(APT))

**4.4 热分析**
- `method`: (例如：差示扫描量热法(DSC)、膨胀测量法)

---

### **5.0 微观结构表征 (结果)**

**5.1 主要相**
- `phases_identified`: (例如：铁素体(α)、奥氏体(γ))
- `phase_balance`: (例如：铁素体百分比、奥氏体百分比)
- `ferrite_morphology`: (例如：等轴、柱状、薄饼状)
- `austenite_morphology`: (例如：魏氏体(WA)、晶内(IGA)、晶界(GBA))

**5.2 次要相与析出物**
- `phases_identified`: (例如：σ相、χ相、α′相、CrN、Cr2N、M23C6、二次奥氏体(γ2))
- `phase_fraction`: (% 或定性)
- `location_distribution`: (例如：在铁素体晶界、铁素体内部)

**5.3 晶粒结构**
- `grain_size`: (例如：平均晶粒尺寸(μm)、ASTM晶粒度号)
- `grain_boundary_char`: (例如：大角度晶界(HAGBs)百分比、小角度晶界(LAGBs)百分比、重合位置点阵(CSL))

**5.4 缺陷与不均匀结构**
- `defects`: (例如：孔隙率(%)、微裂纹、熔合不良(LOF))
- `inclusions`: (例如：氧化物夹杂、硫化物夹杂)
- `segregation`: (例如：铁素体中的Cr/Mo、奥氏体中的Ni/N)

---

### **6.0 性能测试方法**

**6.1 力学试验方法**
- `tensile_test_standard`: (例如：ASTM_E8/E8M)
- `tensile_parameters`: (例如：应变率(s-1)、试验温度(°C))
- `hardness_test_method`: (例如：维氏硬度(HV)、洛氏硬度(HRC))
- `hardness_parameters`: (例如：载荷(kgf)、保持时间(s))
- `impact_test_standard`: (例如：ASTM_E23、ISO_148)
- `impact_parameters`: (例如：试验温度范围(°C))
- `fatigue_test_method`: (例如：高周疲劳(HCF)、低周疲劳(LCF))

**6.2 腐蚀试验方法**
- `test_environment`:
  - `electrolyte`: (例如：3.5% NaCl溶液、1M H2SO4、人工海水)
  - `temperature`: (°C 或 K)
  - `pH`: (数值)
  - `aeration`: (例如：N2除氧、暴露于空气)
- `electrochemical_setup`:
  - `potentiostat_model`: (例如：Gamry、Solartron)
  - `reference_electrode`: (例如：Ag/AgCl、SCE)
  - `counter_electrode`: (例如：铂网、石墨棒)
- `polarization_test_params`:
  - `standard`: (例如：ASTM_G5、ASTM_G61)
  - `scan_rate`: (mV/s)
  - `potential_range`: (V)
- `cpt_test_params`:
  - `standard`: (例如：ASTM_G150、ASTM_G48方法E)
  - `applied_potential`: (mV)
  - `heating_rate`: (°C/min)
- `scc_test_method`: (例如：慢应变率试验(SSRT)、U型弯曲、C环)
- `sensitization_test_method`: (例如：双环电化学动电位再活化(DLEPR)、ASTM_A262)

---

### **7.0 测量性能与试后分析 (结果)**

**7.1 力学性能结果**
- `yield_strength_0.2_offset`: (MPa)
- `ultimate_tensile_strength(UTS)`: (MPa)
- `elongation_to_failure`: (%)
- `hardness_value`: (例如：HV1、HRC)
- `impact_energy`: (焦耳)
- `ductile_to_brittle_transition_temp(DBTT)`: (°C)
- `fatigue_limit`: (MPa)

**7.2 腐蚀性能结果**
- `corrosion_potential(E_corr)`: (V)
- `corrosion_current_density(i_corr)`: (A/cm²)
- `pitting_potential(E_pit)`: (V)
- `repassivation_potential(E_rep)`: (V)
- `passive_current_density`: (A/cm²)
- `critical_pitting_temperature(CPT)`: (°C)
- `degree_of_sensitization(DOS)`: (%)

**7.3 数据定量方法**
- `phase_quant_method`: (例如：ASTM_E562点计数法、XRD Rietveld精修、EBSD软件分析)
- `grain_size_quant_method`: (例如：ASTM_E112截距法)
- `corrosion_param_quant_method`: (例如：Tafel外推法、极化电阻拟合)
- `eis_quant_method`: (例如：使用的等效电路模型)

**7.4 试后失效分析**
- `fracture_surface_features`: (例如：韧窝、解理面、沿晶开裂、准解理)
- `corrosion_damage_features`: (例如：点蚀形貌、花边覆盖层、穿晶应力腐蚀开裂(TGSCC)、沿晶应力腐蚀开裂(IGSCC))
- `associated_microstructure`: (例如：裂纹路径穿过铁素体、点蚀起始于MnS夹杂、Cr贫化区)

---

### **8.0 计算建模与仿真**

**8.1 模型类型**
- `type`: (例如：热力学建模(CALPHAD)、动力学建模(DICTRA)、有限元法(FEM))
**8.2 软件与数据库**
- `software`: (例如：Thermo-Calc、JMatPro、Abaqus)
- `database`: (例如：TCFE11、MOBFE5)
**8.3 预测输出**
- `outputs`: (例如：平衡相分数、TTP图、应力分布、预测CPT)

---

### **9.0 元数据与作者结论**

**9.1 统计报告**
- `replication`: (例如：N=3个样品、5次试验的平均值)
- `error_reporting`: (例如：标准偏差、显示误差棒)
**9.2 作者陈述的结论**
- `structure_property_relationship`: (例如："作者指出σ相导致韧性下降50%"、"AM孔隙被确定为低延伸率的主要原因")
