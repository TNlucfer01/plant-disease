package com.aathi.plantguard.ml

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Color
import androidx.core.graphics.scale
import ai.onnxruntime.*
import java.nio.FloatBuffer
import java.util.*
import kotlin.math.exp
import kotlin.math.ln

class PlantClassifier(context: Context) : AutoCloseable {

    private val session: OrtSession
    private val env: OrtEnvironment = OrtEnvironment.getEnvironment()

    companion object {
        // 114 classes – matches best_plant_disease_model.onnx (92.9% val accuracy)
        // Format: "PlantName Disease Name" (underscores replaced with spaces)
        val CLASS_NAMES = listOf(
            "Apple Apple Scab",
            "Apple Black Rot",
            "Apple Cedar Apple Rust",
            "Apple Healthy",
            "Banana Cordana",
            "Banana Healthy",
            "Banana Pestalotiopsis",
            "Banana Sigatoka",
            "Blueberry Healthy",
            "Cherry Healthy",
            "Cherry Powdery Mildew",
            "Coconut Caterpillars",
            "Coconut Drying Of Leaflets",
            "Coconut Flaccidity",
            "Coconut Healthy",
            "Coconut Yellowing",
            "Corn Common Rust",
            "Corn Gray Leaf Spot",
            "Corn Healthy",
            "Corn Northern Leaf Blight",
            "Cotton Aphids",
            "Cotton Army Worm",
            "Cotton Bacterial Blight",
            "Cotton Curl Virus",
            "Cotton Disease",
            "Cotton Fusarium Wilt",
            "Cotton Healthy",
            "Cotton Insect Pest",
            "Cotton Powdery Mildew",
            "Cotton Small Leaf",
            "Cotton Target Spot",
            "Cotton White Mold",
            "Cotton Wilt",
            "Eggplant Healthy",
            "Eggplant Insect Pest",
            "Eggplant Leaf Spot",
            "Eggplant Mosaic Virus",
            "Eggplant Small Leaf",
            "Eggplant White Mold",
            "Eggplant Wilt",
            "Grape Black Rot",
            "Grape Esca Black Measles",
            "Grape Healthy",
            "Grape Leaf Blight",
            "Groundnut Early Leaf Spot",
            "Groundnut Early Rust",
            "Groundnut Healthy",
            "Groundnut Late Leaf Spot",
            "Groundnut Nutrition Deficiency",
            "Groundnut Rust",
            "Mango Bacterial Canker",
            "Mango Cutting Weevil",
            "Mango Die Back",
            "Mango Gall Midge",
            "Mango Healthy",
            "Mango Powdery Mildew",
            "Mango Sooty Mould",
            "Okra Healthy",
            "Okra Yellow Vein Mosaic",
            "Orange Citrus Greening",
            "Peach Bacterial Spot",
            "Peach Healthy",
            "Peanut Dead Leaf",
            "Peanut Healthy",
            "Pepper Bacterial Spot",
            "Pepper Healthy",
            "Potato Early Blight",
            "Potato Healthy",
            "Potato Late Blight",
            "Raspberry Healthy",
            "Rice Bacterial Leaf Blight",
            "Rice Brown Spot",
            "Rice Healthy",
            "Rice Hispa",
            "Rice Leaf Blast",
            "Rice Leaf Scald",
            "Rice Leaf Smut",
            "Rice Sheath Blight",
            "Sorghum Anthracnose Red Rot",
            "Sorghum Covered Kernel Smut",
            "Sorghum Grain Mold",
            "Sorghum Head Smut",
            "Sorghum Loose Smut",
            "Soybean Healthy",
            "Squash Powdery Mildew",
            "Strawberry Healthy",
            "Strawberry Leaf Scorch",
            "Sugarcane Bacterial Blight",
            "Sugarcane Healthy",
            "Sugarcane Mosaic",
            "Sugarcane Red Rot",
            "Sugarcane Rust",
            "Sugarcane Yellow",
            "Tea Algal Leaf",
            "Tea Anthracnose",
            "Tea Bird Eye Spot",
            "Tea Brown Blight",
            "Tea Gray Blight",
            "Tea Green Mirid Bug",
            "Tea Healthy",
            "Tea Helopeltis",
            "Tea Red Leaf Spot",
            "Tea Red Spider",
            "Tea White Spot",
            "Tomato Bacterial Spot",
            "Tomato Early Blight",
            "Tomato Healthy",
            "Tomato Late Blight",
            "Tomato Leaf Mold",
            "Tomato Mosaic Virus",
            "Tomato Septoria Leaf Spot",
            "Tomato Spider Mites",
            "Tomato Target Spot",
            "Tomato Yellow Leaf Curl Virus"
        )

        // Confidence below this → "Unknown"
        const val CONFIDENCE_THRESHOLD = 0.70f

        // Entropy above this fraction of max entropy → "Unknown"
        // (catches cases where probability spreads across many classes)
        const val ENTROPY_RATIO_THRESHOLD = 0.75f
    }

    init {
        // New model is a single self-contained .onnx file (no .data sidecar)
        val modelFile = copyAssetToCache(context, "plant_disease_model.onnx")
        session = env.createSession(modelFile.absolutePath, OrtSession.SessionOptions())
    }

