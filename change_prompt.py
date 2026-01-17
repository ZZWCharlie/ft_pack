
from langchain_openai import ChatOpenAI
import os
import json
from graph_utils.chatgpt.config.config import (
    OPENAI_CONFIG,
)
API_SECRET_KEY = OPENAI_CONFIG['api_key']
BASE_URL = OPENAI_CONFIG['base_url']
os.environ["OPENAI_API_KEY"] = API_SECRET_KEY
os.environ["OPENAI_API_BASE"] = BASE_URL

# 新主题示例
# subject = "Metal organic framework (MOF) materials"
# subject = "Covalent organic frameworks (COFs)"
subject = "Overall Water Splitting(OWS)"
graphllm = ChatOpenAI(temperature=0, model_name="gpt-4.1-2025-04-14",max_retries=10)
result = graphllm.invoke('who are you?').content
print(result)

subject_template_file = "./template/OWS.md"
subject_kg_prompt_file = "./graph_utils/OWS_kg_prompt.md"
prompts_config_file="./graph_utils/chatgpt/config/prompts_config_OWS.json"
# 加载费托合成的大提示词
template=  """# FT Experiment Template

## 1. Materials

### 1.1 Reagents

**Objective**:  
Generate a detailed extraction of **all reagents** involved in the Fischer–Tropsch synthesis experiments described in the article. This includes **metal precursors**, **additive/promoter precursors**, **solvents**, **base/acid regulators**, **complexing agents**, **surface modifiers**, **passivation atmosphere gases**, **synthesis gas environment gases**, and **any other reagents** reported. The goal is to ensure that the content is **precisely extracted**, **relevant**, and **comprehensive** without introducing unnecessary examples, while **omitting any empty categories**.

---

- **Content Requirements**  
- Extract all **reagents** involved in the experiments based on the following categories (only generate a subsection if at least one reagent of that type appears in the article):  
  1. **Metal precursors**: Reagents providing active metal species for the catalyst.  
  2. **Additive/Promoter precursors**: Promoters, surface modifiers, pH adjusters, etc., that affect catalyst structure or reactivity.  
  3. **Solvents**: For dissolving or dispersing other reagents.  
  4. **Base/Acid Regulators**: Controlling pH or precipitating metal ions.  
  5. **Complexing agents**: Form coordination complexes with metal ions.  
  6. **Surface modifiers**: For coating or special treatment (e.g., silica shells).  
  7. **Passivation Atmosphere Gases**: Gases used to passivate the catalyst surface (e.g., N₂, Ar), including mixtures, flow rates, temperatures, durations.  
  8. **Synthesis Gas Environment Gases**: Gases/mixtures used during synthesis or pretreatment (e.g., H₂/CO, syngas), with ratios, flow, pressure, temperature, and purpose.  
  9. **Other Reagents**: Any additional chemicals (e.g., drying agents, titrants, cleaning agents) not covered above.

- **For each reagent**, extract these details when available:  
  - **Name**  
  - **Chemical Formula / Composition**  
  - **Purity**  
  - **Supplier/Brand & Catalog Number**  
  - **Operational Conditions** (for gases: flow rate, pressure, temperature, duration)  
  - **Purpose**  

- **Specific Guidance**  
  - Assign each reagent to the most specific category.  
  - For dual‐function reagents (e.g., promoter + surface modifier), state both roles in the Purpose field.  
  - **Conditional Subsection Generation**: If no reagents of a given category are reported, skip that subsection entirely and renumber subsequent subsections sequentially.

---

**Formatting Instructions**

1. **Subsection Headers**: Use `####` with the updated number/title (e.g., `#### 1.1.7 Surface Modifiers` or `#### 1.1.5 Surface Modifiers` if previous categories were skipped).  
2. **Bullet Points**: Each reagent as `- **Reagent Name**:`.  
3. **Detail Order**: Chemical Formula/Composition, Purity, Supplier/Brand & Catalog Number, Operational Conditions (for gases), Purpose.  
4. **Detail Formatting**: Commas between items, brackets for optional details, e.g.:  
   ```
   - **Nitrogen**: N₂, 99.999% purity, Air Products, Flow 50 mL/min at 25 °C for 2 h, Used for passivation of reduced catalyst surface.
   ```  
5. **Grouping**: Within a subsection, you may add bolded sub‐labels (e.g., **Promoter Precursors**, **pH Adjusters**).  
6. **No Extra Text**: Only list reagents and their details—no explanatory prose.

---

**Example** (assuming all categories appear):

```markdown
    ### 1.1 Reagents

    #### 1.1.1 Metal Precursors
    - **Iron nitrate nonahydrate**: Fe(NO₃)₃·9H₂O, 98.5% purity, Sigma‑Aldrich, Used as a metal precursor in Fischer–Tropsch synthesis.

    #### 1.1.2 Additive/Promoter Precursors
    - **Promoter Precursors**:  
      - **Cerium nitrate hexahydrate**: Ce(NO₃)₃·6H₂O, AR, Sigma‑Aldrich, Used as a promoter.  
    - **pH Adjusters**:  
      - **Sodium hydroxide**: NaOH, AR, Sigma‑Aldrich, Used for pH adjustment.

    #### 1.1.3 Solvents
    - **Ethanol**: C₂H₅OH, 99.8% purity, Merck, Used for dispersion.
    - **Acetone**: C₃H₆O, 99.5% purity, Sigma‑Aldrich, Used for cleaning.

    #### 1.1.4 Base/Acid Regulators
    - **Nitric acid**: HNO₃, 68–70% purity, Sigma‑Aldrich, Used for pH control.

    #### 1.1.5 Complexing Agents
    - **Ethylenediamine**: C₂H₈N₂, AR, Sigma‑Aldrich, Used to complex metal ions.

    #### 1.1.6 Surface Modifiers
    - **Tetraethyl orthosilicate**: Si(OC₂H₅)₄, 98% purity, Merck, Used to form silica shell.

    #### 1.1.7 Passivation Atmosphere Gases
    - **Nitrogen**: N₂, 99.999% purity, Air Products, Flow 50 mL/min at 25 °C for 2 h, Used for passivation.

    #### 1.1.8 Synthesis Gas Environment Gases
    - **Syngas (H₂/CO = 2:1)**: H₂/CO mixture, Research grade, Praxair, Ratio 2:1, 1 MPa, 300 °C, Feed gas for reaction.

    #### 1.1.9 Other Reagents
    - **Magnesium sulfate**: MgSO₄, 99% purity, Aladdin, Used as a drying agent.
```

### 1.2 Specific Experimental Equipment

**Objective**: Extract and list specific equipment used in catalyst synthesis, characterization, activation, and analysis, including clear names, brands, and models (if available). **No descriptions or explanations are needed; list only equipment names and models. If brand or model is not specified but reactor dimensions (e.g., length, width, height, volume) are provided in the source, include those dimensions. Otherwise, include a one‑sentence generic description of the equipment’s typical function.**

- **Synthesis Equipment**: Equipment used for reacting chemical reagents and synthesizing catalysts, such as autoclaves, reactors, or other specialized equipment required for catalyst preparation.  
- **Characterization Equipment**: Instruments used to analyze the physical and chemical properties of catalysts. This includes characterization methods like:  
  - **ICP**  
  - **TEM** and **EDS**  
  - **FTIR**  
  - **Water‑droplet contact angle tests**  
  - **XPS**  
  - **XRD**  
  - **CO‑TPR** and **H₂‑TPR**  
  - **DRIFTS**  
  - **Mössbauer spectrum**

- **Activation Equipment**: Equipment specifically used for activating catalysts, such as furnaces or reactors used for thermal treatment or reduction.  
- **Product Analysis Equipment**: Instruments used for evaluating the products after the reaction phase, such as gas chromatographs, mass spectrometers, or other tools used for analyzing reaction outputs.  
- **Reaction Equipment**: List general equipment used to carry out chemical reactions, such as reactors, stirred tanks, or flow reactors.
- **Other Specific Equipment**: Laboratory tools used for experimental preparation, reaction monitoring, or sample handling, including balance scales, magnetic stirrers, pumps, etc.  

---

**Example Output Format**:

```markdown
    ### 1.2 Specific Experimental Equipment

    #### **Synthesis Equipment**
      - [Brief description of role] – [Equipment Name]

    #### **Characterization Equipment**
      - [Brief description of role] – [Equipment Name] (Model: [Model Name])
      - [Brief description of role] – [Equipment Name] (Model: [Model Name])
      - [Additional equipment in this category with descriptions]

    #### **Activation Equipment**
      - [Brief description of role] – [Equipment Name]
      - [Additional equipment in this category with descriptions]

    #### **Reaction Equipment**
      - [Brief description of role] – [Equipment Name]
      - [Additional equipment in this category with descriptions]

    #### **Product Analysis Equipment**
      - [Brief description of role] – [Equipment Name]
      - [Additional equipment in this category with descriptions]

    #### **Other Specific Equipment**
      - [Brief description of role] – [Equipment Name]
      - [Additional equipment in this category with descriptions]

```

---

**Special Notes:**

- **Synthesis equipment**: Focus only on the equipment involved in the catalyst synthesis process. This excludes equipment used for non-synthesis phases like reactant preparation or product analysis (unless it directly contributes to the synthesis).
- Includes tools used across various laboratory tasks but not necessarily involved in catalyst synthesis itself. However, many of these tools play a supportive or auxiliary role in the synthesis, characterization, or evaluation process.
- The model should identify and select relevant equipment for each phase based on the specific experimental context.
  
### 1.3 Common Laboratory Equipment

**Objective**: Extract and list common laboratory equipment that is often used in various stages of experimental work, even if it is not directly related to catalyst synthesis. This can include equipment for general lab preparation, handling reagents, or ensuring appropriate experimental conditions during synthesis or analysis.

- **Drying Equipment**: List equipment used to dry reagents or catalysts, such as ovens, freeze dryers, or other drying technologies.
- **Calcination Equipment**: List equipment used for controlled heating, calcining catalyst precursors, or removing impurities during synthesis or post-synthesis.
- **Other Common Equipment**: List other laboratory tools used for general purposes during experimental preparation, reaction monitoring, or sample handling (e.g., balance scales, magnetic stirrers, pumps, etc.). This section includes equipment that plays a supportive or auxiliary role in the synthesis, characterization, or evaluation process.

---

**Example Output Format**:

```markdown
    ### 1.3 Common Laboratory Equipment

    #### **Drying Equipment**
      - [Equipment Name]
      - [Equipment Name]

    #### **Calcination Equipment**
      - [Equipment Name]
      - [Equipment Name]

    #### **Other Common Equipment**
      - [Equipment Name]
      - [Equipment Name]
```

**Formatting Instructions**

1. **Section Header**  
   - Use `###` for the main subsection title (`1.3 Common Laboratory Equipment`).

2. **Category Headers**  
   - Use `####` for each equipment category.  
   - Enclose the category name in double asterisks (e.g., `#### **Drying Equipment**`).

3. **Bullet Lists**  
   - Use hyphens (`-`) for listing each piece of equipment.  
   - Indent list items by two spaces under their category header.

4. **Consistency**  
   - Maintain exact terminology and capitalization as in the article.  
   - Do not include equipment not mentioned in the source.

---

**Special Notes:**

- Includes tools used across various laboratory tasks but not necessarily involved in catalyst synthesis itself. However, many of these tools play a supportive or auxiliary role in the synthesis, characterization, or evaluation process.
- The model should identify and select relevant equipment for each phase based on the specific experimental context.

## 2. Synthesis Methods

**Objective:**  
Generate a structured and comprehensive section detailing the **synthesis methods** used for Fischer–Tropsch catalysts. The content should be **strictly extracted** from the article, ensuring accuracy, reproducibility, and relevance.

**Content Requirements**  

```markdown
    ## 2. Synthesis Methods

    ### Extraction of Detailed Preparation and Post‑processing Steps
    - **Overview of Catalyst Synthesis Techniques**  
      - Provide a **comparative analysis** of the methods, discussing **advantages and disadvantages** regarding synthesis complexity, scalability, cost, and equipment requirements.

    For **each** synthesis method reported in the article:

    ### Step-by-step Experimental Procedures
    - **Order of Steps:**  
      1. Precursor mixing / co‑precipitation  
      2. **Precipitation–Deposition** *(if reported)*  
      3. Drying  
      4. Calcination  
      5. Any additional post‑treatments (e.g., reduction, passivation)  
    - **Details to Extract:**  
      - Chemical reagents and their concentrations  
      - Reaction conditions (temperature, pressure, duration)  
      - Equipment used (e.g., Teflon‑lined autoclave, pH meter, rotary evaporator)  
      - Observed experimental phenomena (e.g., color change, precipitate formation)  
      - All numerical values and units exactly as in the article
```

- **Example Formats**
  - **Hydrothermal Method:**  
    - Reactor: Teflon‑lined autoclave  
    - Temperature: 180 °C, Duration: 12 h  
    - Post‑treatment: Washing → Drying at 80 °C → Calcination at 500 °C for 4 h  

  - **Co‑precipitation Method:**  
    - Metal precursor mixing: Fe(NO₃)₃ and Co(NO₃)₂ in water  
    - pH control: Adjust to 9 with NH₄OH  
    - Aging: 2 h at 60 °C under stirring  
    - **Precipitation–Deposition:** Add support precursor dropwise, stir 1 h  
    - Drying: 100 °C, 6 h  
    - Calcination: 450 °C, 5 h  

  - **Impregnation Method:**  
    - Soaking: Catalyst support in metal nitrate solution, 12 h  
    - Drying: 80 °C, overnight  
    - Calcination: 400 °C, 3 h

---

**Formatting Instructions**

1. **Headers & Hierarchy**  
   - Use `##` for the main section title (`2. Synthesis Methods`).  
   - Use `###` for the extraction subheading.  
   - Use `####` (or bullet “•”) for each procedural block.

2. **Step Order & Numbering**  
   - Clearly number the sequence of steps.  
   - Explicitly insert the “Precipitation–Deposition” step **after** precursor mixing/co‑precipitation and **before** drying/calcination.

3. **Bulleted Details**  
   - List reagents, conditions, equipment, and observations as separate bullets.  
   - Maintain the same terminology and units as in the article.

4. **Example Formats**  
   - Provide one example per method as a template; **do not** leave placeholders.  
   - Replace example values with actual data when populating.

5. **Units & Numerical Values**  
   - Report all temperatures (°C), durations (h, min), pH values, and concentrations (M, wt %) exactly as given.

---

**Special Instructions for the Model**  

- **Strictly extract** content from the article—do **not** generate hypothetical information.  
- **Autonomously structure** the section based on reported methods.  
- **Maintain clarity and reproducibility**, ensuring that another researcher could replicate the procedure.  
- **Exclude unrelated content**, focusing **only on catalyst synthesis** (no reactant prep, product analysis, or characterization).  
  
## 3. Synthesis Procedures

### 3.1 Reagent Preparation

**Objective**  
Extract the detailed reagent preparation steps **for each individual catalyst** used in Fischer–Tropsch synthesis experiments, focusing on solid reagent weighing, liquid transfer, and mixing, with clarity and full reproducibility.

---

- Content Requirements

  - Catalyst‑Specific Grouping  
  Under **each** of the following second‑level sections (Weighing / Liquid Transfer / Mixing), create a third‑level subsection for **each catalyst** (e.g., Catalyst A, FeCo/SiO₂, etc.).

  - Weighing of Reagents  
    - **Task**: Extract all details of weighing **solid reagents** (precursors, promoters, additives).  
    - **Include**:  
      - Chemical name and formula  
      - Exact mass (e.g., “0.15 g”)  
      - Balance type or precision (if specified)  
    - **Entry Format**:  
  
      ```
      **[Chemical Name]**: Weighed [amount] [on balance if specified].
      ```

  - Liquid Transfer  
    - **Task**: Extract how liquid reagents are transferred or added.  
    - **Include**:  
      - Liquid name and volume (e.g., “50 mL ethanol”)  
      - Transfer method (poured, pumped, etc.)  
      - Container or equipment used (graduated cylinder, syringe, etc.)  
    - **Entry Format**:  

      ```
      **[Liquid Name]**: [Transfer method] [volume] using [equipment if specified].
      ```

  - Mixing  
    - **Task**: Extract how reagents are mixed to form a homogeneous solution or suspension.  
    - **Include**:  
      - Stirring speed and duration  
      - Ultrasonic treatment or other techniques  
      - Environmental conditions (temperature, inert atmosphere, etc.)  
    - **Entry Format**:  

      ```
      **[Solution or Reagents]**: Mixed [how] for [duration] under [conditions if any].
      ```

---

- Output Structure

Only include sections and entries **actually present** in the article:

```markdown
    ### 3.1 Reagent Preparation

    #### 3.1.1 Weighing

    ##### 3.1.1.1 Catalyst A
    - **Fe(NO₃)₃·9H₂O**: Weighed 0.15 g using an analytical balance.
    - **Co(NO₃)₂·6H₂O**: Weighed 0.10 g.

    ##### 3.1.1.2 Catalyst B
    - **Cu(NO₃)₂·3H₂O**: Weighed 0.20 g.

    #### 3.1.2 Liquid Transfer

    ##### 3.1.2.1 Catalyst A
    - **Deionized water**: Poured 50 mL into a beaker containing the metal salts.

    ##### 3.1.2.2 Catalyst B
    - **Ethanol**: Pumped 30 mL into the reaction vessel using a syringe.

    #### 3.1.3 Mixing

    ##### 3.1.3.1 Catalyst A
    - **Fe/Co nitrate solution**: Stirred at 800 rpm for 30 minutes at room temperature.
    - **Final mixture**: Ultrasonically treated for 15 minutes.

    ##### 3.1.3.2 Catalyst B
    - **Cu solution**: Stirred at 600 rpm for 20 minutes under N₂ atmosphere.
```

---

- Usage Instructions

1. **Second‑Level Sections**  
   - 3.1.1 Weighing  
   - 3.1.2 Liquid Transfer  
   - 3.1.3 Mixing

2. **Third‑Level Subsections**  
   Under each of the above, add one subsection per catalyst:  
   `3.1.X.Y Catalyst Name` (X = 1/2/3, Y = catalyst index).

3. **Strictly Article‑Based**  
   Only extract details explicitly given in the main text or supplementary materials. No invented or assumed steps.

4. **Consistent Entry Format**  
   Use `**[Reagent]**: [Detailed operation]` for every bullet.

### 3.2 Detailed synthesis process

**Objective**: The goal is to extract detailed experimental steps for Fischer-Tropsch catalyst synthesis, focusing on reagent preparation, temperature, pH, drying, calcination, and other relevant conditions. The structure should be flexible enough to apply to various catalysts, with a focus on clarity and reproducibility. **Always begin each catalyst’s workflow by listing and describing the synthesis of all primary precursors—from available salts, oxides or ligands—before any intermediate steps.** Extract *every* step of Fischer–Tropsch catalyst synthesis *starting from the raw chemical precursors*, so that a reader could reproduce the work by following this report alone.

Format for each Catalyst Synthesis Step:

```markdown
    ### 3.2 Detailed synthesis process
    #### Catalyst Preparation [1]: [Catalyst Name (e.g., NiO)]
    ##### Step [1]: [Preparation Step Name, e.g., Synthesis of NiO Catalyst]
    - **Reagents**: [List of reagents and their quantities, e.g., 10.0 g Ni(NO₃)₂·6H₂O, 50 mL deionized water]
    - **Conditions**: [Key operational conditions such as temperature, pH, time, and equipment, e.g., Stir for 1 hour at room temperature]
    - **Process**:
      - [Point 1: Specific operational step, e.g., Dissolve 10.0 g of Ni(NO₃)₂·6H₂O in 50 mL deionized water to form a homogeneous solution.]
      - [Point 2: Any specific time and temperature conditions, e.g., Stir the solution at room temperature for 1 hour to ensure complete dissolution of the reagent.]
      - [Point 3: Any reagent additions or reaction conditions, e.g., Add 5.0 g of NaOH solution dropwise to adjust the pH to 9.]
      - [Point 4: Any other significant operational steps, e.g., Stir for an additional 30 minutes to ensure complete precipitation of nickel hydroxide.]
    - **Key Steps**: [Important points or conditions to watch out for during the process]

    ##### Step [2]: [Purification or Post-Processing Step]
    - [Details similar to Step 1, focusing on washing, drying, filtration, etc.]

    [Repeat for each catalyst: Workflow order: Precursor Preparation → Purification → Drying → Calcination → Final Activation.]

```

What to include:

For each Catalyst:

1. **Precursor Preparation**  
   - **Reagents**: List *all* primary chemicals (e.g., metal nitrates, ligands, supports) with exact amounts.  
   - **Conditions**: Temperatures, pH, stirring rates, equipment.  
   - **Process**: Step‐by‐step synthesis of each precursor.  
   - **If precursor preparation is not described in the paper, note: “Not reported.”**

2. **Catalyst Assembly**  
   - **Reagents**: Include precursors made above plus any additional chemicals.  
   - **Conditions**: Co‐precipitation, impregnation, pH, temperature, etc.  
   - **Process**: Bullet‐point steps, in chronological order.

3. **Purification**  
   - **Process**: Centrifugation, washing, filtration—include speeds, durations, solvents.

4. **Drying & Calcination**  
   - **Drying**: Temperature, time, oven type.  
   - **Calcination**: Ramp rate, final temperature, atmosphere.

5. **Activation (if any)**  
   - **Process**: e.g. reduction under H₂, flow rates, temperature program.

6. **Key Steps**, **Caution**, **Troubleshooting**, **Pause Points** as before.

**Workflow order must be strictly followed** so that nothing is skipped or assumed.

**Special Notes:**

- Avoid overly detailed steps that replicate the prompt content.
- Focus on capturing the essence of each catalyst preparation without unnecessary repetition.
- Each catalyst synthesis should be treated separately and follow a clear, logical flow from raw precursor preparation to final catalyst formation.

## 4. Characterization Methods

**Objective**
Extract detailed **characterization methods** and their **operating conditions** for analyzing **Fischer–Tropsch catalysts** as described in the article. For each technique below, pull out the **step‑by‑step procedure**, including **equipment used** (with brand/model if available), **operating conditions** (temperatures, pressures, gas flow rates, scan ranges, heating rates, etc.), and any **test parameters** specified:

- **Inductively Coupled Plasma (ICP)**
- **X‑ray Diffraction (XRD)**
- **H₂ Temperature‑Programmed Reduction (H₂‑TPR)**
- **CO Temperature‑Programmed Reduction (CO‑TPR)**
- **Diffuse Reflectance Infrared Fourier Transform Spectroscopy (DRIFTS)**
- **Fourier Transform Infrared Spectroscopy (FTIR)**
- **Transmission Electron Microscopy (TEM)** & **Energy Dispersive Spectroscopy (EDS)**
- **Scanning Electron Microscopy (SEM)**
- **X‑ray Photoelectron Spectroscopy (XPS)**
- **BET Surface Area Analysis**
- **Water‑droplet Contact Angle Measurements**
- **In‑situ Techniques** (e.g., in‑situ XRD, in‑situ FTIR)

---

**Content Requirements**
**1. Detect & Extract Only Reported Methods**

- **Characterization Techniques**:
  - Scan the article and identify every characterization technique that is explicitly described. Do not include any method that is not mentioned in the text. If the paper uses a method not in the original list, add it as a new section. If a method from the original list is not in the paper, omit it entirely.
  - Extract and summarize the purpose and step-by-step procedure for each identified characterization method. The characterization techniques could include, but are not limited to:
    - **Crystal Structure Analysis** (e.g., **X-ray Diffraction [XRD]**).
    - **Reduction Behavior Analysis** (e.g., **H₂ Temperature Programmed Reduction [H₂-TPR]**, **CO-TPR**).
    - **Surface Area and Porosity Analysis** (e.g., **BET Surface Area Analysis**).
    - **Microscopy Techniques** (e.g., **SEM**, **TEM**).
    - **Elemental Analysis** (e.g., **XPS**).
    - **In-situ Techniques** (e.g., **In-situ XPS**, **In-situ FTIR**, **In-situ DRIFT**, **In Situ Mössbauer Spectroscopy**).
    - **Other Methods** (e.g., **Raman Spectroscopy**, **FTIR**, **CO oxidation studies**).
  - **For each method**:
    - **Sample Preparation**: Note any specific procedures for preparing the catalyst or sample for characterization, such as pretreatment, sample mounting, etc.
    - **Instrument & Model**: Record the manufacturer and model number of the instrument, if available.
    - **Instrument Parameters**: Specify the specific settings for the instruments, including voltage, current, temperature, gas flow, etc.
    - **Characterization Conditions**: Identify any critical conditions like temperature, pressure, atmosphere (e.g., inert gas, vacuum), or radiation source.
    - **Test Parameters**: List the scan range, step size, heating/ramping rate, gas flow rate, exposure time, detector settings, or other parameters crucial for the accuracy of the test.
    - **Operational Procedure**: Present chronological bullet-points of how the measurement was performed.
    - **Purpose**: Explain the purpose of the method and how it contributes to understanding the catalyst properties.
    - **Key Notes**: Highlight any cautions, limitations, or special considerations mentioned. If applicable, summarize the scope and limitations of the methods as discussed in the article.

**2. Individual Sections**

- Each characterization method must have its own numbered heading (e.g., `### 4.3 XRD`). Never group multiple techniques under a single heading or paragraph.

**3. Sequential Order**

- Present methods in the exact order they appear in the article.

**4. Summary of Methods and Limitations**

- For each characterization method, summarize the purpose, instrument used, characterization conditions, and test parameters.
- If mentioned in the article, summarize the limitations and scope of application of the method (e.g., suitability for crystalline vs. amorphous materials, temperature ranges, specific applications, etc.).

---

**Output Structure**  
Ensure that the characterization methods are described in **sequential order** as per the article, each in its own clearly labeled section. The following structure should be followed:

- **4.1 [Method Name]** (e.g., XRD etc.)
  - **Operational Description**: [Extract description from the article.]  
  - **Instruments and Models**: [Extract instruments and models used.]  
  - **Characterization Conditions**: [Extract specific conditions like radiation source, temperature, pressure, gas flow, pressure, temperature, etc.]  
  - **Test Parameters**: [Extract step size, scanning rate, exposure time, test parameters like temperature ramping, time duration, etc.]  
  - **Key Notes**: [Any important observations or special conditions.]

- **4.2 [Method Name]**
<!-- Repeat for every method actually described in the article -->

---

**Usage Instructions for the Model**  

1. **Extract Specific Details**:  
   - Extract **exact experimental details** for each characterization method as described in the article.  
   - Ensure that all **techniques** are **clearly identified** and **relevant to Fischer-Tropsch catalyst characterization**.
2. **Group Similar Methods**:  
   - Group methods by type (e.g., XRD, TPR, microscopy, elemental analysis) and ensure that they are described in **sequential order** as per the article.
3. **Clear and Reproducible Descriptions**:  
   - Each method should be described **clearly and thoroughly** with **complete instrument details**, **test parameters**, and **operating conditions**.
4. **Summarize Limitations**:  
   - If limitations or specific applications are discussed for a given method, ensure that **limitations** and **scope** are summarized at the end of each characterization method section.
5. **Avoid Hypothetical Content**:  
   - Only extract information explicitly stated in the article. Do not introduce, infer, or add any details, methods, or parameters that are not present in the source text.
   - Do not introduce **hypothetical examples** or content that is not explicitly described in the article.
6. **Ensure Consistency and Completeness**:  
   - Ensure all characterization techniques are well-explained and that **every step** is fully detailed, providing complete experimental setups for replication.

---

**Example Output Format (Markdown)**

```markdown
    ## 4. Characterization Methods
    ### 4.1 [First Method Name as in paper e.g.: XRD]
    - **Operational Description**: XRD patterns were collected to determine the crystalline structure of the catalyst.
    - **Instruments and Models**: PANalytical X’pert-3 Powder diffractometer.
    - **Characterization Conditions**: Cu Kα radiation at 40 kV and 40 mA.
    - **Test Parameters**: Step size of 0.02°, scanning rate of 10°/min, 2θ range of 10°-80°.
    - **Key Notes**: Ensure that samples are properly aligned on the sample holder to avoid errors in diffraction.

    ### 4.2 [Second Method Name as in paper e.g.: H2-TPR]
    - **Operational Description**: The reduction behavior of the catalyst was analyzed using a micro fixed-bed reactor coupled with a thermal conductivity detector (TCD).
    - **Instruments and Models**: Micro fixed-bed reactor with TCD.
    - **Characterization Conditions**: 10% H2/Ar flow at 25 mL/min, temperature range from 100 to 800°C, ramping rate of 10°C/min.
    - **Test Parameters**: Sample pretreatment in pure Ar at 150°C for 2 hours to remove physically adsorbed moisture.
    - **Key Notes**: Ensure uniform catalyst loading and precise temperature control to avoid inaccuracies in reduction profiles.

    ...
```

## 5. Catalytic Evaluation Methods  

### 5.1 Activation  

- **Objective:**  
Generate a structured section detailing the catalyst activation process used in Fischer-Tropsch synthesis experiments. This section should include precise activation parameters such as temperature, pressure, gas composition, space-time velocity, and activation time.  

- **Content Requirements:**

1. **Strict Extraction from the Article:**
   - **All activation conditions must be sourced directly from the article.**
   - **Only extract activation steps related to catalyst synthesis or pre-reaction treatment.**  
     **Do not extract activation procedures that are part of characterization techniques (e.g., TPR, XPS).**
   - Do **not** generate missing data—only report explicitly provided values.
   - Ensure all reported activation steps are relevant to **Fischer-Tropsch catalysts.**

2. **Accurate Parameter Reporting:**  
   Each subsection should:  
   - **Define the parameter** and its role in catalyst activation (e.g., reduction or carbonization).  
   - **Report the exact experimental conditions** as described in the article.  
   - **Include relevant observations** regarding activation efficiency, catalyst stability, or performance impact.  

3. **Consistent Formatting and Units:**  
   - Use **standard scientific notation** for units (e.g., °C for temperature, MPa for pressure, mL/(gcat·h) for space-time velocity).  
   - Maintain clarity and structure for ease of interpretation.
  
4. **Exclude Activation in Characterization:**
   - Only include activation procedures performed as part of the catalyst synthesis or preparation for Fischer-Tropsch reaction.
   - Do **not** include activation steps mentioned in relation to characterization techniques (e.g., TPR, XPS).

- **Subsection Format Example (Markdown):**  

```markdown
    ### 5.1 Activation

    #### 5.1.1 Activation Temperature
    - **Definition:** Activation temperature plays a critical role in catalyst reduction or carbonization, ensuring the exposure of active sites.
    - **Experimental Conditions:** The catalyst was activated at 400 °C in a tube furnace under a controlled gas flow.
    - **Observations:** Higher activation temperatures led to increased metal dispersion but excessive heating caused sintering effects.

    #### 5.1.2 Activation Pressure
    - **Definition:** The pressure during activation influences gas interaction with the catalyst and affects reduction kinetics.
    - **Experimental Conditions:** The activation was carried out under atmospheric pressure (1 bar).
    - **Observations:** A higher pressure was found to enhance reduction efficiency, but excessive pressure led to catalyst agglomeration.

    #### 5.1.3 Activation Gas
    - **Definition:** The gas composition used during activation determines the extent of catalyst reduction and carburization.
    - **Experimental Conditions:** A mixture of 10% H₂/Ar was used for activation.
    - **Observations:** H₂-rich atmospheres facilitated metal reduction, while the presence of CO led to partial carbide formation.

    #### 5.1.4 Activation Space-Time Velocity
    - **Definition:** The space-time velocity (flow rate per unit catalyst weight) controls the exposure of catalyst particles to the activation gas.
    - **Experimental Conditions:** The activation gas was flowed at 5000 mL/(gcat·h).
    - **Observations:** A higher space-time velocity prevented over-reduction but insufficient flow led to incomplete activation.

    #### 5.1.5 Activation Time
    - **Definition:** Activation duration ensures complete catalyst transformation without excessive sintering.
    - **Experimental Conditions:** The catalyst was activated for 6 hours.
    - **Observations:** Prolonged activation times led to minor deactivation due to sintering effects.
```

- **Usage Instructions for the Model:**  

- **Strictly extract** all activation conditions from the article—**do not generate missing values.**  
- **Autonomously structure the section** based on the activation parameters reported in the article.  
- **Ensure clarity and reproducibility** so that researchers can replicate the activation process accurately.  
- **Avoid unrelated content**—only include activation conditions relevant to Fischer-Tropsch catalysts.  

### 5.2 Reaction

- **Objective:**  
Generate a structured section on the reaction conditions used in the Fischer-Tropsch catalytic evaluation. This section should present experimental parameters such as reaction temperature, pressure, H₂/CO ratio, and space-time velocity, ensuring clarity, reproducibility, and direct extraction from the article.  

- **Content Requirements:**  

1. **Strict Extraction from the Article:**  
   - **All values and conditions must be taken directly from the article.**  
   - Do **not** generate missing data—only report what is provided.  
   - Ensure all reported conditions are relevant to **Fischer-Tropsch synthesis.**  

2. **Accurate Parameter Reporting:**  
   Each subsection should:  
   - **Define the parameter** and its role in Fischer-Tropsch catalysis.  
   - **Report the exact experimental conditions** as described in the article.  
   - **Include relevant observations** regarding reaction stability, catalyst deactivation, or performance trends.  

3. **Consistent Formatting and Units:**  
   - Use **standard scientific notation** for units (e.g., °C for temperature, bar for pressure, mL/(gcat·h) for space-time velocity).  
   - Maintain clarity and structure so results are easily interpretable.  

- **Subsection Format Example (Markdown):**  

```markdown
    ### 5.2 Reaction

    #### 5.2.1 Reaction Temperature
    - **Definition:** The temperature at which the Fischer-Tropsch reaction occurs, influencing syngas activation and catalyst performance.
    - **Experimental Conditions:** The reactor temperature was maintained at 260 °C during the catalytic tests.
    - **Observations:** Catalyst stability was observed under this condition, with no significant deactivation over 50 hours of reaction.

    #### 5.2.2 Reaction Pressure
    - **Definition:** The total system pressure, affecting syngas concentration and product selectivity.
    - **Experimental Conditions:** The reaction was conducted at 10 bar in a fixed-bed reactor.
    - **Observations:** Higher pressure favored C₅+ hydrocarbon formation, aligning with previous studies on iron-based catalysts.

    #### 5.2.3 Reaction H₂/CO Ratio
    - **Definition:** The ratio of hydrogen to carbon monoxide in the feed gas, which influences hydrocarbon distribution.
    - **Experimental Conditions:** An H₂/CO ratio of 2.0 was used for all catalytic tests.
    - **Observations:** Increasing the H₂/CO ratio led to higher methane selectivity, while a lower ratio promoted olefin formation.

    #### 5.2.4 Reaction Space-Time Velocity
    - **Definition:** The ratio of syngas flow rate to catalyst mass, determining reactant exposure time.
    - **Experimental Conditions:** The gas hourly space velocity (GHSV) was set to 20,000 mL/(gcat·h).
    - **Observations:** A higher space-time velocity led to lower CO conversion but improved catalyst stability over time.
```

- **Usage Instructions for the Model:**  

- **Strictly extract** all experimental conditions from the article—**do not generate missing values.**  
- **Autonomously structure the section** based on the parameters reported in the article.  
- **Ensure clarity and reproducibility** so the conditions can be replicated in future experiments.  
- **Avoid unrelated information**—only include Fischer-Tropsch synthesis reaction conditions.  

## 6 Results

### 6.1 Characterization Results

**Objective:**  
Generate a structured "Characterization Results" section by extracting experimental data from the article. This section should comprehensively present the characterization findings, including physical and chemical properties such as crystal structure, elemental composition, surface area, porosity, and morphology. The model should **autonomously determine the appropriate subsections** based on the article’s data while ensuring that no unrelated content is introduced.

**Content Requirements:**

1. **Strict Extraction from the Article:**  
   - **All data and findings must come directly from the article.** The model should not generate or infer missing results.  
   - Ensure that only characterization results related to **Fischer-Tropsch catalysts** are included.

2. **Flexible Subsection Structure:**  
   - The model should **create appropriate subsections** (e.g., 6.1.1, 6.1.2) based on the available experimental results.  
   - Each subsection should cover a distinct characterization parameter (e.g., crystal phase, element valence, porosity).  
   - If the article provides additional characterization results beyond the suggested subsections, include them under new headings.

3. **Detailed Reporting of Each Parameter:**  
   Each subsection must include:  
   - **Description of the parameter** (e.g., how it is measured, its relevance to catalyst performance).  
   - **Experimental findings extracted from the article**, formatted clearly and with appropriate units.  
   - **Observations and trends** reported in the article, if applicable.

**Subsection Format Example (Markdown):**

```markdown
### 6.1 Characterization Results

#### 6.1.1 Crystal Phase and Structure
- **Description:** Crystal phase composition and transformations identified through XRD.
- **Findings:** XRD patterns indicate that Fe⁰ in the bare Fe catalyst is mainly transformed into Fe₅C₂ and Fe₃O₄ under syngas conditions.
- **Observations:** The presence of Fe₅C₂ suggests active carbide formation, which is known to enhance Fischer-Tropsch activity.

#### 6.1.2 Elemental Composition and Valence
- **Description:** Elemental composition and oxidation states determined by XPS.
- **Findings:** From XPS spectra, the Fe 2p3/2 peaks of s-Fe and s-FeM catalysts could be fitted with three peaks at 710.2-709.8 eV, 708.2–708.1 eV, and 707.0–706.6 eV, corresponding to Fe³⁺, Fe²⁺, and FeCx, respectively.
- **Observations:** The presence of FeCx indicates significant carburization, which is crucial for catalytic performance.

#### 6.1.3 Surface Area and Porosity
- **Description:** BET surface area, pore volume, and pore size distribution.
- **Findings:** BET analysis revealed a surface area of 85 m²/g, an average pore size of 3.2 nm, and a pore volume of 0.25 cm³/g.
- **Observations:** The relatively large pore volume suggests improved reactant diffusion, which can enhance catalytic efficiency.

#### 6.1.4 Morphology and Particle Size
- **Description:** Catalyst morphology and particle size distribution observed via SEM/TEM.
- **Findings:** SEM images showed spherical particles with an average crystallite size of 15 nm, as confirmed by Scherrer equation calculations from XRD data.
- **Observations:** The uniform particle size distribution suggests good control over catalyst synthesis conditions.
```

**Formatting Instructions:**

- **Headers:** Use "####" for each subsection header (e.g., 6.1.1, 6.1.2, etc.).
- **Descriptions and Findings:** Format the description and findings clearly, using bulleted lists if appropriate.
- **Units:** Always report numerical values with their respective units (e.g., m²/g, nm, cm³/g, eV).
- **Observations:** If trends or additional insights are provided in the article, include them after the findings section, preceded by "Observations."
- **Clarity:** Ensure that all extracted data is clearly separated and presented in a consistent, readable manner.

**Usage Instructions for the Model:**

- **Autonomy in Subdivision:** The model should create additional subsections if the article contains more detailed characterization results.
- **Strict Extraction from the Article:** All data and descriptions **must be taken directly** from the article—**do not generate information that is not explicitly stated.**
- **Clarity and Consistency:** Ensure numerical values, units, and terminology remain consistent across all subsections.
- **Avoid Redundant or Unrelated Details:** If a characterization method is **not** reported in the article, it should **not** be included in the output.

### 6.2 Catalyst Performance

**Objective:**  
Generate a structured "Catalyst Performance" section by extracting experimental results from the article. This section should report key performance indicators, including CO conversion, selectivity, chain growth factor (α factor), and catalyst stability. The model should autonomously determine the necessary subsections while ensuring all content is strictly based on the article.

**Content Requirements:**

1. **Relevance and Accuracy:**  
   - Extract all reported performance metrics and data from the article.  
   - Ensure consistency in units, definitions, and terminology.  

2. **Subsection Flexibility:**  
   - The model should generate subsections based on available performance parameters.  
   - If additional performance indicators exist in the article, include them as new subsections.  

3. **Comprehensive Data Extraction:**  
   - Each subsection should include:  
     - **Description of the Performance Metric:** Explanation and formula.  
     - **Experimental Data:** Extracted from the article (not just an example).  
     - **Key Observations and Trends:** Discussion of relevant findings.  

4. **Strictly No Hallucination:**  
   - Do not generate hypothetical results or introduce external data.  
   - Ensure all reported values, equations, and trends align with the article's content.  

---

**Proposed Flexible Format (Markdown)**

```markdown
### 6.2 Catalyst Performance

#### 6.2.1 CO Conversion
- **Description:** The ratio of CO molecules converted by the catalyst to the CO molecules in the reactant feed. Defined as:
  \[
  \text{CO Conversion} = \frac{F_{\text{CO,in}} - F_{\text{CO,out}}}{F_{\text{CO,in}}} \times 100
  \]
- **Experimental Data:** Extract all relevant CO conversion values reported in the article, including variations with different catalyst compositions or conditions.
- **Observations and Trends:** Discuss any trends or peak values, such as optimal metal ratios affecting CO conversion.

#### 6.2.2 CO₂ Selectivity
- **Description:** The proportion of converted CO molecules that form CO₂, indicating the extent of oxidation reactions. Defined as:
  \[
  \text{CO₂ Selectivity} = \frac{F_{\text{CO₂,out}}}{F_{\text{CO,in}} - F_{\text{CO,out}}} \times 100
  \]
- **Experimental Data:** Extract all reported CO₂ selectivity values, including catalyst-dependent variations.
- **Observations and Trends:** Analyze any catalyst-related effects on CO₂ formation.

#### 6.2.3 CH₄ Selectivity
- **Description:** The proportion of converted CO molecules that form CH₄, which affects hydrocarbon distribution. Defined as:
  \[
  \text{CH₄ Selectivity} = \frac{F_{\text{CH₄,out}}}{F_{\text{CO,in}} - F_{\text{CO,out}}} \times 100
  \]
- **Experimental Data:** Extract CH₄ selectivity results and their dependence on catalyst composition or reaction conditions.
- **Observations and Trends:** Highlight any significant differences in methane selectivity.

#### 6.2.4 C₃⁺ Selectivity
- **Description:** The fraction of converted CO that forms hydrocarbons with three or more carbon atoms. Defined as:
  \[
  \text{C₃⁺ Selectivity} = 100 - \frac{F_{\text{CO₂,out}} + F_{\text{CH₄,out}} + 2F_{\text{C₂H₂,out}} + 2F_{\text{C₂H₄,out}} + 2F_{\text{C₂H₆,out}}}{F_{\text{CO,in}} - F_{\text{CO,out}}} \times 100
  \]
- **Experimental Data:** Extract reported selectivity values for C₃⁺ hydrocarbons.
- **Observations and Trends:** Discuss trends in hydrocarbon distribution.

#### 6.2.5 α Factor (Chain Growth Factor)
- **Description:** The probability of hydrocarbon chain growth relative to termination, affecting product distribution. The α value ranges from 0 to 1, with higher values indicating greater selectivity toward long-chain hydrocarbons.
- **Experimental Data:** Extract reported α values from the article.
- **Observations and Trends:** Discuss how α values correlate with catalyst properties.

#### 6.2.6 Catalyst Deactivation Rate
- **Description:** A measure of reaction stability, defined as the rate at which CO conversion decreases over time. Expressed as:
  \[
  \text{Deactivation Rate} = \frac{\text{CO Conversion at initial stage} - \text{CO Conversion at final stage}}{\text{Overall reaction time}} \quad (\text{h}^{-1})
  \]
- **Experimental Data:** Extract all reported deactivation rate values.
- **Observations and Trends:** Analyze stability differences between catalysts.
```

**Formatting Instructions:**

- **Headers:** Use "####" for each subsection header (e.g., 6.2.1, 6.2.2, etc.).
- **Descriptions and Findings:** Format the description and findings clearly, using bulleted lists where appropriate.
- **Units and Definitions:** Always report numerical values with their respective units (e.g., % conversion, α factor values from 0 to 1, h⁻¹ for deactivation rate).
- **Equations:** Use LaTeX-style formatting for equations to ensure clarity.
- **Observations:** If trends or additional insights are provided in the article, include them after the findings section, preceded by "Observations."
- **Clarity:** Ensure that all extracted data is clearly separated and presented in a consistent, readable manner.

**Usage Instructions for the Model:**

- **Autonomy in Subsection Generation:**  
  - The model must structure subsections based on available performance data.  
  - If additional metrics are present in the article, generate new subsections accordingly.  

- **Strict Content Extraction:**  
  - **Extract full experimental results** rather than just providing an example.  
  - Maintain consistency with reported units and definitions.  

- **Clarity and Reproducibility:**  
  - Define all performance metrics clearly using standard formulas.  
  - Ensure accurate reporting of numerical values and trends.  

- **Avoid Unrelated Content:**  
  - Only include content directly derived from the article.  
  - Do not introduce hypothetical data or external sources.  
"""

