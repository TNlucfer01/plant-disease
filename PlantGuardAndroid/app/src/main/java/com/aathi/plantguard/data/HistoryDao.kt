package com.aathi.plantguard.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface HistoryDao {
    @Query("SELECT * FROM classification_history ORDER BY timestamp DESC")
    fun getAllHistory(): Flow<List<ClassificationHistory>>

    @Insert
    suspend fun insertHistory(history: ClassificationHistory)

    @Query("DELETE FROM classification_history WHERE id = :id")
    suspend fun deleteHistory(id: Long)

    @Query("DELETE FROM classification_history")
    suspend fun clearHistory()
}
