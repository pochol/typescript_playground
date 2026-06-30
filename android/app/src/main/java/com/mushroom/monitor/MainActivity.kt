package com.mushroom.monitor

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.WindowManager
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.mushroom.monitor.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Prosty panel sterowania na telefonie:
 *  - „Zrób zdjęcie teraz" (test),
 *  - „Start" / „Stop" cyklicznego robienia zdjęć,
 *  - wybór lampy i rozdzielczości.
 *
 * Ekran trzymamy włączony (FLAG_KEEP_SCREEN_ON) — telefon stoi na statywie i
 * pracuje jako kamera growkitu.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    private val requestCamera = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        binding.status.text = if (granted) "Aparat OK — gotowe."
        else "Brak zgody na aparat — aplikacja nie zadziała."
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Telefon na statywie — ekran ma nie gasnąć.
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        ensureCameraPermission()

        binding.btnShootNow.setOnClickListener { shootNow() }
        binding.btnStart.setOnClickListener { startSchedule() }
        binding.btnStop.setOnClickListener {
            CaptureScheduler.cancel(this)
            binding.status.text = "Harmonogram zatrzymany."
        }
    }

    private fun ensureCameraPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
            != PackageManager.PERMISSION_GRANTED
        ) {
            requestCamera.launch(Manifest.permission.CAMERA)
        } else {
            binding.status.text = "Aparat OK — gotowe."
        }
    }

    private fun selectedFlash(): CameraController.FlashMode = when {
        binding.flashTorch.isChecked -> CameraController.FlashMode.TORCH
        binding.flashOff.isChecked -> CameraController.FlashMode.OFF
        else -> CameraController.FlashMode.ON
    }

    private fun shootNow() {
        binding.status.text = "Robię zdjęcie…"
        lifecycleScope.launch {
            try {
                val file = CaptureStorage.newPhotoFile(this@MainActivity, System.currentTimeMillis())
                val res = withContext(Dispatchers.IO) {
                    CameraController(this@MainActivity)
                        .capture(file, selectedFlash(), binding.maxRes.isChecked)
                }
                binding.status.text =
                    "Zapisano: ${res.file.name}\n${res.width}x${res.height} " +
                    "(${"%.1f".format(res.width.toLong() * res.height / 1_000_000.0)} MP)\n" +
                    "Folder: ${res.file.parent}"
            } catch (e: Exception) {
                binding.status.text = "Błąd: ${e.message}"
            }
        }
    }

    private fun startSchedule() {
        val interval = binding.interval.text.toString().toLongOrNull() ?: 30L
        CaptureScheduler.schedule(
            context = this,
            intervalMinutes = interval,
            flash = selectedFlash(),
            maxResolution = binding.maxRes.isChecked,
        )
        binding.status.text = "Harmonogram włączony: co $interval min " +
                "(min. 15). Lampa: ${selectedFlash()}. " +
                if (binding.maxRes.isChecked) "108 MP." else "12 MP."
    }
}
