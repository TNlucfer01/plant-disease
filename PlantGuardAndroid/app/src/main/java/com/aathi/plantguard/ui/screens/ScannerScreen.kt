package com.aathi.plantguard.ui.screens

import android.graphics.Bitmap
import android.util.Size
import androidx.camera.core.*
import androidx.camera.core.resolutionselector.AspectRatioStrategy
import androidx.camera.core.resolutionselector.ResolutionSelector
import androidx.camera.core.resolutionselector.ResolutionStrategy
import androidx.camera.view.PreviewView
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.PhotoLibrary
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import com.aathi.plantguard.ui.theme.AccentOrange
import com.aathi.plantguard.ui.theme.GreenDark
import java.util.concurrent.Executors

@Composable
fun ScannerScreen(
    onImageCaptured: (Bitmap) -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraExecutor = remember { Executors.newSingleThreadExecutor() }
    
    var imageCapture: ImageCapture? by remember { mutableStateOf(null) }

    Box(modifier = Modifier.fillMaxSize().background(GreenDark)) {
        // Camera Preview
        AndroidView(
            factory = { ctx ->
                val previewView = PreviewView(ctx)
                val cameraProviderFuture = androidx.camera.lifecycle.ProcessCameraProvider.getInstance(ctx)
                
                cameraProviderFuture.addListener({
                    val cameraProvider = cameraProviderFuture.get()
                    
                    val resolutionSelector = ResolutionSelector.Builder()
                        .setResolutionStrategy(
                            ResolutionStrategy(
                                Size(720, 1280),
                                ResolutionStrategy.FALLBACK_RULE_CLOSEST_HIGHER_THEN_LOWER
                            )
                        )
                        .setAspectRatioStrategy(AspectRatioStrategy.RATIO_4_3_FALLBACK_AUTO_STRATEGY)
                        .build()

                    val preview = Preview.Builder()
                        .setResolutionSelector(resolutionSelector)
                        .build()
                        .also {
                            it.setSurfaceProvider(previewView.surfaceProvider)
                        }
                    
                    imageCapture = ImageCapture.Builder()
                        .setResolutionSelector(resolutionSelector)
                        .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                        .build()

                    val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
                    
                    try {
                        cameraProvider.unbindAll()
                        cameraProvider.bindToLifecycle(
                            lifecycleOwner, cameraSelector, preview, imageCapture
                        )
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }, androidx.core.content.ContextCompat.getMainExecutor(ctx))
                previewView
            },
            modifier = Modifier.fillMaxSize()
        )

        // Overlay Guide
        ScannerOverlay()

        // Header
        Column(
            modifier = Modifier.padding(24.dp).align(Alignment.TopStart)
        ) {
            Text(
                "Plant Guard",
                color = Color.White,
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                "Identify plant diseases instantly",
                color = Color.White.copy(alpha = 0.8f),
                fontSize = 14.sp
            )
        }
        
        // History Icon
        IconButton(
            onClick = { /* TODO */ },
            modifier = Modifier.padding(24.dp).align(Alignment.TopEnd).background(Color.Black.copy(0.3f), CircleShape)
        ) {
            Icon(Icons.Default.History, contentDescription = "History", tint = Color.White)
        }

        // Bottom Controls
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 48.dp)
                .align(Alignment.BottomCenter),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Gallery Button
            IconButton(
                onClick = { /* TODO */ },
                modifier = Modifier.size(56.dp).background(Color.White.copy(0.1f), CircleShape)
            ) {
                Icon(Icons.Default.PhotoLibrary, contentDescription = "Gallery", tint = Color.White)
            }

            // Capture Button
            Button(
                onClick = {
                    imageCapture?.let { capture ->
                        capture.takePicture(
                            cameraExecutor,
                            object : ImageCapture.OnImageCapturedCallback() {
                                override fun onCaptureSuccess(image: ImageProxy) {
                                    val bitmap = image.toBitmap()
                                    onImageCaptured(bitmap)
                                    image.close()
                                }
                                override fun onError(exception: ImageCaptureException) {
                                    exception.printStackTrace()
                                }
                            }
                        )
                    }
                },
                modifier = Modifier.size(80.dp),
                shape = CircleShape,
                colors = ButtonDefaults.buttonColors(containerColor = AccentOrange),
                contentPadding = PaddingValues(0.dp)
            ) {
                Icon(Icons.Default.CameraAlt, contentDescription = "Capture", modifier = Modifier.size(32.dp), tint = Color.White)
            }
            
            // Dummy spacer for balance
            Box(modifier = Modifier.size(56.dp))
        }
    }
}

@Composable
fun ScannerOverlay() {
    Box(modifier = Modifier.fillMaxSize()) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val canvasWidth = size.width
            val canvasHeight = size.height
            val rectSize = 280.dp.toPx()
            
            val left = (canvasWidth - rectSize) / 2
            val top = (canvasHeight - rectSize) / 2
            
            // Outer Scrim
            drawRect(color = Color.Black.copy(alpha = 0.4f))
            
            // Guide Corners
            val cornerLength = 40.dp.toPx()
            val strokeWidth = 4.dp.toPx()
            
            // Top Left
            drawPath(
                path = androidx.compose.ui.graphics.Path().apply {
                    moveTo(left, top + cornerLength)
                    lineTo(left, top)
                    lineTo(left + cornerLength, top)
                },
                color = Color.White,
                style = Stroke(width = strokeWidth)
            )
            
            // Top Right
            drawPath(
                path = androidx.compose.ui.graphics.Path().apply {
                    moveTo(left + rectSize - cornerLength, top)
                    lineTo(left + rectSize, top)
                    lineTo(left + rectSize, top + cornerLength)
                },
                color = Color.White,
                style = Stroke(width = strokeWidth)
            )
            
            // Bottom Left
            drawPath(
                path = androidx.compose.ui.graphics.Path().apply {
                    moveTo(left, top + rectSize - cornerLength)
                    lineTo(left, top + rectSize)
                    lineTo(left + cornerLength, top + rectSize)
                },
                color = Color.White,
                style = Stroke(width = strokeWidth)
            )
            
            // Bottom Right
            drawPath(
                path = androidx.compose.ui.graphics.Path().apply {
                    moveTo(left + rectSize - cornerLength, top + rectSize)
                    lineTo(left + rectSize, top + rectSize)
                    lineTo(left + rectSize, top + rectSize - cornerLength)
                },
                color = Color.White,
                style = Stroke(width = strokeWidth)
            )
        }
        
        Text(
            "Center the affected leaf in the frame",
            color = Color.White,
            modifier = Modifier.align(Alignment.Center).padding(bottom = 320.dp),
            fontWeight = FontWeight.Medium
        )
    }
}

// Helper to convert ImageProxy to Bitmap
fun ImageProxy.toBitmap(): Bitmap {
    val plane = planes[0]
    val buffer = plane.buffer
    val bytes = ByteArray(buffer.remaining())
    buffer.get(bytes)
    return android.graphics.BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
}
