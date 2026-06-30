package com.mushroom.monitor

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.ImageFormat
import android.hardware.camera2.CameraCaptureSession
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraDevice
import android.hardware.camera2.CameraManager
import android.hardware.camera2.CameraMetadata
import android.hardware.camera2.CaptureRequest
import android.hardware.camera2.TotalCaptureResult
import android.hardware.camera2.params.OutputConfiguration
import android.hardware.camera2.params.SessionConfiguration
import android.media.ImageReader
import android.os.Handler
import android.os.HandlerThread
import android.util.Log
import android.util.Size
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.Executors
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlin.coroutines.suspendCoroutine

/**
 * Sterowanie aparatem przez Camera2 API.
 *
 * Robi JEDNO zdjęcie w maksymalnej dostępnej rozdzielczości (na Mi 11 = 108 MP
 * z głównego sensora), z opcjonalnie włączoną lampą, i zapisuje plik JPEG.
 *
 * Camera2 (a nie CameraX) jest tu konieczne, bo tylko ono daje pewny dostęp do
 * pełnej rozdzielczości sensora i ręczne sterowanie lampą (FLASH_MODE_TORCH /
 * FLASH_MODE_SINGLE). CameraX domyślnie ogranicza rozdzielczość.
 */
class CameraController(private val context: Context) {

    companion object {
        private const val TAG = "CameraController"
    }

    private val cameraManager =
        context.getSystemService(Context.CAMERA_SERVICE) as CameraManager

    /** Tryb lampy przy zdjęciu. */
    enum class FlashMode { OFF, ON, TORCH }

    data class Result(val file: File, val width: Int, val height: Int)

    /**
     * Wykonuje pojedyncze zdjęcie i zapisuje do [outputFile].
     *
     * @param flash    tryb lampy
     * @param maxResolution true = pełna rozdzielczość sensora (108 MP); false =
     *                      ok. 12 MP (mniejszy plik, szybszy transfer).
     */
    @SuppressLint("MissingPermission") // uprawnienie sprawdzane w MainActivity
    suspend fun capture(
        outputFile: File,
        flash: FlashMode = FlashMode.ON,
        maxResolution: Boolean = true,
    ): Result {
        val cameraId = selectBackCamera()
        val characteristics = cameraManager.getCameraCharacteristics(cameraId)
        val size = chooseJpegSize(characteristics, maxResolution)
        Log.i(TAG, "Wybrana rozdzielczość JPEG: ${size.width}x${size.height} " +
                "(${"%.1f".format(size.width.toLong() * size.height / 1_000_000.0)} MP)")

        val thread = HandlerThread("camera-bg").apply { start() }
        val handler = Handler(thread.looper)
        val executor = Executors.newSingleThreadExecutor()

        val reader = ImageReader.newInstance(size.width, size.height, ImageFormat.JPEG, 1)
        var device: CameraDevice? = null
        try {
            device = openCamera(cameraId, handler)
            val session = createSession(device, reader.surface, executor)
            captureStill(device, session, reader.surface, flash, handler)
            val savedSize = saveImage(reader, outputFile, handler)
            session.close()
            return Result(outputFile, savedSize.width, savedSize.height)
        } finally {
            device?.close()
            reader.close()
            thread.quitSafely()
            executor.shutdown()
        }
    }

    /** Wybiera tylny aparat (LENS_FACING_BACK) — główny sensor 108 MP. */
    private fun selectBackCamera(): String {
        for (id in cameraManager.cameraIdList) {
            val facing = cameraManager.getCameraCharacteristics(id)
                .get(CameraCharacteristics.LENS_FACING)
            if (facing == CameraCharacteristics.LENS_FACING_BACK) return id
        }
        // awaryjnie pierwszy dostępny
        return cameraManager.cameraIdList.firstOrNull()
            ?: throw IllegalStateException("Brak dostępnego aparatu")
    }

    /**
     * Wybiera rozmiar JPEG. Dla [maxResolution]=true bierze NAJWIĘKSZY oferowany
     * przez sensor (na Mi 11 to 12000x9000 ≈ 108 MP). Xiaomi udostępnia pełną
     * rozdzielczość przez StreamConfigurationMap; jeśli na danym egzemplarzu
     * jest zablokowana, lista po prostu nie będzie jej zawierać i weźmiemy
     * największą dostępną.
     */
    private fun chooseJpegSize(c: CameraCharacteristics, maxResolution: Boolean): Size {
        val map = c.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
            ?: throw IllegalStateException("Brak konfiguracji strumieni aparatu")
        val sizes = map.getOutputSizes(ImageFormat.JPEG).toList()
        require(sizes.isNotEmpty()) { "Aparat nie oferuje formatu JPEG" }
        return if (maxResolution) {
            sizes.maxByOrNull { it.width.toLong() * it.height }!!
        } else {
            // najbliżej ~12 MP (pixel-binned), typowo 4000x3000
            val target = 12_000_000L
            sizes.minByOrNull {
                Math.abs(it.width.toLong() * it.height - target)
            }!!
        }
    }

