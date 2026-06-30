package com.mushroom.monitor

import android.content.Context
import android.os.PowerManager
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters

/**
 * Cyklicznie (co N minut) budzi ekran, robi zdjęcie growkitu i **wysyła je po
 * Bluetooth** do zapamiętanego komputera (Prefs). Uruchamiane przez WorkManager.
 *
 * WorkManager wybrany zamiast AlarmManager bo:
 *  - przeżywa restart telefonu,
 *  - sam zarządza wakelockiem na czas pracy.
 *
 * Minimalny interwał WorkManager to 15 min — dla powolnego wzrostu grzybni aż nadto.
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
        val pm = applicationContext.getSystemService(Context.POWER_SERVICE) as PowerManager
        @Suppress("DEPRECATION")
        val wake = pm.newWakeLock(
            PowerManager.SCREEN_BRIGHT_WAKE_LOCK or PowerManager.ACQUIRE_CAUSES_WAKEUP,
            "MushroomMonitor:capture"
        )
        wake.acquire(60_000L)
        return try {
            val flash = when (inputData.getString(KEY_FLASH)) {
                "OFF" -> CameraController.FlashMode.OFF
                "TORCH" -> CameraController.FlashMode.TORCH
                else -> CameraController.FlashMode.ON
            }
            val maxRes = inputData.getBoolean(KEY_MAX_RES, false)
            val file = CaptureStorage.newPhotoFile(applicationContext, System.currentTimeMillis())
            val result = CameraController(applicationContext).capture(file, flash, maxRes)
            Log.i(TAG, "Zdjęcie OK: ${result.file.name} ${result.width}x${result.height}")

            val addr = Prefs.targetAddress(applicationContext)
            if (addr == null) {
                Log.w(TAG, "Brak zapamiętanego komputera — zdjęcie zapisane, ale nie wysłane.")
                return Result.success()
            }
            BluetoothSender(applicationContext).send(addr, result.file)
            Log.i(TAG, "Wysłano ${result.file.name} po Bluetooth.")
            Result.success()
        } catch (e: Exception) {
            Log.e(TAG, "Zdjęcie/wysłka nie powiodły się", e)
            Result.retry()
        } finally {
            if (wake.isHeld) wake.release()
        }
    }
}
