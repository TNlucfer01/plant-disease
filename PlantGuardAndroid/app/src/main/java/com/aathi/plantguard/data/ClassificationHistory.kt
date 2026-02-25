package com.aathi.plantguard.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "classification_history")
data class ClassificationHistory(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val label: String,
    val confidence: Float,
    val imagePath: String,
    val timestamp: Long = System.currentTimeMillis()
)
