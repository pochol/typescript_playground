package com.mushroom.monitor

import android.content.Context
import android.os.PowerManager
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters

/**
 * Cyklicznie (co N minut) budzi ekran, robi zdjęcie growkitu i zapisuje plik.
 * Uruchamiane przez WorkManager (patrz [CaptureScheduler]).
 *
 * WorkManager wybrany zamiast AlarmManager bo:
 *  - przeżywa restart telefonu,
 *  - sam zarządza wakelockiem na czas pracy,
 *  - nie wymaga utrzymywania foreground service całą dobę.
 *
 * Minimalny interwał WorkManager to 15 min. Dla gęstszego timelapse użyj
 * trybu „one-shot łańcuchowy" z [CaptureScheduler.scheduleOneShot].
 */
class CaptureWorker(
    appContext: Context,
    params: WorkerParameters,
) : CoroutineWorker(appContext, params) {

    companion object {
        private const val TAG = "CaptureWorker"
        const val KEY_FLASH = "flash"          // "OFF" | "ON" | "TORCH"
        const val KEY_MAX_RES = "max_res"      // Boolean
    }

    override suspend fun doWork(): Result {
        // Wybudź ekran na chwilę — autofokus/ekspozycja działają stabilniej,
        // a Ty widzisz, że telefon „żyje".
        val pm = applicationContext.getSystemService(Context.POWER_SERVICE) as PowerManager
        @Suppress("DEPRECATION")
        val wake = pm.newWakeLock(
            PowerManager.SCREEN_BRIGHT_WAKE_LOCK or PowerManager.ACQUIRE_CAUSES_WAKEUP,
            "MushroomMonitor:capture"
        )
        wake.acquire(30_000L)
        return try {
            val flash = when (inputData.getString(KEY_FLASH)) {
                "OFF" -> CameraController.FlashMode.OFF
                "TORCH" -> CameraController.FlashMode.TORCH
                else -> CameraController.FlashMode.ON
            }
            val maxRes = inputData.getBoolean(KEY_MAX_RES, true)
            val file = CaptureStorage.newPhotoFile(applicationContext, System.currentTimeMillis())
            val result = CameraController(applicationContext).capture(file, flash, maxRes)
            Log.i(TAG, "OK: ${result.file.name} ${result.width}x${result.height}")
            Result.success()
        } catch (e: Exception) {
            Log.e(TAG, "Zdjęcie nie powiodło się", e)
            Result.retry()
        } finally {
            if (wake.isHeld) wake.release()
        }
    }
}
