package com.aathi.plantguard.ml

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Color
import androidx.core.graphics.scale
import ai.onnxruntime.*
import java.nio.FloatBuffer
import java.util.*

class PlantClassifier(context: Context) : AutoCloseable {

    private val session: OrtSession
    private val env: OrtEnvironment = OrtEnvironment.getEnvironment()

    companion object {
        val CLASS_NAMES = listOf(
            "Apple Scab", "Apple Black Rot", "Apple Cedar Rust", "Apple Healthy",
            "Blueberry Healthy", "Cherry Powdery Mildew", "Cherry Healthy",
            "Corn Gray Leaf Spot", "Corn Common Rust", "Corn Northern Leaf Blight", "Corn Healthy",
            "Grape Black Rot", "Grape Esca", "Grape Leaf Blight", "Grape Healthy",
            "Orange Haunglongbing", "Peach Bacterial Spot", "Peach Healthy",
            "Pepper Bell Bacterial Spot", "Pepper Bell Healthy", "Potato Early Blight",
            "Potato Late Blight", "Potato Healthy", "Raspberry Healthy", "Soybean Healthy",
            "Squash Powdery Mildew", "Strawberry Leaf Scorch", "Strawberry Healthy",
            "Tomato Bacterial Spot", "Tomato Early Blight", "Tomato Late Blight",
            "Tomato Leaf Mold", "Tomato Septoria Leaf Spot", "Tomato Spider Mites",
            "Tomato Target Spot", "Tomato Yellow Leaf Curl Virus", "Tomato Mosaic Virus",
            "Tomato Healthy"
        )
    }

    init {
        val modelFile = copyAssetToCache(context, "plant_disease_model.onnx")
        copyAssetToCache(context, "plant_disease_model.onnx.data")
        session = env.createSession(modelFile.absolutePath, OrtSession.SessionOptions())
    }

    private fun copyAssetToCache(context: Context, assetName: String): java.io.File {
        val file = java.io.File(context.cacheDir, assetName)
        // Clean up or overwrite if exists to ensure we have the latest model
        if (file.exists()) {
            file.delete()
        }
        context.assets.open(assetName).use { input ->
            file.outputStream().use { output ->
                input.copyTo(output)
            }
        }
        return file
    }

    fun classify(bitmap: Bitmap): ClassificationResult {
        // Preprocess: Resize(256) -> CenterCrop(224) -> Normalize
        val resized = resizeBitmap(bitmap, 256)
        val cropped = centerCrop(resized, 224)
        val tensorData = bitmapToTensor(cropped)

        val inputName = session.inputNames.iterator().next()
        val inputTensor = OnnxTensor.createTensor(env, tensorData, longArrayOf(1, 3, 224, 224))

        inputTensor.use {
            val results = session.run(Collections.singletonMap(inputName, inputTensor))
            results.use {
                @Suppress("UNCHECKED_CAST")
                val output = results[0].value as Array<FloatArray>
                val logits = output[0]
                val maxIdx = logits.indices.maxByOrNull { logits[it] } ?: 0
                val confidence = softmax(logits)[maxIdx]

                return ClassificationResult(
                    label = CLASS_NAMES[maxIdx],
                    confidence = confidence,
                    logits = logits
                )
            }
        }
    }

    private fun resizeBitmap(bitmap: Bitmap, size: Int): Bitmap {
        val width = bitmap.width
        val height = bitmap.height
        val scale = size.toFloat() / minOf(width, height)
        val newWidth = (width * scale).toInt()
        val newHeight = (height * scale).toInt()
        return bitmap.scale(newWidth, newHeight, true)
    }

    private fun centerCrop(bitmap: Bitmap, size: Int): Bitmap {
        val x = (bitmap.width - size) / 2
        val y = (bitmap.height - size) / 2
        return Bitmap.createBitmap(bitmap, x, y, size, size)
    }

    private fun bitmapToTensor(bitmap: Bitmap): FloatBuffer {
        val buffer = FloatBuffer.allocate(1 * 3 * 224 * 224)
        val mean = floatArrayOf(0.485f, 0.456f, 0.406f)
        val std = floatArrayOf(0.229f, 0.224f, 0.225f)

        for (i in 0 until 224) {
            for (j in 0 until 224) {
                val pixel = bitmap.getPixel(j, i)
                // R
                buffer.put(0 * 224 * 224 + i * 224 + j, (Color.red(pixel) / 255f - mean[0]) / std[0])
                // G
                buffer.put(1 * 224 * 224 + i * 224 + j, (Color.green(pixel) / 255f - mean[1]) / std[1])
                // B
                buffer.put(2 * 224 * 224 + i * 224 + j, (Color.blue(pixel) / 255f - mean[2]) / std[2])
            }
        }
        buffer.rewind()
        return buffer
    }

    private fun softmax(logits: FloatArray): FloatArray {
        val maxLogit = logits.maxOrNull() ?: 0f
        val exps = logits.map { Math.exp((it - maxLogit).toDouble()).toFloat() }
        val sumExps = exps.sum()
        return exps.map { it / sumExps }.toFloatArray()
    }

    override fun close() {
        session.close()
        env.close()
    }
}

data class ClassificationResult(
    val label: String,
    val confidence: Float,
    val logits: FloatArray = floatArrayOf()
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false
        other as ClassificationResult
        if (label != other.label) return false
        if (confidence != other.confidence) return false
        if (!logits.contentEquals(other.logits)) return false
        return true
    }

    override fun hashCode(): Int {
        var result = label.hashCode()
        result = 31 * result + confidence.hashCode()
        result = 31 * result + logits.contentHashCode()
        return result
    }
}
