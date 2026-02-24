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
import com.aathi.plantguard.ui.theme.PlantGuardTheme

class MainActivity : ComponentActivity() {
    
    private lateinit var classifier: PlantClassifier

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        classifier = PlantClassifier(this)

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

                if (hasCameraPermission) {
                    if (currentResult == null || currentImage == null) {
                        ScannerScreen(
                            onImageCaptured = { bitmap ->
                                val result = classifier.classify(bitmap)
                                currentImage = bitmap
                                currentResult = result
                            }
                        )
                    } else {
                        ResultScreen(
                            result = currentResult!!,
                            image = currentImage!!,
                            onBack = {
                                currentResult = null
                                currentImage = null
                            }
                        )
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
}