# 加载费托合成的知识图谱生成提示词
allowed_rels=["description",
                "mention",
                "is_used_by","uses_material_from","consumes","produces","is_synthesized_from","is_synthesized_of",
                "is_mixed_with","is_dissolved_in","is_filtered_from","is_purification_of",
                "contains_chemical","is_contained_in","is_heated_in","is_cooled_in","is_stirred_in",
                "is_followed_by","precedes","is_part_of",
                "is_analyzed_by","is_characterized_by","is_characterization_of",
                "has_temperature","has_pressure","has_duration","has_concentration",
                "has_property","is_a","has_value"]
allowed_nodes=["description",
                "Equipment:Synthesis Equipment","Equipment:Characterization Equipment","Equipment:Purification and Drying Equipment","Equipment:Other",
                "Reagents:Solvents","Reagents:Base or Acid Regulators","Reagents:Gases","Reagents:Other",
                "Characterization Methods:Thermogravimetric analysis(TGA) ","Characterization Methods:X-ray diffraction(XRD)", "Characterization Method:temperature-programmed desorption of ammonia (NH3-TPD) ","Characterization Method:Fourier-transform infrared spectroscopy (FTIR)","Characterization Method:Scanning electron microscopy (SEM)","Characterization Method:Transmission electron microscopy (TEM)","Characterization Method:BET surface area analysis","Characterization Method:Ultraviolet-visible spectroscopy (UV-Vis)",
                "reaction:temperature","reaction:time","reaction:solvent","reaction:pressure","reaction:atmosphere","reaction:stirring rate","reaction:other",
                "Purification:filtration","Purification:Centrifugation","Purification:Washing","Purification:Column chromatography","Purification:Recrystallization","Purification:Distillation","Purification:Extraction","Purification:other",
                "Drying:temperature","Drying:time","Drying:atmosphere","Drying:other",
                "Documents"]
