### **1.0 Material Specification & Source**

**1.1 Source Identification**
- `doi`: (Digital Object Identifier)
- `publication_year`: (e.g., 2023)
- `article_title`: (Title of the paper)
- `journal`: (e.g., Corrosion_Science, Materials_Science_and_Engineering_A)

**1.2 Material Grade & Source**
- `dss_class`: (e.g., lean_duplex(LDSS), standard_duplex, super_duplex(SDSS), hyper_duplex(HDSS))
- `grade_designation`: (e.g., DSS_2205, SDSS_2507, UNS_S32205, EN_1.4462)
- `material_source`: (e.g., commercial_supplier, lab_fabricated)
- `as_received_form`: (e.g., hot_rolled_plate, bar_stock, as_cast_ingot, powder, wire)

**1.3 Chemical Composition (wt% or at%)**
- `measurement_method`: (e.g., OES, XRF, ICP-OES, EDS, combustion_analysis)
- `composition_type`: (e.g., nominal, measured_bulk, measured_powder, measured_wire)
- `elements`:
  - `Cr`: (value)
  - `Ni`: (value)
  - `Mo`: (value)
  - `N`: (value)
  - `Mn`: (value)
  - `Si`: (value)
  - `C`: (value)
  - `Cu`: (value)
  - `W`: (value)
  - `S`: (value)
  - `P`: (value)
  - `Fe`: (e.g., balance, measured_value)
- `calculated_indices`:
  - `pren_value`: (value)
  - `pren_formula`: (e.g., Cr + 3.3*Mo + 16*N)
  - `Creq_Nieq_ratio`: (value)

**1.4 Feedstock (for AM/Welding)**
- `feedstock_type`: (e.g., powder, wire)
- `feedstock_fab_method`: (e.g., gas_atomization(GA), plasma_rotating_electrode_process(PREP))
- `feedstock_characteristics`: (e.g., particle_size_distribution(D10, D50, D90), morphology)

---

### **2.0 Material Processing & Fabrication (Bulk)**

**2.1 Primary Fabrication (Wrought/Cast)**
- `method`: (e.g., hot_rolling, cold_rolling, forging, casting)
- `parameters`: (e.g., temperature, total_reduction_percent, strain_rate)

**2.2 Additive Manufacturing (AM)**
- `am_method`: (e.g., laser_powder_bed_fusion(L-PBF)/selective_laser_melting(slm), directed_energy_deposition(DED), wire_arc_additive_manufacturing(WAAM))
- `am_parameters`:
  - `energy_source`: (e.g., laser_power(W), arc_current(A))
  - `scan_speed`: (mm/s)
  - `hatch_spacing`: (mm)
  - `layer_thickness`: (mm)
  - `energy_density`: (J/mm³)
  - `shielding_gas`: (e.g., Argon, Nitrogen)
  - `build_orientation`: (e.g., horizontal, vertical)

**2.3 Joining & Welding**
- `weld_method`: (e.g., gas_tungsten_arc_welding(GTAW)/TIG, gas_metal_arc_welding(GMAW)/MIG, laser_beam_welding(LBW))
- `weld_parameters`:
  - `heat_input`: (kJ/mm)
  - `filler_metal`: (e.g., ER2209, ER2594)
  - `shielding_gas`: (composition, flow_rate)
- `zone_analyzed`: (e.g., base_metal(BM), heat_affected_zone(HAZ), fusion_zone(FZ))

**2.4 Post-Process Heat Treatment (PPHT)**
- `treatment_type`: (e.g., solution_annealing, aging, solution_treatment(ST), post_weld_heat_treatment(PWHT), stress_relief, hot_isostatic_pressing(HIP))
- `treatment_parameters`:
  - `temperature`: (°C or K)
  - `time`: (hours, minutes)
  - `cooling_method`: (e.g., water_quench(WQ), furnace_cooling(FC), air_cooling(AC))

---

### **3.0 Test Specimen Preparation**

