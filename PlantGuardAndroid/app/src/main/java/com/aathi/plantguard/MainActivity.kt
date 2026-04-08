package com.aathi.plantguard

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.*
import androidx.core.content.ContextCompat
import com.aathi.plantguard.ml.PlantClassifier
import com.aathi.plantguard.ml.ClassificationResult
import com.aathi.plantguard.ui.screens.ScannerScreen
import com.aathi.plantguard.ui.screens.ResultScreen
import com.aathi.plantguard.ui.screens.HistoryScreen
import com.aathi.plantguard.ui.theme.PlantGuardTheme
import com.aathi.plantguard.data.AppDatabase
import com.aathi.plantguard.data.ClassificationHistory
import kotlinx.coroutines.launch
import java.io.File
import androidx.lifecycle.lifecycleScope

class MainActivity : ComponentActivity() {
    
    private lateinit var classifier: PlantClassifier
    private lateinit var database: AppDatabase

    private enum class Screen {
        Scanner, Result, History
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        classifier = PlantClassifier(this)
        database = AppDatabase.getDatabase(this)

        setContent {
            PlantGuardTheme {
                var hasCameraPermission by remember {
                    mutableStateOf(
                        ContextCompat.checkSelfPermission(
                            this,
                            Manifest.permission.CAMERA
                        ) == PackageManager.PERMISSION_GRANTED
                    )
                }

                val launcher = rememberLauncherForActivityResult(
                    contract = ActivityResultContracts.RequestPermission(),
                    onResult = { granted ->
                        hasCameraPermission = granted
                        if (!granted) {
                            Toast.makeText(this, "Camera permission is required to scan plants", Toast.LENGTH_LONG).show()
                        }
                    }
                )

                LaunchedEffect(Unit) {
                    if (!hasCameraPermission) {
                        launcher.launch(Manifest.permission.CAMERA)
                    }
                }

                var currentImage by remember { mutableStateOf<Bitmap?>(null) }
                var currentResult by remember { mutableStateOf<ClassificationResult?>(null) }
                var currentScreen by remember { mutableStateOf(Screen.Scanner) }

                val historyList by database.historyDao().getAllHistory().collectAsState(initial = emptyList())

                if (hasCameraPermission) {
                    when (currentScreen) {
                        Screen.Scanner -> {
                            ScannerScreen(
                                onImageCaptured = { bitmap ->
                                    val result = classifier.classify(bitmap)
                                    currentImage = bitmap
                                    currentResult = result
                                    currentScreen = Screen.Result
                                    
                                    // Save to history
                                    lifecycleScope.launch {
                                        val path = saveImageToInternalStorage(bitmap)
                                        database.historyDao().insertHistory(
                                            ClassificationHistory(
                                                label = result.label,
                                                confidence = result.confidence,
                                                imagePath = path
                                            )
                                        )
                                    }
                                },
                                onHistoryClick = {
                                    currentScreen = Screen.History
                                }
                            )
                        }
                        Screen.Result -> {
                            if (currentResult != null && currentImage != null) {
                                ResultScreen(
                                    result = currentResult!!,
                                    image = currentImage!!,
                                    onBack = {
                                        currentScreen = Screen.Scanner
                                        currentResult = null
                                        currentImage = null
                                    }
                                )
                            }
                        }
                        Screen.History -> {
                            HistoryScreen(
                                historyList = historyList,
                                onBack = {
                                    currentScreen = Screen.Scanner
                                },
                                onDelete = { history ->
                                    lifecycleScope.launch {
                                        // Delete image file first
                                        File(history.imagePath).delete()
                                        database.historyDao().deleteHistory(history.id)
                                    }
                                },
                                onItemClick = { history ->
                                    val bitmap = android.graphics.BitmapFactory.decodeFile(history.imagePath)
                                    if (bitmap != null) {
                                        currentImage = bitmap
                                        val spaceIdx = history.label.indexOf(' ')
                                        val plant = if (spaceIdx >= 0) history.label.substring(0, spaceIdx) else history.label
                                        val disease = if (spaceIdx >= 0) history.label.substring(spaceIdx + 1) else "Unknown"
                                        currentResult = ClassificationResult(
                                            label      = history.label,
                                            plant      = plant,
                                            disease    = disease,
                                            confidence = history.confidence,
                                            isUnknown  = history.label == "Unknown"
                                        )
                                        currentScreen = Screen.Result
                                    }
                                }
                            )
                        }
                    }
                }
            }
        }
    }

    override fun onDestroy() {
        if (::classifier.isInitialized) {
            classifier.close()
        }
        super.onDestroy()
    }

    private fun saveImageToInternalStorage(bitmap: Bitmap): String {
        val filename = "scan_${System.currentTimeMillis()}.jpg"
        val file = File(filesDir, filename)
        file.outputStream().use { 
            bitmap.compress(Bitmap.CompressFormat.JPEG, 90, it)
        }
        return file.absolutePath
    }
}
