"""
CropCare - Disease Knowledge Base
Comprehensive agronomic database for all 19 supported crop disease classes.
Provides evidence-based symptoms, treatments, active ingredients, safety precautions,
and long-term preventive measures.
"""

DISEASE_DATABASE = {
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight",
        "scientific_name": "Alternaria solani",
        "is_healthy": False,
        "summary": "Early blight is a prevalent fungal disease affecting potatoes, characterized by dark brown concentric ring lesions primarily on older foliage.",
        "symptoms": [
            "Circular to angular dark brown necrotic spots on older leaves",
            "Distinct target-board concentric rings within leaf lesions",
            "Chlorotic yellow halo surrounding brown diseased areas",
            "Progressive leaf yellowing, drying, and premature leaf drop",
            "Stem lesions that may cause girdling in severe cases"
        ],
        "immediate_actions": [
            "Prune heavily infected lower leaves and safely dispose of them away from fields",
            "Disinfect pruning tools with 70% alcohol or 10% bleach solution between cuts",
            "Cease overhead sprinkler irrigation immediately; switch to drip or furrow watering",
            "Remove weeds around the potato canopy to improve air circulation"
        ],
        "treatment": [
            "Apply protective contact fungicides prior to rain or humid weather periods",
            "Rotate systemic fungicides with multi-site contact protectants to prevent resistance",
            "Ensure complete coverage of both upper and lower leaf surfaces during spraying",
            "Re-apply fungicides according to pathogen pressure and weather forecasts"
        ],
        "medicines": [
            {
                "name": "Chlorothalonil 75% WP",
                "active_ingredient": "Chlorothalonil (Group M05)",
                "purpose": "Broad-spectrum contact protectant; inhibits fungal enzyme activity and prevents spore germination.",
                "guidance": "Foliar spray at 2.0–2.5 g/L of water. Ensure thorough coverage on lower foliage.",
                "safety_notes": "Wear chemical-resistant gloves, goggles, and respirator. Toxic to aquatic life. Pre-harvest interval (PHI): 7 days.",
                "frequency": "Apply every 7 to 10 days during favorable weather."
            },
            {
                "name": "Mancozeb 75% WP",
                "active_ingredient": "Mancozeb (Dithiocarbamate, Group M03)",
                "purpose": "Protective multi-site contact fungicide; controls Alternaria fungal mycelium development.",
                "guidance": "Mix 2.5 g/L of water and apply uniformly across the canopy.",
                "safety_notes": "Avoid skin contact; wear protective overalls. Do not graze treated fields. PHI: 14 days.",
                "frequency": "Repeat at 7–14 day intervals as required by disease pressure."
            },
            {
                "name": "Azoxystrobin 23% SC",
                "active_ingredient": "Azoxystrobin (Strobilurin, Group 11)",
                "purpose": "Translaminar and systemic fungicide for early curative and preventative control.",
                "guidance": "Apply 1.0 ml/L of water at first symptom onset. Do not apply more than 2 consecutive sprays.",
                "safety_notes": "Extremely toxic to certain apple varieties (drift hazard). Wear protective gear. PHI: 14 days.",
                "frequency": "Re-apply after 14 days in rotation with non-strobilurin fungicides."
            }
        ],
        "safety_precautions": [
            "Always wear personal protective equipment (PPE): nitrile gloves, protective goggles, and a particulate respirator",
            "Do not spray chemicals during high winds (>10 km/h) or temperatures above 30°C to avoid drift and crop burn",
            "Strictly observe the Pre-Harvest Interval (PHI) specified on the fungicide product label",
            "Keep all agricultural chemicals locked in original containers away from children, livestock, and drinking water sources",
            "Dispose of infected plant residues by burning or deep burial; do not compost diseased leaves"
        ],
        "prevention": [
            "Practice 3-to-4 year crop rotation with non-solanaceous crops (e.g., corn, legumes)",
            "Plant certified disease-free, high-vigor seed tubers",
            "Ensure optimal plant spacing (minimum 25-30 cm) to encourage rapid leaf drying",
            "Apply balanced nitrogen fertilizer; avoid excessive nitrogen that promotes lush, susceptible foliage",
            "Apply mulch to prevent soil-borne fungal spores from splashing onto lower leaves during rainfall"
        ]
    },

    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Late Blight",
        "scientific_name": "Phytophthora infestans",
        "is_healthy": False,
        "summary": "Late blight is a destructive oomycete disease capable of wiping out entire potato fields within days under cool, wet, humid conditions.",
        "symptoms": [
            "Irregular water-soaked pale-green to dark brown lesions on leaves and stems",
            "White velvety fungal/oomycete downy mildew on the underside of leaves in humid mornings",
            "Rapid necrosis spreading rapidly across the entire foliage turning leaves black and limp",
            "Distinct foul odor emanating from rapidly decaying infected plant tissue",
            "Purplish-brown dry rot lesions spreading to potato tubers"
        ],
        "immediate_actions": [
            "Immediately destroy and bury heavily infected plants to stop airborne zoospore spread",
            "Halt all overhead sprinkler irrigation immediately",
            "Alert neighboring farms about confirmed late blight sporulation in the locality",
            "Inspect field daily, focusing on low-lying or poorly ventilated shaded rows"
        ],
        "treatment": [
            "Apply specialized oomycete-targeted systemic fungicides immediately upon first detection",
            "Tank-mix systemic fungicides with contact protectants (e.g., Mancozeb or Copper) to reduce resistance risk",
            "Maintain continuous spray schedules while wet, cool (10–20°C) weather persists",
            "Ensure early morning spray applications when wind velocity is lowest"
        ],
        "medicines": [
            {
                "name": "Metalaxyl-M + Mancozeb (64% + 4% WP)",
                "active_ingredient": "Metalaxyl-M + Mancozeb (Phenylamide + Dithiocarbamate)",
                "purpose": "Systemic and contact dual action; rapidly halts internal oomycete growth and shields uninfected foliage.",
                "guidance": "Mix 2.5 g/L of water. Spray immediately at first warning or blight appearance.",
                "safety_notes": "Wear full protective chemical suit, boots, and face shield. PHI: 14 days.",
                "frequency": "Apply 1–2 applications spaced 10–12 days apart."
            },
            {
                "name": "Dimethomorph 50% WP",
                "active_ingredient": "Dimethomorph (CAA fungicide, Group 40)",
                "purpose": "Inhibits cell wall synthesis in oomycetes; provides strong curative and anti-sporulant action.",
                "guidance": "Mix 1.0–1.5 g/L of water in tank combination with contact fungicide.",
                "safety_notes": "Toxic to aquatic organisms. Prevent spray runoff into ponds or ditches. PHI: 7 days.",
                "frequency": "Apply every 7 to 10 days during high disease risk periods."
            },
            {
                "name": "Copper Hydroxide 77% WP",
                "active_ingredient": "Copper Hydroxide (Inorganic Copper, Group M01)",
                "purpose": "Contact multi-site protective barrier preventing zoospore germination on foliage.",
                "guidance": "Mix 2.0 g/L of water. Spray thoroughly before forecasted rain events.",
                "safety_notes": "Causes serious eye irritation. Wear chemical splash goggles. PHI: 3 days.",
                "frequency": "Repeat every 5–7 days when humid, wet conditions persist."
            }
        ],
        "safety_precautions": [
            "Wear full protective clothing including chemical-resistant apron, nitrile gloves, and respirator",
            "Never harvest wet tubers from a blight-infected field to avoid tuber rot in storage",
            "Decontaminate machinery, boots, and crates after exiting an infected field",
            "Comply strictly with environmental buffer zones near natural waterways",
            "Follow all local agricultural department regulations and disease outbreak notices"
        ],
        "prevention": [
            "Cultivate late-blight resistant or tolerant potato varieties (e.g., Sarpo Mira, Defender)",
            "Plant only certified pathogen-free seed potatoes tested for Phytophthora",
            "Maintain hill height (hilling up) with loose soil to prevent spores washing into tubers",
            "Eliminate all cull piles, volunteer potato plants, and solanaceous weeds near the field",
            "Harvest only after vines have been completely dead and dry for at least 14 days"
        ]
    },

    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy Plant",
        "scientific_name": "Solanum tuberosum",
        "is_healthy": True,
        "summary": "No visual signs of infectious pathogen disease or pest damage detected. The potato canopy exhibits vigorous vegetative growth.",
        "symptoms": [
            "Uniform vibrant green leaf coloration across the canopy",
            "Intact leaf lamina with well-defined margins and strong cuticle",
            "Absence of necrotic lesions, water-soaked spots, or chlorotic halos",
            "Normal vascular leaf venation and balanced stem development",
            "Smooth, healthy leaf surfaces without fungal mycelium or powdery growth"
        ],
        "immediate_actions": [
            "Continue standard agronomic management and balanced soil moisture monitoring",
            "Conduct routine twice-weekly scouting for early pest or pathogen presence",
            "Ensure good field aeration and weed-free row middles"
        ],
        "treatment": [
            "No chemical fungicide or bactericide treatment required at this time",
            "Optional: Apply bio-stimulant or balanced foliar micronutrients (Zinc, Boron) if required by soil test",
            "Maintain preventative biological soil health practices"
        ],
        "medicines": [
            {
                "name": "Preventative Organic Bio-Fungicide (Bacillus amyloliquefaciens)",
                "active_ingredient": "Bacillus amyloliquefaciens strain D747",
                "purpose": "Optional bio-protective preventive colonization of leaf surfaces against fungal colonization.",
                "guidance": "1.5 g/L of water as a preventative canopy misting.",
                "safety_notes": "OMRI listed organic input. Non-toxic. Minimum PPE required.",
                "frequency": "Optional monthly preventive application."
            }
        ],
        "safety_precautions": [
            "Maintain regular clean field hygiene and sanitized farming implements",
            "Avoid excessive synthetic fertilizer applications which can weaken cell wall defenses",
            "Store any agricultural supplies safely in a dry, ventilated shed"
        ],
        "prevention": [
            "Maintain consistent drip irrigation to keep root zones uniformly moist without foliage wetting",
            "Continue scheduled soil nutrient management based on periodic soil testing",
            "Maintain proper plant spacing (30 cm apart in 75 cm rows)",
            "Regularly scout underneath leaves and around lower canopies for early signs of blight"
        ]
    },

    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Early Blight",
        "scientific_name": "Alternaria linariae / Alternaria solani",
        "is_healthy": False,
        "summary": "Early blight is a major fungal disease of tomato plants, causing distinctive concentric target spots on foliage, stems, and fruits.",
        "symptoms": [
            "Brown to black circular necrotic spots with pronounced concentric target rings",
            "Prominent chlorotic yellow halos surrounding affected leaf tissue",
            "Symptoms initiate on oldest lower leaves and progress upward through the canopy",
            "Yellowing, browning, and desiccation of affected foliage leading to defoliation",
            "Sunscald vulnerability on fruit as canopy defoliates"
        ],
        "immediate_actions": [
            "Prune off lower infected leaves up to 30 cm from the ground level",
            "Sterilize cutting shears with isopropyl alcohol after each tomato plant",
            "Stake or cage tomato vines to lift all foliage completely off the soil",
            "Switch strictly to ground-level drip irrigation; do not wet foliage"
        ],
        "treatment": [
            "Initiate protective fungicide sprays immediately upon detecting initial leaf spots",
            "Alternate chemical classes (FRAC codes) to maintain high fungicidal efficacy",
            "Spray in early morning hours so residual moisture dries rapidly",
            "Ensure full coverage under the canopy where humidity remains highest"
        ],
        "medicines": [
            {
                "name": "Chlorothalonil 720 SC",
                "active_ingredient": "Chlorothalonil (Group M05)",
                "purpose": "Multi-site protective fungicide creating a chemical barrier against spore penetration.",
                "guidance": "Apply 2.0 ml/L of water. Spray canopy thoroughly until runoff.",
                "safety_notes": "Causes skin sensitization and eye injury. Wear goggles and chemical gloves. PHI: 1 day.",
                "frequency": "Every 7 to 10 days until harvest."
            },
            {
                "name": "Difenoconazole 25% EC",
                "active_ingredient": "Difenoconazole (Triazole, Group 3)",
                "purpose": "Systemic curative and preventative fungicide that halts fungal sterol biosynthesis.",
                "guidance": "Mix 0.5–0.75 ml/L of water. Apply at first sign of target spots.",
                "safety_notes": "Wear respirator during mixing. PHI: 7 days.",
                "frequency": "Apply maximum 2 times per season, rotated with contact fungicides."
            },
            {
                "name": "Copper Oxychloride 50% WP",
                "active_ingredient": "Copper Oxychloride (Group M01)",
                "purpose": "Broad-spectrum contact protectant against Alternaria and bacterial secondary infections.",
                "guidance": "Mix 2.5 g/L of water. Apply uniform mist over foliage.",
                "safety_notes": "Do not apply in temperatures exceeding 32°C. PHI: 1 day.",
                "frequency": "Repeat at 7–10 day intervals during wet periods."
            }
        ],
        "safety_precautions": [
            "Wear waterproof gloves, protective eyewear, and long sleeves during spray preparation",
            "Avoid spraying immediately before predicted rain events to prevent chemical runoff",
            "Respect the 1-day to 7-day pre-harvest intervals before picking ripe tomatoes",
            "Bag and discard removed foliage in closed trash bags; never leave clippings on field floor"
        ],
        "prevention": [
            "Implement a minimum 3-year crop rotation without tomatoes, potatoes, or eggplants",
            "Apply straw, plastic, or organic mulch beneath plants to block soil splash",
            "Stake and prune indeterminate tomatoes to maintain open, well-aerated canopies",
            "Plant early-blight tolerant cultivars (e.g., Mountain Supreme, Defiant, Iron Lady)",
            "Disinfect stakes, trellises, and greenhouse structures between growing seasons"
        ]
    },

    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Late Blight",
        "scientific_name": "Phytophthora infestans",
        "is_healthy": False,
        "summary": "Late blight is a fast-moving, devastating oomycete disease of tomatoes, causing oily dark lesions, white underside sporulation, and rapid plant collapse.",
        "symptoms": [
            "Greasy, water-soaked irregular lesions rapidly turning dark brown to black",
            "Delicate white downy fungal growth on the undersides of leaves during high humidity",
            "Dark brown to black greasy lesions on petioles and main stems causing vine breakage",
            "Golden-brown, firm, rough sunken rot on green and ripe tomato fruits",
            "Entire foliage wilts, turns brown, and shrivels rapidly as if struck by severe frost"
        ],
        "immediate_actions": [
            "Bag and remove infected tomato plants entirely; do not compost",
            "Cease all sprinkler or overhead irrigation immediately",
            "Inspect nearby tomato and potato plants across the entire plot",
            "Inform local agricultural extension services or farm alert networks"
        ],
        "treatment": [
            "Apply targeted anti-oomycete systemic fungicides without delay",
            "Combine systemic translaminar fungicides with broad-spectrum contact fungicides",
            "Re-apply fungicides frequently (every 5-7 days) while rainy or humid conditions prevail",
            "Ensure coverage reaches the undersides of leaves where sporangia emerge"
        ],
        "medicines": [
            {
                "name": "Cymoxanil + Mancozeb (8% + 64% WP)",
                "active_ingredient": "Cymoxanil + Mancozeb (Cyanoacetamide-oxime + Dithiocarbamate)",
                "purpose": "Locally systemic kickback curative and multi-site protective combination.",
                "guidance": "Mix 2.5 g/L of water. Spray immediately upon blight confirmation.",
                "safety_notes": "Wear full PPE: nitrile gloves, coveralls, chemical goggles. PHI: 7 days.",
                "frequency": "Repeat after 7 days if weather conditions remain favorable for blight."
            },
            {
                "name": "Fluopicolide + Propamocarb HCl (62.5 SC)",
                "active_ingredient": "Fluopicolide + Propamocarb (Acylpicolide + Carbamate)",
                "purpose": "Powerful anti-sporulant that stops zoospore release and germ tube elongation.",
                "guidance": "Mix 1.5–2.0 ml/L of water. Apply evenly across whole tomato vine.",
                "safety_notes": "Toxic to aquatic invertebrates. Prevent spray drift into waterways. PHI: 3 days.",
                "frequency": "Apply at 7–10 day intervals during high risk periods."
            },
            {
                "name": "Copper Hydroxide 53.8% WG",
                "active_ingredient": "Copper Hydroxide (Group M01)",
                "purpose": "Contact multi-site spore barrier protecting developing leaves and fruit.",
                "guidance": "Mix 1.5–2.0 g/L of water. Ensure thorough canopy wetting.",
                "safety_notes": "Skin and eye irritant. Wear eye protection. PHI: 1 day.",
                "frequency": "Apply every 5–7 days while cool, damp weather continues."
            }
        ],
        "safety_precautions": [
            "Always wear full PPE: respirator mask, eye protection, and rubber gloves",
            "Never leave blighted vines or fruit on the soil; bury them at least 60 cm underground",
            "Strictly observe the Pre-Harvest Interval (PHI) before picking tomatoes",
            "Wash hands, boots, and tools thoroughly with disinfectant before moving to clean plots"
        ],
        "prevention": [
            "Select resistant tomato hybrids (e.g., Mountain Magic, Plum Regal, Legend, Defiant)",
            "Plant in full sun with rows oriented in the direction of prevailing winds for quick drying",
            "Maintain wide plant spacing (at least 60–90 cm between plants)",
            "Remove all volunteer tomato and potato plants emerging from previous seasons",
            "Never bring uncertified tomato transplants into the field without rigorous inspection"
        ]
    },

    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato",
        "disease": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "scientific_name": "Tomato yellow leaf curl begomovirus (TYLCV)",
        "is_healthy": False,
        "summary": "TYLCV is a severe viral disease transmitted by the silverleaf whitefly (Bemisia tabaci), causing stunted growth, severe upward leaf cupping, and crop failure.",
        "symptoms": [
            "Severe upward curling and cupping of tomato leaflets",
            "Pronounced interveinal yellowing (chlorosis) with reduced leaf size",
            "Erect, bushy, stunted plant growth with bunched internodes",
            "Severe blossom drop leading to negligible fruit set",
            "Fruit formed prior to infection remains small, pale, and unmarketable"
        ],
        "immediate_actions": [
            "Rogue out (uproot) severely infected plants, seal in plastic bags, and destroy",
            "Install yellow sticky traps immediately to monitor and trap adult whitefly populations",
            "Inspect underside of leaves for whitefly nymphs and adults",
            "Erect 50-mesh insect-proof netting in greenhouse or nursery seedling areas"
        ],
        "treatment": [
            "Viruses cannot be cured with fungicides; focus entirely on controlling the whitefly vector",
            "Apply systemic insecticides targeting both nymphal and adult whitefly stages",
            "Rotate insecticidal modes of action (IRAC codes) to avoid rapid whitefly resistance",
            "Apply insecticidal soap or horticultural oil to smother whitefly nymphs under leaves"
        ],
        "medicines": [
            {
                "name": "Imidacloprid 17.8% SL",
                "active_ingredient": "Imidacloprid (Neonicotinoid, IRAC Group 4A)",
                "purpose": "Systemic insecticide absorbed through foliage and roots to kill sap-sucking whiteflies.",
                "guidance": "Foliar spray at 0.5 ml/L of water or soil drench around root zone at 1.0 ml/L.",
                "safety_notes": "Extremely toxic to bees and pollinators. Never apply during open bloom. PHI: 7 days.",
                "frequency": "Single application at seedling or early vegetative stage."
            },
            {
                "name": "Spiromesifen 22.9% SC",
                "active_ingredient": "Spiromesifen (Tetronic acid, IRAC Group 23)",
                "purpose": "Lipid biosynthesis inhibitor; highly effective against whitefly nymphs and eggs.",
                "guidance": "Mix 1.0 ml/L of water. Spray thoroughly covering the undersides of leaves.",
                "safety_notes": "Wear protective gloves and mask. Avoid skin and eye contact. PHI: 3 days.",
                "frequency": "Apply once when nymph populations begin rising."
            },
            {
                "name": "Cold-Pressed Neem Oil (Azadirachtin 10,000 PPM)",
                "active_ingredient": "Azadirachtin (Botanical insecticide/antifeedant)",
                "purpose": "Organic insect growth regulator; disrupts whitefly feeding, egg laying, and molting.",
                "guidance": "Mix 3–5 ml/L of water with an organic emulsifier/soap. Spray in the cool evening.",
                "safety_notes": "Organic input; minimal toxicity to mammals. Safe for beneficial predators if used properly.",
                "frequency": "Repeat every 5–7 days for continuous repellent protection."
            }
        ],
        "safety_precautions": [
            "Never apply neonicotinoid insecticides while bees are actively foraging or plants are flowering",
            "Wear protective chemical goggles, respirator, and nitrile gloves during mixing and spraying",
            "Dispose of empty insecticide containers according to hazardous agricultural waste standards",
            "Keep farm workers out of treated areas during the designated re-entry interval (REI)"
        ],
        "prevention": [
            "Plant TYLCV-resistant tomato cultivars (e.g., Tycoon, Charger, Invictus, Foronti)",
            "Grow seedlings under fine 50-mesh insect netting to protect young plants before field planting",
            "Use reflective silver polyethylene mulch to disorient incoming flying whiteflies",
            "Maintain a 60-day host-free period between consecutive tomato or solanaceous plantings",
            "Eradicate alternative weed hosts (e.g., Datura, Malva, Solanum nigrum) around farm perimeters"
        ]
    },

    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Bacterial Spot",
        "scientific_name": "Xanthomonas perforans / Xanthomonas vesicatoria",
        "is_healthy": False,
        "summary": "Bacterial spot is a damaging bacterial disease that causes dark angular lesions, leaf drop, and rough scabby blisters on tomato fruit in hot, rainy weather.",
        "symptoms": [
            "Small (less than 3 mm), dark, water-soaked angular leaf spots",
            "Spots turn brown to black with a distinctive chlorotic yellow halo",
            "Centers of older lesions may dry, tear, and drop out, creating a shot-hole appearance",
            "Extensive leaf yellowing, browning, and premature defoliation exposing fruit to sunscald",
            "Black raised blister-like spots on green tomatoes with scabby, cracked centers"
        ],
        "immediate_actions": [
            "Never cultivate, prune, or harvest tomato plants when foliage is wet with rain or dew",
            "Disinfect all cutting implements with 10% household bleach or quaternary ammonium solution",
            "Isolate and mark infected areas in the row to prevent human and equipment spread",
            "Avoid overhead irrigation; splash droplets are the primary vehicle for bacterial dispersion"
        ],
        "treatment": [
            "Standard synthetic fungicides are ineffective against bacteria; use copper-bactericide tank mixes",
            "Combine fixed copper compounds with Mancozeb to enhance copper bactericidal efficacy",
            "Apply systemic acquired resistance (SAR) inducers to activate the tomato plant's natural defenses",
            "Ensure regular applications during periods of continuous rainfall and high temperatures (24–30°C)"
        ],
        "medicines": [
            {
                "name": "Copper Hydroxide + Mancozeb Tank Mix",
                "active_ingredient": "Copper Hydroxide (Group M01) + Mancozeb (Group M03)",
                "purpose": "Synergistic bactericidal and protective mix; copper ions rupture bacterial cell walls.",
                "guidance": "Mix 2.0 g/L Copper Hydroxide + 2.0 g/L Mancozeb in water. Spray canopy thoroughly.",
                "safety_notes": "Causes serious eye irritation. Wear chemical splash goggles and nitrile gloves. PHI: 5 days.",
                "frequency": "Apply every 7 days during warm, rainy weather."
            },
            {
                "name": "Streptomycin Sulfate 9% + Tetracycline Hydrochloride 1% SP",
                "active_ingredient": "Agrimycin / Plant Streptomycin (Agricultural Antibiotic)",
                "purpose": "Curative bactericide for critical seedbed or emergency field infection control where registered.",
                "guidance": "Mix 0.5–1.0 g/L of water. Check local agricultural pesticide regulations for authorization.",
                "safety_notes": "Subject to strict regional regulatory restrictions to prevent resistance. PHI: 14 days.",
                "frequency": "Maximum 2 applications per season during severe outbreaks."
            },
            {
                "name": "Bacillus subtilis strain QST 713",
                "active_ingredient": "Bacillus subtilis (Bio-bactericide)",
                "purpose": "Bio-fungicide/bactericide; produces lipopeptides that inhibit bacterial colonization.",
                "guidance": "Mix 2.5–3.0 ml/L of water. Safe for continuous preventive spraying.",
                "safety_notes": "OMRI listed organic bio-pesticide. Minimal toxicity. PHI: 0 days (can apply up to harvest).",
                "frequency": "Apply every 5 to 7 days preventatively."
            }
        ],
        "safety_precautions": [
            "Wear full protective eye shields and gloves when handling copper compounds",
            "Do not enter wet fields after treatment; wait until foliage has dried completely",
            "Do not exceed maximum seasonal copper application limits to prevent heavy metal soil accumulation",
            "Dispose of wash water away from natural water bodies and irrigation wells"
        ],
        "prevention": [
            "Purchase certified pathogen-free, hot-water treated tomato seeds",
            "Select bacterial-spot tolerant cultivars if available locally",
            "Rotate fields with non-host crops (corn, beans, brassicas) for at least 2 consecutive years",
            "Use plastic mulch and drip tape to prevent soil bacteria from splashing onto foliage",
            "Deep-plow or destroy tomato crop debris immediately following the final harvest"
        ]
    },

    "Tomato___healthy": {
        "crop": "Tomato",
        "disease": "Healthy Plant",
        "scientific_name": "Solanum lycopersicum",
        "is_healthy": True,
        "summary": "The tomato plant exhibits normal physiological vigor without evidence of viral, bacterial, or fungal pathogens.",
        "symptoms": [
            "Vibrant, uniform green leaf coloration across the canopy",
            "Normal serrated leaflet morphology with intact epidermal cuticle",
            "No necrotic spots, water-soaked lesions, or yellowing halos",
            "Firm upright stems with active flower clusters and normal fruit set",
            "Clean leaf undersides free of fungal sporulation, downy growth, or pest webbing"
        ],
        "immediate_actions": [
            "Maintain current balanced irrigation and fertilization schedule",
            "Perform bi-weekly visual scouting on lower leaves and new shoot growth",
            "Maintain clean trellising and weed-free row beds"
        ],
        "treatment": [
            "No therapeutic chemical application required",
            "Maintain preventative biological canopy protection or seaweed foliar tonics",
            "Monitor soil electrical conductivity (EC) and pH (ideal 6.0–6.8)"
        ],
        "medicines": [
            {
                "name": "Foliar Seaweed Extract + Micronutrient Booster",
                "active_ingredient": "Ascophyllum nodosum extract with Zn, B, Fe",
                "purpose": "Optional bio-stimulant enhancing chlorophyll synthesis and natural crop vigor.",
                "guidance": "Mix 2.0 ml/L of water. Spray lightly over canopy during cool morning hours.",
                "safety_notes": "Non-toxic organic fertilizer product. Safe handling.",
                "frequency": "Every 14–21 days during flowering and fruit sizing."
            }
        ],
        "safety_precautions": [
            "Keep pruning shears sanitized before training healthy vines",
            "Avoid nitrogen over-fertilization which produces soft tissue vulnerable to pathogens",
            "Store farm tools and fertilizers in clean, dry storage areas"
        ],
        "prevention": [
            "Ensure steady soil moisture using automated drip emitters",
            "Maintain sturdy staking or Florida-weave trellis to maximize air flow",
            "Mulch beds with clean organic or polyethylene barriers",
            "Inspect weekly for early signs of aphids, whiteflies, or hornworms"
        ]
    },

    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "disease": "Leaf Mold",
        "scientific_name": "Passalora fulva (formerly Cladosporium fulvum)",
        "is_healthy": False,
        "summary": "Leaf mold is a high-humidity fungal disease primarily attacking greenhouse and tunnel tomatoes, producing yellow upper-leaf spots and olive-green velvety mold underneath.",
        "symptoms": [
            "Pale green to distinct yellow chlorotic spots on the upper leaf surface",
            "Dense, velvety, olive-green to grayish-brown fungal mycelium on corresponding leaf undersides",
            "Infected leaves curl, wither, and prematurely drop, starting from the lower canopy",
            "Blossoms may become infected and drop before setting fruit",
            "High severity in protected structures where relative humidity exceeds 85%"
        ],
        "immediate_actions": [
            "Increase greenhouse/tunnel ventilation immediately; open sidewalls and run circulation fans",
            "Heat or ventilate protected structures at sunset to prevent dew condensation on leaves",
            "Prune bottom leaves to improve under-canopy air movement",
            "Cease all overhead watering immediately"
        ],
        "treatment": [
            "Apply protective and curative fungicides registered for tomato leaf mold",
            "Maintain good airflow so chemical deposits dry quickly across both leaf faces",
            "Alternate systemic fungicides with protectants to avert resistance development",
            "Ensure spray nozzles are angled upward to coat the underside of the foliage"
        ],
        "medicines": [
            {
                "name": "Chlorothalonil 75% WP",
                "active_ingredient": "Chlorothalonil (Group M05)",
                "purpose": "Broad-spectrum multi-site protectant preventing fungal conidia germination.",
                "guidance": "Mix 2.0 g/L of water. Apply ensuring complete under-leaf coverage.",
                "safety_notes": "Wear eye protection and respirator. Toxic to aquatic life. PHI: 1 day.",
                "frequency": "Every 7–10 days during periods of high humidity."
            },
            {
                "name": "Difenoconazole + Azoxystrobin (20% + 12.5% SC)",
                "active_ingredient": "Difenoconazole + Azoxystrobin (Triazole + Strobilurin)",
                "purpose": "Dual systemic curative and preventative treatment that halts internal fungal mycelia.",
                "guidance": "Mix 1.0 ml/L of water. Spray at first sign of velvety under-leaf sporulation.",
                "safety_notes": "Wear nitrile gloves and goggles. Maximum 2 sprays per season. PHI: 7 days.",
                "frequency": "Repeat after 10–14 days if needed."
            },
            {
                "name": "Potassium Bicarbonate (Bio-Fungicide)",
                "active_ingredient": "Potassium Bicarbonate 85% SP",
                "purpose": "Organic contact curative; alters leaf surface pH to rupture fungal spores.",
                "guidance": "Mix 3.0–4.0 g/L of water with an organic wetting agent.",
                "safety_notes": "OMRI listed organic input. Non-toxic. Safe for indoor greenhouse usage. PHI: 0 days.",
                "frequency": "Apply every 5 to 7 days as a preventative or early curative."
            }
        ],
        "safety_precautions": [
            "Wear respirator and eye protection when spraying inside enclosed high tunnels or greenhouses",
            "Do not re-enter enclosed structures until spray mist has fully settled and dried (minimum 4 hours)",
            "Follow product PHI guidelines before picking tomatoes for consumption",
            "Dispose of pruned moldy foliage outside the greenhouse perimeter in sealed bags"
        ],
        "prevention": [
            "Grow tomato varieties carrying resistant genes (Cf-2, Cf-4, Cf-5, or Cf-9)",
            "Maintain relative humidity inside greenhouse structures strictly below 80%",
            "Provide ample spacing between rows (at least 1.2–1.5 m) to facilitate airflow",
            "Install horizontal airflow fans to keep air moving constantly over leaf surfaces",
            "Thoroughly clean and disinfect greenhouse structures, trellises, and ground sheets between crops"
        ]
    },

    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "disease": "Target Spot",
        "scientific_name": "Corynespora cassiicola",
        "is_healthy": False,
        "summary": "Target spot is a fungal pathogen causing dark brown lesions with subtle target rings on leaves, stems, and sunken circular rots on tomato fruit.",
        "symptoms": [
            "Small pinpoint brown necrotic spots expanding into circular lesions with light brown centers",
            "Faint concentric rings visible inside mature spots resembling a target board",
            "Dark brown margins around lesions with chlorotic yellow surrounding leaf halos",
            "Lesions coalesce, causing large blighted zones, leaf curling, and severe canopy defoliation",
            "Deep, sunken, circular brown lesions on green and ripening tomato fruit"
        ],
        "immediate_actions": [
            "Prune off heavily infected lower foliage and remove from the field area",
            "Sanitize pruning equipment between rows with 70% alcohol",
            "Transition to drip irrigation; eliminate any splashing water",
            "Widen row spacing and prune suckers to improve airflow"
        ],
        "treatment": [
            "Apply registered foliar fungicides upon detection of initial target spots",
            "Rotate strobilurin or carboxamide fungicides with multi-site contact protectants",
            "Direct spray coverage thoroughly into the dense middle and lower canopy layers",
            "Maintain spray schedules while warm (25–30°C) and humid conditions continue"
        ],
        "medicines": [
            {
                "name": "Pyraclostrobin + Boscalid (6.8% + 13.6% WG)",
                "active_ingredient": "Pyraclostrobin + Boscalid (Strobilurin + SDHI, Group 11 + 7)",
                "purpose": "Dual systemic fungicide providing powerful curative and preventative protection against Corynespora.",
                "guidance": "Mix 1.0–1.2 g/L of water. Spray thoroughly covering whole canopy.",
                "safety_notes": "Wear full PPE: gloves, goggles, respirator. Toxic to aquatic organisms. PHI: 0 days.",
                "frequency": "Apply maximum 2 consecutive sprays, spaced 10–14 days apart."
            },
            {
                "name": "Chlorothalonil 720 SC",
                "active_ingredient": "Chlorothalonil (Group M05)",
                "purpose": "Contact multi-site protectant creating an unpenetrable barrier on foliage.",
                "guidance": "Mix 2.0 ml/L of water. Spray to full canopy coverage.",
                "safety_notes": "Skin and eye irritant. Wear protective overalls. PHI: 1 day.",
                "frequency": "Every 7–10 days during periods of frequent rainfall."
            },
            {
                "name": "Mancozeb 75% WP",
                "active_ingredient": "Mancozeb (Group M03)",
                "purpose": "Protective contact fungicide that inhibits multiple fungal spore enzymes.",
                "guidance": "Mix 2.5 g/L of water. Apply evenly before anticipated rains.",
                "safety_notes": "Wear chemical-resistant gloves. PHI: 5 days.",
                "frequency": "Repeat at 7–10 day intervals as needed."
            }
        ],
        "safety_precautions": [
            "Wear eye protection and nitrile gloves when measuring and mixing fungicides",
            "Never apply chemicals during windy conditions to avoid accidental drift onto nearby waterways",
            "Comply strictly with product Pre-Harvest Intervals before picking fruit",
            "Clean and triple-rinse spray equipment in an approved wash bay"
        ],
        "prevention": [
            "Avoid planting tomatoes adjacent to old cucumber, cotton, or soybean fields which host Corynespora",
            "Ensure generous plant spacing and prune suckers to maintain open canopy ventilation",
            "Rotate crops for at least 3 years with non-susceptible species (grasses, corn)",
            "Apply clean plastic mulch to suppress soil splash during heavy downpours",
            "Disinfect stakes, wires, and equipment thoroughly at the end of each season"
        ]
    },

    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "crop": "Tomato",
        "disease": "Two-Spotted Spider Mite Infestation",
        "scientific_name": "Tetranychus urticae",
        "is_healthy": False,
        "summary": "Spider mites are microscopic arachnid pests that suck plant sap from leaf cells, creating yellow stippling, fine silken webbing, and bronzed drying foliage in hot, dry conditions.",
        "symptoms": [
            "Fine yellow, white, or bronze stippling (speckling) across the upper leaf surface",
            "Delicate silken webbing visible on leaf undersides, growing tips, and flower clusters",
            "Leaves turn chlorotic, bronze, dry out, and take on a scorched appearance",
            "Severe canopy defoliation and flower drop under severe mite populations",
            "Tiny crawling red or greenish-yellow mites visible on leaf undersides under 10x hand lens"
        ],
        "immediate_actions": [
            "Isolate heavily infested plants; prune off heavily webbed leaves and bag immediately",
            "Spray plants with a firm stream of clean water to knock mites off and disrupt webbing",
            "Avoid broad-spectrum synthetic pyrethroid insecticides which kill natural mite predators",
            "Increase relative humidity in greenhouse settings; spider mites thrive in hot, arid conditions"
        ],
        "treatment": [
            "Apply specialized miticides/acaricides targeting multiple life stages (eggs, nymphs, adults)",
            "Ensure spray thoroughly coats leaf undersides where mites live and lay eggs",
            "Release biological predatory mites (e.g., Phytoseiulus persimilis, Neoseiulus californicus)",
            "Rotate miticides with different IRAC modes of action to prevent rapid resistance buildup"
        ],
        "medicines": [
            {
                "name": "Abamectin 1.9% EC",
                "active_ingredient": "Abamectin (Avermectin, IRAC Group 6)",
                "purpose": "Translaminar miticide absorbed into leaf tissue, poisoning mites as they feed.",
                "guidance": "Mix 0.5 ml/L of water. Spray thoroughly, focusing on the undersides of leaves.",
                "safety_notes": "Highly toxic to bees and aquatic life. Apply at dusk when pollinators are not active. PHI: 3 days.",
                "frequency": "Apply once; repeat after 7–10 days if surviving nymphs emerge."
            },
            {
                "name": "Bifenazate 50% WP",
                "active_ingredient": "Bifenazate (Carbazate, IRAC Group 20D)",
                "purpose": "Selective miticide offering fast knockdown and long residual control with minimal harm to predatory mites.",
                "guidance": "Mix 0.6 g/L of water. Apply at first sign of stippling.",
                "safety_notes": "Wear gloves and eye goggles. Do not make more than 2 applications per crop cycle. PHI: 3 days.",
                "frequency": "Single application with minimum 14-day interval before any repeat."
            },
            {
                "name": "Insecticidal Soap / Horticultural Potassium Salts (49.5%)",
                "active_ingredient": "Potassium salts of fatty acids",
                "purpose": "Organic contact miticide; dissolves the protective cuticle of mites causing rapid dehydration.",
                "guidance": "Mix 15–20 ml/L of water. Spray thoroughly covering all leaf undersides in the evening.",
                "safety_notes": "OMRI listed organic input. Non-toxic to humans. Do not spray in direct sunlight or above 30°C. PHI: 0 days.",
                "frequency": "Repeat every 3 to 5 days until mite population is eradicated."
            }
        ],
        "safety_precautions": [
            "Wear protective eyewear, rubber gloves, and a mask during miticide spraying",
            "Do not spray abamectin during active bee foraging hours; apply strictly in the late evening",
            "Never harvest tomatoes before the product pre-harvest interval has elapsed",
            "Wash hands thoroughly after inspecting or handling mite-infested foliage"
        ],
        "prevention": [
            "Avoid allowing tomato plants to suffer from drought stress; keep irrigation consistent",
            "Keep farm roadways and row paths dampened or vegetated to suppress dust (dust promotes mites)",
            "Introduce beneficial predatory mites (Phytoseiulus persimilis) preventatively in greenhouses",
            "Inspect field edges and weed borders weekly with a 10x pocket magnifier",
            "Eradicate broadleaf weeds (e.g., pigweed, morning glory) that serve as overwintering mite reservoirs"
        ]
    },

    "Cherry___Powdery_mildew": {
        "crop": "Cherry",
        "disease": "Powdery Mildew",
        "scientific_name": "Podosphaera clandestina",
        "is_healthy": False,
        "summary": "Powdery mildew is a fungal disease of sweet and sour cherry trees, producing white powdery fungal patches on new leaves, shoots, and developing fruit.",
        "symptoms": [
            "White to grayish-white powdery fungal coating on young expanding leaves and shoot tips",
            "Leaf margins curl upward, pucker, and distort, often turning pinkish or reddish",
            "Shoots become stunted, brittle, and exhibit delayed growth or tip dieback",
            "Young developing cherry fruit develops white superficial fungal patches or web-like scarring",
            "Severely affected fruit shrivels, cracks, or fails to ripen properly"
        ],
        "immediate_actions": [
            "Prune out infected powdery shoot tips and destroy them to reduce seasonal inoculum",
            "Disinfect pruning shears with 70% ethanol after pruning infected branches",
            "Prune interior canopy branches during winter or dry periods to maximize sun penetration and air circulation",
            "Avoid high rates of nitrogen fertilizer which trigger excessive tender shoot flushes"
        ],
        "treatment": [
            "Apply preventative fungicides beginning at petal fall when young leaves emerge",
            "Maintain spray protection through shuck fall and until fruit development completes",
            "Rotate DMIs (Group 3), SDHIs (Group 7), and Strobilurins (Group 11) with sulfur to avoid resistance",
            "Ensure complete coverage of the upper and interior tree canopy"
        ],
        "medicines": [
            {
                "name": "Micronized Wettable Sulfur 80% WDG",
                "active_ingredient": "Elemental Sulfur (Group M02)",
                "purpose": "Multi-site contact protectant and vapor-action fungicide preventing spore germination.",
                "guidance": "Mix 3.0–4.0 g/L of water. Spray thoroughly covering new foliage.",
                "safety_notes": "Do not apply within 14 days of horticultural oil or when temperatures exceed 30°C (causes phytotoxicity). PHI: 1 day.",
                "frequency": "Apply every 7 to 10 days from petal fall onward."
            },
            {
                "name": "Myclobutanil 20% EW",
                "active_ingredient": "Myclobutanil (Triazole / DMI, Group 3)",
                "purpose": "Systemic fungicide with protective and post-infection curative activity against powdery mildew.",
                "guidance": "Mix 0.4–0.5 ml/L of water. Spray evenly over tree canopy.",
                "safety_notes": "Wear chemical-resistant gloves and goggles. Maximum 3 applications per season. PHI: 7 days.",
                "frequency": "Apply at 10–14 day intervals in rotation with non-DMI fungicides."
            },
            {
                "name": "Potassium Bicarbonate (Bio-Fungicide 85%)",
                "active_ingredient": "Potassium Bicarbonate",
                "purpose": "Organic contact curative; disrupts cell membrane integrity of powdery mildew conidia on contact.",
                "guidance": "Mix 3.0 g/L of water with a horticultural wetting agent.",
                "safety_notes": "OMRI listed organic. Safe for farm workers. No harmful environmental residue. PHI: 0 days.",
                "frequency": "Apply every 7 days as needed."
            }
        ],
        "safety_precautions": [
            "Wear protective chemical goggles, respirator, and gloves when spraying orchard canopies",
            "Never spray wettable sulfur in hot weather (>30°C) to prevent leaf burn and fruit injury",
            "Observe mandatory pre-harvest intervals before picking cherries for market",
            "Do not discharge orchard spray tank remnants into streams or irrigation ditches"
        ],
        "prevention": [
            "Prune cherry trees annually with an open-center or central-leader architecture for maximum sunlight penetration",
            "Avoid overhead orchard sprinklers; use drip lines or low-angle under-tree microsprinklers",
            "Plant resistant or less-susceptible cherry cultivars where powdery mildew pressure is historically severe",
            "Monitor new terminal shoot growth closely twice a week from early spring through midsummer",
            "Collect and shred or bury fallen orchard leaves in autumn to reduce overwintering chasmothecia"
        ]
    },

    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "disease": "Tomato Mosaic Virus (ToMV)",
        "scientific_name": "Tomato mosaic tobamovirus (ToMV)",
        "is_healthy": False,
        "summary": "ToMV is an exceptionally stable and contagious viral disease transmitted mechanically via hands, tools, and infected seeds, causing mottled leaves and distorted growth.",
        "symptoms": [
            "Prominent light and dark green mosaic or mottling on tomato leaves",
            "Leaf distortion, strapping, narrowing, or severe fern-leaf blistering",
            "Stunted plant stature and shortened internodes throughout the vine",
            "Internal brown browning (necrosis) inside green and ripe tomato fruit walls",
            "Uneven fruit ripening, blotchiness, and reduced overall crop yield"
        ],
        "immediate_actions": [
            "Immediately remove and bag infected plants; do not drag through the field",
            "Require all workers to wash hands with warm water and soap or 20% non-fat dry milk solution",
            "Strictly prohibit tobacco smoking, chewing, or handling around tomato crops (tobacco carries virus)",
            "Disinfect all tools, trellising stakes, and clips in 20% non-fat dry milk or 10% bleach"
        ],
        "treatment": [
            "There are no chemical pesticides, antibiotics, or cures for viral infections once established",
            "Focus entirely on strict phytosanitary hygiene and preventing mechanical transmission",
            "Immediately destroy infected plants to protect surrounding healthy crop rows",
            "Provide optimal balanced fertilization to help undamaged plants maintain productivity"
        ],
        "medicines": [
            {
                "name": "Non-Fat Dry Milk Solution (Phytosanitary Tool Wash)",
                "active_ingredient": "20% Reconstituted skim milk / powdered milk proteins",
                "purpose": "Inactivates viral particles on hands, gloves, pruning shears, and harvesting crates via protein binding.",
                "guidance": "Dissolve 200 g of powdered skim milk per liter of water. Dip tools and hands frequently during pruning.",
                "safety_notes": "Completely non-toxic food product. Safe for unrestricted field use. PHI: 0 days.",
                "frequency": "Use continuously between pruning individual plants."
            },
            {
                "name": "Trisodium Phosphate (TSP 10%) Disinfectant",
                "active_ingredient": "Trisodium Phosphate",
                "purpose": "Heavy-duty viral disinfectant for sterilizing greenhouse benches, stakes, and pruning knives.",
                "guidance": "Dissolve 100 g per liter of water. Soak stakes and pruning knives for 15 minutes.",
                "safety_notes": "Strongly alkaline. Wear eye goggles and heavy rubber gloves. Do not apply directly to living foliage.",
                "frequency": "Clean tools between every work row or bed."
            }
        ],
        "safety_precautions": [
            "Always disinfect hands and pruning equipment before moving between tomato greenhouses or rows",
            "Prohibit farm workers from using tobacco products anywhere on the farm grounds",
            "Bury or incinerate culled infected tomato plants far from production fields",
            "Avoid entering tomato rows when plants are wet with morning dew"
        ],
        "prevention": [
            "Plant certified ToMV-resistant tomato hybrids (look for 'Tm-2' or 'Tm-2a' genetic resistance)",
            "Use only certified virus-free seed treated with trisodium phosphate or dry heat (70°C for 4 days)",
            "Do not handle tomato plants after touching tobacco products without rigorous hand-washing",
            "Maintain strict greenhouse quarantine and tool dipping protocols",
            "Rotate field with non-solanaceous crops for a minimum of 2 years"
        ]
    },

    "Pepper___Bacterial_spot": {
        "crop": "Pepper",
        "disease": "Bacterial Spot",
        "scientific_name": "Xanthomonas euvesicatoria / Xanthomonas perforans",
        "is_healthy": False,
        "summary": "Bacterial spot on bell and chili peppers causes dark water-soaked leaf spots, extensive defoliation, and raised warty lesions on pepper fruits.",
        "symptoms": [
            "Small (1–3 mm) water-soaked circular to irregular dark spots on leaves",
            "Lesions turn purplish-brown to black with a pale green or yellow chlorotic halo",
            "Infected leaves turn yellow and drop off rapidly, exposing peppers to sunscald",
            "Stems develop elongated dark brown cankers",
            "Raised, circular, rough warty pustules (scabs) on developing pepper pods"
        ],
        "immediate_actions": [
            "Stay out of pepper rows when plants are wet from rain or dew to prevent spreading bacteria",
            "Sanitize pruning and harvesting tools with 70% alcohol or quaternary ammonium disinfectant",
            "Remove and destroy severely infected pepper plants",
            "Switch off overhead sprinkler irrigation immediately"
        ],
        "treatment": [
            "Apply copper bactericide combined with Mancozeb to control bacterial multiplication",
            "Begin protective spray program at first transplanting or prior to rainy storm fronts",
            "Apply biological bactericides (Bacillus subtilis) in rotation to reduce copper accumulation",
            "Ensure spray nozzles deliver fine mist covering the undersides of the foliage"
        ],
        "medicines": [
            {
                "name": "Copper Hydroxide + Mancozeb (Tank Mix)",
                "active_ingredient": "Copper Hydroxide 77% WP + Mancozeb 75% WP",
                "purpose": "Synergistic bactericidal and protective contact barrier rupture bacterial cell walls.",
                "guidance": "Mix 2.0 g/L Copper Hydroxide + 2.0 g/L Mancozeb. Spray to wet all foliage thoroughly.",
                "safety_notes": "Causes eye irritation. Wear chemical splash goggles, mask, and nitrile gloves. PHI: 3 days.",
                "frequency": "Apply every 7 to 10 days during warm, rainy weather."
            },
            {
                "name": "Bacillus amyloliquefaciens strain D747",
                "active_ingredient": "Bacillus amyloliquefaciens (Bio-Bactericide)",
                "purpose": "Colonizes leaf surfaces and produces natural antimicrobial metabolites against Xanthomonas.",
                "guidance": "Mix 2.0 g/L of water. Apply as a preventive spray.",
                "safety_notes": "OMRI listed organic input. Non-toxic. PHI: 0 days.",
                "frequency": "Every 5–7 days preventatively."
            },
            {
                "name": "Regalia Biofungicide (Giant Knotweed Extract)",
                "active_ingredient": "Reynoutria sachalinensis extract",
                "purpose": "Induces systemic acquired resistance (SAR), prompting the plant to synthesize defense phytoalexins.",
                "guidance": "Mix 2.5 ml/L of water. Spray canopy preventatively.",
                "safety_notes": "Organic bio-pesticide. Minimal PPE required. PHI: 0 days.",
                "frequency": "Every 7–10 days in rotation."
            }
        ],
        "safety_precautions": [
            "Wear eye protection, gloves, and protective clothing when applying copper mixtures",
            "Do not apply copper products when temperatures exceed 32°C to prevent foliar burn",
            "Comply with product pre-harvest intervals before picking peppers",
            "Store all agricultural chemicals in locked, ventilated storage cabinets"
        ],
        "prevention": [
            "Plant certified bacterial-spot resistant bell pepper cultivars (races 1–10 resistance)",
            "Use only certified disease-free pepper seeds that have been hot-water treated (50°C for 25 min)",
            "Practice 2–3 year crop rotation excluding tomatoes, potatoes, and eggplants",
            "Install drip irrigation under plastic mulch to eliminate leaf splashing",
            "Plow under or destroy crop residues immediately after the final harvest"
        ]
    },

    "Pepper___healthy": {
        "crop": "Pepper",
        "disease": "Healthy Plant",
        "scientific_name": "Capsicum annuum",
        "is_healthy": True,
        "summary": "The pepper plant displays robust physiological vigor with uniform green foliage, strong stems, and no visible pathogen symptoms.",
        "symptoms": [
            "Vibrant, uniform dark green leaf pigmentation",
            "Smooth, glossy leaf surface without spots, blisters, or yellowing halos",
            "Firm upright stems with active nodes, buds, and healthy blossoms",
            "Absence of bacterial water-soaked lesions or insect stippling",
            "Well-formed green or ripening pepper pods without scabs or lesions"
        ],
        "immediate_actions": [
            "Maintain consistent drip irrigation to prevent moisture stress and blossom end rot",
            "Scout canopy twice weekly for early signs of aphids, thrips, or leaf spots",
            "Maintain weed-free beds and clean row middles"
        ],
        "treatment": [
            "No chemical fungicide or bactericide treatment required",
            "Optional: Apply calcium-rich foliar feed to safeguard against blossom-end rot",
            "Maintain soil organic matter and beneficial mycorrhizal root health"
        ],
        "medicines": [
            {
                "name": "Calcium-Boron Micronutrient Foliar Feed",
                "active_ingredient": "Chelated Calcium (10%) + Boron (0.5%)",
                "purpose": "Prevents blossom-end rot and strengthens plant cell walls against opportunistic pathogens.",
                "guidance": "Mix 2.0 ml/L of water. Mist canopy during early morning.",
                "safety_notes": "Standard agricultural fertilizer. Non-hazardous.",
                "frequency": "Every 14 days during flowering and fruit setting."
            }
        ],
        "safety_precautions": [
            "Sanitize pruning tools before cutting healthy pepper stems",
            "Avoid over-fertilizing with nitrogen to prevent weak, succulent growth",
            "Keep farm inputs organized and safely stored"
        ],
        "prevention": [
            "Ensure steady drip moisture; maintain soil pH between 6.2 and 6.8",
            "Use reflective mulch to deter vector pests such as thrips and aphids",
            "Maintain proper spacing (45 cm between plants in 90 cm rows)",
            "Perform routine field inspections around lower leaves"
        ]
    },

    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "disease": "Septoria Leaf Spot",
        "scientific_name": "Septoria lycopersici",
        "is_healthy": False,
        "summary": "Septoria leaf spot is a widespread fungal disease that produces numerous small circular spots with gray centers and black fruiting bodies on lower tomato foliage.",
        "symptoms": [
            "Numerous small (2–3 mm), circular spots with dark brown margins and sunken grayish-white centers",
            "Tiny black specks (pycnidia fruiting bodies) clearly visible in lesion centers under magnification",
            "Progressive chlorotic yellow halos encircling the leaf spots",
            "Spots coalesce, leading to rapid yellowing, withering, and drop of lower leaves",
            "Upward progression from oldest foliage leaving bare lower stems with exposed fruit"
        ],
        "immediate_actions": [
            "Prune off all infected lower leaves up to the first healthy fruit cluster; discard in bags",
            "Disinfect pruning blades in 70% rubbing alcohol between each tomato plant",
            "Stop any overhead watering immediately; use ground-level drip tubing only",
            "Apply a fresh layer of clean straw or plastic mulch under plants to seal in soil spores"
        ],
        "treatment": [
            "Begin a preventative and curative fungicide spray regimen immediately upon first spot detection",
            "Thoroughly spray the lower and inner canopy layers where humidity remains high",
            "Alternate multi-site protectants (Chlorothalonil, Mancozeb) with systemic triazole fungicides",
            "Continue regular spray intervals throughout periods of warm (20–25°C) wet weather"
        ],
        "medicines": [
            {
                "name": "Chlorothalonil 720 SC",
                "active_ingredient": "Chlorothalonil (Group M05)",
                "purpose": "Protective contact fungicide that prevents pycnidiospore germination and infection.",
                "guidance": "Mix 2.0 ml/L of water. Spray canopy thoroughly to complete coverage.",
                "safety_notes": "Causes skin sensitization and eye irritation. Wear chemical splash goggles and gloves. PHI: 1 day.",
                "frequency": "Every 7 to 10 days during warm, rainy weather."
            },
            {
                "name": "Azoxystrobin + Difenoconazole (32.5% SC)",
                "active_ingredient": "Azoxystrobin + Difenoconazole (Group 11 + 3)",
                "purpose": "Curative and translaminar systemic combination halting established Septoria fungal hyphae.",
                "guidance": "Mix 1.0 ml/L of water. Apply at first sign of lower leaf spotting.",
                "safety_notes": "Toxic to aquatic life. Do not apply near water bodies. PHI: 7 days.",
                "frequency": "Maximum 2 applications per season, spaced 14 days apart."
            },
            {
                "name": "Copper Hydroxide 50% WP",
                "active_ingredient": "Copper Hydroxide (Group M01)",
                "purpose": "Protective multi-site copper shield preventing spore spread across clean upper foliage.",
                "guidance": "Mix 2.0 g/L of water. Spray before forecasted rain events.",
                "safety_notes": "Eye irritant. Wear goggles and face mask. PHI: 1 day.",
                "frequency": "Every 7 days in rotation during damp periods."
            }
        ],
        "safety_precautions": [
            "Wear nitrile gloves, protective eyewear, and long-sleeved clothing when mixing and spraying",
            "Do not work in tomato rows while plants are wet with morning dew or rain",
            "Respect Pre-Harvest Intervals before picking ripe tomatoes for market or home use",
            "Dispose of infected plant clippings by burning or deep burial; never use in garden compost"
        ],
        "prevention": [
            "Rotate tomato fields for a minimum of 2 to 3 years with non-solanaceous crops",
            "Apply a thick 5–8 cm mulch layer of clean straw or plastic beneath all tomato vines",
            "Stake, cage, and prune plants to keep vines lifted at least 30 cm above soil level",
            "Provide generous row spacing (at least 90–120 cm) to ensure rapid morning leaf drying",
            "Plow under or thoroughly remove all crop debris immediately after harvest ends"
        ]
    },

    "Cherry___healthy": {
        "crop": "Cherry",
        "disease": "Healthy Plant",
        "scientific_name": "Prunus avium / Prunus cerasus",
        "is_healthy": True,
        "summary": "The cherry tree foliage and shoots demonstrate excellent physiological health with no symptoms of fungal, bacterial, or viral disease.",
        "symptoms": [
            "Lush, uniform green leaf coloration across the canopy",
            "Smooth, healthy leaf margins without puckering, curling, or chlorosis",
            "Absence of powdery mildew patches, leaf spots, or bacterial shot-hole symptoms",
            "Vigorous shoot extension with firm, clean bark and healthy lateral buds",
            "Clean developing cherry fruit clusters free of blemishes or fungal scarring"
        ],
        "immediate_actions": [
            "Maintain current irrigation schedule based on orchard soil moisture tensiometers",
            "Conduct weekly visual orchard scouting on new terminal growth and inner spurs",
            "Keep orchard row floors mowed and free of tall weed competition"
        ],
        "treatment": [
            "No chemical pesticide application required at this stage",
            "Maintain preventative orchard sanitation and soil fertility management",
            "Apply balanced dormant-season sprays as scheduled in orchard calendar"
        ],
        "medicines": [
            {
                "name": "Orchard Foliar Micronutrient Spray",
                "active_ingredient": "Zinc (Zn), Boron (B), and Magnesium (Mg) Chelate",
                "purpose": "Enhances photosynthetic capacity and fruit set in stone fruits.",
                "guidance": "Mix 1.5 g/L of water. Apply during pre-bloom or early post-harvest foliage maintenance.",
                "safety_notes": "Standard agricultural fertilizer. Low toxicity.",
                "frequency": "Once or twice per season as indicated by leaf tissue analysis."
            }
        ],
        "safety_precautions": [
            "Sanitize orchard pruning equipment before working in clean orchard blocks",
            "Follow orchard safety guidelines when operating tractors and ladders",
            "Safely store any seasonal orchard inputs in an approved chemical shed"
        ],
        "prevention": [
            "Prune cherry canopies during the dormant season to maintain good interior airflow and light penetration",
            "Employ under-tree drip or micro-sprinkler irrigation to prevent wetting foliage",
            "Maintain a clean herbicide strip along tree drip lines to suppress weed competition",
            "Monitor orchard traps for spotted-wing drosophila (SWD) and cherry fruit fly"
        ]
    },

    "Papaya___disease": {
        "crop": "Papaya",
        "disease": "Papaya Leaf Disease",
        "scientific_name": "Carica papaya pathogen complex (Anthracnose / Ringspot / Black Spot)",
        "is_healthy": False,
        "summary": "Foliar disease on papaya involving fungal leaf spot, anthracnose (Colletotrichum), or viral ringspot symptoms causing necrotic lesions, yellowing, and defoliation.",
        "symptoms": [
            "Circular to irregular brown necrotic spots with chlorotic yellow surrounding margins",
            "Water-soaked lesions on leaf undersides expanding into dark sunken spots",
            "Premature yellowing and desiccation of older lower papaya leaves",
            "Small circular spots or ring-like markings on petioles and developing fruit",
            "Reduced crown foliage and stunted new leaf emergence"
        ],
        "immediate_actions": [
            "Prune off heavily diseased lower leaves and remove them from the orchard",
            "Disinfect harvesting and pruning knives in 10% bleach or 70% alcohol between trees",
            "Ensure field drainage is clear; papaya roots are highly sensitive to waterlogging",
            "Avoid overhead irrigation; water exclusively at the base using drip emitters"
        ],
        "treatment": [
            "Apply protective broad-spectrum fungicides targeting foliar fungal pathogens",
            "Spray during early morning or late afternoon to avoid chemical phytotoxicity in tropical heat",
            "Alternate copper-based protectants with systemic fungicides (e.g., Azoxystrobin, Difenoconazole)",
            "Ensure spray thoroughly covers both sides of the large papaya leaf fan"
        ],
        "medicines": [
            {
                "name": "Copper Oxychloride 50% WP",
                "active_ingredient": "Copper Oxychloride (Group M01)",
                "purpose": "Broad-spectrum contact protectant against anthracnose and black spot fungi.",
                "guidance": "Mix 2.5 g/L of water. Spray canopy thoroughly until slight runoff.",
                "safety_notes": "Eye irritant. Wear goggles, rubber gloves, and protective mask. PHI: 1 day.",
                "frequency": "Every 10 to 14 days during wet or rainy periods."
            },
            {
                "name": "Azoxystrobin 23% SC",
                "active_ingredient": "Azoxystrobin (Strobilurin, Group 11)",
                "purpose": "Systemic and translaminar control halting internal fungal mycelial growth.",
                "guidance": "Mix 1.0 ml/L of water. Apply at early lesion onset.",
                "safety_notes": "Wear protective gear. Toxic to aquatic life. PHI: 1 day.",
                "frequency": "Apply maximum 2 consecutive sprays, rotated with contact fungicides."
            },
            {
                "name": "Mancozeb 75% WP",
                "active_ingredient": "Mancozeb (Group M03)",
                "purpose": "Multi-site contact protectant shielding newly emerging crown leaves from infection.",
                "guidance": "Mix 2.5 g/L of water. Apply before anticipated rainy periods.",
                "safety_notes": "Wear nitrile gloves and face mask. PHI: 7 days.",
                "frequency": "Every 14 days as required."
            }
        ],
        "safety_precautions": [
            "Wear full personal protective equipment including protective eyewear, gloves, and boots",
            "Avoid spraying during high wind conditions or midday tropical heat (>32°C)",
            "Observe pre-harvest intervals strictly before picking ripe papaya fruit",
            "Destroy diseased leaves and culled fruit by burning or deep burying outside the orchard"
        ],
        "prevention": [
            "Plant papaya on raised beds or mounds with excellent drainage to prevent root and collar rot",
            "Maintain generous tree spacing (2.5 to 3 meters apart) to ensure rapid leaf drying",
            "Control aphid populations that transmit Papaya Ringspot Virus using reflective mulch or barrier crops",
            "Remove all fallen leaves and decaying fruit from the orchard floor on a weekly schedule",
            "Use certified pathogen-free papaya seedlings from reputable nurseries"
        ]
    },

    "Papaya___healthy": {
        "crop": "Papaya",
        "disease": "Healthy Plant",
        "scientific_name": "Carica papaya",
        "is_healthy": True,
        "summary": "The papaya tree displays strong vegetative vigor, healthy deep green palmate leaves, a stout central trunk, and no signs of pathogen damage.",
        "symptoms": [
            "Large, well-expanded deep green palmate leaves radiating symmetrically from crown",
            "Stout, clean petioles without dark lesions, rings, or water-soaked spotting",
            "Smooth, healthy trunk with clean leaf scar rings",
            "Absence of chlorotic yellow mosaic, leaf curling, or anthracnose lesions",
            "Healthy flower buds and smooth developing green fruit clusters along trunk"
        ],
        "immediate_actions": [
            "Maintain consistent drip irrigation; avoid both water stress and waterlogging",
            "Scout weekly for early signs of mites, whiteflies, or anthracnose leaf spots",
            "Keep the root zone weed-free and lightly mulched with organic material"
        ],
        "treatment": [
            "No chemical pesticide or fungicide intervention required",
            "Maintain scheduled soil organic amendment and balanced NPK + Boron fertilization",
            "Monitor root aeration and soil moisture level"
        ],
        "medicines": [
            {
                "name": "Balanced Tropical Fruit Micronutrient Drench",
                "active_ingredient": "Boron (B), Zinc (Zn), and Iron (Fe) Complex",
                "purpose": "Maintains healthy crown development and prevents 'bumpy fruit' caused by boron deficiency.",
                "guidance": "Mix 2.0 g/L of water. Apply as a light soil drench around the drip line.",
                "safety_notes": "Standard agricultural fertilizer. Non-hazardous when used as directed.",
                "frequency": "Every 4 to 6 weeks during active growth."
            }
        ],
        "safety_precautions": [
            "Keep pruning and harvesting knives sanitized before moving between papaya trees",
            "Avoid soil compaction around papaya root zones",
            "Store all agricultural inputs in a cool, dry, secure location"
        ],
        "prevention": [
            "Ensure excellent soil drainage with ditches or raised ridges to avoid Phytophthora root rot",
            "Maintain 2.5–3.0 meter planting distance for optimal sunlight interception and aeration",
            "Surround papaya plots with barrier border crops (e.g., corn, sorghum) to reduce aphid vector flight",
            "Conduct routine bi-weekly inspections of leaf undersides and fruit clusters"
        ]
    }
}


