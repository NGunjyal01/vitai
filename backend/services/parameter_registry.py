"""
VitaI Health Platform — Complete Parameter Registry

Contains all 85+ blood test parameters across 14 panels with:
- Display names and aliases (200+ alternate names)
- Reference ranges (default, male, female, fitness-adjusted)
- Score weights and categories for health scoring
- Clinical context for embedding enrichment
- Helper functions for normalization, classification, and scoring
"""

from typing import Optional

# ---------------------------------------------------------------------------
# PARAMETER REGISTRY
# ---------------------------------------------------------------------------

PARAMETER_REGISTRY: dict = {
    # -----------------------------------------------------------------------
    # 1. CBC Panel (18 parameters)
    # -----------------------------------------------------------------------
    "hemoglobin": {
        "name": "Hemoglobin",
        "aliases": ["hb", "hgb", "haemoglobin", "hb%", "hemoglobin (hb)"],
        "unit": "g/dL",
        "ranges": {
            "default": {"low": 12.0, "high": 17.5},
            "male": {"low": 13.5, "high": 17.5},
            "female": {"low": 12.0, "high": 15.5},
            "fitness": {"low": 14.0, "high": 18.0},
        },
        "category": "blood_health",
        "score_weight": 10,
        "clinical_context": "Oxygen-carrying protein in red blood cells; low levels indicate anemia.",
        "fitness_note": "Endurance athletes may have slightly lower Hb due to plasma volume expansion (sports anemia).",
    },
    "rbc": {
        "name": "Red Blood Cell Count",
        "aliases": ["rbc count", "erythrocyte count", "red cell count", "total rbc", "rbc (red blood cells)"],
        "unit": "million/uL",
        "ranges": {
            "default": {"low": 4.0, "high": 6.0},
            "male": {"low": 4.5, "high": 6.0},
            "female": {"low": 4.0, "high": 5.5},
        },
        "category": "blood_health",
        "score_weight": 7,
        "clinical_context": "Total number of red blood cells per unit volume; reflects oxygen transport capacity.",
    },
    "wbc": {
        "name": "White Blood Cell Count",
        "aliases": [
            "tlc", "total leucocyte count", "total leukocyte count", "wbc count",
            "white cell count", "leucocyte count", "leukocyte count", "wbc (tlc)",
            "tc (wbc)", "total wbc count",
        ],
        "unit": "cells/uL",
        "ranges": {
            "default": {"low": 4000.0, "high": 11000.0},
            "male": {"low": 4000.0, "high": 11000.0},
            "female": {"low": 4000.0, "high": 11000.0},
        },
        "category": "blood_health",
        "score_weight": 8,
        "clinical_context": "Total white blood cells indicating immune system activity; elevated in infection or inflammation.",
    },
    "platelets": {
        "name": "Platelet Count",
        "aliases": ["plt", "platelet count", "thrombocyte count", "thrombocytes", "plt count"],
        "unit": "lakh/uL",
        "ranges": {
            "default": {"low": 1.5, "high": 4.0},
            "male": {"low": 1.5, "high": 4.0},
            "female": {"low": 1.5, "high": 4.0},
        },
        "category": "blood_health",
        "score_weight": 7,
        "clinical_context": "Cell fragments essential for blood clotting; abnormal counts indicate bleeding or clotting disorders.",
    },
    "pcv": {
        "name": "PCV / Hematocrit",
        "aliases": [
            "hematocrit", "hct", "packed cell volume", "pcv (hematocrit)",
            "haematocrit", "pcv/hematocrit",
        ],
        "unit": "%",
        "ranges": {
            "default": {"low": 36.0, "high": 54.0},
            "male": {"low": 40.0, "high": 54.0},
            "female": {"low": 36.0, "high": 48.0},
        },
        "category": "blood_health",
        "score_weight": 6,
        "clinical_context": "Percentage of blood volume occupied by red blood cells; reflects hydration and erythropoiesis.",
    },
    "mcv": {
        "name": "Mean Corpuscular Volume",
        "aliases": ["mcv", "mean cell volume", "mean corpuscular vol"],
        "unit": "fL",
        "ranges": {
            "default": {"low": 80.0, "high": 100.0},
            "male": {"low": 80.0, "high": 100.0},
            "female": {"low": 80.0, "high": 100.0},
        },
        "category": "blood_health",
        "score_weight": 5,
        "clinical_context": "Average volume of a single red blood cell; helps classify anemia as microcytic or macrocytic.",
    },
    "mch": {
        "name": "Mean Corpuscular Hemoglobin",
        "aliases": ["mch", "mean cell hemoglobin", "mean cell hb"],
        "unit": "pg",
        "ranges": {
            "default": {"low": 27.0, "high": 33.0},
            "male": {"low": 27.0, "high": 33.0},
            "female": {"low": 27.0, "high": 33.0},
        },
        "category": "blood_health",
        "score_weight": 4,
        "clinical_context": "Average amount of hemoglobin per red blood cell; low values suggest iron deficiency.",
    },
    "mchc": {
        "name": "Mean Corpuscular Hemoglobin Concentration",
        "aliases": ["mchc", "mean cell hb concentration", "mean corpuscular hb conc"],
        "unit": "g/dL",
        "ranges": {
            "default": {"low": 32.0, "high": 36.0},
            "male": {"low": 32.0, "high": 36.0},
            "female": {"low": 32.0, "high": 36.0},
        },
        "category": "blood_health",
        "score_weight": 4,
        "clinical_context": "Average concentration of hemoglobin in red blood cells; elevated in hereditary spherocytosis.",
    },
    "rdw": {
        "name": "Red Cell Distribution Width",
        "aliases": ["rdw", "rdw-cv", "rdw cv", "red cell distribution width", "rdw-sd"],
        "unit": "%",
        "ranges": {
            "default": {"low": 11.5, "high": 15.5},
            "male": {"low": 11.5, "high": 15.5},
            "female": {"low": 11.5, "high": 15.5},
        },
        "category": "blood_health",
        "score_weight": 4,
        "clinical_context": "Measures variation in red blood cell size; elevated in mixed or early nutritional anemias.",
    },
    "neutrophils": {
        "name": "Neutrophils",
        "aliases": [
            "neutrophil", "neutrophils %", "neutrophil %", "neutrophils percentage",
            "segmented neutrophils", "polymorphs", "poly",
        ],
        "unit": "%",
        "ranges": {
            "default": {"low": 40.0, "high": 70.0},
            "male": {"low": 40.0, "high": 70.0},
            "female": {"low": 40.0, "high": 70.0},
        },
        "category": "blood_health",
        "score_weight": 5,
        "clinical_context": "Most abundant white blood cell type; elevated in bacterial infections.",
    },
    "lymphocytes": {
        "name": "Lymphocytes",
        "aliases": [
            "lymphocyte", "lymphocytes %", "lymphocyte %", "lymph %",
            "lymphocytes percentage",
        ],
        "unit": "%",
        "ranges": {
            "default": {"low": 20.0, "high": 40.0},
            "male": {"low": 20.0, "high": 40.0},
            "female": {"low": 20.0, "high": 40.0},
        },
        "category": "blood_health",
        "score_weight": 5,
        "clinical_context": "Immune cells responsible for adaptive immunity; elevated in viral infections.",
    },
    "monocytes": {
        "name": "Monocytes",
        "aliases": ["monocyte", "monocytes %", "monocyte %", "monocytes percentage", "mono %"],
        "unit": "%",
        "ranges": {
            "default": {"low": 2.0, "high": 10.0},
            "male": {"low": 2.0, "high": 10.0},
            "female": {"low": 2.0, "high": 10.0},
        },
        "category": "blood_health",
        "score_weight": 3,
        "clinical_context": "Large white blood cells that become macrophages; elevated in chronic infections.",
    },
    "eosinophils": {
        "name": "Eosinophils",
        "aliases": [
            "eosinophil", "eosinophils %", "eosinophil %", "eosinophils percentage",
            "eosino %",
        ],
        "unit": "%",
        "ranges": {
            "default": {"low": 1.0, "high": 6.0},
            "male": {"low": 1.0, "high": 6.0},
            "female": {"low": 1.0, "high": 6.0},
        },
        "category": "blood_health",
        "score_weight": 3,
        "clinical_context": "White blood cells involved in allergic responses and parasitic defense; elevated in allergies.",
    },
    "basophils": {
        "name": "Basophils",
        "aliases": ["basophil", "basophils %", "basophil %", "basophils percentage", "baso %"],
        "unit": "%",
        "ranges": {
            "default": {"low": 0.0, "high": 2.0},
            "male": {"low": 0.0, "high": 2.0},
            "female": {"low": 0.0, "high": 2.0},
        },
        "category": "blood_health",
        "score_weight": 2,
        "clinical_context": "Least common white blood cell; involved in histamine release and allergic inflammation.",
    },
    "esr": {
        "name": "Erythrocyte Sedimentation Rate",
        "aliases": ["esr", "sed rate", "sedimentation rate", "westergren esr", "esr (westergren)"],
        "unit": "mm/hr",
        "ranges": {
            "default": {"low": 0.0, "high": 20.0},
            "male": {"low": 0.0, "high": 15.0},
            "female": {"low": 0.0, "high": 20.0},
        },
        "category": "inflammation",
        "score_weight": 5,
        "clinical_context": "Non-specific marker of inflammation; elevated in infections, autoimmune diseases, and malignancies.",
    },
    "mpv": {
        "name": "Mean Platelet Volume",
        "aliases": ["mpv", "mean platelet vol"],
        "unit": "fL",
        "ranges": {
            "default": {"low": 7.5, "high": 12.5},
            "male": {"low": 7.5, "high": 12.5},
            "female": {"low": 7.5, "high": 12.5},
        },
        "category": "blood_health",
        "score_weight": 3,
        "clinical_context": "Average size of platelets; larger platelets are more reactive and may indicate active thrombopoiesis.",
    },
    "pdw": {
        "name": "Platelet Distribution Width",
        "aliases": ["pdw", "platelet distribution width"],
        "unit": "%",
        "ranges": {
            "default": {"low": 9.0, "high": 17.0},
            "male": {"low": 9.0, "high": 17.0},
            "female": {"low": 9.0, "high": 17.0},
        },
        "category": "blood_health",
        "score_weight": 2,
        "clinical_context": "Measures variation in platelet size; elevated in reactive thrombocytosis.",
    },
    "pct": {
        "name": "Plateletcrit",
        "aliases": ["pct", "plateletcrit", "platelet crit"],
        "unit": "%",
        "ranges": {
            "default": {"low": 0.15, "high": 0.40},
            "male": {"low": 0.15, "high": 0.40},
            "female": {"low": 0.15, "high": 0.40},
        },
        "category": "blood_health",
        "score_weight": 2,
        "clinical_context": "Percentage of blood volume occupied by platelets; analogous to hematocrit for platelets.",
    },

    # -----------------------------------------------------------------------
    # 2. Diabetes / Glycemic Panel (5 parameters)
    # -----------------------------------------------------------------------
    "hba1c": {
        "name": "HbA1c",
        "aliases": [
            "glycated hemoglobin", "glycosylated hemoglobin", "a1c", "hb a1c",
            "hba1c %", "glycated hb", "hemoglobin a1c",
        ],
        "unit": "%",
        "ranges": {
            "default": {"low": 4.0, "high": 5.6},
            "male": {"low": 4.0, "high": 5.6},
            "female": {"low": 4.0, "high": 5.6},
            "fitness": {"low": 4.0, "high": 5.3},
        },
        "category": "metabolic_health",
        "score_weight": 10,
        "clinical_context": "Reflects average blood sugar over 2-3 months; primary marker for diabetes diagnosis and control.",
        "fitness_note": "Optimal for metabolic performance is below 5.3%.",
    },
    "fasting_glucose": {
        "name": "Fasting Blood Glucose",
        "aliases": [
            "fasting glucose", "fbg", "fbs", "fasting blood sugar",
            "fasting plasma glucose", "fpg", "glucose fasting",
            "blood sugar fasting", "glucose (fasting)",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 70.0, "high": 100.0},
            "male": {"low": 70.0, "high": 100.0},
            "female": {"low": 70.0, "high": 100.0},
            "fitness": {"low": 72.0, "high": 90.0},
        },
        "category": "metabolic_health",
        "score_weight": 9,
        "clinical_context": "Blood sugar level after overnight fasting; elevated values indicate impaired glucose metabolism.",
        "fitness_note": "Optimal fasting glucose for athletic performance is 72-90 mg/dL.",
    },
    "pp_glucose": {
        "name": "Post-Prandial Glucose",
        "aliases": [
            "ppbs", "pp glucose", "post prandial blood sugar", "pp blood sugar",
            "glucose pp", "2 hour pp glucose", "ppg", "glucose (pp)",
            "post prandial glucose", "blood sugar pp",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 70.0, "high": 140.0},
            "male": {"low": 70.0, "high": 140.0},
            "female": {"low": 70.0, "high": 140.0},
            "fitness": {"low": 70.0, "high": 120.0},
        },
        "category": "metabolic_health",
        "score_weight": 7,
        "clinical_context": "Blood sugar measured 2 hours after a meal; indicates how well the body handles glucose post-eating.",
    },
    "fasting_insulin": {
        "name": "Fasting Insulin",
        "aliases": [
            "insulin fasting", "fasting serum insulin", "insulin (fasting)",
            "serum insulin", "insulin level",
        ],
        "unit": "uIU/mL",
        "ranges": {
            "default": {"low": 2.0, "high": 25.0},
            "male": {"low": 2.0, "high": 25.0},
            "female": {"low": 2.0, "high": 25.0},
            "fitness": {"low": 2.0, "high": 10.0},
        },
        "category": "metabolic_health",
        "score_weight": 8,
        "clinical_context": "Insulin level after fasting; elevated values indicate insulin resistance even before glucose rises.",
        "fitness_note": "Optimal insulin sensitivity is indicated by fasting insulin below 10 uIU/mL.",
    },
    "homa_ir": {
        "name": "HOMA-IR",
        "aliases": [
            "homa ir", "homa-ir index", "homeostatic model assessment",
            "insulin resistance index", "homa index",
        ],
        "unit": "",
        "ranges": {
            "default": {"low": 0.0, "high": 2.0},
            "male": {"low": 0.0, "high": 2.0},
            "female": {"low": 0.0, "high": 2.0},
            "fitness": {"low": 0.0, "high": 1.5},
        },
        "category": "metabolic_health",
        "score_weight": 8,
        "clinical_context": "Calculated index of insulin resistance from fasting glucose and insulin; higher values indicate greater resistance.",
        "fitness_note": "Optimal HOMA-IR for athletes is below 1.5.",
    },

    # -----------------------------------------------------------------------
    # 3. Lipid Panel (7 parameters)
    # -----------------------------------------------------------------------
    "total_cholesterol": {
        "name": "Total Cholesterol",
        "aliases": [
            "cholesterol total", "tc", "total chol", "serum cholesterol",
            "cholesterol", "cholesterol (total)",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 125.0, "high": 200.0},
            "male": {"low": 125.0, "high": 200.0},
            "female": {"low": 125.0, "high": 200.0},
        },
        "category": "heart_health",
        "score_weight": 7,
        "clinical_context": "Sum of all cholesterol fractions; elevated levels increase cardiovascular disease risk.",
    },
    "ldl": {
        "name": "LDL Cholesterol",
        "aliases": [
            "ldl", "ldl-c", "ldl cholesterol", "low density lipoprotein",
            "ldl direct", "ldl-cholesterol", "bad cholesterol",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 0.0, "high": 100.0},
            "male": {"low": 0.0, "high": 100.0},
            "female": {"low": 0.0, "high": 100.0},
            "fitness": {"low": 0.0, "high": 90.0},
        },
        "category": "heart_health",
        "score_weight": 9,
        "clinical_context": "Primary atherogenic lipoprotein; elevated LDL drives plaque formation in arteries.",
        "fitness_note": "Strength athletes may have mildly elevated LDL from high protein diets; context matters.",
    },
    "hdl": {
        "name": "HDL Cholesterol",
        "aliases": [
            "hdl", "hdl-c", "hdl cholesterol", "high density lipoprotein",
            "hdl-cholesterol", "good cholesterol",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 40.0, "high": 100.0},
            "male": {"low": 40.0, "high": 80.0},
            "female": {"low": 50.0, "high": 100.0},
            "fitness": {"low": 50.0, "high": 100.0},
        },
        "category": "heart_health",
        "score_weight": 8,
        "clinical_context": "Protective lipoprotein that removes cholesterol from arteries; higher levels are cardioprotective.",
        "fitness_note": "Regular exercise significantly raises HDL; levels above 60 mg/dL are considered protective.",
    },
    "triglycerides": {
        "name": "Triglycerides",
        "aliases": [
            "tg", "trigs", "triglyceride", "serum triglycerides",
            "triglycerides (tg)", "tri glycerides",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 0.0, "high": 150.0},
            "male": {"low": 0.0, "high": 150.0},
            "female": {"low": 0.0, "high": 150.0},
            "fitness": {"low": 0.0, "high": 100.0},
        },
        "category": "heart_health",
        "score_weight": 8,
        "clinical_context": "Blood fats linked to metabolic syndrome; elevated by refined carbs, alcohol, and insulin resistance.",
        "fitness_note": "Optimal triglycerides for metabolic fitness are below 100 mg/dL.",
    },
    "vldl": {
        "name": "VLDL Cholesterol",
        "aliases": [
            "vldl", "vldl-c", "very low density lipoprotein", "vldl cholesterol",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 5.0, "high": 40.0},
            "male": {"low": 5.0, "high": 40.0},
            "female": {"low": 5.0, "high": 40.0},
        },
        "category": "heart_health",
        "score_weight": 5,
        "clinical_context": "Triglyceride-rich lipoprotein; elevated VLDL contributes to atherosclerosis.",
    },
    "tc_hdl_ratio": {
        "name": "TC/HDL Ratio",
        "aliases": [
            "total cholesterol/hdl ratio", "cholesterol ratio", "tc/hdl",
            "chol/hdl ratio", "cholesterol hdl ratio",
        ],
        "unit": "",
        "ranges": {
            "default": {"low": 0.0, "high": 4.5},
            "male": {"low": 0.0, "high": 5.0},
            "female": {"low": 0.0, "high": 4.5},
        },
        "category": "heart_health",
        "score_weight": 6,
        "clinical_context": "Ratio of total cholesterol to HDL; a better predictor of heart disease than total cholesterol alone.",
    },
    "ldl_hdl_ratio": {
        "name": "LDL/HDL Ratio",
        "aliases": [
            "ldl/hdl", "ldl hdl ratio", "ldl to hdl ratio",
        ],
        "unit": "",
        "ranges": {
            "default": {"low": 0.0, "high": 3.0},
            "male": {"low": 0.0, "high": 3.5},
            "female": {"low": 0.0, "high": 3.0},
        },
        "category": "heart_health",
        "score_weight": 6,
        "clinical_context": "Ratio of atherogenic to protective cholesterol; lower ratios indicate better cardiovascular health.",
    },

    # -----------------------------------------------------------------------
    # 4. Thyroid Panel (5 parameters)
    # -----------------------------------------------------------------------
    "tsh": {
        "name": "TSH",
        "aliases": [
            "thyroid stimulating hormone", "tsh ultrasensitive",
            "tsh (ultrasensitive)", "tsh (3rd generation)", "serum tsh",
            "thyrotropin",
        ],
        "unit": "uIU/mL",
        "ranges": {
            "default": {"low": 0.4, "high": 4.0},
            "male": {"low": 0.4, "high": 4.0},
            "female": {"low": 0.4, "high": 4.0},
            "fitness": {"low": 0.5, "high": 2.5},
        },
        "category": "thyroid_function",
        "score_weight": 10,
        "clinical_context": "Pituitary hormone regulating thyroid function; most sensitive screening test for thyroid disorders.",
        "fitness_note": "Optimal TSH for metabolic efficiency is 0.5-2.5 uIU/mL.",
    },
    "free_t3": {
        "name": "Free T3",
        "aliases": [
            "ft3", "free triiodothyronine", "t3 free", "free t3 level",
            "ft3 (free triiodothyronine)",
        ],
        "unit": "pg/mL",
        "ranges": {
            "default": {"low": 2.0, "high": 4.4},
            "male": {"low": 2.0, "high": 4.4},
            "female": {"low": 2.0, "high": 4.4},
        },
        "category": "thyroid_function",
        "score_weight": 8,
        "clinical_context": "Active thyroid hormone; drives metabolism, energy production, and body temperature regulation.",
    },
    "free_t4": {
        "name": "Free T4",
        "aliases": [
            "ft4", "free thyroxine", "t4 free", "free t4 level",
            "ft4 (free thyroxine)",
        ],
        "unit": "ng/dL",
        "ranges": {
            "default": {"low": 0.8, "high": 1.8},
            "male": {"low": 0.8, "high": 1.8},
            "female": {"low": 0.8, "high": 1.8},
        },
        "category": "thyroid_function",
        "score_weight": 8,
        "clinical_context": "Unbound thyroxine available to tissues; converted to active T3 in peripheral tissues.",
    },
    "total_t3": {
        "name": "Total T3",
        "aliases": [
            "t3", "triiodothyronine", "t3 total", "total triiodothyronine",
            "serum t3",
        ],
        "unit": "ng/dL",
        "ranges": {
            "default": {"low": 80.0, "high": 200.0},
            "male": {"low": 80.0, "high": 200.0},
            "female": {"low": 80.0, "high": 200.0},
        },
        "category": "thyroid_function",
        "score_weight": 5,
        "clinical_context": "Total triiodothyronine including bound fraction; affected by binding protein levels.",
    },
    "total_t4": {
        "name": "Total T4",
        "aliases": [
            "t4", "thyroxine", "t4 total", "total thyroxine", "serum t4",
        ],
        "unit": "ug/dL",
        "ranges": {
            "default": {"low": 4.5, "high": 12.5},
            "male": {"low": 4.5, "high": 12.5},
            "female": {"low": 4.5, "high": 12.5},
        },
        "category": "thyroid_function",
        "score_weight": 5,
        "clinical_context": "Total thyroxine including protein-bound fraction; may be altered by estrogen or liver disease.",
    },

    # -----------------------------------------------------------------------
    # 5. Kidney / Renal Panel (7 parameters)
    # -----------------------------------------------------------------------
    "creatinine": {
        "name": "Serum Creatinine",
        "aliases": [
            "creat", "creatinine serum", "s. creatinine", "serum creatinine",
            "creatinine (serum)", "blood creatinine",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 0.6, "high": 1.2},
            "male": {"low": 0.7, "high": 1.3},
            "female": {"low": 0.6, "high": 1.1},
            "fitness": {"low": 0.8, "high": 1.5},
        },
        "category": "kidney_function",
        "score_weight": 9,
        "clinical_context": "Waste product from muscle metabolism filtered by kidneys; elevated levels indicate impaired kidney function.",
        "fitness_note": "Muscular individuals and those on high-protein diets or creatine may have physiologically elevated creatinine.",
    },
    "egfr": {
        "name": "eGFR",
        "aliases": [
            "estimated gfr", "glomerular filtration rate", "gfr",
            "egfr (ckd-epi)", "estimated glomerular filtration rate",
        ],
        "unit": "mL/min/1.73m2",
        "ranges": {
            "default": {"low": 90.0, "high": 120.0},
            "male": {"low": 90.0, "high": 120.0},
            "female": {"low": 90.0, "high": 120.0},
        },
        "category": "kidney_function",
        "score_weight": 10,
        "clinical_context": "Estimated kidney filtration rate; the single best overall measure of kidney function.",
    },
    "bun": {
        "name": "Blood Urea Nitrogen",
        "aliases": [
            "bun", "blood urea nitrogen", "urea nitrogen",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 7.0, "high": 20.0},
            "male": {"low": 8.0, "high": 24.0},
            "female": {"low": 6.0, "high": 21.0},
            "fitness": {"low": 10.0, "high": 25.0},
        },
        "category": "kidney_function",
        "score_weight": 6,
        "clinical_context": "Nitrogen content from urea in blood; elevated by high protein intake, dehydration, or kidney disease.",
        "fitness_note": "High-protein diets common in fitness will elevate BUN without indicating kidney disease.",
    },
    "urea": {
        "name": "Blood Urea",
        "aliases": [
            "urea", "serum urea", "blood urea", "urea (serum)", "s. urea",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 15.0, "high": 45.0},
            "male": {"low": 17.0, "high": 50.0},
            "female": {"low": 13.0, "high": 45.0},
        },
        "category": "kidney_function",
        "score_weight": 6,
        "clinical_context": "End product of protein metabolism excreted by kidneys; elevated in renal impairment or dehydration.",
    },
    "uric_acid": {
        "name": "Uric Acid",
        "aliases": [
            "uric acid", "serum uric acid", "s. uric acid", "uric acid (serum)",
            "urate",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 3.0, "high": 7.0},
            "male": {"low": 3.5, "high": 7.2},
            "female": {"low": 2.5, "high": 6.0},
        },
        "category": "kidney_function",
        "score_weight": 6,
        "clinical_context": "Purine metabolism end product; elevated levels cause gout and are linked to cardiovascular risk.",
    },
    "microalbumin": {
        "name": "Microalbumin (Urine)",
        "aliases": [
            "microalbumin", "urine microalbumin", "microalbumin urine",
            "urine albumin", "microalbuminuria", "malb",
        ],
        "unit": "mg/L",
        "ranges": {
            "default": {"low": 0.0, "high": 30.0},
            "male": {"low": 0.0, "high": 30.0},
            "female": {"low": 0.0, "high": 30.0},
        },
        "category": "kidney_function",
        "score_weight": 7,
        "clinical_context": "Small amounts of albumin in urine; early marker of diabetic nephropathy and kidney damage.",
    },
    "bun_creatinine_ratio": {
        "name": "BUN/Creatinine Ratio",
        "aliases": [
            "bun/creatinine", "bun creatinine ratio", "urea creatinine ratio",
            "bun:creatinine",
        ],
        "unit": "",
        "ranges": {
            "default": {"low": 10.0, "high": 20.0},
            "male": {"low": 10.0, "high": 20.0},
            "female": {"low": 10.0, "high": 20.0},
        },
        "category": "kidney_function",
        "score_weight": 4,
        "clinical_context": "Helps differentiate pre-renal, renal, and post-renal causes of elevated urea or creatinine.",
    },

    # -----------------------------------------------------------------------
    # 6. Liver Panel (11 parameters)
    # -----------------------------------------------------------------------
    "alt": {
        "name": "ALT (SGPT)",
        "aliases": [
            "sgpt", "alt", "alanine aminotransferase", "alanine transaminase",
            "sgpt (alt)", "alt (sgpt)", "serum sgpt", "s.g.p.t",
            "glutamic pyruvic transaminase",
        ],
        "unit": "U/L",
        "ranges": {
            "default": {"low": 7.0, "high": 56.0},
            "male": {"low": 7.0, "high": 56.0},
            "female": {"low": 7.0, "high": 45.0},
            "fitness": {"low": 7.0, "high": 70.0},
        },
        "category": "liver_function",
        "score_weight": 9,
        "clinical_context": "Liver-specific enzyme; elevated primarily in liver cell damage from hepatitis, fatty liver, or toxins.",
        "fitness_note": "Intense resistance training can transiently elevate ALT; retest after 48-72h rest.",
    },
    "ast": {
        "name": "AST (SGOT)",
        "aliases": [
            "sgot", "ast", "aspartate aminotransferase", "aspartate transaminase",
            "sgot (ast)", "ast (sgot)", "serum sgot", "s.g.o.t",
            "glutamic oxaloacetic transaminase",
        ],
        "unit": "U/L",
        "ranges": {
            "default": {"low": 10.0, "high": 40.0},
            "male": {"low": 10.0, "high": 40.0},
            "female": {"low": 9.0, "high": 32.0},
            "fitness": {"low": 10.0, "high": 60.0},
        },
        "category": "liver_function",
        "score_weight": 8,
        "clinical_context": "Enzyme found in liver, heart, and muscle; elevated in liver damage but also after strenuous exercise.",
        "fitness_note": "Eccentric exercise and heavy lifting can elevate AST for 3-5 days post-workout.",
    },
    "alp": {
        "name": "Alkaline Phosphatase",
        "aliases": [
            "alp", "alkaline phosphatase", "alk phos", "alkp", "alk phosphatase",
            "serum alp",
        ],
        "unit": "U/L",
        "ranges": {
            "default": {"low": 44.0, "high": 147.0},
            "male": {"low": 44.0, "high": 147.0},
            "female": {"low": 44.0, "high": 147.0},
        },
        "category": "liver_function",
        "score_weight": 6,
        "clinical_context": "Enzyme from liver and bone; elevated in biliary obstruction, bone disease, or pregnancy.",
    },
    "ggt": {
        "name": "GGT",
        "aliases": [
            "gamma gt", "gamma glutamyl transferase", "gamma glutamyl transpeptidase",
            "ggt", "ggtp", "gamma-gt", "g.g.t",
        ],
        "unit": "U/L",
        "ranges": {
            "default": {"low": 0.0, "high": 61.0},
            "male": {"low": 8.0, "high": 61.0},
            "female": {"low": 5.0, "high": 36.0},
        },
        "category": "liver_function",
        "score_weight": 7,
        "clinical_context": "Sensitive marker for biliary disease and alcohol use; often elevated before other liver enzymes.",
    },
    "total_bilirubin": {
        "name": "Total Bilirubin",
        "aliases": [
            "bilirubin total", "total bili", "t. bilirubin", "serum bilirubin",
            "bilirubin (total)", "t.bili",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 0.1, "high": 1.2},
            "male": {"low": 0.1, "high": 1.2},
            "female": {"low": 0.1, "high": 1.2},
        },
        "category": "liver_function",
        "score_weight": 7,
        "clinical_context": "Breakdown product of hemoglobin; elevated in liver disease, hemolysis, or bile duct obstruction.",
    },
    "direct_bilirubin": {
        "name": "Direct Bilirubin",
        "aliases": [
            "bilirubin direct", "conjugated bilirubin", "d. bilirubin",
            "bilirubin (direct)", "d.bili",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 0.0, "high": 0.3},
            "male": {"low": 0.0, "high": 0.3},
            "female": {"low": 0.0, "high": 0.3},
        },
        "category": "liver_function",
        "score_weight": 5,
        "clinical_context": "Conjugated bilirubin processed by the liver; elevated specifically in obstructive or hepatocellular jaundice.",
    },
    "indirect_bilirubin": {
        "name": "Indirect Bilirubin",
        "aliases": [
            "bilirubin indirect", "unconjugated bilirubin", "id. bilirubin",
            "bilirubin (indirect)", "id.bili",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 0.1, "high": 0.9},
            "male": {"low": 0.1, "high": 0.9},
            "female": {"low": 0.1, "high": 0.9},
        },
        "category": "liver_function",
        "score_weight": 4,
        "clinical_context": "Unconjugated bilirubin before liver processing; elevated in hemolysis or Gilbert syndrome.",
    },
    "albumin": {
        "name": "Serum Albumin",
        "aliases": [
            "albumin", "alb", "serum albumin", "s. albumin", "albumin (serum)",
        ],
        "unit": "g/dL",
        "ranges": {
            "default": {"low": 3.5, "high": 5.5},
            "male": {"low": 3.5, "high": 5.5},
            "female": {"low": 3.5, "high": 5.5},
        },
        "category": "liver_function",
        "score_weight": 7,
        "clinical_context": "Major blood protein synthesized by the liver; low levels indicate liver disease or malnutrition.",
    },
    "globulin": {
        "name": "Serum Globulin",
        "aliases": [
            "globulin", "serum globulin", "s. globulin", "globulin (serum)",
        ],
        "unit": "g/dL",
        "ranges": {
            "default": {"low": 2.0, "high": 3.5},
            "male": {"low": 2.0, "high": 3.5},
            "female": {"low": 2.0, "high": 3.5},
        },
        "category": "liver_function",
        "score_weight": 5,
        "clinical_context": "Group of proteins including antibodies; elevated in chronic infections and autoimmune conditions.",
    },
    "total_protein": {
        "name": "Total Protein",
        "aliases": [
            "total protein", "serum total protein", "tp", "s. total protein",
            "protein total", "total protein (serum)",
        ],
        "unit": "g/dL",
        "ranges": {
            "default": {"low": 6.0, "high": 8.3},
            "male": {"low": 6.0, "high": 8.3},
            "female": {"low": 6.0, "high": 8.3},
        },
        "category": "liver_function",
        "score_weight": 5,
        "clinical_context": "Sum of albumin and globulin; reflects liver synthetic function and nutritional status.",
    },
    "ag_ratio": {
        "name": "Albumin/Globulin Ratio",
        "aliases": [
            "a/g ratio", "ag ratio", "albumin globulin ratio", "a:g ratio",
            "alb/glob ratio",
        ],
        "unit": "",
        "ranges": {
            "default": {"low": 1.0, "high": 2.2},
            "male": {"low": 1.0, "high": 2.2},
            "female": {"low": 1.0, "high": 2.2},
        },
        "category": "liver_function",
        "score_weight": 4,
        "clinical_context": "Ratio of albumin to globulin; low ratio may indicate chronic liver disease or inflammation.",
    },

    # -----------------------------------------------------------------------
    # 7. Iron / Anemia Panel (5 parameters)
    # -----------------------------------------------------------------------
    "serum_iron": {
        "name": "Serum Iron",
        "aliases": [
            "iron", "serum iron", "s. iron", "iron (serum)", "fe",
            "iron serum",
        ],
        "unit": "ug/dL",
        "ranges": {
            "default": {"low": 60.0, "high": 170.0},
            "male": {"low": 65.0, "high": 175.0},
            "female": {"low": 50.0, "high": 170.0},
        },
        "category": "blood_health",
        "score_weight": 7,
        "clinical_context": "Circulating iron in the blood; low levels precede anemia and cause fatigue.",
    },
    "ferritin": {
        "name": "Ferritin",
        "aliases": [
            "ferritin", "serum ferritin", "s. ferritin", "ferritin (serum)",
            "ferritin level",
        ],
        "unit": "ng/mL",
        "ranges": {
            "default": {"low": 20.0, "high": 250.0},
            "male": {"low": 30.0, "high": 400.0},
            "female": {"low": 13.0, "high": 150.0},
            "fitness": {"low": 50.0, "high": 300.0},
        },
        "category": "blood_health",
        "score_weight": 8,
        "clinical_context": "Iron storage protein; the most sensitive marker for iron deficiency and overload.",
        "fitness_note": "Athletes should target ferritin above 50 ng/mL for optimal oxygen transport and performance.",
    },
    "tibc": {
        "name": "TIBC",
        "aliases": [
            "tibc", "total iron binding capacity", "iron binding capacity",
            "tibc (total iron binding capacity)",
        ],
        "unit": "ug/dL",
        "ranges": {
            "default": {"low": 250.0, "high": 400.0},
            "male": {"low": 250.0, "high": 400.0},
            "female": {"low": 250.0, "high": 400.0},
        },
        "category": "blood_health",
        "score_weight": 5,
        "clinical_context": "Maximum amount of iron that blood proteins can carry; elevated in iron deficiency, low in overload.",
    },
    "transferrin_saturation": {
        "name": "Transferrin Saturation",
        "aliases": [
            "transferrin saturation", "tsat", "iron saturation", "% saturation",
            "transferrin sat", "tsat %",
        ],
        "unit": "%",
        "ranges": {
            "default": {"low": 20.0, "high": 50.0},
            "male": {"low": 20.0, "high": 50.0},
            "female": {"low": 15.0, "high": 50.0},
        },
        "category": "blood_health",
        "score_weight": 6,
        "clinical_context": "Percentage of transferrin bound to iron; low values confirm iron deficiency.",
    },
    "reticulocyte_count": {
        "name": "Reticulocyte Count",
        "aliases": [
            "reticulocyte count", "retic count", "reticulocytes", "retic %",
            "reticulocyte percentage",
        ],
        "unit": "%",
        "ranges": {
            "default": {"low": 0.5, "high": 2.5},
            "male": {"low": 0.5, "high": 2.5},
            "female": {"low": 0.5, "high": 2.5},
        },
        "category": "blood_health",
        "score_weight": 5,
        "clinical_context": "Immature red blood cells; reflects bone marrow response to anemia or blood loss.",
    },

    # -----------------------------------------------------------------------
    # 8. Vitamins Panel (4 parameters)
    # -----------------------------------------------------------------------
    "vitamin_d": {
        "name": "Vitamin D",
        "aliases": [
            "vitamin d", "vit d", "25-oh vitamin d", "25 hydroxy vitamin d",
            "cholecalciferol", "vitamin d3", "25(oh)d", "vit d3",
            "vitamin d 25-hydroxy", "25 oh d",
        ],
        "unit": "ng/mL",
        "ranges": {
            "default": {"low": 30.0, "high": 100.0},
            "male": {"low": 30.0, "high": 100.0},
            "female": {"low": 30.0, "high": 100.0},
            "fitness": {"low": 40.0, "high": 80.0},
        },
        "category": "vitamins",
        "score_weight": 9,
        "clinical_context": "Essential for calcium absorption, bone health, and immune function; widespread deficiency in India.",
        "fitness_note": "Optimal range for athletes is 40-80 ng/mL; supports testosterone production and muscle recovery.",
    },
    "vitamin_b12": {
        "name": "Vitamin B12",
        "aliases": [
            "vitamin b12", "vit b12", "b12", "cobalamin", "cyanocobalamin",
            "serum b12", "vitamin b-12",
        ],
        "unit": "pg/mL",
        "ranges": {
            "default": {"low": 200.0, "high": 900.0},
            "male": {"low": 200.0, "high": 900.0},
            "female": {"low": 200.0, "high": 900.0},
            "fitness": {"low": 400.0, "high": 900.0},
        },
        "category": "vitamins",
        "score_weight": 8,
        "clinical_context": "Essential for nerve function and red blood cell formation; deficiency common in vegetarians.",
        "fitness_note": "Optimal B12 for recovery and neurological function is above 400 pg/mL.",
    },
    "folate": {
        "name": "Folate",
        "aliases": [
            "folate", "folic acid", "serum folate", "vitamin b9", "vit b9",
            "folate (serum)", "s. folate",
        ],
        "unit": "ng/mL",
        "ranges": {
            "default": {"low": 3.0, "high": 20.0},
            "male": {"low": 3.0, "high": 20.0},
            "female": {"low": 3.0, "high": 20.0},
        },
        "category": "vitamins",
        "score_weight": 6,
        "clinical_context": "B vitamin essential for DNA synthesis and red blood cell production; critical during pregnancy.",
    },
    "vitamin_b6": {
        "name": "Vitamin B6",
        "aliases": [
            "vitamin b6", "vit b6", "b6", "pyridoxine", "pyridoxal phosphate",
            "plp",
        ],
        "unit": "ng/mL",
        "ranges": {
            "default": {"low": 5.0, "high": 50.0},
            "male": {"low": 5.0, "high": 50.0},
            "female": {"low": 5.0, "high": 50.0},
        },
        "category": "vitamins",
        "score_weight": 5,
        "clinical_context": "Coenzyme in amino acid metabolism and neurotransmitter synthesis; deficiency causes neuropathy.",
    },

    # -----------------------------------------------------------------------
    # 9. Electrolytes Panel (6 parameters)
    # -----------------------------------------------------------------------
    "sodium": {
        "name": "Sodium",
        "aliases": [
            "sodium", "na", "na+", "serum sodium", "s. sodium", "sodium (serum)",
        ],
        "unit": "mEq/L",
        "ranges": {
            "default": {"low": 136.0, "high": 145.0},
            "male": {"low": 136.0, "high": 145.0},
            "female": {"low": 136.0, "high": 145.0},
        },
        "category": "electrolytes",
        "score_weight": 8,
        "clinical_context": "Primary extracellular cation; regulates fluid balance, blood pressure, and nerve function.",
    },
    "potassium": {
        "name": "Potassium",
        "aliases": [
            "potassium", "k", "k+", "serum potassium", "s. potassium",
            "potassium (serum)",
        ],
        "unit": "mEq/L",
        "ranges": {
            "default": {"low": 3.5, "high": 5.0},
            "male": {"low": 3.5, "high": 5.0},
            "female": {"low": 3.5, "high": 5.0},
        },
        "category": "electrolytes",
        "score_weight": 9,
        "clinical_context": "Critical for cardiac rhythm and muscle contraction; abnormal levels can be life-threatening.",
    },
    "calcium": {
        "name": "Calcium",
        "aliases": [
            "calcium", "ca", "ca++", "serum calcium", "s. calcium",
            "calcium (serum)", "total calcium",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 8.5, "high": 10.5},
            "male": {"low": 8.5, "high": 10.5},
            "female": {"low": 8.5, "high": 10.5},
        },
        "category": "electrolytes",
        "score_weight": 7,
        "clinical_context": "Essential for bone health, muscle contraction, and nerve signaling; regulated by PTH and vitamin D.",
    },
    "magnesium": {
        "name": "Magnesium",
        "aliases": [
            "magnesium", "mg", "mg++", "serum magnesium", "s. magnesium",
            "magnesium (serum)",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 1.7, "high": 2.2},
            "male": {"low": 1.7, "high": 2.2},
            "female": {"low": 1.7, "high": 2.2},
            "fitness": {"low": 1.8, "high": 2.3},
        },
        "category": "electrolytes",
        "score_weight": 7,
        "clinical_context": "Cofactor in 300+ enzymatic reactions; deficiency causes muscle cramps, fatigue, and arrhythmias.",
        "fitness_note": "Athletes lose magnesium through sweat; supplementation often improves sleep and recovery.",
    },
    "phosphorus": {
        "name": "Phosphorus",
        "aliases": [
            "phosphorus", "phosphate", "serum phosphorus", "s. phosphorus",
            "phosphorus (serum)", "inorganic phosphorus", "po4",
        ],
        "unit": "mg/dL",
        "ranges": {
            "default": {"low": 2.5, "high": 4.5},
            "male": {"low": 2.5, "high": 4.5},
            "female": {"low": 2.5, "high": 4.5},
        },
        "category": "electrolytes",
        "score_weight": 5,
        "clinical_context": "Essential for bone mineralization and ATP energy production; linked to calcium metabolism.",
    },
    "chloride": {
        "name": "Chloride",
        "aliases": [
            "chloride", "cl", "cl-", "serum chloride", "s. chloride",
            "chloride (serum)",
        ],
        "unit": "mEq/L",
        "ranges": {
            "default": {"low": 98.0, "high": 106.0},
            "male": {"low": 98.0, "high": 106.0},
            "female": {"low": 98.0, "high": 106.0},
        },
        "category": "electrolytes",
        "score_weight": 5,
        "clinical_context": "Major extracellular anion; helps maintain acid-base balance and osmotic pressure.",
    },

    # -----------------------------------------------------------------------
    # 10. Inflammation Panel (3 parameters)
    # -----------------------------------------------------------------------
    "crp": {
        "name": "C-Reactive Protein",
        "aliases": [
            "crp", "c-reactive protein", "c reactive protein", "crp (quantitative)",
            "serum crp",
        ],
        "unit": "mg/L",
        "ranges": {
            "default": {"low": 0.0, "high": 10.0},
            "male": {"low": 0.0, "high": 10.0},
            "female": {"low": 0.0, "high": 10.0},
        },
        "category": "inflammation",
        "score_weight": 7,
        "clinical_context": "Acute-phase protein rising rapidly in infection and inflammation; used to monitor treatment response.",
    },
    "hs_crp": {
        "name": "hs-CRP",
        "aliases": [
            "hs-crp", "high sensitivity crp", "high sensitivity c-reactive protein",
            "hscrp", "hs crp", "cardio crp", "ultra sensitive crp",
        ],
        "unit": "mg/L",
        "ranges": {
            "default": {"low": 0.0, "high": 1.0},
            "male": {"low": 0.0, "high": 1.0},
            "female": {"low": 0.0, "high": 1.0},
            "fitness": {"low": 0.0, "high": 0.5},
        },
        "category": "inflammation",
        "score_weight": 9,
        "clinical_context": "Highly sensitive inflammatory marker predicting cardiovascular risk; optimal is below 1.0 mg/L.",
        "fitness_note": "Chronic low-grade inflammation impairs recovery; optimal for athletes is below 0.5 mg/L.",
    },
    "homocysteine": {
        "name": "Homocysteine",
        "aliases": [
            "homocysteine", "hcy", "serum homocysteine", "plasma homocysteine",
            "homocystiene", "s. homocysteine",
        ],
        "unit": "umol/L",
        "ranges": {
            "default": {"low": 5.0, "high": 15.0},
            "male": {"low": 5.0, "high": 15.0},
            "female": {"low": 5.0, "high": 12.0},
            "fitness": {"low": 5.0, "high": 10.0},
        },
        "category": "inflammation",
        "score_weight": 8,
        "clinical_context": "Amino acid linked to cardiovascular disease and B-vitamin deficiency; elevated levels damage blood vessels.",
        "fitness_note": "Optimal homocysteine for cardiovascular performance is below 10 umol/L.",
    },

    # -----------------------------------------------------------------------
    # 11. Pancreatic Panel (2 parameters)
    # -----------------------------------------------------------------------
    "amylase": {
        "name": "Amylase",
        "aliases": [
            "amylase", "serum amylase", "s. amylase", "amylase (serum)",
            "pancreatic amylase",
        ],
        "unit": "U/L",
        "ranges": {
            "default": {"low": 28.0, "high": 100.0},
            "male": {"low": 28.0, "high": 100.0},
            "female": {"low": 28.0, "high": 100.0},
        },
        "category": "pancreatic",
        "score_weight": 6,
        "clinical_context": "Digestive enzyme from pancreas and salivary glands; elevated in acute pancreatitis.",
    },
    "lipase": {
        "name": "Lipase",
        "aliases": [
            "lipase", "serum lipase", "s. lipase", "lipase (serum)",
            "pancreatic lipase",
        ],
        "unit": "U/L",
        "ranges": {
            "default": {"low": 0.0, "high": 160.0},
            "male": {"low": 0.0, "high": 160.0},
            "female": {"low": 0.0, "high": 160.0},
        },
        "category": "pancreatic",
        "score_weight": 7,
        "clinical_context": "Pancreas-specific enzyme for fat digestion; more specific than amylase for pancreatitis.",
    },

    # -----------------------------------------------------------------------
    # 12. Hormones Panel (10 parameters)
    # -----------------------------------------------------------------------
    "testosterone": {
        "name": "Total Testosterone",
        "aliases": [
            "testosterone", "total testosterone", "serum testosterone",
            "testosterone total", "testosterone (total)", "s. testosterone",
        ],
        "unit": "ng/dL",
        "ranges": {
            "default": {"low": 270.0, "high": 1070.0},
            "male": {"low": 270.0, "high": 1070.0},
            "female": {"low": 15.0, "high": 70.0},
            "fitness": {"low": 500.0, "high": 1070.0},
        },
        "category": "hormones",
        "score_weight": 9,
        "clinical_context": "Primary male sex hormone; affects muscle mass, bone density, mood, and libido.",
        "fitness_note": "Optimal testosterone for muscle building and recovery is above 500 ng/dL in males.",
    },
    "free_testosterone": {
        "name": "Free Testosterone",
        "aliases": [
            "free testosterone", "free testo", "testosterone free",
            "free testosterone (direct)", "ft",
        ],
        "unit": "pg/mL",
        "ranges": {
            "default": {"low": 5.0, "high": 30.0},
            "male": {"low": 9.0, "high": 30.0},
            "female": {"low": 0.3, "high": 1.9},
        },
        "category": "hormones",
        "score_weight": 8,
        "clinical_context": "Unbound active testosterone; better indicator of androgenic activity than total testosterone.",
    },
    "shbg": {
        "name": "SHBG",
        "aliases": [
            "shbg", "sex hormone binding globulin", "sex hormone-binding globulin",
            "shbg (sex hormone binding globulin)",
        ],
        "unit": "nmol/L",
        "ranges": {
            "default": {"low": 18.0, "high": 144.0},
            "male": {"low": 18.0, "high": 54.0},
            "female": {"low": 25.0, "high": 144.0},
        },
        "category": "hormones",
        "score_weight": 5,
        "clinical_context": "Protein binding sex hormones; high SHBG reduces free testosterone availability.",
    },
    "estradiol": {
        "name": "Estradiol",
        "aliases": [
            "estradiol", "e2", "oestradiol", "serum estradiol", "estradiol (e2)",
            "estrogen",
        ],
        "unit": "pg/mL",
        "ranges": {
            "default": {"low": 10.0, "high": 50.0},
            "male": {"low": 10.0, "high": 40.0},
            "female": {"low": 15.0, "high": 350.0},
        },
        "category": "hormones",
        "score_weight": 6,
        "clinical_context": "Primary female estrogen; also important in males for bone health and libido in balance with testosterone.",
    },
    "prolactin": {
        "name": "Prolactin",
        "aliases": [
            "prolactin", "prl", "serum prolactin", "prolactin (serum)",
            "s. prolactin",
        ],
        "unit": "ng/mL",
        "ranges": {
            "default": {"low": 2.0, "high": 18.0},
            "male": {"low": 2.0, "high": 18.0},
            "female": {"low": 2.0, "high": 29.0},
        },
        "category": "hormones",
        "score_weight": 5,
        "clinical_context": "Pituitary hormone primarily for lactation; elevated levels suppress testosterone and cause infertility.",
    },
    "cortisol": {
        "name": "Cortisol (Morning)",
        "aliases": [
            "cortisol", "serum cortisol", "cortisol (morning)", "morning cortisol",
            "cortisol am", "cortisol 8am", "s. cortisol",
        ],
        "unit": "ug/dL",
        "ranges": {
            "default": {"low": 6.0, "high": 18.0},
            "male": {"low": 6.0, "high": 18.0},
            "female": {"low": 6.0, "high": 18.0},
            "fitness": {"low": 8.0, "high": 15.0},
        },
        "category": "hormones",
        "score_weight": 7,
        "clinical_context": "Stress hormone from adrenal glands; chronically elevated cortisol causes muscle wasting and fat gain.",
        "fitness_note": "Chronically elevated cortisol indicates overtraining; optimal morning level is 8-15 ug/dL.",
    },
    "dhea_s": {
        "name": "DHEA-S",
        "aliases": [
            "dhea-s", "dhea sulfate", "dehydroepiandrosterone sulfate", "dheas",
            "dhea-so4", "dhea",
        ],
        "unit": "ug/dL",
        "ranges": {
            "default": {"low": 80.0, "high": 560.0},
            "male": {"low": 80.0, "high": 560.0},
            "female": {"low": 35.0, "high": 430.0},
        },
        "category": "hormones",
        "score_weight": 5,
        "clinical_context": "Adrenal androgen precursor; declines with age and is a marker of adrenal function.",
    },
    "igf1": {
        "name": "IGF-1",
        "aliases": [
            "igf-1", "igf1", "insulin like growth factor", "insulin-like growth factor 1",
            "somatomedin c", "igf 1",
        ],
        "unit": "ng/mL",
        "ranges": {
            "default": {"low": 100.0, "high": 350.0},
            "male": {"low": 100.0, "high": 350.0},
            "female": {"low": 100.0, "high": 350.0},
        },
        "category": "hormones",
        "score_weight": 6,
        "clinical_context": "Growth hormone mediator; reflects GH activity and is important for muscle growth and recovery.",
    },
    "lh": {
        "name": "LH",
        "aliases": [
            "lh", "luteinizing hormone", "luteinising hormone", "serum lh",
            "lh (luteinizing hormone)",
        ],
        "unit": "mIU/mL",
        "ranges": {
            "default": {"low": 1.0, "high": 12.0},
            "male": {"low": 1.5, "high": 9.3},
            "female": {"low": 1.0, "high": 12.0},
        },
        "category": "hormones",
        "score_weight": 5,
        "clinical_context": "Pituitary hormone stimulating gonadal function; triggers ovulation in females and testosterone production in males.",
    },
    "fsh": {
        "name": "FSH",
        "aliases": [
            "fsh", "follicle stimulating hormone", "follicle-stimulating hormone",
            "serum fsh", "fsh (follicle stimulating hormone)",
        ],
        "unit": "mIU/mL",
        "ranges": {
            "default": {"low": 1.0, "high": 12.0},
            "male": {"low": 1.5, "high": 12.4},
            "female": {"low": 1.0, "high": 12.0},
        },
        "category": "hormones",
        "score_weight": 5,
        "clinical_context": "Pituitary hormone for reproductive function; stimulates egg development in females and sperm production in males.",
    },

    # -----------------------------------------------------------------------
    # 13. Cardiac Markers Panel (3 parameters)
    # -----------------------------------------------------------------------
    "troponin": {
        "name": "Troponin I",
        "aliases": [
            "troponin", "troponin i", "troponin-i", "trop i", "cardiac troponin",
            "hs troponin", "high sensitivity troponin", "ctni",
        ],
        "unit": "ng/mL",
        "ranges": {
            "default": {"low": 0.0, "high": 0.04},
            "male": {"low": 0.0, "high": 0.04},
            "female": {"low": 0.0, "high": 0.04},
        },
        "category": "cardiac_markers",
        "score_weight": 10,
        "clinical_context": "Highly specific marker of heart muscle damage; elevated in myocardial infarction.",
    },
    "bnp": {
        "name": "BNP",
        "aliases": [
            "bnp", "brain natriuretic peptide", "b-type natriuretic peptide",
            "nt-probnp", "nt pro bnp", "pro-bnp",
        ],
        "unit": "pg/mL",
        "ranges": {
            "default": {"low": 0.0, "high": 100.0},
            "male": {"low": 0.0, "high": 100.0},
            "female": {"low": 0.0, "high": 100.0},
        },
        "category": "cardiac_markers",
        "score_weight": 9,
        "clinical_context": "Hormone released by heart under stress; elevated in heart failure and volume overload.",
    },
    "ldh": {
        "name": "LDH",
        "aliases": [
            "ldh", "lactate dehydrogenase", "lactic dehydrogenase", "serum ldh",
            "ldh (serum)", "l.d.h",
        ],
        "unit": "U/L",
        "ranges": {
            "default": {"low": 120.0, "high": 246.0},
            "male": {"low": 120.0, "high": 246.0},
            "female": {"low": 120.0, "high": 246.0},
            "fitness": {"low": 120.0, "high": 300.0},
        },
        "category": "cardiac_markers",
        "score_weight": 6,
        "clinical_context": "Enzyme present in many tissues; elevated in tissue damage including heart, liver, and muscle.",
        "fitness_note": "Intense exercise can elevate LDH for 24-48 hours; retest after adequate rest.",
    },

    # -----------------------------------------------------------------------
    # 14. Coagulation Panel (3 parameters)
    # -----------------------------------------------------------------------
    "pt": {
        "name": "Prothrombin Time",
        "aliases": [
            "pt", "prothrombin time", "pt (prothrombin time)", "pro time",
            "pt time",
        ],
        "unit": "seconds",
        "ranges": {
            "default": {"low": 11.0, "high": 13.5},
            "male": {"low": 11.0, "high": 13.5},
            "female": {"low": 11.0, "high": 13.5},
        },
        "category": "coagulation",
        "score_weight": 7,
        "clinical_context": "Measures extrinsic clotting pathway; prolonged in liver disease, vitamin K deficiency, or warfarin use.",
    },
    "inr": {
        "name": "INR",
        "aliases": [
            "inr", "international normalized ratio", "pt/inr", "pt inr",
            "inr (international normalized ratio)",
        ],
        "unit": "",
        "ranges": {
            "default": {"low": 0.8, "high": 1.1},
            "male": {"low": 0.8, "high": 1.1},
            "female": {"low": 0.8, "high": 1.1},
        },
        "category": "coagulation",
        "score_weight": 8,
        "clinical_context": "Standardized ratio of prothrombin time; used to monitor anticoagulant therapy.",
    },
    "aptt": {
        "name": "APTT",
        "aliases": [
            "aptt", "activated partial thromboplastin time", "ptt", "partial thromboplastin time",
            "aptt (activated partial thromboplastin time)", "a.p.t.t",
        ],
        "unit": "seconds",
        "ranges": {
            "default": {"low": 25.0, "high": 35.0},
            "male": {"low": 25.0, "high": 35.0},
            "female": {"low": 25.0, "high": 35.0},
        },
        "category": "coagulation",
        "score_weight": 7,
        "clinical_context": "Measures intrinsic clotting pathway; prolonged in hemophilia or heparin therapy.",
    },

    # -----------------------------------------------------------------------
    # 15. Muscle / Recovery Panel (2 parameters)
    # -----------------------------------------------------------------------
    "creatine_kinase": {
        "name": "Creatine Kinase (CK)",
        "aliases": [
            "ck", "cpk", "creatine kinase", "creatine phosphokinase",
            "ck total", "cpk total", "ck (creatine kinase)", "serum ck",
            "total ck",
        ],
        "unit": "U/L",
        "ranges": {
            "default": {"low": 30.0, "high": 200.0},
            "male": {"low": 39.0, "high": 308.0},
            "female": {"low": 26.0, "high": 192.0},
            "fitness": {"low": 50.0, "high": 500.0},
        },
        "category": "muscle_recovery",
        "score_weight": 8,
        "clinical_context": "Enzyme released during muscle damage; elevated after intense exercise, rhabdomyolysis, or myocardial injury.",
        "fitness_note": "Resistance training routinely elevates CK; levels up to 500 U/L can be normal 24-72h post-workout.",
    },
    "myoglobin": {
        "name": "Myoglobin",
        "aliases": [
            "myoglobin", "serum myoglobin", "myoglobin (serum)", "myo",
        ],
        "unit": "ng/mL",
        "ranges": {
            "default": {"low": 0.0, "high": 85.0},
            "male": {"low": 28.0, "high": 72.0},
            "female": {"low": 25.0, "high": 58.0},
            "fitness": {"low": 28.0, "high": 110.0},
        },
        "category": "muscle_recovery",
        "score_weight": 6,
        "clinical_context": "Oxygen-binding protein in muscle; early marker of muscle damage that rises before CK.",
        "fitness_note": "Transient elevation after intense training is expected; persistent elevation warrants investigation.",
    },
}