example = f"""# Knowledge Graph Instructions for GPT-4 (Fischer-Tropsch Synthesis Edition)

## 1. Overview  
You are designed to extract structured information for building a knowledge graph focused on Fischer-Tropsch synthesis experiments.  
- **Nodes**: Represent entities/concepts (e.g., catalysts, reaction conditions, products).  
- **Goal**: Keep the graph simple, focusing on catalyst development, reaction conditions, and product analysis.  

## 2. Node Labeling  
- **Consistency**: Use general labels (e.g., "catalyst" instead of "cobalt catalyst").  
- **Node IDs**: Use text-based identifiers (e.g., names from the text).  

## 3. Numerical Data and Dates  
- Include numerical values (e.g., temperature, pressure) as node attributes.  
- **Format**: Key-value pairs (e.g., `activationTemperature: 350`).  
- **Naming**: Use camel case (e.g., `activationTemperature`).  

## 4. Coreference Resolution  
- Maintain consistency for entities mentioned multiple times (e.g., use "Temperature-Programmed Reduction" consistently).  

## 5. Relationship Direction  
- Use active voice for clarity.  
- Ensure direction reflects interactions (e.g., "Tubular Furnace - REDUCES -> Catalyst").  

## 6. Strict Compliance  
Adhere strictly to rules; non-compliance will result in termination.  

## 7. Chemistry-Specific Rules  
- **Catalyst components**: Reflect hierarchy (active phase, promoter, support).  
- **Synthesis relationships**: Use labels like "is_synthesized_from" or "is_supported_on".  
- **Reaction conditions**: Connect equipment to parameters (e.g., "operates_under_Temperature").  
- **Performance metrics**: Use relationships like "exhibits_selectivity_for".  

## 8. Example  
- **Text**: A cobalt-based catalyst on silica was prepared via impregnation. The precursor was reduced in a tubular furnace at 350°C under hydrogen for 2 hours. The catalyst showed 65% C5+ selectivity and an alpha value of 0.85.  

- **Nodes**:  
  - "Cobalt-Based Catalyst" (type: catalyst, supportMaterial: "silica", preparationMethod: "impregnation")  
  - "Reduction Condition" (type: reaction condition, temperature: 350, gas: "hydrogen", duration: "2h")  
  - "C5+ Hydrocarbons" (type: product, carbonRange: "C5+")  

- **Relationships**:  
  - "Reduction Condition" - PRODUCES -> "Cobalt-Based Catalyst"  
  - "Cobalt-Based Catalyst" - EXHIBITS_SELECTIVITY_FOR -> "C5+ Hydrocarbons"  

This example demonstrates correct node and relationship extraction for catalyst preparation, activation, and performance evaluation."""


