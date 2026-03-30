"""
Static medical knowledge base for VitaI Coach prompt enrichment.
Provides clinically relevant context, food recommendations (India-specific),
and improvement timelines for key health parameters.
"""

import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Medical knowledge dictionary
# ---------------------------------------------------------------------------

MEDICAL_KNOWLEDGE: dict[str, dict] = {

    "hba1c": {
        "display_name": "HbA1c (Glycated Hemoglobin)",
        "related_markers": ["fasting_glucose", "insulin", "triglycerides", "hdl"],
        "common_causes_high": [
            "Insulin resistance / pre-diabetes / diabetes",
            "High refined carbohydrate intake",
            "Sedentary lifestyle",
            "Chronic stress (cortisol-driven glucose elevation)",
            "PCOS (in women)",
            "Medications: steroids, certain antipsychotics",
        ],
        "common_causes_low": [
            "Hemolytic anemia (falsely low due to RBC turnover)",
            "Chronic kidney disease",
            "Recent blood transfusion",
            "Iron deficiency anemia (can falsely elevate or lower)",
        ],
        "improvement_timeline": (
            "HbA1c reflects average blood sugar over 2-3 months. Dietary and "
            "exercise changes will show in the next HbA1c test after 3 months."
        ),
        "food_recommendations_india": [
            "Methi (fenugreek) seeds soaked overnight — lowers post-meal glucose",
            "Bitter gourd (karela) — contains plant insulin (polypeptide-p)",
            "Whole grains: ragi (finger millet), jowar, bajra instead of white rice",
            "Cinnamon (dalchini) — 1/2 tsp daily may improve insulin sensitivity",
            "Replace sugar with jaggery in moderation; avoid maida-based foods",
            "Include protein with every meal (dal, paneer, eggs, chicken) to slow glucose spike",
        ],
        "when_to_worry": (
            "HbA1c above 6.5% is diabetic range — see a doctor immediately. "
            "Between 5.7-6.4% is pre-diabetic and reversible with lifestyle changes. "
            "If you have symptoms like excessive thirst, frequent urination, or unexplained "
            "weight loss, seek urgent medical attention regardless of HbA1c level."
        ),
        "interacts_with": ["fasting_glucose", "triglycerides", "hdl", "vitamin_d"],
    },

    "hemoglobin": {
        "display_name": "Hemoglobin",
        "related_markers": ["ferritin", "iron", "vitamin_b12", "folate", "mcv"],
        "common_causes_high": [
            "Dehydration (relative increase)",
            "Polycythemia vera",
            "Living at high altitude",
            "Chronic lung disease / smoking",
            "Anabolic steroid use",
        ],
        "common_causes_low": [
            "Iron deficiency (most common in India)",
            "Vitamin B12 or folate deficiency",
            "Chronic disease / inflammation",
            "Thalassemia trait (very common in India)",
            "Heavy menstrual bleeding (in women)",
            "Chronic kidney disease (low EPO)",
        ],
        "improvement_timeline": (
            "Iron supplementation typically raises hemoglobin by 1-2 g/dL per month. "
            "Full recovery from iron deficiency anemia takes 2-3 months. B12 deficiency "
            "anemia may take 2-6 months depending on severity."
        ),
        "food_recommendations_india": [
            "Ragi (finger millet) — highest iron among millets",
            "Jaggery (gud) with roasted chana — traditional iron-rich snack",
            "Spinach (palak) and amaranth leaves (chaulai) cooked with lemon",
            "Pomegranate (anaar) — iron + vitamin C combo",
            "Dates (khajoor) and black raisins (kali kishmish) daily",
            "Beetroot juice with amla for iron absorption",
            "Cook in iron kadhai/tawa for additional dietary iron",
        ],
        "when_to_worry": (
            "Hemoglobin below 7 g/dL is severe anemia — may need transfusion. "
            "Below 10 g/dL with symptoms (breathlessness, chest pain, dizziness) "
            "needs urgent medical attention. Above 18 g/dL may indicate polycythemia "
            "and requires investigation."
        ),
        "interacts_with": ["ferritin", "iron", "vitamin_b12", "folate"],
    },

    "tsh": {
        "display_name": "TSH (Thyroid Stimulating Hormone)",
        "related_markers": ["t3", "t4", "free_t4", "vitamin_d", "total_cholesterol", "ldl"],
        "common_causes_high": [
            "Hashimoto's thyroiditis (autoimmune — most common cause)",
            "Iodine deficiency",
            "Vitamin D deficiency (impairs thyroid function)",
            "Post-thyroiditis recovery phase",
            "Medications: lithium, amiodarone",
        ],
        "common_causes_low": [
            "Graves' disease (autoimmune hyperthyroidism)",
            "Thyroid nodules / toxic adenoma",
            "Excessive thyroid medication",
            "Early pregnancy (normal physiological drop)",
            "Pituitary disorder (central hypothyroidism — rare)",
        ],
        "improvement_timeline": (
            "TSH takes 6-8 weeks to stabilize after starting or adjusting thyroid "
            "medication. Retest at 6-week intervals when adjusting dose. "
            "Lifestyle improvements (vitamin D, selenium) may show effects in 2-3 months."
        ),
        "food_recommendations_india": [
            "Use iodised salt (not rock salt / sendha namak exclusively)",
            "Brazil nuts (2-3 daily) for selenium — supports T4 to T3 conversion",
            "Coconut oil — medium chain fatty acids support thyroid",
            "Eggs — contain iodine, selenium, and B12",
            "Avoid excess raw cruciferous vegetables (goitrogens) if hypothyroid",
            "Ashwagandha (under doctor supervision) may support thyroid function",
        ],
        "when_to_worry": (
            "TSH above 10 with symptoms (weight gain, fatigue, cold intolerance, "
            "constipation) needs treatment. TSH below 0.1 with palpitations, weight "
            "loss, tremors, or heat intolerance needs urgent evaluation. Thyroid storm "
            "(very low TSH + fever + rapid heart rate) is a medical emergency."
        ),
        "interacts_with": ["vitamin_d", "total_cholesterol", "ldl", "hemoglobin", "ferritin"],
    },

    "ldl": {
        "display_name": "LDL Cholesterol",
        "related_markers": ["hdl", "triglycerides", "total_cholesterol", "hba1c", "tsh"],
        "common_causes_high": [
            "High saturated fat diet (ghee, full-fat dairy, red meat)",
            "Genetic: familial hypercholesterolemia",
            "Hypothyroidism (check TSH)",
            "Insulin resistance / metabolic syndrome",
            "Sedentary lifestyle",
            "Obesity",
            "Nephrotic syndrome",
        ],
        "common_causes_low": [
            "Hyperthyroidism",
            "Malabsorption / malnutrition",
            "Liver disease",
            "Statin medications",
            "Very low-fat diet",
        ],
        "improvement_timeline": (
            "Dietary changes can lower LDL by 10-15% within 4-6 weeks. Adding "
            "soluble fiber and plant sterols shows results in 3-4 weeks. Statins "
            "typically lower LDL by 30-50% within 4-6 weeks."
        ),
        "food_recommendations_india": [
            "Oats (rolled/steel-cut) with flaxseeds — soluble fiber binds cholesterol",
            "Methi seeds — proven to lower LDL by 10-15%",
            "Garlic (lahsun) — 2-3 raw cloves daily",
            "Walnuts and almonds (handful daily) — replace fried snacks",
            "Replace ghee with mustard oil or cold-pressed sesame oil",
            "Psyllium husk (isabgol) — 5-10g daily",
            "Green tea instead of chai with full-fat milk",
        ],
        "when_to_worry": (
            "LDL above 190 mg/dL may indicate familial hypercholesterolemia — "
            "needs genetic screening and likely medication. LDL above 160 with "
            "diabetes or heart disease history needs aggressive treatment. "
            "Any LDL level with chest pain or stroke symptoms is an emergency."
        ),
        "interacts_with": ["hdl", "triglycerides", "tsh", "hba1c"],
    },

    "vitamin_d": {
        "display_name": "Vitamin D (25-hydroxy)",
        "related_markers": ["calcium", "pth", "tsh", "hemoglobin", "testosterone"],
        "common_causes_high": [
            "Excessive supplementation",
            "Granulomatous diseases (sarcoidosis, TB)",
            "Hyperparathyroidism",
        ],
        "common_causes_low": [
            "Inadequate sun exposure (indoor lifestyle, dark skin)",
            "Vegetarian/vegan diet (few plant sources)",
            "Obesity (vitamin D sequestered in fat)",
            "Malabsorption (celiac, IBD)",
            "Chronic kidney or liver disease",
            "Very common in India despite sunny climate (70-90% prevalence)",
        ],
        "improvement_timeline": (
            "Vitamin D levels respond to supplementation within 4-8 weeks. "
            "Standard Indian protocol: 60,000 IU weekly for 8 weeks, then "
            "60,000 IU monthly for maintenance. Retest after 3 months."
        ),
        "food_recommendations_india": [
            "Morning sunlight (7-9 AM) for 15-20 min with arms and legs exposed",
            "Fortified milk and dairy products",
            "Egg yolks (2 daily provide ~80 IU)",
            "Fatty fish: salmon, mackerel (bangda), sardines",
            "Mushrooms exposed to sunlight",
            "Fortified cereals and orange juice",
        ],
        "when_to_worry": (
            "Below 10 ng/mL is severe deficiency — can cause osteomalacia (bone "
            "softening), muscle weakness, and increased fracture risk. Needs "
            "aggressive supplementation under medical supervision. Above 100 ng/mL "
            "is toxicity risk — can cause hypercalcemia (nausea, kidney stones, "
            "confusion). Stop supplements and see a doctor."
        ),
        "interacts_with": ["calcium", "pth", "tsh", "testosterone", "hemoglobin"],
    },

    "vitamin_b12": {
        "display_name": "Vitamin B12 (Cobalamin)",
        "related_markers": ["hemoglobin", "mcv", "homocysteine", "folate", "ferritin"],
        "common_causes_high": [
            "Liver disease (B12 released from liver stores)",
            "Chronic myeloid leukemia (rare)",
            "Excessive supplementation",
        ],
        "common_causes_low": [
            "Vegetarian/vegan diet (most common cause in India)",
            "Pernicious anemia (autoimmune — anti-intrinsic factor antibodies)",
            "Metformin use (reduces B12 absorption by 10-30%)",
            "H. pylori infection (common in India, damages stomach lining)",
            "Atrophic gastritis / low stomach acid (elderly)",
            "Malabsorption disorders",
        ],
        "improvement_timeline": (
            "Oral B12 supplements (1000-2000 mcg daily) raise levels within "
            "1-2 months. Injections work faster (2-4 weeks for symptom relief). "
            "Neurological symptoms from severe deficiency may take 6-12 months "
            "to fully resolve — early treatment is critical."
        ),
        "food_recommendations_india": [
            "Curd / dahi (1-2 cups daily) — best vegetarian source",
            "Paneer and cheese — moderate B12 content",
            "Milk — 200mL provides ~1 mcg B12",
            "Eggs — 2 daily provide ~1.5 mcg (if eggetarian)",
            "Fortified foods: nutritional yeast, plant milks, cereals",
            "For non-veg: liver, chicken, fish (mackerel, sardines)",
        ],
        "when_to_worry": (
            "Below 200 pg/mL is deficiency — start supplementation. Below 150 "
            "pg/mL with neurological symptoms (tingling, numbness, balance issues, "
            "memory problems) is urgent — nerve damage can become irreversible. "
            "If on metformin for diabetes, get B12 checked every 6 months."
        ),
        "interacts_with": ["hemoglobin", "folate", "homocysteine", "ferritin"],
    },

    "ferritin": {
        "display_name": "Ferritin (Iron Stores)",
        "related_markers": ["hemoglobin", "iron", "tibc", "transferrin_saturation", "mcv"],
        "common_causes_high": [
            "Inflammation / infection (ferritin is an acute-phase reactant)",
            "Hemochromatosis (iron overload — genetic)",
            "Liver disease / fatty liver",
            "Metabolic syndrome",
            "Excessive iron supplementation",
        ],
        "common_causes_low": [
            "Iron-deficient diet (very common in India, especially vegetarians)",
            "Heavy menstrual bleeding",
            "Chronic blood loss (GI — check for ulcers, piles)",
            "Pregnancy / breastfeeding",
            "Celiac disease / malabsorption",
            "Frequent blood donation",
        ],
        "improvement_timeline": (
            "Ferritin takes 3-6 months of supplementation to fully replenish. "
            "A typical regimen: ferrous sulfate 325mg on alternate days (better "
            "absorption than daily). Take on empty stomach with vitamin C. "
            "Retest at 3 months."
        ),
        "food_recommendations_india": [
            "Jaggery (gud) — traditional iron source, 10-15g daily",
            "Ragi (nachni) porridge or roti",
            "Green leafy vegetables: palak, bathua, chaulai, moringa (drumstick leaves)",
            "Soaked and sprouted moong/chana — iron + improved bioavailability",
            "Pomegranate and beetroot juice",
            "Cook in iron kadhai — can increase iron content of food by 16%",
            "Pair iron-rich foods with amla/lemon (vitamin C) for absorption",
        ],
        "when_to_worry": (
            "Below 12 ng/mL is depleted iron stores — supplementation mandatory. "
            "Below 30 ng/mL with symptoms (fatigue, hair loss, brittle nails, "
            "restless legs) needs treatment. Very high ferritin (>500) without "
            "obvious inflammation needs investigation for hemochromatosis or "
            "liver disease."
        ),
        "interacts_with": ["hemoglobin", "iron", "vitamin_b12", "tsh"],
    },

    "creatinine": {
        "display_name": "Serum Creatinine",
        "related_markers": ["bun", "egfr", "uric_acid", "potassium", "creatine_kinase"],
        "common_causes_high": [
            "Kidney dysfunction / chronic kidney disease",
            "Dehydration",
            "Creatine supplementation (benign elevation)",
            "High protein diet / high meat intake",
            "Intense exercise (temporary spike from muscle breakdown)",
            "Medications: ACE inhibitors, NSAIDs, aminoglycosides",
        ],
        "common_causes_low": [
            "Low muscle mass (elderly, malnutrition)",
            "Liver disease (reduced creatine production)",
            "Pregnancy (increased kidney filtration)",
        ],
        "improvement_timeline": (
            "Creatinine from dehydration normalises within 24-48 hours with "
            "rehydration. Creatine supplement-related elevation persists as long "
            "as supplementation continues. Kidney disease progression is slow — "
            "trend over 3-6 months matters more than a single reading."
        ),
        "food_recommendations_india": [
            "Stay well-hydrated: 2.5-3.5L water daily",
            "Reduce excess protein if consuming >2g/kg body weight",
            "Barley water (jau ka paani) — traditional kidney-friendly drink",
            "Reduce sodium: avoid papad, pickles, processed foods",
            "Include kidney-friendly foods: apple, cabbage, cauliflower, onion",
            "Limit potassium-rich foods if eGFR is low: bananas, potatoes, coconut water",
        ],
        "when_to_worry": (
            "Creatinine above 1.5 mg/dL with declining eGFR needs nephrologist "
            "referral. Sudden spike (>0.3 mg/dL from baseline) suggests acute "
            "kidney injury — urgent evaluation needed. If you supplement creatine "
            "and creatinine is mildly elevated with normal BUN, it is likely benign "
            "— ask for a Cystatin C test for clarity."
        ),
        "interacts_with": ["bun", "egfr", "uric_acid", "potassium"],
    },

    "alt": {
        "display_name": "ALT / SGPT (Liver Enzyme)",
        "related_markers": ["ast", "ggt", "bilirubin", "albumin", "alkaline_phosphatase"],
        "common_causes_high": [
            "Non-alcoholic fatty liver disease (NAFLD) — most common in India",
            "Alcohol consumption",
            "Hepatitis B/C infection",
            "Medications: paracetamol, statins, anti-TB drugs, certain antibiotics",
            "Obesity / metabolic syndrome",
            "Intense exercise (temporary mild elevation)",
            "Herbal supplements / Ayurvedic medicines (some contain liver-toxic metals)",
        ],
        "common_causes_low": [
            "Very low ALT is usually normal",
            "Vitamin B6 deficiency (rare — ALT needs B6 as cofactor)",
        ],
        "improvement_timeline": (
            "ALT from fatty liver improves within 4-8 weeks of lifestyle changes "
            "(weight loss, reduced alcohol, diet improvement). Medication-induced "
            "elevation resolves 2-4 weeks after stopping the offending drug. "
            "Hepatitis treatment timelines vary by type."
        ),
        "food_recommendations_india": [
            "Avoid alcohol completely if ALT is elevated",
            "Turmeric (haldi) milk — curcumin has hepatoprotective properties",
            "Green tea (1-2 cups) — catechins support liver function",
            "Amla (Indian gooseberry) — powerful antioxidant for liver",
            "Reduce refined carbs and sugar (major driver of fatty liver)",
            "Include cruciferous vegetables: broccoli, cabbage, cauliflower",
            "Avoid maida, fried foods, and excess ghee/oil",
        ],
        "when_to_worry": (
            "ALT above 3x upper limit (>120 U/L) needs investigation — get hepatitis "
            "panel and ultrasound. Above 10x upper limit (>400 U/L) suggests acute "
            "hepatitis — urgent medical attention. If associated with jaundice "
            "(yellowing of eyes/skin), dark urine, or abdominal pain, go to the "
            "hospital immediately."
        ),
        "interacts_with": ["ast", "ggt", "bilirubin", "hba1c", "triglycerides"],
    },

    "testosterone": {
        "display_name": "Testosterone (Total)",
        "related_markers": ["lh", "fsh", "shbg", "cortisol", "vitamin_d", "prolactin"],
        "common_causes_high": [
            "Anabolic steroid or testosterone use",
            "PCOS (in women)",
            "Adrenal tumors (rare)",
            "Congenital adrenal hyperplasia",
        ],
        "common_causes_low": [
            "Obesity (adipose tissue converts testosterone to estrogen)",
            "Sleep deprivation (even 1 week of 5hr sleep reduces T by 10-15%)",
            "Chronic stress / high cortisol",
            "Vitamin D deficiency",
            "Zinc deficiency",
            "Type 2 diabetes / insulin resistance",
            "Aging (1-2% decline per year after 30)",
            "Opioid medications",
            "Overtraining without adequate recovery",
        ],
        "improvement_timeline": (
            "Lifestyle improvements (sleep, weight loss, exercise, stress reduction) "
            "can raise testosterone by 15-30% over 3-6 months. Resistance training "
            "shows acute increases within 2-4 weeks. Vitamin D supplementation "
            "(if deficient) may improve T over 3 months."
        ),
        "food_recommendations_india": [
            "Eggs (whole) — cholesterol is a testosterone precursor",
            "Ashwagandha (KSM-66, 600mg daily) — shown to increase T by 15%",
            "Zinc-rich foods: pumpkin seeds, sesame seeds, chickpeas",
            "Pomegranate juice — may reduce cortisol and support T",
            "Ginger (adrak) — studies show 17% increase in T with daily use",
            "Healthy fats: almonds, walnuts, desi ghee in moderation",
            "Cruciferous vegetables (broccoli, cabbage) — reduce excess estrogen",
        ],
        "when_to_worry": (
            "Total testosterone below 250 ng/dL with symptoms (low libido, erectile "
            "dysfunction, fatigue, depression, muscle loss) needs endocrinologist "
            "evaluation. Check LH/FSH to differentiate primary vs secondary "
            "hypogonadism. In women, elevated testosterone with irregular periods "
            "and acne needs PCOS workup."
        ),
        "interacts_with": ["cortisol", "vitamin_d", "shbg", "lh", "fsh", "hba1c"],
    },
}


