package com.mushroom.monitor

import android.content.Context
import androidx.work.Data
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit

/**
 * Planowanie cyklicznych zdjęć. Domyślnie co [intervalMinutes] minut.
 *
 * Uwaga: WorkManager wymusza minimum 15 min dla pracy okresowej (oszczędność
 * baterii). Do monitorowania grzybni, gdzie zmiany są powolne, 15–60 min w
 * zupełności wystarcza (30 zdjęć = ~7,5h przy 15 min, lub ~30h przy 1h).
 */
object CaptureScheduler {

    private const val WORK_NAME = "mushroom-capture-periodic"

    fun schedule(
        context: Context,
        intervalMinutes: Long = 30,
        flash: CameraController.FlashMode = CameraController.FlashMode.ON,
        maxResolution: Boolean = true,
    ) {
        val data = Data.Builder()
            .putString(CaptureWorker.KEY_FLASH, flash.name)
            .putBoolean(CaptureWorker.KEY_MAX_RES, maxResolution)
            .build()

        val request = PeriodicWorkRequestBuilder<CaptureWorker>(
            intervalMinutes.coerceAtLeast(15), TimeUnit.MINUTES
        ).setInputData(data).build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            WORK_NAME,
            ExistingPeriodicWorkPolicy.UPDATE,
            request
        )
    }

    fun cancel(context: Context) {
        WorkManager.getInstance(context).cancelUniqueWork(WORK_NAME)
    }
}