def get_disease_info(key):
    """
    Retrieve structured agronomic information for a predicted class.
    Falls back to a safe generic response if key is unrecognized.
    """
    if key in DISEASE_DATABASE:
        return DISEASE_DATABASE[key]

    # Fallback for unknown disease
    crop = key.split("___")[0] if "___" in key else "Crop"
    disease = key.split("___")[1].replace("_", " ") if "___" in key else "Condition"
    is_healthy = "healthy" in key.lower()

    return {
        "crop": crop,
        "disease": disease,
        "scientific_name": "Undetermined",
        "is_healthy": is_healthy,
        "summary": f"Detected {disease} on {crop}.",
        "symptoms": [
            "Visible leaf tissue discoloration or spotting",
            "Atypical leaf surface texture or coloration",
            "Altered chlorophyll distribution"
        ],
        "immediate_actions": [
            "Isolate suspected plants from surrounding crop rows",
            "Inspect underside of leaves under bright light for pests or sporulation",
            "Avoid overhead irrigation until diagnosis is verified"
        ],
        "treatment": [
            "Consult with a local certified agronomist or extension office",
            "Apply broad-spectrum preventative bio-fungicide if fungal symptoms worsen"
        ],
        "medicines": [
            {
                "name": "General Agronomic Consultation",
                "active_ingredient": "Expert Verification Required",
                "purpose": "Verify exact local pathogen strain before applying synthetic chemistry.",
                "guidance": "Submit a fresh sample to your local agricultural extension service.",
                "safety_notes": "Do not apply unregistered or unsupported pesticides.",
                "frequency": "As advised by agricultural specialist."
            }
        ],
        "safety_precautions": [
            "Wear gloves while handling diseased foliage",
            "Disinfect tools between plants",
            "Follow all local pesticide application regulations"
        ],
        "prevention": [
            "Implement multi-year crop rotation",
            "Use certified pathogen-free planting stock",
            "Maintain optimal plant spacing and drip irrigation"
        ]
    }