**3.1 Mechanical Test Specimen**
- `standard`: (e.g., ASTM_E8, ASTM_E23)
- `geometry`: (e.g., dog_bone, charpy_v_notch)
- `dimensions`: (e.g., gauge_length, cross_section)
- `orientation`: (e.g., longitudinal(L), transverse(T), short_transverse(ST), build_direction(BD))

**3.2 Corrosion Test Specimen**
- `dimensions_area`: (e.g., 10x10x1mm, exposed_area_1cm2)
- `surface_finish`: (e.g., ground_to_1200_grit_sic, polished_to_1um_diamond)
- `cleaning_method`: (e.g., acetone, ethanol, ultrasonic_bath)
- `mounting`: (e.g., cold_set_epoxy, teflon_holder)

**3.3 Metallographic Sample Preparation**
- `polishing_routine`: (e.g., final_step_0.05um_colloidal_silica)
- `etching_reagent`: (e.g., Beraha, 40%_NaOH_electrolytic, 10%_Oxalic)
- `etching_parameters`: (e.g., time, voltage)

---

### **4.0 Characterization & Analytical Methods (Tools)**

**4.1 Microscopy**
- `method`: (e.g., optical_microscopy(OM), scanning_electron_microscopy(SEM), transmission_electron_microscopy(TEM))
- `instrument_details`: (e.g., model, voltage(kV))
- `detectors_modes`: (e.g., secondary_electron(SE), backscattered_electron(BSE), bright_field(BF), dark_field(DF))

**4.2 Phase & Crystallographic Analysis**
- `method`: (e.g., x_ray_diffraction(XRD), electron_backscatter_diffraction(EBSD))
- `instrument_details`: (e.g., XRD_source(Cu_Ka), EBSD_step_size(um))

**4.3 Compositional Analysis (Micro)**
- `method`: (e.g., energy_dispersive_x_ray_spectroscopy(EDS), wavelength_dispersive_spectroscopy(WDS), atom_probe_tomography(APT))

**4.4 Thermal Analysis**
- `method`: (e.g., differential_scanning_calorimetry(DSC), dilatometry)

---

### **5.0 Microstructural Characterization (Results)**

**5.1 Primary Phases**
- `phases_identified`: (e.g., ferrite(α), austenite(γ))
- `phase_balance`: (e.g., ferrite_percent, austenite_percent)
- `ferrite_morphology`: (e.g., equiaxed, columnar, pancake)
- `austenite_morphology`: (e.g., widmanstatten(WA), intragranular(IGA), grain_boundary(GBA))

**5.2 Secondary Phases & Precipitates**
- `phases_identified`: (e.g., sigma(σ), chi(χ), alpha_prime(α′), CrN, Cr2N, M23C6, secondary_austenite(γ2))
- `phase_fraction`: (% or qualitative)
- `location_distribution`: (e.g., at_ferrite_grain_boundary, inside_ferrite)

**5.3 Grain Structure**
- `grain_size`: (e.g., avg_grain_size(um), ASTM_grain_size_number)
- `grain_boundary_char`: (e.g., high_angle(HAGBs)_percent, low_angle(LAGBs)_percent, coincidence_site_lattice(CSL))

**5.4 Defect & Inhomogeneity Structure**
- `defects`: (e.g., porosity(%), microcracks, lack_of_fusion(LOF))
- `inclusions`: (e.g., oxide_inclusion, sulfide_inclusion)
- `segregation`: (e.g., Cr/Mo_in_ferrite, Ni/N_in_austenite)

---

### **6.0 Performance Testing Methods**

**6.1 Mechanical Test Methods**
- `tensile_test_standard`: (e.g., ASTM_E8/E8M)
- `tensile_parameters`: (e.g., strain_rate(s-1), test_temperature(°C))
- `hardness_test_method`: (e.g., vickers(HV), rockwell(HRC))
- `hardness_parameters`: (e.g., load(kgf), dwell_time(s))
- `impact_test_standard`: (e.g., ASTM_E23, ISO_148)
- `impact_parameters`: (e.g., test_temperature_range(°C))
- `fatigue_test_method`: (e.g., high_cycle_fatigue(HCF), low_cycle_fatigue(LCF))

