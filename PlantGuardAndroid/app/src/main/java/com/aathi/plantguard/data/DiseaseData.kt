package com.aathi.plantguard.data

data class DiseaseInfo(
    val description: String,
    val remedy: String,
    val prevention: List<String>
)

object DiseaseRepository {
    private val infoMap = mapOf(
        "Apple Apple Scab" to DiseaseInfo(
            description = "Fungal disease caused by Venturia inaequalis. It appears as olive-green to black velvety spots on leaves and fruit.",
            remedy = "Apply fungicides containing captan, sulfur, or myclobutanil during the growing season. Remove and destroy fallen leaves in autumn.",
            prevention = listOf("Plant resistant varieties", "Prune to improve air circulation", "Avoid overhead watering", "Rake and remove fallen leaves")
        ),
        "Apple Black Rot" to DiseaseInfo(
            description = "Caused by the fungus Diplodia seriata. It causes frog-eye leaf spots, fruit rot, and cankers on branches.",
            remedy = "Prune out dead wood and cankers during dormancy. Apply fungicides like captan or sulfur from silver tip to harvest.",
            prevention = listOf("Remove mummified fruit", "Prune out diseased branches", "Maintain tree vigor", "Late dormant spray with lime-sulfur")
        ),
        "Apple Cedar Apple Rust" to DiseaseInfo(
            description = "A fungal disease that requires both apple trees and junipers/cedars to complete its life cycle.",
            remedy = "Apply fungicides such as myclobutanil or triadimefon in spring.",
            prevention = listOf("Remove nearby juniper trees if possible", "Plant rust-resistant cultivars", "Follow a preventive fungicide schedule")
        ),
        "Apple Healthy" to DiseaseInfo(
            description = "Your apple tree looks healthy!",
            remedy = "No remedy needed. Continue regular care.",
            prevention = listOf("Maintain balanced fertilization", "Ensure adequate watering", "Prune annually", "Monitor for pests")
        ),
        "Banana Cordana" to DiseaseInfo(
            description = "Cordana leaf spot causes oval brown spots with pale yellow halos on banana leaves.",
            remedy = "Remove infected leaves. Apply copper-based or systemic fungicides.",
            prevention = listOf("Remove dead leaves promptly", "Avoid waterlogging", "Ensure good drainage", "Apply balanced fertilizer")
        ),
        "Banana Healthy" to DiseaseInfo(
            description = "Your banana plant is healthy with vibrant green leaves.",
            remedy = "No treatment required.",
            prevention = listOf("Consistent watering", "Potassium-rich fertilizer", "Protect from strong winds", "Remove old leaves")
        ),
        "Banana Pestalotiopsis" to DiseaseInfo(
            description = "Pestalotiopsis leaf spot causes dark brown spots with light centers and dark borders on banana leaves.",
            remedy = "Remove infected leaves. Apply systemic fungicides.",
            prevention = listOf("Remove crop debris", "Avoid overhead irrigation", "Ensure good airflow", "Use disease-free planting material")
        ),
        "Banana Sigatoka" to DiseaseInfo(
            description = "Black Sigatoka is a devastating fungal disease that causes streaks and spots on leaves, reducing photosynthesis.",
            remedy = "Apply systemic fungicides such as propiconazole. Remove heavily infected leaves.",
            prevention = listOf("Regular leaf removal", "Good drainage", "Balanced fertilization", "Use resistant varieties")
        ),
        "Blueberry Healthy" to DiseaseInfo(
            description = "Your blueberry plant is in great shape!",
            remedy = "No treatment required.",
            prevention = listOf("Keep soil pH 4.5â€“5.5", "Apply mulch", "Prune older canes", "Consistent moisture")
        ),
        "Cherry Healthy" to DiseaseInfo(
            description = "Your cherry tree is healthy with robust foliage.",
            remedy = "Maintain current care routine.",
            prevention = listOf("Proper pruning", "Spring fertilization", "Mulching to protect roots", "Regular monitoring")
        ),
        "Cherry Powdery Mildew" to DiseaseInfo(
            description = "White powdery fungal growth on new cherry leaves and fruit.",
            remedy = "Apply sulfur or potassium bicarbonate-based fungicides.",
            prevention = listOf("Improve air circulation", "Plant in full sun", "Avoid late nitrogen", "Use resistant varieties")
        ),
        "Coconut Caterpillars" to DiseaseInfo(
            description = "Caterpillar infestation on coconut palms causes leaf defoliation and damage.",
            remedy = "Apply insecticides or biological control agents like Bacillus thuringiensis.",
            prevention = listOf("Monitor regularly", "Introduce natural predators", "Use light traps", "Targeted insecticide spraying")
        ),
        "Coconut Drying Of Leaflets" to DiseaseInfo(
            description = "Progressive drying of coconut leaflets, often caused by nutrient deficiency or bud rot.",
            remedy = "Apply foliar micronutrients, especially boron and manganese. Treat with copper fungicide for bud rot.",
            prevention = listOf("Regular fertilization", "Adequate irrigation", "Monitor for pests", "Remove dead fronds")
        ),
        "Coconut Flaccidity" to DiseaseInfo(
            description = "Coconut flaccidity disease is caused by a phytoplasma infection, causing wilting and yellowing of leaves.",
            remedy = "No cure. Remove and destroy infected palms. Control the insect vector.",
            prevention = listOf("Control insect vectors", "Use healthy nursery stock", "Quarantine infected areas", "Regular monitoring")
        ),
        "Coconut Healthy" to DiseaseInfo(
            description = "Your coconut palm is healthy with long, arching fronds.",
            remedy = "No treatment needed.",
            prevention = listOf("Regular fertilization", "Adequate watering", "Monitor for pests", "Remove old fronds")
        ),
        "Coconut Yellowing" to DiseaseInfo(
            description = "Lethal yellowing is a phytoplasma disease causing progressive yellowing and death of coconut palms.",
            remedy = "Antibiotic injections (oxytetracycline) can slow progression. Remove severely infected palms.",
            prevention = listOf("Plant resistant varieties", "Control leafhopper vectors", "Quarantine new planting material", "Regular inspection")
        ),
        "Corn Common Rust" to DiseaseInfo(
            description = "Caused by Puccinia sorghi. Cinnamon-brown pustules on upper and lower leaf surfaces.",
            remedy = "Fungicides are usually not necessary unless on highly susceptible hybrids.",
            prevention = listOf("Use resistant hybrids", "Plant early", "Monitor regularly")
        ),
        "Corn Gray Leaf Spot" to DiseaseInfo(
            description = "Caused by Cercospora zeae-maydis. Rectangular gray-to-tan spots on leaves.",
            remedy = "Apply strobilurin or triazole fungicides if infection is high before silking.",
            prevention = listOf("Rotate crops", "Manage corn residue", "Use resistant hybrids", "Ensure proper spacing")
        ),
        "Corn Healthy" to DiseaseInfo(
            description = "Your corn plant is healthy with deep green leaves.",
            remedy = "Keep up the good work!",
            prevention = listOf("Proper nitrogen management", "Adequate irrigation", "Weed control", "Pest monitoring")
        ),
        "Corn Northern Leaf Blight" to DiseaseInfo(
            description = "Long, cigar-shaped tan lesions on corn leaves caused by Exserohilum turcicum.",
            remedy = "Apply foliar fungicides at silking if disease is on the ear leaf or above.",
            prevention = listOf("Crop rotation", "Tillage to bury infected residue", "Use resistant hybrids", "Manage soil fertility")
        ),
        "Cotton Aphids" to DiseaseInfo(
            description = "Cotton aphids are small, soft-bodied insects that suck plant sap, causing leaf curl and stunted growth.",
            remedy = "Apply insecticidal soap, neem oil, or systemic insecticides like imidacloprid.",
            prevention = listOf("Monitor early season", "Encourage natural predators", "Avoid excessive nitrogen", "Use reflective mulch")
        ),
        "Cotton Army Worm" to DiseaseInfo(
            description = "Army worms (Spodoptera species) cause severe leaf defoliation on cotton plants.",
            remedy = "Apply insecticides such as chlorpyrifos or spinosad. Use pheromone traps.",
            prevention = listOf("Monitor field regularly", "Use pheromone traps", "Timely insecticide application", "Crop rotation")
        ),
        "Cotton Bacterial Blight" to DiseaseInfo(
            description = "Caused by Xanthomonas citri pv. malvacearum. Water-soaked angular spots on leaves that turn brown.",
            remedy = "Apply copper-based bactericides. Remove infected plant parts.",
            prevention = listOf("Use disease-free seeds", "Avoid overhead irrigation", "Crop rotation", "Plant resistant varieties")
        ),
        "Cotton Curl Virus" to DiseaseInfo(
            description = "Cotton Leaf Curl Virus (CLCuV) is transmitted by whiteflies, causing leaf curling, thickening, and stunted growth.",
            remedy = "No cure. Control whiteflies with insecticides. Remove infected plants.",
            prevention = listOf("Control whitefly populations", "Use tolerant varieties", "Avoid late planting", "Use reflective mulch")
        ),
        "Cotton Disease" to DiseaseInfo(
            description = "General infected cotton leaf showing disease symptoms.",
            remedy = "Identify the specific pathogen and apply appropriate fungicide or insecticide treatment.",
            prevention = listOf("Use certified seeds", "Crop rotation", "Monitor regularly", "Proper irrigation management")
        ),
        "Cotton Fusarium Wilt" to DiseaseInfo(
            description = "caused by Fusarium oxysporum. Causes yellowing, wilting, and vascular browning in cotton.",
            remedy = "No chemical cure once infected. Remove and destroy infected plants. Apply soil fumigation before planting.",
            prevention = listOf("Use resistant varieties", "Solarize soil", "Avoid over-irrigation", "Crop rotation for 4+ years")
        ),
        "Cotton Healthy" to DiseaseInfo(
            description = "Your cotton plant is healthy with lush, green leaves.",
            remedy = "No treatment required.",
            prevention = listOf("Balanced fertilization", "Timely irrigation", "Weed control", "Regular scouting")
        ),
        "Cotton Insect Pest" to DiseaseInfo(
            description = "Various insect pests are damaging the cotton plant, causing holes and discoloration.",
            remedy = "Identify the pest and apply targeted insecticide. Consider biological controls.",
            prevention = listOf("Regular field monitoring", "Pheromone traps", "Biological controls (Trichogramma)", "Timely pesticide applications")
        ),
        "Cotton Powdery Mildew" to DiseaseInfo(
            description = "White powdery fungal growth on cotton leaves caused by Leveillula taurica.",
            remedy = "Apply sulfur-based fungicides or azoxystrobin.",
            prevention = listOf("Avoid overcrowding", "Improve air circulation", "Reduce humidity", "Use resistant varieties")
        ),
        "Cotton Small Leaf" to DiseaseInfo(
            description = "Small leaf disease in cotton is caused by phytoplasma, resulting in small, chlorotic leaves and stunted plants.",
            remedy = "No cure. Remove and destroy infected plants. Control the leafhopper vector.",
            prevention = listOf("Control insect vectors", "Use quality seeds", "Remove infected plants early", "Monitor regularly")
        ),
        "Cotton Target Spot" to DiseaseInfo(
            description = "Caused by Corynespora cassiicola. Circular spots with concentric rings on cotton leaves.",
            remedy = "Apply fungicides like thiophanate-methyl or azoxystrobin.",
            prevention = listOf("Improve air circulation", "Avoid overhead irrigation", "Remove crop debris", "Crop rotation")
        ),
        "Cotton White Mold" to DiseaseInfo(
            description = "Caused by Sclerotinia sclerotiorum. White cottony mycelium and black sclerotia on stem and leaves.",
            remedy = "Apply fungicides such as iprodione or boscalid. Improve drainage.",
            prevention = listOf("Avoid excessive moisture", "Crop rotation", "Deep plowing", "Plant at proper density")
        ),
        "Cotton Wilt" to DiseaseInfo(
            description = "Wilting in cotton caused by Fusarium or Verticillium fungi, causing vascular browning.",
            remedy = "No chemical cure. Remove infected plants and destroy them.",
            prevention = listOf("Use resistant varieties", "Maintain soil health", "Crop rotation", "Reduce soil compaction")
        ),
        "Eggplant Healthy" to DiseaseInfo(
            description = "Your eggplant is healthy with deep green leaves.",
            remedy = "No treatment needed.",
            prevention = listOf("Regular watering", "Balanced fertilizer", "Monitor for pests", "Stake for support")
        ),
        "Eggplant Insect Pest" to DiseaseInfo(
            description = "Insect pests attacking eggplant leaves, causing holes and discoloration.",
            remedy = "Identify and apply targeted insecticide or neem oil.",
            prevention = listOf("Regular scouting", "Use sticky traps", "Encourage natural predators", "Crop rotation")
        ),
        "Eggplant Leaf Spot" to DiseaseInfo(
            description = "Fungal or bacterial leaf spots causing round or irregular spots on eggplant leaves.",
            remedy = "Apply copper-based or mancozeb fungicides. Remove infected leaves.",
            prevention = listOf("Avoid overhead watering", "Improve air circulation", "Crop rotation", "Remove leaf debris")
        ),
        "Eggplant Mosaic Virus" to DiseaseInfo(
            description = "Causes mosaic pattern of light and dark green on leaves, stunted growth.",
            remedy = "No chemical cure. Remove infected plants. Control aphid vectors.",
            prevention = listOf("Use virus-free transplants", "Control aphids", "Remove infected plants early", "Wash tools")
        ),
        "Eggplant Small Leaf" to DiseaseInfo(
            description = "Phytoplasma disease causing small, yellow leaves and bushy growth.",
            remedy = "No cure. Remove infected plants. Control the leafhopper vector.",
            prevention = listOf("Control leafhoppers", "Use healthy transplants", "Remove infected plants", "Monitor regularly")
        ),
        "Eggplant White Mold" to DiseaseInfo(
            description = "White cottony fungal growth caused by Sclerotinia on eggplant stems and leaves.",
            remedy = "Apply iprodione or boscalid fungicides. Improve drainage and reduce humidity.",
            prevention = listOf("Avoid dense planting", "Reduce moisture", "Crop rotation", "Remove infected debris")
        ),
        "Eggplant Wilt" to DiseaseInfo(
            description = "Bacterial or Fusarium wilt causing rapid wilting of eggplant despite adequate water.",
            remedy = "No chemical cure. Remove infected plants. Solarize soil.",
            prevention = listOf("Use resistant varieties", "Crop rotation", "Soil solarization", "Avoid wounding roots")
        ),
        "Grape Black Rot" to DiseaseInfo(
            description = "A serious fungal disease (Guignardia bidwellii) that turns grapes into hard, black mummies.",
            remedy = "Apply mancozeb, captan, or myclobutanil. Remove mummified clusters.",
            prevention = listOf("Prune to improve drying", "Sanitation", "Early season fungicide", "Weed control")
        ),
        "Grape Esca Black Measles" to DiseaseInfo(
            description = "Complex wood-rotting disease causing tiger-stripe leaf patterns and spotted fruit.",
            remedy = "No known chemical cure. Protect pruning wounds. Prune out infected wood.",
            prevention = listOf("Avoid large pruning cuts", "Disinfect tools", "Use healthy nursery stock", "Improve vine nutrition")
        ),
        "Grape Healthy" to DiseaseInfo(
            description = "Your grapes are healthy! The vines look vigorous.",
            remedy = "Continue your vineyard management.",
            prevention = listOf("Thinning for airflow", "Regular leaf pulling", "Soil testing", "Drip irrigation")
        ),
        "Grape Leaf Blight" to DiseaseInfo(
            description = "Caused by Phomopsis viticola. Dark spots with yellow halos on leaves.",
            remedy = "Apply mancozeb or captan early in the growing season.",
            prevention = listOf("Aggressive dormant pruning", "Good sun exposure", "Avoid overhead irrigation")
        ),
        "Groundnut Early Leaf Spot" to DiseaseInfo(
            description = "Caused by Cercospora arachidicola. Dark spots with yellow halos on groundnut leaves.",
            remedy = "Apply chlorothalonil or mancozeb fungicides at early stages.",
            prevention = listOf("Crop rotation", "Remove infected debris", "Use resistant varieties", "Avoid dense planting")
        ),
        "Groundnut Early Rust" to DiseaseInfo(
            description = "Rust pustules on groundnut leaves causing defoliation and yield loss.",
            remedy = "Apply triazole-based fungicides like propiconazole.",
            prevention = listOf("Use resistant varieties", "Early planting", "Crop rotation", "Monitor regularly")
        ),
        "Groundnut Healthy" to DiseaseInfo(
            description = "Your groundnut crop is healthy and growing well.",
            remedy = "No treatment needed.",
            prevention = listOf("Balanced fertilization", "Adequate irrigation", "Weed control", "Regular scouting")
        ),
        "Groundnut Late Leaf Spot" to DiseaseInfo(
            description = "Caused by Phaeoisariopsis personata. Dark spots on undersides of groundnut leaves.",
            remedy = "Apply mancozeb or chlorothalonil. Start spraying 30 days after sowing.",
            prevention = listOf("Crop rotation", "Resistant varieties", "Remove crop debris", "Timely planting")
        ),
        "Groundnut Nutrition Deficiency" to DiseaseInfo(
            description = "Nutrient deficiency causing yellowing and stunted growth in groundnut.",
            remedy = "Apply balanced fertilizer. Address specific deficiencies (N, P, K, Ca, Fe, Zn).",
            prevention = listOf("Soil testing before planting", "Apply recommended fertilizers", "Maintain soil pH 6.0-6.5", "Regular monitoring")
        ),
        "Groundnut Rust" to DiseaseInfo(
            description = "Groundnut rust causes cinnamon-brown pustules on leaves leading to severe defoliation.",
            remedy = "Apply propiconazole or tebuconazole fungicides preventively.",
            prevention = listOf("Plant resistant varieties", "Early planting", "Crop rotation", "Regular fungicide schedule")
        ),
        "Mango Bacterial Canker" to DiseaseInfo(
            description = "Caused by Xanthomonas campestris. Water-soaked spots that turn brown-black on mango leaves. Cankers on fruits and stems.",
            remedy = "Apply copper-based bactericides. Prune infected parts and destroy them.",
            prevention = listOf("Avoid injuries to plant", "Spray copper bactericide preventively", "Use disease-free nursery stock", "Sanitize tools")
        ),
        "Mango Cutting Weevil" to DiseaseInfo(
            description = "The mango stone weevil larvae damage the seed inside the mango fruit.",
            remedy = "Apply insecticides at fruit set. Post-harvest heat treatment.",
            prevention = listOf("Collect and destroy fallen fruit", "Bagging developing fruit", "Timely insecticide sprays", "Monitor orchards")
        ),
        "Mango Die Back" to DiseaseInfo(
            description = "Caused by Lasiodiplodia theobromae. Tips of branches dry from tip towards the base.",
            remedy = "Prune affected branches 2-3 inches below infection. Apply copper oxychloride to wounded areas.",
            prevention = listOf("Prune during dry season", "Sanitize pruning tools", "Avoid water stress", "Apply balanced fertilizer")
        ),
        "Mango Gall Midge" to DiseaseInfo(
            description = "The gall midge (Erosomyia indica) causes galls on mango leaves leading to curling and stunted growth.",
            remedy = "Apply systemic insecticides at leaf flush. Remove and destroy affected leaves.",
            prevention = listOf("Monitor during leaf flush", "Apply insecticides at first sign", "Remove galled leaves", "Avoid excessive nitrogen")
        ),
        "Mango Healthy" to DiseaseInfo(
            description = "Your mango tree is healthy with lush, green foliage.",
            remedy = "No treatment needed.",
            prevention = listOf("Regular pruning", "Balanced fertilization", "Proper irrigation", "Monitor for pests")
        ),
        "Mango Powdery Mildew" to DiseaseInfo(
            description = "White powdery coating on mango leaves, flowers, and young fruit caused by Oidium mangiferae.",
            remedy = "Apply sulfur-based fungicides or wettable sulfur at 0.2% concentration.",
            prevention = listOf("Spray protective fungicides before flowering", "Ensure airflow", "Avoid dense planting", "Use resistant varieties")
        ),
        "Mango Sooty Mould" to DiseaseInfo(
            description = "Black sooty mould grows on honeydew excreted by mealybugs, scale insects, and aphids on mango.",
            remedy = "Control the feeding insects. Wash off sooty mould with soapy water or neem oil.",
            prevention = listOf("Control sap-sucking insects", "Prune to reduce humidity", "Regular monitoring", "Sticky traps for insects")
        ),
        "Okra Healthy" to DiseaseInfo(
            description = "Your okra plant is healthy and productive.",
            remedy = "No treatment needed.",
            prevention = listOf("Consistent watering", "Balanced fertilizer", "Monitor for pests", "Weed control")
        ),
        "Okra Yellow Vein Mosaic" to DiseaseInfo(
            description = "Caused by Yellow Vein Mosaic Virus, spread by whiteflies. Yellow veins and mosaic pattern on leaves.",
            remedy = "No cure. Remove infected plants. Control whitefly population with insecticides.",
            prevention = listOf("Use resistant varieties", "Control whiteflies", "Use reflective mulch", "Avoid late planting")
        ),
        "Orange Citrus Greening" to DiseaseInfo(
            description = "Also known as Huanglongbing. Bacterial disease spread by the Asian citrus psyllid. Causes blotchy mottle on leaves.",
            remedy = "No cure. Infected trees must be removed and destroyed.",
            prevention = listOf("Control psyllids", "Use certified disease-free stock", "Monitor constantly", "Remove infected trees")
        ),
        "Peach Bacterial Spot" to DiseaseInfo(
            description = "Caused by Xanthomonas arboricola. Angular water-soaked spots on peach leaves that turn brown and fall out.",
            remedy = "Apply copper sprays or oxytetracycline starting at bud break.",
            prevention = listOf("Plant resistant cultivars", "Avoid excessive nitrogen", "Prune for airflow", "Manage orchard moisture")
        ),
        "Peach Healthy" to DiseaseInfo(
            description = "Your peach tree is healthy with lush foliage.",
            remedy = "Continue standard maintenance.",
            prevention = listOf("Thin fruit", "Winter pruning", "Dormant oil spray", "Consistent watering")
        ),
        "Peanut Dead Leaf" to DiseaseInfo(
            description = "Dead leaves on peanut plants caused by disease, drought, or pest damage.",
            remedy = "Identify the underlying cause and treat accordingly with fertilizer, water, or pesticide.",
            prevention = listOf("Monitor soil moisture", "Regular scouting", "Balanced nutrition", "Pest management")
        ),
        "Peanut Healthy" to DiseaseInfo(
            description = "Your peanut crop is healthy and growing well.",
            remedy = "No treatment needed.",
            prevention = listOf("Proper soil preparation", "Balanced fertilization", "Weed control", "Monitor regularly")
        ),
        "Pepper Bacterial Spot" to DiseaseInfo(
            description = "Small water-soaked scabby spots on pepper leaves and fruit caused by Xanthomonas.",
            remedy = "Apply copper-based sprays. Remove infected plants if needed.",
            prevention = listOf("Pathogen-free seeds", "Crop rotation", "Avoid working in wet foliage", "Mulch to prevent splash")
        ),
        "Pepper Healthy" to DiseaseInfo(
            description = "Your pepper plant is healthy and productive!",
            remedy = "No treatment needed.",
            prevention = listOf("Stake for support", "Even soil moisture", "Organic fertilizer", "Protect from extreme heat")
        ),
        "Potato Early Blight" to DiseaseInfo(
            description = "Dark brown spots with concentric rings on older potato leaves caused by Alternaria solani.",
            remedy = "Apply chlorothalonil or mancozeb. Increase potassium fertilization.",
            prevention = listOf("3-year rotation", "Remove debris", "Space for airflow", "Avoid overhead irrigation")
        ),
        "Potato Healthy" to DiseaseInfo(
            description = "Your potatoes are healthy with full green foliage.",
            remedy = "Continue current care.",
            prevention = listOf("Hill soil to protect tubers", "Mulch", "Proper spacing", "Balanced nutrients")
        ),
        "Potato Late Blight" to DiseaseInfo(
            description = "Caused by Phytophthora infestans. Dark water-soaked patches on leaves that can destroy a field quickly.",
            remedy = "Apply late-blight-specific fungicides immediately. Destroy infected plants.",
            prevention = listOf("Certified disease-free seed", "Avoid cull piles", "Monitor weather", "Destroy volunteers")
        ),
        "Raspberry Healthy" to DiseaseInfo(
            description = "Your raspberry bush is healthy and resilient.",
            remedy = "No treatment required.",
            prevention = listOf("Prune spent canes", "Good drainage", "Protect from wind", "Remove wild brambles")
        ),
        "Rice Bacterial Leaf Blight" to DiseaseInfo(
            description = "Caused by Xanthomonas oryzae. Water-soaked to yellowish stripes on leaf margins of rice.",
            remedy = "Apply copper-based bactericides. Drain fields and reduce nitrogen.",
            prevention = listOf("Use resistant varieties", "Balanced nitrogen", "Use pathogen-free seeds", "Avoid flood irrigation")
        ),
        "Rice Brown Spot" to DiseaseInfo(
            description = "Caused by Cochliobolus miyabeanus. Oval to circular brown spots on rice leaves and grains.",
            remedy = "Apply mancozeb or iprodione fungicides. Improve soil health.",
            prevention = listOf("Balanced fertilization", "Use certified seeds", "Crop rotation", "Treat seeds before planting")
        ),
        "Rice Healthy" to DiseaseInfo(
            description = "Your rice crop is healthy and growing vigorously.",
            remedy = "No treatment needed.",
            prevention = listOf("Maintain water levels", "Balanced fertilization", "Weed control", "Regular scouting")
        ),
        "Rice Hispa" to DiseaseInfo(
            description = "Rice hispa beetle scrapes upper leaf surface and mines inside the leaves, causing white streaks.",
            remedy = "Apply carbofuran or chlorpyrifos. Clip and destroy affected leaves.",
            prevention = listOf("Clip affected leaf tips at transplanting", "Use light traps", "Avoid dense planting", "Monitor regularly")
        ),
        "Rice Leaf Blast" to DiseaseInfo(
            description = "Caused by Magnaporthe oryzae. Diamond-shaped lesions with gray centers and brown borders on rice leaves.",
            remedy = "Apply tricyclazole or isoprothiolane fungicides immediately.",
            prevention = listOf("Use resistant varieties", "Avoid excess nitrogen", "Maintain proper water depth", "Seed treatment")
        ),
        "Rice Leaf Scald" to DiseaseInfo(
            description = "Caused by Microdochium oryzae. Irregular water-soaked lesions on rice leaves.",
            remedy = "Apply mancozeb or propiconazole. Reduce nitrogen applications.",
            prevention = listOf("Use resistant varieties", "Balanced fertilization", "Avoid water stress", "Crop rotation")
        ),
        "Rice Leaf Smut" to DiseaseInfo(
            description = "Caused by Entyloma oryzae. Small black or dark spots on rice leaves.",
            remedy = "Treat seeds with fungicides. Apply propiconazole if severe.",
            prevention = listOf("Treat seeds before planting", "Crop rotation", "Remove infected debris", "Monitor regularly")
        ),
        "Rice Sheath Blight" to DiseaseInfo(
            description = "Caused by Rhizoctonia solani. Oval or irregular spots on the rice leaf sheath near water level.",
            remedy = "Apply validamycin or propiconazole fungicides. Reduce plant density.",
            prevention = listOf("Reduce plant density", "Balanced nitrogen", "Avoid excess irrigation", "Crop rotation")
        ),
        "Sorghum Anthracnose Red Rot" to DiseaseInfo(
            description = "Caused by Colletotrichum sublineolum. Red rot of stalk and anthracnose lesions on leaves.",
            remedy = "Apply propiconazole fungicide. Remove infected stalks.",
            prevention = listOf("Use resistant hybrids", "Crop rotation", "Remove crop debris", "Avoid plant injury")
        ),
        "Sorghum Covered Kernel Smut" to DiseaseInfo(
            description = "Caused by Sporisorium sorghi. Sorghum seeds replaced by masses of black spores.",
            remedy = "Treat seeds with systemic fungicides (carboxin, thiram) before planting.",
            prevention = listOf("Seed treatment", "Use clean seeds", "Crop rotation", "Use resistant varieties")
        ),
        "Sorghum Grain Mold" to DiseaseInfo(
            description = "Complex of fungi causing discoloration and molding of sorghum grains during development.",
            remedy = "Apply fungicides at flowering. Harvest early when possible.",
            prevention = listOf("Use resistant varieties", "Harvest at proper moisture", "Adequate plant spacing", "Avoid lodging")
        ),
        "Sorghum Head Smut" to DiseaseInfo(
            description = "Caused by Sporisorium reilianum. Entire grain head replaced by a mass of smut spores.",
            remedy = "Treat seeds with systemic fungicide. No in-season cure.",
            prevention = listOf("Seed treatment", "Crop rotation", "Use resistant hybrids", "Remove smutted heads before spore release")
        ),
        "Sorghum Loose Smut" to DiseaseInfo(
            description = "Caused by Sporisorium cruentum. Powdery black mass replaces grain on individual florets.",
            remedy = "Use fungicide-treated seeds. Destroy infected plants.",
            prevention = listOf("Seed treatment", "Use disease-free seeds", "Crop rotation", "Resistant varieties")
        ),
        "Soybean Healthy" to DiseaseInfo(
            description = "Your soybeans are healthy and forming pods well.",
            remedy = "Keep monitoring your crop.",
            prevention = listOf("IPM", "Soil health monitoring", "Proper seeding rate", "Weed management")
        ),
        "Squash Powdery Mildew" to DiseaseInfo(
            description = "White flour-like dust on squash leaves and stems causing yellowing and death.",
            remedy = "Spray with neem oil, sulfur, or milk-and-water mix (1:9 ratio).",
            prevention = listOf("Plant in full sun", "Avoid high nitrogen", "Use resistant varieties", "Mulch to keep leaves off soil")
        ),
        "Strawberry Healthy" to DiseaseInfo(
            description = "Your strawberries are healthy and looking delicious!",
            remedy = "Continue standard care.",
            prevention = listOf("Pine needle or straw mulch", "Morning watering", "Replace plants every 3 years", "Keep fruit off soil")
        ),
        "Strawberry Leaf Scorch" to DiseaseInfo(
            description = "Fungal disease causing purple-to-brown spots that merge, making leaves look scorched.",
            remedy = "Remove infected foliage in fall. Use captan fungicides in severe cases.",
            prevention = listOf("Renovate beds annually", "Avoid overhead watering", "Remove weeds", "Use resistant plants")
        ),
        "Sugarcane Bacterial Blight" to DiseaseInfo(
            description = "Caused by Xanthomonas albilineans. White leaf scald affecting sugarcane leaves and stalk.",
            remedy = "Remove and burn infected clumps. Use hot water treatment on setts.",
            prevention = listOf("Use disease-free setts", "Hot water treatment (50Â°C for 2 hours)", "Plant resistant varieties", "Sanitary measures")
        ),
        "Sugarcane Healthy" to DiseaseInfo(
            description = "Your sugarcane crop is growing vigorously.",
            remedy = "No treatment needed.",
            prevention = listOf("Balanced fertilization", "Proper irrigation", "Weed control", "Regular scouting")
        ),
        "Sugarcane Mosaic" to DiseaseInfo(
            description = "Sugarcane mosaic virus (SCMV) causes mosaic pattern on leaves and stunted growth.",
            remedy = "No cure. Remove and destroy infected plants. Control aphid vectors.",
            prevention = listOf("Use virus-free planting material", "Control aphids", "Plant resistant varieties", "Quarantine measures")
        ),
        "Sugarcane Red Rot" to DiseaseInfo(
            description = "Caused by Colletotrichum falcatum. Red discoloration of internal tissue with white patches.",
            remedy = "Remove and burn infected stalks. Treat seed setts with carbendazim.",
            prevention = listOf("Use disease-free setts", "Treat setts before planting", "Use resistant varieties", "Crop rotation")
        ),
        "Sugarcane Rust" to DiseaseInfo(
            description = "Brown rust pustules on sugarcane leaves caused by Puccinia melanocephala.",
            remedy = "Apply propiconazole or triadimefon fungicides when rust first appears.",
            prevention = listOf("Plant resistant varieties", "Balanced fertilization", "Avoid dense planting", "Timely harvest")
        ),
        "Sugarcane Yellow" to DiseaseInfo(
            description = "Sugarcane Yellow Leaf Virus (SCYLV) causes midrib yellowing from leaf tip downwards.",
            remedy = "No chemical cure. Remove infected plants. Control aphid vectors.",
            prevention = listOf("Use clean planting material", "Control aphids", "Use resistant varieties", "Certified virus-free setts")
        ),
        "Tea Algal Leaf" to DiseaseInfo(
            description = "Caused by Cephaleuros parasiticus. Greenish-grey velvety spots on tea leaves.",
            remedy = "Apply copper-based fungicides. Remove infected leaves.",
            prevention = listOf("Prune for good air circulation", "Copper spray during wet season", "Avoid overhead irrigation", "Proper shade management")
        ),
        "Tea Anthracnose" to DiseaseInfo(
            description = "Caused by Colletotrichum camelliae. Dark sunken lesions on tea leaves and stems.",
            remedy = "Apply mancozeb or carbendazim. Remove infected plant parts.",
            prevention = listOf("Improve drainage", "Prune for airflow", "Avoid mechanical injury", "Use disease-free planting stock")
        ),
        "Tea Bird Eye Spot" to DiseaseInfo(
            description = "Caused by Cercospora theae. Small round spots with brown to grey center on tea leaves.",
            remedy = "Apply copper fungicides or mancozeb.",
            prevention = listOf("Improve air circulation", "Avoid overhead watering", "Balanced nutrition", "Regular monitoring")
        ),
        "Tea Brown Blight" to DiseaseInfo(
            description = "Caused by Colletotrichum camelliae. Brown water-soaked lesions on tea leaves that turn light brown.",
            remedy = "Apply mancozeb or copper fungicides. Remove infected leaves.",
            prevention = listOf("Ensure proper drainage", "Improve canopy aeration", "Avoid shade extremes", "Monitor during wet season")
        ),
        "Tea Gray Blight" to DiseaseInfo(
            description = "Caused by Pestalotiopsis theae. Irregular gray lesions with darker borders on tea leaves.",
            remedy = "Apply mancozeb or thiophanate-methyl. Remove infected leaves.",
            prevention = listOf("Prune dead stems", "Improve air circulation", "Maintain vigor through fertilization", "Reduce moisture")
        ),
        "Tea Green Mirid Bug" to DiseaseInfo(
            description = "The tea green mirid bug (Helopeltis antonii) causes brown necrotic spots on young tea shoots.",
            remedy = "Apply insecticides such as cypermethrin or dimethoate. Prune affected shoots.",
            prevention = listOf("Regular monitoring", "Timely insecticide application", "Maintain field hygiene", "Conserve natural enemies")
        ),
        "Tea Healthy" to DiseaseInfo(
            description = "Your tea plant is healthy with vibrant, green flush.",
            remedy = "No treatment needed.",
            prevention = listOf("Regular pruning", "Balanced fertilization", "Proper shade management", "Monitor for pests")
        ),
        "Tea Helopeltis" to DiseaseInfo(
            description = "Helopeltis theivora causes dark brown necrotic lesions on young tea leaves and shoots.",
            remedy = "Apply systemic insecticides. Prune affected areas and destroy.",
            prevention = listOf("Regular field monitoring", "Timely insecticide spray", "Keep field weed-free", "Conserve natural predators")
        ),
        "Tea Red Leaf Spot" to DiseaseInfo(
            description = "Caused by Phoma or Colletotrichum. Red-brown circular spots on tea leaves.",
            remedy = "Apply copper-based or mancozeb fungicides.",
            prevention = listOf("Prune for airflow", "Remove infected leaves", "Balanced nutrition", "Avoid overhead irrigation")
        ),
        "Tea Red Spider" to DiseaseInfo(
            description = "Red spider mites (Oligonychus coffeae) cause bronze discoloration of tea leaves.",
            remedy = "Apply acaricides such as dicofol or propargite. Increase irrigation.",
            prevention = listOf("Monitor during dry season", "Avoid dust on leaves", "Conserve predatory mites", "Adequate irrigation")
        ),
        "Tea White Spot" to DiseaseInfo(
            description = "Caused by Didymella sp. White circular spots with dark borders on tea leaves.",
            remedy = "Apply mancozeb or copper fungicides.",
            prevention = listOf("Proper pruning", "Improve drainage", "Remove fallen leaves", "Monitor during wet season")
        ),
        "Tomato Bacterial Spot" to DiseaseInfo(
            description = "Small greasy spots on tomato leaves and scabby spots on fruit. Spread by rain and wind.",
            remedy = "Apply copper-based sprays. Remove infected plant debris at end of season.",
            prevention = listOf("Treated seeds", "4-year crop rotation", "Mulch", "Drip irrigation only")
        ),
        "Tomato Early Blight" to DiseaseInfo(
            description = "Concentric target spots on lower tomato leaves. Can cause defoliation.",
            remedy = "Apply copper or chlorothalonil. Prune lower leaves to prevent soil contact.",
            prevention = listOf("Staking", "Mulching", "Crop rotation", "Avoid wetting foliage")
        ),
        "Tomato Healthy" to DiseaseInfo(
            description = "Your tomato plant looks fantastic!",
            remedy = "No treatment necessary.",
            prevention = listOf("Consistent watering", "Prune suckers", "Weekly fertilization", "Companion planting")
        ),
        "Tomato Late Blight" to DiseaseInfo(
            description = "Large pale-green to brown water-soaked spots on tomato. Can kill plants in days.",
            remedy = "Remove and destroy entire plant immediately. Apply preventative fungicides.",
            prevention = listOf("Choose resistant varieties", "Avoid late planting", "Good leaf drying conditions")
        ),
        "Tomato Leaf Mold" to DiseaseInfo(
            description = "Olive-green to brown velvety growth on underside of tomato leaves. Common in greenhouses.",
            remedy = "Improve ventilation. Apply chlorothalonil or mancozeb.",
            prevention = listOf("Reduce humidity below 85%", "Avoid leaf wetness", "Prune canopy", "Grow resistant types")
        ),
        "Tomato Mosaic Virus" to DiseaseInfo(
            description = "Causes mottled patterns on tomato leaves. May cause thin, stringy leaves.",
            remedy = "No chemical control. Destroy infected plants. Disinfect tools.",
            prevention = listOf("Virus-free seeds", "Wash hands after handling tobacco", "Control aphids", "Clean tools")
        ),
        "Tomato Septoria Leaf Spot" to DiseaseInfo(
            description = "Small circular spots with gray centers and dark borders starting on lowest tomato leaves.",
            remedy = "Remove infected lower leaves. Apply copper or mancozeb. Clear debris.",
            prevention = listOf("Mulch to stop soil splash", "Stake plants", "Wait until dry to prune", "Rotation")
        ),
        "Tomato Spider Mites" to DiseaseInfo(
            description = "Reddish mites causing yellow stippling and webbing on tomato leaves.",
            remedy = "Blast with water. Use insecticidal soap or neem oil for heavy infestations.",
            prevention = listOf("Keep plants well-watered", "Release predatory mites", "Control dust around plants")
        ),
        "Tomato Target Spot" to DiseaseInfo(
            description = "Brown spots with concentric circles on tomato. Similar to early blight but more numerous.",
            remedy = "Use chlorothalonil or azoxystrobin fungicides. Remove infected material.",
            prevention = listOf("Improve airflow", "Avoid overhead irrigation", "Sanitize tools")
        ),
        "Tomato Yellow Leaf Curl Virus" to DiseaseInfo(
            description = "Whitefly-spread virus causing upward leaf curl, yellowing, and stunted tomato growth.",
            remedy = "No cure. Pull out infected plants. Focus on whitefly control.",
            prevention = listOf("Whitefly-resistant varieties", "Yellow sticky traps", "Fine mesh covers", "Reflective mulch")
        ),
        "Unknown" to DiseaseInfo(
            description = "This plant or disease could not be identified by the model.",
            remedy = "Please take a clearer photo in good lighting, ensuring the leaf fills the frame.",
            prevention = listOf("Use good natural lighting", "Ensure the leaf is in focus", "Avoid shadows on the leaf", "Try multiple angles")
        )
    )

    fun getInfo(label: String): DiseaseInfo {
        return infoMap[label] ?: DiseaseInfo(
            description = "Information not yet available for this specific disease. It is often caused by fungal or bacterial pathogens that spread in moist conditions.",
            remedy = "Remove infected leaves immediately to prevent spreading. Apply a suitable fungicide or consult an agricultural expert.",
            prevention = listOf("Improve air circulation", "Avoid overhead watering", "Maintain soil health", "Monitor regularly")
        )
    }
}
