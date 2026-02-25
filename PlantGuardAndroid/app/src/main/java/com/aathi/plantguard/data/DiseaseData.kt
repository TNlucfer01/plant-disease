package com.aathi.plantguard.data

data class DiseaseInfo(
    val description: String,
    val remedy: String,
    val prevention: List<String>
)

object DiseaseRepository {
    private val infoMap = mapOf(
        "Apple Scab" to DiseaseInfo(
            description = "Fungal disease caused by Venturia inaequalis. It appears as olive-green to black velvety spots on leaves and fruit.",
            remedy = "Apply fungicides containing captan, sulfur, or myclobutanil during the growing season. Remove and destroy fallen leaves in autumn.",
            prevention = listOf("Plant resistant varieties", "Prune to improve air circulation", "Avoid overhead watering", "Rake and remove fallen leaves")
        ),
        "Apple Black Rot" to DiseaseInfo(
            description = "Caused by the fungus Diplodia seriata. It causes frog-eye leaf spots, fruit rot, and cankers on branches.",
            remedy = "Prune out dead wood and cankers during dormancy. Apply fungicides like captan or sulfur from silver tip to harvest.",
            prevention = listOf("Remove mummified fruit", "Prune out diseased branches", "Maintain tree vigor", "Late dormant spray with lime-sulfur")
        ),
        "Apple Cedar Rust" to DiseaseInfo(
            description = "A fungal disease that requires both apple trees and junipers/cedars to complete its life cycle. Causes bright orange spots on leaves.",
            remedy = "Apply fungicides such as myclobutanil or triadimefon in spring as the orange galls on junipers become visible.",
            prevention = listOf("Remove nearby juniper trees if possible", "Plant rust-resistant cultivars", "Follow a preventive fungicide schedule")
        ),
        "Apple Healthy" to DiseaseInfo(
            description = "Your apple tree looks healthy! The leaves are vibrant and free from significant spots or rot.",
            remedy = "No remedy needed. Continue regular care.",
            prevention = listOf("Maintain balanced fertilization", "Ensure adequate watering during dry spells", "Prune annually for tree structure", "Monitor for pests")
        ),
        "Blueberry Healthy" to DiseaseInfo(
            description = "Your blueberry plant is in great shape! Healthy blueberries have green, waxy leaves and sturdy stems.",
            remedy = "No treatment required.",
            prevention = listOf("Keep soil pH between 4.5 and 5.5", "Apply mulch to retain moisture", "Prune older canes to encourage new growth", "Provide consistent moisture")
        ),
        "Cherry Powdery Mildew" to DiseaseInfo(
            description = "Caused by Podosphaera clandestina. It appears as patches of white, powdery fungal growth on new leaves and fruit.",
            remedy = "Apply sulfur or potassium bicarbonate-based fungicides. Severely infected shoots should be pruned out.",
            prevention = listOf("Improve air circulation", "Plant in full sun", "Avoid late-season nitrogen fertilization", "Use resistant varieties where available")
        ),
        "Cherry Healthy" to DiseaseInfo(
            description = "Your cherry tree is healthy. The foliage looks robust and the growth pattern is normal.",
            remedy = "Maintain current care routine.",
            prevention = listOf("Proper pruning", "Spring fertilization", "Mulching to protect roots", "Regular monitoring")
        ),
        "Corn Gray Leaf Spot" to DiseaseInfo(
            description = "A fungal disease (Cercospora zeae-maydis) that causes rectangular, gray-to-tan spots on corn leaves.",
            remedy = "Apply foliar fungicides like strobilurins or triazoles if infection level is high before silking.",
            prevention = listOf("Rotate crops (don't plant corn on corn)", "Manage corn residue through tillage", "Use resistant hybrids", "Ensure proper plant spacing")
        ),
        "Corn Common Rust" to DiseaseInfo(
            description = "Caused by Puccinia sorghi. It appears as small, cinnamon-brown pustules on both upper and lower leaf surfaces.",
            remedy = "Fungicides are usually not necessary for field corn unless it's a seed production field or a highly susceptible hybrid.",
            prevention = listOf("Use resistant hybrids", "Plant early to avoid peak rust season", "Monitor fields regularly")
        ),
        "Corn Northern Leaf Blight" to DiseaseInfo(
            description = "Fungal disease causing long, cigar-shaped tan lesions (1-6 inches long) on the leaves.",
            remedy = "Apply foliar fungicides if the disease is found on the ear leaf or above during silking.",
            prevention = listOf("Crop rotation", "Tillage to bury infected residue", "Use resistant hybrids", "Manage soil fertility")
        ),
        "Corn Healthy" to DiseaseInfo(
            description = "Your corn plant is healthy. The leaves are deep green with no visible blight or rust.",
            remedy = "Keep up the good work!",
            prevention = listOf("Proper nitrogen management", "Adequate irrigation", "Weed control", "Pest monitoring")
        ),
        "Grape Black Rot" to DiseaseInfo(
            description = "A serious fungal disease (Guignardia bidwellii) that attacks leaves, shoots, and fruit, turning grapes into hard, black mummies.",
            remedy = "Apply fungicides containing mancozeb, captan, or myclobutanil. Remove all mummified clusters.",
            prevention = listOf("Prune to improve drying", "Sanitation: remove old fruit and infected stems", "Early season fungicide sprays", "Weed control under vines")
        ),
        "Grape Esca" to DiseaseInfo(
            description = "A complex of wood-rotting fungi (Black Measles). Causes 'tiger-stripe' leaf patterns and spotted fruit.",
            remedy = "There is no known chemical cure. Protect pruning wounds with paste. Prune out infected wood if possible.",
            prevention = listOf("Avoid large pruning cuts", "Disinfect pruning tools", "Use healthy nursery stock", "Improve vine health through nutrition")
        ),
        "Grape Leaf Blight" to DiseaseInfo(
            description = "Caused by Phomopsis viticola. It results in small dark spots with yellow halos on leaves and cracked shoots.",
            remedy = "Apply fungicides (mancozeb, captan) early in the growing season starting at bud break.",
            prevention = listOf("Aggressive dormant pruning to remove infected wood", "Ensure good sun exposure", "Avoid overhead irrigation")
        ),
        "Grape Healthy" to DiseaseInfo(
            description = "Your grapes are healthy! The vines look vigorous and the leaves are clear.",
            remedy = "Continue your vineyard management.",
            prevention = listOf("Thinning for airflow", "Regular leaf pulling", "Soil testing and fertilization", "Drip irrigation")
        ),
        "Orange Haunglongbing" to DiseaseInfo(
            description = "Also known as Citrus Greening. It's a bacterial disease spread by the Asian citrus psyllid. Causes blotchy mottle on leaves and bitter, small fruit.",
            remedy = "There is currently no cure. Infected trees must be removed and destroyed to prevent spread.",
            prevention = listOf("Control psyllids with insecticides", "Use certified disease-free nursery stock", "Monitor for symptoms constantly", "Remove neighboring infected trees")
        ),
        "Peach Bacterial Spot" to DiseaseInfo(
            description = "Caused by Xanthomonas arboricola. Results in small, angular, water-soaked spots on leaves that turn brown and fall out (shot-hole).",
            remedy = "Apply copper-based sprays or oxytetracycline starting at bud break. Copper can be phytotoxic, so use caution.",
            prevention = listOf("Plant resistant cultivars", "Avoid excessive nitrogen", "Prune for airflow", "Manage orchard floor to reduce moisture")
        ),
        "Peach Healthy" to DiseaseInfo(
            description = "Your peach tree is healthy. The leaves are lush and fruit development looks normal.",
            remedy = "Continue standard maintenance.",
            prevention = listOf("Thinning fruit to prevent branch breakage", "Proper winter pruning", "Dormant oil spray for pests", "Consistent watering")
        ),
        "Pepper Bell Bacterial Spot" to DiseaseInfo(
            description = "Bacterial disease causing small, water-soaked, scabby spots on both leaves and fruit.",
            remedy = "Copper-based fungicides can help slow spread. Remove infected plants if possible to save others.",
            prevention = listOf("Use pathogen-free seeds", "Rotate crops (avoid peppers/tomatoes in same spot)", "Avoid working in wet foliage", "Mulch to prevent soil splash")
        ),
        "Pepper Bell Healthy" to DiseaseInfo(
            description = "Your pepper plant is healthy and productive!",
            remedy = "No treatment needed.",
            prevention = listOf("Stake for support", "Maintain even soil moisture", "Apply organic fertilizer", "Protect from extreme heat")
        ),
        "Potato Early Blight" to DiseaseInfo(
            description = "Caused by Alternaria solani. Shows as dark brown spots with concentric rings ('target' appearance) on older leaves.",
            remedy = "Apply chlorothalonil, mancozeb, or copper fungicides. Increase potassium fertilization.",
            prevention = listOf("3-year crop rotation", "Remove crop debris", "Space plants for airflow", "Avoid overhead irrigation")
        ),
        "Potato Late Blight" to DiseaseInfo(
            description = "Caused by Phytophthora infestans. A destructive disease that causes dark, water-soaked patches on leaves that can rot an entire field quickly.",
            remedy = "Immediate application of specific late-blight fungicides. Destroy infected plants and tubers completely.",
            prevention = listOf("Plant certified disease-free seed potatoes", "Avoid planting near cull piles", "Monitor weather for high-risk periods", "Destroy volunteer potatoes")
        ),
        "Potato Healthy" to DiseaseInfo(
            description = "Your potatoes are healthy. The foliage is full and green.",
            remedy = "Continue current care.",
            prevention = listOf("Hilling up soil to protect tubers", "Mulching", "Proper spacing", "Balanced nutrients")
        ),
        "Raspberry Healthy" to DiseaseInfo(
            description = "Your raspberry bush is healthy and resilient.",
            remedy = "No treatment required.",
            prevention = listOf("Annual pruning of spent canes", "Good drainage", "Protect from wind", "Remove wild brambles nearby")
        ),
        "Soybean Healthy" to DiseaseInfo(
            description = "Your soybeans are healthy and forming pods well.",
            remedy = "Keep monitoring your crop.",
            prevention = listOf("Integrated pest management", "Soil health monitoring", "Proper seeding rate", "Weed management")
        ),
        "Squash Powdery Mildew" to DiseaseInfo(
            description = "White, flour-like dust on leaves and stems. Can cause leaves to turn yellow and die.",
            remedy = "Spray with neem oil, sulfur, or a mix of milk and water (1:9 ratio).",
            prevention = listOf("Plant in full sun", "Avoid high nitrogen", "Use resistant varieties", "Mulch to keep leaves off soil")
        ),
        "Strawberry Leaf Scorch" to DiseaseInfo(
            description = "Fungal disease (Diplocarpon earlianum) causing purple-to-brown spots that merge, making leaves look scorched.",
            remedy = "Remove infected foliage in fall. Fungicides like captan can be used in severe cases.",
            prevention = listOf("Renovate beds annually", "Avoid overhead watering", "Remove weeds", "Use disease-resistant plants")
        ),
        "Strawberry Healthy" to DiseaseInfo(
            description = "Your strawberries are healthy and looking delicious!",
            remedy = "Continue standard care.",
            prevention = listOf("Pine needle or straw mulch", "Morning watering", "Replace plants every 3 years", "Keep fruit off the soil")
        ),
        "Tomato Bacterial Spot" to DiseaseInfo(
            description = "Small, greasy-looking spots on leaves and scabby spots on fruit. Spread by rain and wind.",
            remedy = "Apply copper-based sprays early. Remove and destroy infected plant debris at end of season.",
            prevention = listOf("Use treated seeds", "4-year crop rotation", "Mulch around plants", "Drip irrigation only")
        ),
        "Tomato Early Blight" to DiseaseInfo(
            description = "Concentric 'target' spots on lower leaves. Can cause fruit rot and defoliation.",
            remedy = "Apply copper or chlorothalonil fungicides. Prune lower leaves to prevent soil contact.",
            prevention = listOf("Staking or caging", "Mulching", "Crop rotation", "Avoid wetting foliage")
        ),
        "Tomato Late Blight" to DiseaseInfo(
            description = "Large, pale green to brown water-soaked spots. Can kill plants and rot fruit in days during cool/wet weather.",
            remedy = "Remove and destroy entire plant immediately if symptoms appear. Apply preventative fungicides during wet periods.",
            prevention = listOf("Choose resistant varieties (e.g., 'Mountain Magic')", "Avoid late-season planting", "Ensure good leaf drying conditions")
        ),
        "Tomato Leaf Mold" to DiseaseInfo(
            description = "Olive-green to brown velvety growth on the underside of leaves and yellow spots on top. Common in greenhouses.",
            remedy = "Improve ventilation. Apply fungicides containing chlorothalonil or mancozeb.",
            prevention = listOf("Reduce humidity below 85%", "Avoid leaf wetness", "Prune to open up the canopy", "Grow resistant types")
        ),
        "Tomato Septoria Leaf Spot" to DiseaseInfo(
            description = "Small circular spots with gray centers and dark borders. Usually starts on lowest leaves.",
            remedy = "Remove infected lower leaves. Apply copper or mancozeb fungicides. Clear debris in winter.",
            prevention = listOf("Mulch to stop soil splash", "Stake plants", "Wait untill leaves are dry to prune", "Rotation")
        ),
        "Tomato Spider Mites" to DiseaseInfo(
            description = "Tiny reddish mites. Cause yellow stippling on leaves and fine webbing. Leaves may dry up and fall.",
            remedy = "Blast with water to knock them off. Use insecticidal soap or neem oil for heavy infestations.",
            prevention = listOf("Keep plants well-watered (mites love thirst)", "Release predatory mites", "Control dust around plants")
        ),
        "Tomato Target Spot" to DiseaseInfo(
            description = "Caused by Corynespora cassiicola. Brown spots with concentric circles, similar to Early Blight but more numerous and smaller.",
            remedy = "Use fungicides containing chlorothalonil or azoxystrobin. Remove infected plant material.",
            prevention = listOf("Improve airflow", "Avoid overhead irrigation", "Sanitize tools between plants")
        ),
        "Tomato Yellow Leaf Curl Virus" to DiseaseInfo(
            description = "Spread by whiteflies. Leaves turn yellow, curl upward, and become stunted. Flower drop is common.",
            remedy = "No cure for the virus. Pull out infected plants to prevent spread. Focus on whitefly control.",
            prevention = listOf("Use whitefly-resistant varieties", "Use yellow sticky traps", "Cover plants with fine mesh", "Reflective mulch")
        ),
        "Tomato Mosaic Virus" to DiseaseInfo(
            description = "Causes mottled patterns of light and dark green on leaves. Leaves may be thin and stringy ('fern leaf').",
            remedy = "No chemical control. Destroy infected plants immediately. Disinfect tools with bleach or milk.",
            prevention = listOf("Buy virus-free seeds", "Wash hands after handling tobacco", "Control aphids", "Clean tools")
        ),
        "Tomato Healthy" to DiseaseInfo(
            description = "Your tomato plant looks fantastic! The leaves are green and the growth is strong.",
            remedy = "No treatment necessary.",
            prevention = listOf("Consistent watering for blossom-end rot prevention", "Prune suckers", "Weekly fertilization", "Companion planting with basil or marigolds")
        )
    )

    fun getInfo(label: String): DiseaseInfo {
        return infoMap[label] ?: DiseaseInfo(
            description = "Information not yet available for this specific disease. It's often caused by fungal or bacterial pathogens that spread in moist environments.",
            remedy = "Remove infected leaves immediately to prevent spreading. Apply a suitable fungicide if the symptoms persist.",
            prevention = listOf("Improve air circulation", "Avoid overhead watering", "Maintain soil health", "Monitor regularly")
        )
    }
}