**6.2 Corrosion Test Methods**
- `test_environment`:
  - `electrolyte`: (e.g., 3.5%_NaCl_solution, 1M_H2SO4, artificial_seawater)
  - `temperature`: (°C or K)
  - `pH`: (value)
  - `aeration`: (e.g., deaerated_with_N2, open_to_air)
- `electrochemical_setup`:
  - `potentiostat_model`: (e.g., Gamry, Solartron)
  - `reference_electrode`: (e.g., Ag/AgCl, SCE)
  - `counter_electrode`: (e.g., platinum_mesh, graphite_rod)
- `polarization_test_params`:
  - `standard`: (e.g., ASTM_G5, ASTM_G61)
  - `scan_rate`: (mV/s)
  - `potential_range`: (V)
- `cpt_test_params`:
  - `standard`: (e.g., ASTM_G150, ASTM_G48_Method_E)
  - `applied_potential`: (mV)
  - `heating_rate`: (°C/min)
- `scc_test_method`: (e.g., slow_strain_rate_testing(SSRT), U-bend, C-ring)
- `sensitization_test_method`: (e.g., double_loop_EPR(DLEPR), ASTM_A262)

---

### **7.0 Measured Performance & Post-Test Analysis (Results)**

**7.1 Mechanical Property Results**
- `yield_strength_0.2_offset`: (MPa)
- `ultimate_tensile_strength(UTS)`: (MPa)
- `elongation_to_failure`: (%)
- `hardness_value`: (e.g., HV1, HRC)
- `impact_energy`: (Joules)
- `ductile_to_brittle_transition_temp(DBTT)`: (°C)
- `fatigue_limit`: (MPa)

**7.2 Corrosion Performance Results**
- `corrosion_potential(E_corr)`: (V)
- `corrosion_current_density(i_corr)`: (A/cm²)
- `pitting_potential(E_pit)`: (V)
- `repassivation_potential(E_rep)`: (V)
- `passive_current_density`: (A/cm²)
- `critical_pitting_temperature(CPT)`: (°C)
- `degree_of_sensitization(DOS)`: (%)

**7.3 Data Quantification Methods**
- `phase_quant_method`: (e.g., ASTM_E562_point_counting, XRD_Rietveld_refinement, EBSD_software_analysis)
- `grain_size_quant_method`: (e.g., ASTM_E112_intercept_method)
- `corrosion_param_quant_method`: (e.g., Tafel_extrapolation, polarization_resistance_fit)
- `eis_quant_method`: (e.g., equivalent_circuit_model_used)

**7.4 Post-Test Failure Analysis**
- `fracture_surface_features`: (e.g., dimples, cleavage_facets, intergranular_cracking, quasi_cleavage)
- `corrosion_damage_features`: (e.g., pit_morphology, lacy_cover, transgranular_cracking(TGSCC), intergranular_cracking(IGSCC))
- `associated_microstructure`: (e.g., crack_path_through_ferrite, pitting_initiated_at_MnS_inclusion, Cr_depleted_zone)

---

### **8.0 Computational Modeling & Simulation**

**8.1 Model Type**
- `type`: (e.g., thermodynamic_modeling(CALPHAD), kinetic_modeling(DICTRA), finite_element_method(FEM))
**8.2 Software & Databases**
- `software`: (e.g., Thermo-Calc, JMatPro, Abaqus)
- `database`: (e.g., TCFE11, MOBFE5)
**8.3 Predicted Outputs**
- `outputs`: (e.g., equilibrium_phase_fraction, TTP_diagram, stress_distribution, predicted_CPT)

---

### **9.0 Metadata & Author Conclusions**

**9.1 Statistical Reporting**
- `replication`: (e.g., N=3_samples, average_of_5_tests)
- `error_reporting`: (e.g., standard_deviation, error_bars_shown)
**9.2 Author's Stated Conclusions**
- `structure_property_relationship`: (e.g., "Authors state sigma phase led to 50% drop in toughness", "AM porosity identified as primary cause for low elongation")