# 费托合成大提示词迁移
new_subject_template = graphllm.invoke(f"""# Prompt for Designing Experimental Template of Academic Papers

## 🎯 Task Objective

Please construct an experimental template framework for the **{subject}** theme based on the given requirements. The template will be used to extract experiment-related content from academic papers on this theme.

## 📌 Reference Instructions

You are provided with a **reference experimental template** as follows:
**{template}**

> ⚠️ **Strictly follow the structure of the reference template.**
>
> * **Do not** add or remove major sections (e.g., if the template has 6 top-level sections, your output must also contain 6 top-level sections with the same headings or structure).
> * You may flexibly adapt the content **within** each section to suit the new subject, but **the overall framework (headings and order)** must remain consistent.
> * Do not invent new modules or delete existing ones.

## ✅ Core Requirements

1. **Thematic Adaptation**: Ensure the content reflects the experimental characteristics of the **{subject}** domain (e.g., experimental samples, core variables, standard methods, etc.).
2. **Reference Structure Compliance**: The **structure and hierarchy** must fully align with the provided reference template. This includes:

   * Number and names of sections (unless minor renaming is required to suit the subject).
   * Logical ordering of sections.
   * Presence of key content categories (e.g., objective, materials, procedure, evaluation).
3. **Content Refinement**: Remove domain-specific terms from the reference example that do not apply to **{subject}**.
4. **Field-specific Integration**: Replace or extend content where necessary to reflect the unique experimental needs of **{subject}**, such as:

   * Specialized preprocessing or data collection.
   * Field-specific evaluation criteria.
   * Typical experimental platforms or models used in this domain.

## 📤 Expected Output

Return only the **experimental template framework for {subject}**, using the **same structure and granularity** as the reference template. Content can be rewritten or replaced, but **no structural deviation** is allowed.""").content
# print(new_subject_template)
import re
new_subject_template = re.sub(r'^```markdown(.*?)```$', r'\1', new_subject_template, flags=re.DOTALL)
with open(subject_template_file, "w", encoding="utf-8") as f:
    f.write(new_subject_template)
