package com.aathi.plantguard.ui.screens

import android.graphics.Bitmap
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.aathi.plantguard.ml.ClassificationResult
import com.aathi.plantguard.ui.theme.GreenLight
import com.aathi.plantguard.ui.theme.GreenPrimary
import com.aathi.plantguard.data.DiseaseRepository

@Composable
fun ResultScreen(
    result: ClassificationResult,
    image: Bitmap,
    onBack: () -> Unit
) {
    val diseaseInfo = remember(result.label) { DiseaseRepository.getInfo(result.label) }
    val isUnknown = result.isUnknown

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .verticalScroll(rememberScrollState())
    ) {
        // Top Bar
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = onBack) {
                Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = Color.DarkGray)
            }
            Spacer(modifier = Modifier.width(8.dp))
            Text("Analysis Result", fontSize = 20.sp, fontWeight = FontWeight.SemiBold, color = Color.DarkGray)
        }

        // Scanned Image
        Image(
            bitmap = image.asImageBitmap(),
            contentDescription = "Scanned Leaf",
            modifier = Modifier
                .fillMaxWidth()
                .height(300.dp),
            contentScale = ContentScale.Crop
        )

        Column(modifier = Modifier.padding(24.dp)) {

            if (isUnknown) {
                // ── Unknown / Unrecognized ──────────────────────────────────
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.Warning,
                        contentDescription = null,
                        tint = Color(0xFFFFA000),
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Unrecognized Plant", color = Color(0xFFFFA000), fontSize = 14.sp, fontWeight = FontWeight.Medium)
                }

                Text(
                    "Unknown",
                    fontSize = 32.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF1B3121),
                    modifier = Modifier.padding(vertical = 4.dp)
                )

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    "Confidence: ${(result.confidence * 100).toInt()}%",
                    fontSize = 14.sp,
                    color = Color.Gray
                )

                Spacer(modifier = Modifier.height(16.dp))

                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .background(Color(0xFFFFF3E0))
                        .padding(20.dp)
                ) {
                    Column {
                        Text(
                            "This plant or disease was not recognized.",
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF5D4037)
                        )
                        Text(
                            "Tips:\n• Make sure the leaf fills most of the frame\n• Use good lighting with no shadows\n• Avoid blurry or low-quality photos\n• The model supports 114 known plant diseases",
                            modifier = Modifier.padding(top = 12.dp),
                            color = Color(0xFF795548),
                            fontSize = 15.sp,
                            lineHeight = 22.sp
                        )
                    }
                }

            } else {
                // ── Identified Disease ──────────────────────────────────────
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.CheckCircle, contentDescription = null, tint = GreenPrimary, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Identified", color = GreenPrimary, fontSize = 14.sp, fontWeight = FontWeight.Medium)
                }

                // Plant name (large) + disease subtitle
                Text(
                    result.plant,
                    fontSize = 32.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF1B3121),
                    modifier = Modifier.padding(top = 4.dp)
                )
                Text(
                    result.disease,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFF4CAF50),
                    modifier = Modifier.padding(bottom = 4.dp)
                )

                // Confidence chip
                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = if (result.confidence >= 0.85f) Color(0xFFE8F5E9) else Color(0xFFFFF9C4),
                    modifier = Modifier.padding(vertical = 4.dp)
                ) {
                    Text(
                        "Confidence: ${(result.confidence * 100).toInt()}%",
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
                        fontSize = 13.sp,
                        color = if (result.confidence >= 0.85f) Color(0xFF2E7D32) else Color(0xFFF57F17),
                        fontWeight = FontWeight.Medium
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Info Section
                Text("About This Disease", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color(0xFF2E4D32))
                Text(
                    diseaseInfo.description,
                    fontSize = 15.sp,
                    color = Color.Gray,
                    lineHeight = 22.sp,
                    modifier = Modifier.padding(top = 8.dp)
                )

                Spacer(modifier = Modifier.height(24.dp))

                // Remedy Box
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .background(Color(0xFFFFF9E6))
                        .padding(20.dp)
                ) {
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Surface(modifier = Modifier.size(8.dp), shape = CircleShape, color = Color(0xFFFFA000)) {}
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Recommended Action", fontWeight = FontWeight.Bold, color = Color(0xFF5D4037))
                        }
                        Text(
                            diseaseInfo.remedy,
                            modifier = Modifier.padding(top = 12.dp),
                            color = Color(0xFF795548),
                            fontSize = 15.sp,
                            lineHeight = 22.sp
                        )
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))

                Text("Prevention Tips", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color(0xFF2E4D32))
                for ((index, tip) in diseaseInfo.prevention.withIndex()) {
                    Row(modifier = Modifier.padding(vertical = 8.dp)) {
                        Surface(
                            modifier = Modifier.size(24.dp),
                            shape = CircleShape,
                            color = GreenLight
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text((index + 1).toString(), color = GreenPrimary, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                        Spacer(modifier = Modifier.width(16.dp))
                        Text(tip, fontSize = 15.sp, color = Color.Gray)
                    }
                }

                // Top-K predictions (collapsible)
                if (result.topK.size > 1) {
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("Other Possibilities", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color(0xFF2E4D32))
                    result.topK.drop(1).forEach { pred ->
                        Row(
                            modifier = Modifier.padding(vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                "${pred.plant} - ${pred.disease}",
                                fontSize = 14.sp,
                                color = Color.Gray,
                                modifier = Modifier.weight(1f)
                            )
                            Text(
                                "${(pred.confidence * 100).toInt()}%",
                                fontSize = 13.sp,
                                color = Color.LightGray
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(32.dp))

            Button(
                onClick = onBack,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = GreenPrimary)
            ) {
                Text("New Scan", fontSize = 18.sp, fontWeight = FontWeight.Bold)
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