# ---------------------------------------------------------------------------
# SCORE CATEGORIES
# ---------------------------------------------------------------------------

SCORE_CATEGORIES: dict = {
    "metabolic_health": {
        "label": "Metabolic Health",
        "max_possible": 42,  # hba1c(10) + fasting_glucose(9) + pp_glucose(7) + fasting_insulin(8) + homa_ir(8)
        "color": "#FF6B35",
    },
    "heart_health": {
        "label": "Heart Health",
        "max_possible": 49,  # total_cholesterol(7) + ldl(9) + hdl(8) + triglycerides(8) + vldl(5) + tc_hdl_ratio(6) + ldl_hdl_ratio(6)
        "color": "#E63946",
    },
    "blood_health": {
        "label": "Blood Health",
        "max_possible": 102,  # Sum of all CBC + iron panel weights in blood_health category
        "color": "#D62828",
    },
    "thyroid_function": {
        "label": "Thyroid Function",
        "max_possible": 36,  # tsh(10) + free_t3(8) + free_t4(8) + total_t3(5) + total_t4(5)
        "color": "#6A4C93",
    },
    "kidney_function": {
        "label": "Kidney Function",
        "max_possible": 48,  # creatinine(9) + egfr(10) + bun(6) + urea(6) + uric_acid(6) + microalbumin(7) + bun_creatinine_ratio(4)
        "color": "#1982C4",
    },
    "liver_function": {
        "label": "Liver Function",
        "max_possible": 67,  # alt(9) + ast(8) + alp(6) + ggt(7) + total_bilirubin(7) + direct_bilirubin(5) + indirect_bilirubin(4) + albumin(7) + globulin(5) + total_protein(5) + ag_ratio(4)
        "color": "#8AC926",
    },
    "vitamins": {
        "label": "Vitamins",
        "max_possible": 28,  # vitamin_d(9) + vitamin_b12(8) + folate(6) + vitamin_b6(5)
        "color": "#FFCA3A",
    },
    "electrolytes": {
        "label": "Electrolytes",
        "max_possible": 41,  # sodium(8) + potassium(9) + calcium(7) + magnesium(7) + phosphorus(5) + chloride(5)
        "color": "#06D6A0",
    },
    "inflammation": {
        "label": "Inflammation",
        "max_possible": 29,  # crp(7) + hs_crp(9) + homocysteine(8) + esr(5)
        "color": "#EF476F",
    },
    "hormones": {
        "label": "Hormones",
        "max_possible": 61,  # testosterone(9) + free_testosterone(8) + shbg(5) + estradiol(6) + prolactin(5) + cortisol(7) + dhea_s(5) + igf1(6) + lh(5) + fsh(5)
        "color": "#118AB2",
    },
    "pancreatic": {
        "label": "Pancreatic Function",
        "max_possible": 13,  # amylase(6) + lipase(7)
        "color": "#FFD166",
    },
    "cardiac_markers": {
        "label": "Cardiac Markers",
        "max_possible": 25,  # troponin(10) + bnp(9) + ldh(6)
        "color": "#F72585",
    },
    "coagulation": {
        "label": "Coagulation",
        "max_possible": 22,  # pt(7) + inr(8) + aptt(7)
        "color": "#7209B7",
    },
    "muscle_recovery": {
        "label": "Muscle & Recovery",
        "max_possible": 14,  # creatine_kinase(8) + myoglobin(6)
        "color": "#3A0CA3",
    },
}