# import pdb;pdb.set_trace()
# 费托合成知识图谱节点、关系提示词迁移
new_subject_nodes_rels = graphllm.invoke(f"""# Structured Prompt for Knowledge Graph Node and Relationship Generation
To construct an accurate and comprehensive knowledge graph, please assist in completing the following tasks.

## Subject
Please generate nodes and relationships of the knowledge graph around {subject}.

## Node Requirements
1. Node types include equipment, reactants, characterization methods, reaction conditions, etc. Please supplement various node types based on the characteristics of the subject and generate nodes reasonably.
2. Nodes should have clear meanings and accurately represent subject-related entities, concepts, etc.
3. Node format: [Node Type]:[Node Name].

## Relationship Requirements
1. Relationship types include reactant-related relationships, reaction condition relationships, product-performance relationships, mechanism relationships, process flow relationships, characterization relationships, etc. Please reasonably construct relationships based on the generated nodes.
2. Relationships should accurately describe the connections between nodes.
3. Relationship format: [Relationship Type].

## Reference Examples
Node examples: {", ".join(allowed_nodes)}
Relationship examples: {", ".join(allowed_rels)}

## Output Requirements
1. Output only two parts: node list and relationship list. Do not add any explanations, notes, text or formats other than titles.
2. The node list is presented separately, listed in sequence according to the "Node Type: Node Name" format, with each node separated by a comma.
3. The relationship list is presented separately, listed in sequence according to the "Relationship Type" format, with each relationship separated by a comma.
4. The node list and relationship list are completely separated and must not be presented in a mixed manner or nested within each other.""").content
# print(new_subject_nodes_rels)
# 费托合成知识图谱生成提示词迁移
new_subject_kg_prompt = graphllm.invoke(f"""# Prompt: Generate New Subject Knowledge Graph Instructions Based on Example Migration  
## Core Task  
Based on the "existing knowledge graph generation example", customize an exclusive knowledge graph generation instruction for the new subject {subject}, ensuring it can accurately guide large models to extract nodes, relationships, and attributes.  


## Basic Inputs  
1. New Subject: {subject} (specific subject to be supplemented)  
2. Reference Example: {example} (the "Fischer-Tropsch Synthesis Knowledge Graph Instruction" as a structural template)  
3. New Subject Core Elements: {new_subject_nodes_rels} (exclusive node and relationship examples for the subject, which must be fully retained and applied)  


## Example Analysis Requirements  
Analyze the logic of the example to clarify the migration framework and content to be replaced:  
1. Fixed Structure: Adopt the 8 core modules of the example (Overview, Node Labeling, Data Processing Rules, Coreference Resolution, Relationship Direction, Compliance Requirements, Domain-Specific Rules, Example).  
2. Domain Replacement: Replace original domain terms in the example (e.g., "Fischer-Tropsch synthesis", "catalyst") with core entities of the new subject (e.g., materials, parameters, processes).  
3. Logic Retention: Reuse general frameworks such as node labeling and relationship direction rules, adapting them to the characteristics of the new subject.  


## Migration Generation Rules  
### 1. Structure Retention Principle  
Fully retain the 8 modules, with titles exactly consistent with the example (e.g., "1. Overview", "2. Node Labeling"). No addition, deletion, or modification of module names is allowed.  

### 2. Domain Content Replacement  
- Core Terms: Replace with exclusive entities of the new subject {subject} (e.g., for "photovoltaic cell research", replace with "photovoltaic materials", "conversion efficiency").  
- Element Adaptation: Node/relationship types and attribute names must match the professional terminology of the new subject (e.g., chemistry → biology/materials domain terminology).  

### 3. Rule Adaptation Requirements  
- Domain Rules: The "Domain-Specific Rules" module must align with the core logic of the new subject {subject} (e.g., chemical reaction logic → material preparation/biological experiment logic).  
- Data Indicators: "Numerical Data Rules" must adapt to key indicators of the new subject (e.g., temperature → voltage/concentration).  

### 4. Example Update Requirements  
Generate a scenario-based example for the new subject, including: ① text description; ② node list with attributes; ③ entity relationship list. The example must be concise, highlight core relationships, and contain no residual content from the original domain.  


## Core Element Application Requirements  
{new_subject_nodes_rels} must be fully retained and embedded in the "2. Node Labeling" section of the new instruction as standard examples of node/relationship types.  


## Word Count Restrictions  
- The overall instruction should avoid verbosity, focusing on core rules.  
- Section 8 "Example" must be concise, control word count, avoid complex scenario descriptions, and ensure the sample is clear and easy to understand.  


## Output Acceptance Criteria  
1. Module titles are consistent with the example, with all 8 core modules intact;  
2. Terminology, rules, and examples are highly relevant to the new subject {subject}, with no residual content from the original domain;  
3. Logically consistent, able to directly guide large models to extract nodes and relationships.  


Please combine {subject}, {example}, and {new_subject_nodes_rels} to generate the new subject knowledge graph instruction in accordance with the above requirements.""").content
print(new_subject_kg_prompt)
import pdb;pdb.set_trace()
new_subject_kg_prompt = re.sub(r'^```markdown(.*?)```$', r'\1', new_subject_kg_prompt, flags=re.DOTALL)
with open(subject_kg_prompt_file, "w", encoding="utf-8") as f:
    f.write(new_subject_kg_prompt)

