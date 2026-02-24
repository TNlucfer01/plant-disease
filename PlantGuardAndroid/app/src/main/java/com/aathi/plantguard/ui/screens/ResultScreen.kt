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
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
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

@Composable
fun ResultScreen(
    result: ClassificationResult,
    image: Bitmap,
    onBack: () -> Unit
) {
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
            // Badge
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.CheckCircle, contentDescription = null, tint = GreenPrimary, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text("Identified Disease", color = GreenPrimary, fontSize = 14.sp, fontWeight = FontWeight.Medium)
            }
            
            Text(
                result.label,
                fontSize = 32.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF1B3121),
                modifier = Modifier.padding(vertical = 4.dp)
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Info Section
            Text("About This Disease", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color(0xFF2E4D32))
            Text(
                getDiseaseDescription(result.label),
                fontSize = 15.sp,
                color = Color.Gray,
                lineHeight = 22.sp,
                modifier = Modifier.padding(top = 8.dp)
            )

            Spacer(modifier = Modifier.height(24.dp))

            // Action Box
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
                        getRecommendedAction(result.label),
                        modifier = Modifier.padding(top = 12.dp),
                        color = Color(0xFF795548),
                        fontSize = 15.sp,
                        lineHeight = 22.sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            Text("Prevention Tips", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color(0xFF2E4D32))
            
            val tips = getPreventionTips(result.label)
            tips.forEachIndexed { index, tip ->
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

            Spacer(modifier = Modifier.height(32.dp))

            Button(
                onClick = onBack,
                modifier = Modifier.fillMaxWidth().height(56.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = GreenPrimary)
            ) {
                Text("New Scan", fontSize = 18.sp, fontWeight = FontWeight.Bold)
            }
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

// Dummy data helpers - in a real app these could be in a repository
fun getDiseaseDescription(label: String): String {
    return when {
        label.contains("Powdery Mildew") -> "Powdery mildew appears as white, powdery spots on leaves and stems. It thrives in warm, dry conditions with high humidity."
        label.contains("Healthy") -> "Your plant appears to be healthy! Keep up the good work with regular watering and proper sunlight."
        else -> "This disease affecting your plant needs attention. It's often caused by fungal or bacterial pathogens that spread in moist environments."
    }
}

fun getRecommendedAction(label: String): String {
    return when {
        label.contains("Powdery Mildew") -> "Spray affected plants with a mixture of 1 tablespoon baking soda and 1 teaspoon liquid soap per gallon of water. Repeat weekly."
        label.contains("Healthy") -> "No immediate action required. Continue routine maintenance."
        else -> "Remove infected leaves immediately to prevent spreading. Apply a suitable fungicide if the symptoms persist."
    }
}

fun getPreventionTips(label: String): List<String> {
    return listOf(
        "Plant in full sun locations",
        "Improve air circulation by proper spacing",
        "Avoid overhead watering",
        "Remove infected leaves promptly"
    )
}