# ---------------------------------------------------------------------------
# PRE-BUILT ALIAS LOOKUP (built once at import time for O(1) lookups)
# ---------------------------------------------------------------------------

_ALIAS_MAP: dict[str, str] = {}
for _key, _entry in PARAMETER_REGISTRY.items():
    _lower_key = _key.lower()
    _ALIAS_MAP[_lower_key] = _key
    _ALIAS_MAP[_entry["name"].lower()] = _key
    for _alias in _entry["aliases"]:
        _ALIAS_MAP[_alias.lower()] = _key


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------


def normalize_parameter_name(raw_name: str) -> Optional[str]:
    """
    Resolve a raw parameter name (from a lab report) to its canonical registry key.

    Strategy:
    1. Direct key match (case-insensitive)
    2. Alias match (case-insensitive)
    3. Fuzzy partial match — check if the raw name is contained in any alias
       or any alias is contained in the raw name
    Returns the registry key or None if no match is found.
    """
    if not raw_name or not isinstance(raw_name, str):
        return None

    cleaned = raw_name.strip().lower()

    # 1. Direct key or alias match from pre-built map
    if cleaned in _ALIAS_MAP:
        return _ALIAS_MAP[cleaned]

    # 2. Remove common prefixes/suffixes that labs add
    stripped = cleaned
    for prefix in ("serum ", "s. ", "blood ", "plasma "):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix):]
            break
    if stripped in _ALIAS_MAP:
        return _ALIAS_MAP[stripped]

    # 3. Fuzzy partial match — substring containment
    best_match: Optional[str] = None
    best_length = 0

    for alias, key in _ALIAS_MAP.items():
        # Check if cleaned input contains the alias or alias contains the input
        if alias in cleaned or cleaned in alias:
            # Prefer the longest matching alias to avoid false positives
            if len(alias) > best_length:
                best_length = len(alias)
                best_match = key

    return best_match