# ---------------------------------------------------------------------------
# Context builder for LLM injection
# ---------------------------------------------------------------------------

def get_medical_context(
    priority_markers: list[str],
    user_profile: dict = None,
) -> str:
    """
    Build a concise medical-knowledge context block for the given priority
    markers, suitable for injecting into an LLM prompt.

    Tailors content based on user profile (vegetarian diet, fitness goals, etc.).
    Caps output at ~1000 tokens (~4000 characters).
    """
    if not priority_markers:
        return ""

    profile = user_profile or {}
    is_vegetarian = (profile.get("diet_type") or "").lower() in ("vegetarian", "vegan")
    has_fitness_goals = any(
        g.lower() in ("muscle_gain", "fat_loss", "athletic_performance", "bodybuilding",
                       "weight_loss", "fitness", "strength")
        for g in (profile.get("health_goals") or [])
    ) or (profile.get("goal_phase") or "").lower() in ("bulking", "cutting", "recomp")

    sections: list[str] = []
    total_chars = 0
    max_chars = 4000

    for marker in priority_markers:
        marker_key = marker.lower().strip()
        info = MEDICAL_KNOWLEDGE.get(marker_key)
        if info is None:
            continue

        lines: list[str] = []
        display = info.get("display_name", marker_key)
        lines.append(f"### {display}")

        # Related markers
        related = info.get("related_markers", [])
        if related:
            lines.append(f"Related markers: {', '.join(related)}")

        # Common causes — pick based on context if available
        # Include both high and low causes as we may not know the user's status here
        causes_high = info.get("common_causes_high", [])
        causes_low = info.get("common_causes_low", [])
        if causes_high:
            lines.append("If elevated: " + "; ".join(causes_high[:4]))
        if causes_low:
            lines.append("If low: " + "; ".join(causes_low[:4]))

        # Food recommendations
        foods = info.get("food_recommendations_india", [])
        if foods:
            if is_vegetarian and marker_key in ("vitamin_b12", "hemoglobin", "ferritin", "iron"):
                # Emphasize plant-based sources
                lines.append("Diet tips (vegetarian-friendly): " + "; ".join(foods[:5]))
                if marker_key == "vitamin_b12":
                    lines.append(
                        "Note: B12 supplementation is strongly recommended for "
                        "vegetarians — dietary sources alone are rarely sufficient."
                    )
                if marker_key in ("hemoglobin", "ferritin"):
                    lines.append(
                        "Note: Plant-based (non-heme) iron is less absorbable. "
                        "Always pair with vitamin C and avoid tea/coffee with meals."
                    )
            else:
                lines.append("Diet tips: " + "; ".join(foods[:4]))

        # Improvement timeline
        timeline = info.get("improvement_timeline")
        if timeline:
            lines.append(f"Timeline: {timeline}")

        # Fitness-specific notes
        if has_fitness_goals:
            if marker_key == "testosterone":
                lines.append(
                    "Fitness note: Compound lifts (squats, deadlifts) acutely boost T. "
                    "Prioritise sleep (7-9 hrs) and avoid chronic caloric deficits — "
                    "they suppress testosterone. During cutting, keep deficit moderate "
                    "(<500 kcal/day)."
                )
            elif marker_key == "creatinine":
                lines.append(
                    "Fitness note: Creatine supplementation and high protein intake "
                    "raise creatinine without kidney damage. Track eGFR and BUN "
                    "alongside creatinine for accurate kidney assessment."
                )
            elif marker_key == "hemoglobin":
                lines.append(
                    "Fitness note: Low hemoglobin directly reduces VO2max and "
                    "exercise performance. Iron deficiency is a common hidden cause "
                    "of training plateaus and fatigue."
                )
            elif marker_key == "hba1c":
                lines.append(
                    "Fitness note: Good glycemic control supports muscle recovery "
                    "and body composition. Post-workout carbs are beneficial — "
                    "focus on reducing refined carbs at other times."
                )
            elif marker_key == "vitamin_d":
                lines.append(
                    "Fitness note: Vitamin D receptors exist in muscle tissue. "
                    "Deficiency is linked to muscle weakness and increased injury "
                    "risk. Optimal range for athletes: 40-60 ng/mL."
                )
            elif marker_key == "ferritin":
                lines.append(
                    "Fitness note: Athletes need higher ferritin (>50 ng/mL) for "
                    "optimal oxygen transport. Foot-strike hemolysis in runners and "
                    "sweat losses increase iron requirements."
                )

        section_text = "\n".join(lines)
        if total_chars + len(section_text) + 2 > max_chars:
            break
        sections.append(section_text)
        total_chars += len(section_text) + 2  # +2 for double newline separator

    if not sections:
        return ""

    header = "=== Medical Context for Priority Markers ==="
    context = header + "\n\n" + "\n\n".join(sections)

    # Final length cap
    if len(context) > max_chars:
        context = context[:max_chars].rsplit("\n", 1)[0] + "\n..."

    return context
