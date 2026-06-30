package com.mushroom.monitor

import android.content.Context
import android.os.Environment
import java.io.File

/**
 * Gdzie lądują zdjęcia. Używamy katalogu app-specific external:
 *   /sdcard/Android/data/com.mushroom.monitor/files/Pictures/
 * Plusy:
 *  - nie wymaga uprawnień do storage na API 30+ (Mi 11),
 *  - widoczny przez `adb pull` (most na komputerze stąd ściąga pliki).
 */
object CaptureStorage {

    fun outputDir(context: Context): File {
        val dir = File(
            context.getExternalFilesDir(Environment.DIRECTORY_PICTURES),
            "growkit"
        )
        dir.mkdirs()
        return dir
    }

    /** Nazwa pliku zawiera sortowalny znacznik czasu: growkit_20260630-142301.jpg */
    fun newPhotoFile(context: Context, timestampMs: Long): File {
        val stamp = java.text.SimpleDateFormat("yyyyMMdd-HHmmss", java.util.Locale.US)
            .format(java.util.Date(timestampMs))
        return File(outputDir(context), "growkit_$stamp.jpg")
    }
}