def get_normal_range(parameter_key: str, user_profile: dict = None) -> dict:
    """
    Return the appropriate reference range {"low": float, "high": float} for a parameter.

    Selection logic:
    1. If user_profile has a fitness goal and the parameter has a "fitness" range, use fitness range.
    2. If user_profile specifies sex ("male"/"female") and a sex-specific range exists, use it.
    3. Fall back to the "default" range.

    Returns an empty dict if the parameter is not found.
    """
    entry = PARAMETER_REGISTRY.get(parameter_key)
    if not entry:
        return {}

    ranges = entry["ranges"]
    profile = user_profile or {}

    # Check for fitness-adjusted range
    is_fitness = profile.get("goal") in ("fitness", "bodybuilding", "athletic", "muscle_building")
    has_training = profile.get("training_frequency") or profile.get("is_athlete")
    if is_fitness and has_training and "fitness" in ranges:
        return dict(ranges["fitness"])

    # Check sex-specific range
    sex = profile.get("sex", "").lower()
    if sex in ("male", "female") and sex in ranges:
        return dict(ranges[sex])

    return dict(ranges["default"])


def classify_status(value: float, range_low: float, range_high: float) -> str:
    """
    Classify a lab value relative to its reference range.

    Returns one of:
    - "normal"          — within range
    - "low"             — below range (more than 10% below low boundary)
    - "high"            — above range (more than 10% above high boundary)
    - "borderline_low"  — below range but within 10% of the low boundary
    - "borderline_high" — above range but within 10% of the high boundary
    """
    if range_low <= value <= range_high:
        return "normal"

    range_span = range_high - range_low
    if range_span == 0:
        range_span = max(abs(range_high), 1.0)

    margin = range_span * 0.10

    if value < range_low:
        if value >= range_low - margin:
            return "borderline_low"
        return "low"

    # value > range_high
    if value <= range_high + margin:
        return "borderline_high"
    return "high"