    private suspend fun openCamera(cameraId: String, handler: Handler): CameraDevice =
        suspendCoroutine { cont ->
            @SuppressLint("MissingPermission")
            cameraManager.openCamera(cameraId, object : CameraDevice.StateCallback() {
                override fun onOpened(camera: CameraDevice) = cont.resume(camera)
                override fun onDisconnected(camera: CameraDevice) {
                    camera.close()
                }
                override fun onError(camera: CameraDevice, error: Int) {
                    camera.close()
                    cont.resumeWithException(
                        IllegalStateException("Błąd otwarcia aparatu, kod=$error")
                    )
                }
            }, handler)
        }

    private suspend fun createSession(
        device: CameraDevice,
        surface: android.view.Surface,
        executor: java.util.concurrent.Executor,
    ): CameraCaptureSession = suspendCoroutine { cont ->
        val config = SessionConfiguration(
            SessionConfiguration.SESSION_REGULAR,
            listOf(OutputConfiguration(surface)),
            executor,
            object : CameraCaptureSession.StateCallback() {
                override fun onConfigured(session: CameraCaptureSession) =
                    cont.resume(session)
                override fun onConfigureFailed(session: CameraCaptureSession) =
                    cont.resumeWithException(
                        IllegalStateException("Nie udało się skonfigurować sesji")
                    )
            }
        )
        device.createCaptureSession(config)
    }

    private suspend fun captureStill(
        device: CameraDevice,
        session: CameraCaptureSession,
        surface: android.view.Surface,
        flash: FlashMode,
        handler: Handler,
    ): TotalCaptureResult = suspendCoroutine { cont ->
        val request = device.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE).apply {
            addTarget(surface)
            // Autoekspozycja + sterowanie lampą.
            when (flash) {
                FlashMode.OFF -> {
                    set(CaptureRequest.CONTROL_AE_MODE, CameraMetadata.CONTROL_AE_MODE_ON)
                    set(CaptureRequest.FLASH_MODE, CameraMetadata.FLASH_MODE_OFF)
                }
                FlashMode.ON -> {
                    // lampa „pstroboskopowa" zsynchronizowana z migawką
                    set(CaptureRequest.CONTROL_AE_MODE,
                        CameraMetadata.CONTROL_AE_MODE_ON_ALWAYS_FLASH)
                    set(CaptureRequest.FLASH_MODE, CameraMetadata.FLASH_MODE_SINGLE)
                }
                FlashMode.TORCH -> {
                    // ciągłe światło (latarka) — równe doświetlenie growkitu
                    set(CaptureRequest.CONTROL_AE_MODE, CameraMetadata.CONTROL_AE_MODE_ON)
                    set(CaptureRequest.FLASH_MODE, CameraMetadata.FLASH_MODE_TORCH)
                }
            }
            set(CaptureRequest.CONTROL_AF_MODE,
                CameraMetadata.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
            set(CaptureRequest.JPEG_QUALITY, 95.toByte())
        }.build()

        session.capture(request, object : CameraCaptureSession.CaptureCallback() {
            override fun onCaptureCompleted(
                session: CameraCaptureSession,
                request: CaptureRequest,
                result: TotalCaptureResult,
            ) = cont.resume(result)

            override fun onCaptureFailed(
                session: CameraCaptureSession,
                request: CaptureRequest,
                failure: android.hardware.camera2.CaptureFailure,
            ) = cont.resumeWithException(
                IllegalStateException("Zdjęcie nie powiodło się: ${failure.reason}")
            )
        }, handler)
    }

    private suspend fun saveImage(
        reader: ImageReader,
        outputFile: File,
        handler: Handler,
    ): Size = suspendCoroutine { cont ->
        reader.setOnImageAvailableListener({ r ->
            val image = r.acquireNextImage()
            try {
                val buffer = image.planes[0].buffer
                val bytes = ByteArray(buffer.remaining())
                buffer.get(bytes)
                outputFile.parentFile?.mkdirs()
                FileOutputStream(outputFile).use { it.write(bytes) }
                Log.i(TAG, "Zapisano ${outputFile.absolutePath} (${bytes.size / 1024} KB)")
                cont.resume(Size(image.width, image.height))
            } catch (e: Exception) {
                cont.resumeWithException(e)
            } finally {
                image.close()
            }
        }, handler)
    }
}