    private fun copyAssetToCache(context: Context, assetName: String): java.io.File {
        val file = java.io.File(context.cacheDir, assetName)
        if (file.exists()) file.delete()
        context.assets.open(assetName).use { input ->
            file.outputStream().use { output -> input.copyTo(output) }
        }
        return file
    }

    fun classify(bitmap: Bitmap): ClassificationResult {
        // Preprocess: Resize short side to 256 -> CenterCrop 224 -> Normalize (ImageNet)
        val resized  = resizeBitmap(bitmap, 256)
        val cropped  = centerCrop(resized, 224)
        val tensor   = bitmapToTensor(cropped)

        val inputName = session.inputNames.iterator().next()
        val inputTensor = OnnxTensor.createTensor(env, tensor, longArrayOf(1, 3, 224, 224))

        inputTensor.use {
            val results = session.run(Collections.singletonMap(inputName, inputTensor))
            results.use {
                @Suppress("UNCHECKED_CAST")
                val logits = (results[0].value as Array<FloatArray>)[0]
                val probs  = softmax(logits)
                val maxIdx = probs.indices.maxByOrNull { probs[it] } ?: 0
                val confidence = probs[maxIdx]

                // ── Unknown detection ──────────────────────────────────────
                val entropy    = -probs.sumOf { p ->
                    if (p > 0f) (p * ln(p.toDouble())) else 0.0
                }.toFloat()
                val maxEntropy = ln(probs.size.toDouble()).toFloat()
                val isUnknown  = confidence < CONFIDENCE_THRESHOLD ||
                                 entropy > ENTROPY_RATIO_THRESHOLD * maxEntropy

                if (isUnknown) {
                    return ClassificationResult(
                        label      = "Unknown",
                        plant      = "Unknown",
                        disease    = "Unknown",
                        confidence = confidence,
                        isUnknown  = true,
                        topK       = buildTopK(probs, 5)
                    )
                }

                val label = CLASS_NAMES[maxIdx]
                val (plant, disease) = parseLabel(label)

                return ClassificationResult(
                    label      = label,
                    plant      = plant,
                    disease    = disease,
                    confidence = confidence,
                    isUnknown  = false,
                    topK       = buildTopK(probs, 5)
                )
            }
        }
    }

    /** Split "Tomato Early Blight" -> Pair("Tomato", "Early Blight") */
    private fun parseLabel(label: String): Pair<String, String> {
        val idx = label.indexOf(' ')
        return if (idx >= 0) {
            Pair(label.substring(0, idx), label.substring(idx + 1))
        } else {
            Pair(label, "Unknown")
        }
    }

    private fun buildTopK(probs: FloatArray, k: Int): List<TopPrediction> {
        return probs.indices
            .sortedByDescending { probs[it] }
            .take(k)
            .map { idx ->
                val lbl = if (idx < CLASS_NAMES.size) CLASS_NAMES[idx] else "Unknown"
                val (plant, disease) = parseLabel(lbl)
                TopPrediction(plant, disease, probs[idx])
            }
    }

    private fun resizeBitmap(bitmap: Bitmap, size: Int): Bitmap {
        val w = bitmap.width
        val h = bitmap.height
        val scale = size.toFloat() / minOf(w, h)
        return bitmap.scale((w * scale).toInt(), (h * scale).toInt(), true)
    }

    private fun centerCrop(bitmap: Bitmap, size: Int): Bitmap {
        val x = (bitmap.width  - size) / 2
        val y = (bitmap.height - size) / 2
        return Bitmap.createBitmap(bitmap, x, y, size, size)
    }

    private fun bitmapToTensor(bitmap: Bitmap): FloatBuffer {
        val buf  = FloatBuffer.allocate(3 * 224 * 224)
        val mean = floatArrayOf(0.485f, 0.456f, 0.406f)
        val std  = floatArrayOf(0.229f, 0.224f, 0.225f)
        for (i in 0 until 224) {
            for (j in 0 until 224) {
                val px = bitmap.getPixel(j, i)
                buf.put(0 * 224 * 224 + i * 224 + j, (Color.red(px)   / 255f - mean[0]) / std[0])
                buf.put(1 * 224 * 224 + i * 224 + j, (Color.green(px) / 255f - mean[1]) / std[1])
                buf.put(2 * 224 * 224 + i * 224 + j, (Color.blue(px)  / 255f - mean[2]) / std[2])
            }
        }
        buf.rewind()
        return buf
    }

    private fun softmax(logits: FloatArray): FloatArray {
        val maxL = logits.maxOrNull() ?: 0f
        val exps = logits.map { exp((it - maxL).toDouble()).toFloat() }
        val sum  = exps.sum()
        return exps.map { it / sum }.toFloatArray()
    }

    override fun close() {
        session.close()
        env.close()
    }
}

data class TopPrediction(
    val plant: String,
    val disease: String,
    val confidence: Float
)

data class ClassificationResult(
    val label: String,
    val plant: String,
    val disease: String,
    val confidence: Float,
    val isUnknown: Boolean,
    val topK: List<TopPrediction> = emptyList()
)