def get_score_weight(parameter_key: str) -> int:
    """Return the health score weight for a parameter, or 0 if not found."""
    entry = PARAMETER_REGISTRY.get(parameter_key)
    return entry["score_weight"] if entry else 0


def get_category(parameter_key: str) -> str:
    """Return the score category for a parameter, or empty string if not found."""
    entry = PARAMETER_REGISTRY.get(parameter_key)
    return entry["category"] if entry else ""


def get_clinical_context(parameter_key: str) -> str:
    """Return the clinical context string for a parameter, or empty string if not found."""
    entry = PARAMETER_REGISTRY.get(parameter_key)
    return entry["clinical_context"] if entry else ""


def build_embedding_text(parameter_key: str, value: float, unit: str, status: str) -> str:
    """
    Build an enriched text string suitable for vector embedding / RAG context.

    Format:
      "{Name}: {value} {unit} ({status}) — {clinical_context}"

    Example:
      "Hemoglobin: 11.2 g/dL (low) — Oxygen-carrying protein in red blood cells; low levels indicate anemia."

    Returns a plain string if the parameter is not found in the registry.
    """
    entry = PARAMETER_REGISTRY.get(parameter_key)
    if not entry:
        return f"{parameter_key}: {value} {unit} ({status})"

    name = entry["name"]
    context = entry["clinical_context"]
    fitness_note = entry.get("fitness_note", "")

    text = f"{name}: {value} {unit} ({status}) — {context}"
    if fitness_note:
        text += f" Fitness note: {fitness_note}"

    return text