APPLICATION_PROMPTS = json.load(open("question_and_other.json", "r"))['application_prompts']
example_dict = ["reagents_questions",
                "specific_equipment_questions",
                "common_equipment_questions",
                "synthesis_method_questions",
                "reagents_preparation_questions",
                "detailed_steps_questions",
                "characterization_questions",
                "activation_questions",
                "reaction_questions",
                "characterization_results_questions",
                "catalyst_performance_questions"]
# 迁移示例问题
for template_num in range(0, 11):
    origin_question_example = APPLICATION_PROMPTS["decompose_prompts"][example_dict[template_num]]
    new_subject_question_example = graphllm.invoke(f"""# Prompt: Generate New Subject Questions by Migrating Examples  
## Task Objective  
Based on the provided question example structure and guiding logic, generate questions focusing on core elements for the new subject {subject}. Strictly migrate the opening guidance format and content framework of the example, ensuring the number of questions is 5-6.  


## Reference Example and Logical Analysis  
Reference Example: {origin_question_example}  
Analysis of the example’s core structure and logic:  
1. **Fixed Guidance Format**: Begin with "Please tend to ask how many [core elements] there are in the entire text, and what [relevant details] are required for each of them. Please note that the questions you generate are actually used as input for other large language models. You should try your best to ensure the integrity and accuracy of the questions and avoid any ambiguous content." to clarify the focus direction of the questions.  
2. **Question Focus**: Centered on the subject’s core elements (e.g., "catalysts"), covering dimensions such as quantity, specific details (steps, conditions, etc.), and key information extraction.  
3. **Expression Standards**: Questions start with clear guiding words (e.g., "What..."), with specific and unambiguous content, suitable for input into large language models.  


## Generation Rules  
1. **Guidance Migration**: Retain the fixed format of the example’s opening guidance, only replacing "[core elements]" with the core entity of the new subject {subject} (e.g., replacing "catalysts" in the original example with core objects of the new subject such as "materials" or "devices"), and "[relevant details]" with key detail types of the new subject (e.g., "properties" or "operation steps").  
2. **Focus on Core Elements**: Questions must revolve around the core entity of the new subject {subject}, covering its quantity and specific details of each entity (e.g., characteristics, steps, conditions, results, etc.).  
3. **Format Imitation**: Questions start with clear guiding words (e.g., "What [element name]..."), consistent with the sentence style of the example.  
4. **Quantity and Quality Control**: Generate 5-6 questions covering key information dimensions of the new subject; content must be complete and accurate, with no ambiguous expressions, ensuring it can be directly used as input for other large language models.  


Please combine the new subject {subject} to generate questions according to the above requirements, ensuring the opening guidance format is consistent with the example and the questions focus on the core elements of the new subject.""").content
    # print(new_subject_question_example)
    APPLICATION_PROMPTS["decompose_prompts"][example_dict[template_num]] = new_subject_question_example
    # break

new_subject_summary = graphllm.invoke(f"""# Prompt: Generate Abstract Extraction Prompt for New Subject  
## Task Objective  
Based on the provided example of the "Fischer-Tropsch Catalyst Abstract Extraction Prompt", generate a structured abstract extraction prompt adapted to the new subject {subject}. The framework logic of the original example must be retained, with only domain-specific content replaced, ensuring the prompt can guide large language models to accurately extract core information of the new subject.  

## Example Content  
{APPLICATION_PROMPTS["decompose_prompts"]['ft_summary_generation_simplified']}  

## Analysis of Example Structure  
The original example contains the following core modules, whose framework must be fully retained:  
1. **Task Title**: Clearly define the abstract extraction task for the subject;  
2. **Goal**: Specify the focus direction and core dimensions of the summary;  
3. **Extraction Dimensions**: List key information to be extracted in modules (e.g., reagents, equipment, methods, etc.);  
4. **Formatting Rules**: Stipulate the structured format for summary output;  
5. **Guidelines**: Clarify requirements for factuality, accuracy, etc.  


## Generation Rules  
1. **Subject Replacement**: Replace domain terminology related to "Fischer–Tropsch catalysts" in the original example with core entities of the new subject {subject} (e.g., if the new subject is "lithium battery electrode materials", the core entity is "electrode materials").  

2. **Extraction Dimension Adaptation**:  
   - Replace "Reagents and Materials" with core material/reagent elements of the new subject (e.g., "electrode material precursors, electrolyte materials");  
   - Replace "Equipment and Instruments" with specialized equipment for the new subject (e.g., "electrochemical workstations, coating machines");  
   - Replace "Catalyst Synthesis" with preparation/synthesis methods of the new subject (e.g., "electrode material preparation processes");  
   - Replace "Performance and Stability" with performance metrics of the new subject (e.g., "cycle life, specific capacity");  
   - Replace "Characterization Results" with characterization dimensions of the new subject (e.g., "electrochemical performance testing, microstructure characterization").  

3. **Retention of Format and Guidelines**: Retain the framework of formatting rules (e.g., structured output templates) and guideline requirements (factuality, accuracy, etc.) from the original example, with only subject-related expressions adjusted.  


## Output Requirements  
The generated prompt must include:  
- A task title centered on 「{subject} Summary Extraction」;  
- Extraction goals focusing on the core dimensions of {subject};  
- A module-based extraction checklist (corresponding to the 5 extraction sections of the original example, with terminology adapted to the new subject);  
- A structured formatting rule template (with domain-related placeholders replaced);  
- Retention of the original guidelines' requirements for accuracy and factuality.  


Please generate the corresponding abstract extraction prompt based on the above rules and in combination with the new subject {subject}.""").content
# print(new_subject_summary)
APPLICATION_PROMPTS["decompose_prompts"]['ft_summary_generation_simplified'] = new_subject_summary
APPLICATION_PROMPTS["decompose_prompts"]['content_filter'] = "Please remove any content such as author information, references, hyperlinks, and other elements unrelated to the main text while retaining the original input text as much as possible. For example:\n\nOriginal Text:\n\n### **Data availability**\n\nThe main data discussed in this protocol are available in the supporting primary research papers or from the corresponding author on request.\n\nReceived: 17 October 2023; Accepted: 25 September 2024; Published online: xx xx xxx\n\n\n###\n**References**\n- <span id=\"page-13-0\"></span>1. Ma, W. et al. Chiral inorganic nanostructures. *Chem. Rev.* **117**, 8041–8093 (2017).\n- 2. Ahn, H.-Y. et al. Bioinspired toolkit based on intermolecular encoder toward evolutionary\n\n**Acknowledgements**\n\nThis work was supported by the Nano & Material Technology Development Program through the National Research Foundation of Korea (NRF) funded by the Ministry of Science and ICT and the Defense Challengeable Future Technology Program of the Agency for Defense Development, Republic of Korea. K.T.N. appreciates support from the Institute of Engineering Research, Research Institute of Advanced Materials (RIAM), and Soft Foundry at Seoul National University.\n **Author contributions**\n\nS.W.I. and R.M.K. wrote the manuscript with contributions from all authors. J.H.H. and I.H.H. conducted experiments. H.-E.L. and H.-Y.A developed the protocol. K.T.N. guided all aspects of the work.\n **Competing interests**\n\nThe authors declare no competing interests.\n **Additional information**\n\n**Supplementary information** The online version contains supplementary material available.\n\n**Correspondence and requests for materials** should be addressed.\n\n**Peer review information** thanks the contributors for their contribution to the peer review of this work.\n\n**Reprints and permissions information** is available.\n\n**Publisher's note** remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.Filtered Text:\n\n### **Data availability**\n\nThe main data discussed in this protocol are available in the supporting primary research papers or from the corresponding author on request. \n\nNote that only the filtered content should be output. The text to be filtered is as follows: \n\n<CONTENT>\n\n{content}\n\n</CONTENT>\nFiltered Text:"
APPLICATION_PROMPTS = {"application_prompts":APPLICATION_PROMPTS}
json.dump(APPLICATION_PROMPTS, open(prompts_config_file, "w"), ensure_ascii=False, indent=2)

