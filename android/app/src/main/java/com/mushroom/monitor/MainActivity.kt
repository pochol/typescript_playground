package com.mushroom.monitor

import android.Manifest
import android.bluetooth.BluetoothDevice
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.WindowManager
import android.widget.ArrayAdapter
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.mushroom.monitor.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Panel na telefonie:
 *  - wybór sparowanego komputera (cel wysyłki Bluetooth),
 *  - „Zrób zdjęcie teraz" (zdjęcie + wysłka po BT),
 *  - start/stop cyklicznych zdjęć, wybór lampy i rozdzielczości.
 *
 * Telefon stoi na statywie — ekran trzymamy włączony.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private var pairedDevices: List<BluetoothDevice> = emptyList()

    private val requestPerms = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { result ->
        if (result.values.all { it }) {
            binding.status.text = "Uprawnienia OK."
            refreshDevices()
        } else {
            binding.status.text = "Brak wymaganych uprawnień (aparat / Bluetooth)."
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        binding.maxRes.isChecked = Prefs.maxRes(this)
        requestPerms.launch(requiredPermissions())

        binding.btnRefresh.setOnClickListener { refreshDevices() }
        binding.btnShootNow.setOnClickListener { shootAndSend() }
        binding.btnStart.setOnClickListener { startSchedule() }
        binding.btnStop.setOnClickListener {
            CaptureScheduler.cancel(this)
            binding.status.text = "Harmonogram zatrzymany."
        }
    }

    private fun requiredPermissions(): Array<String> {
        val perms = mutableListOf(Manifest.permission.CAMERA)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            perms += Manifest.permission.BLUETOOTH_CONNECT
        }
        return perms.toTypedArray()
    }

    private fun hasBtPermission(): Boolean =
        Build.VERSION.SDK_INT < Build.VERSION_CODES.S ||
            ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) ==
            PackageManager.PERMISSION_GRANTED

    private fun refreshDevices() {
        if (!hasBtPermission()) {
            requestPerms.launch(requiredPermissions())
            return
        }
        pairedDevices = try {
            BluetoothSender(this).pairedDevices()
        } catch (e: Exception) {
            binding.status.text = "Bluetooth: ${e.message}"
            emptyList()
        }
        val names = pairedDevices.map { d ->
            @Suppress("MissingPermission")
            "${d.name ?: "?"} (${d.address})"
        }
        binding.devices.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            if (names.isEmpty()) listOf("— brak sparowanych urządzeń —") else names
        )
        val saved = Prefs.targetAddress(this)
        val idx = pairedDevices.indexOfFirst { it.address == saved }
        if (idx >= 0) binding.devices.setSelection(idx)
        if (pairedDevices.isEmpty()) {
            binding.status.text = "Sparuj telefon z komputerem w ustawieniach Bluetooth, potem Odśwież."
        }
    }

    private fun selectedDeviceAddress(): String? =
        pairedDevices.getOrNull(binding.devices.selectedItemPosition)?.address

    private fun selectedFlash(): CameraController.FlashMode = when {
        binding.flashTorch.isChecked -> CameraController.FlashMode.TORCH
        binding.flashOff.isChecked -> CameraController.FlashMode.OFF
        else -> CameraController.FlashMode.ON
    }

    private fun persistChoices(addr: String) {
        Prefs.setTargetAddress(this, addr)
        Prefs.setFlash(this, selectedFlash().name)
        Prefs.setMaxRes(this, binding.maxRes.isChecked)
    }

    private fun shootAndSend() {
        val addr = selectedDeviceAddress()
        if (addr == null) {
            binding.status.text = "Najpierw wybierz sparowany komputer (Odśwież listę)."
            return
        }
        persistChoices(addr)
        binding.status.text = "Robię zdjęcie…"
        lifecycleScope.launch {
            try {
                val file = CaptureStorage.newPhotoFile(this@MainActivity, System.currentTimeMillis())
                val res = withContext(Dispatchers.IO) {
                    CameraController(this@MainActivity)
                        .capture(file, selectedFlash(), binding.maxRes.isChecked)
                }
                val mp = "%.1f".format(res.width.toLong() * res.height / 1_000_000.0)
                binding.status.text = "Zdjęcie ${res.file.name} ($mp MP). Wysyłam po Bluetooth…"
                withContext(Dispatchers.IO) {
                    BluetoothSender(this@MainActivity).send(addr, res.file)
                }
                binding.status.text = "✔ Wysłano ${res.file.name} do komputera."
            } catch (e: Exception) {
                binding.status.text = "Błąd: ${e.message}"
            }
        }
    }

    private fun startSchedule() {
        val addr = selectedDeviceAddress()
        if (addr == null) {
            binding.status.text = "Najpierw wybierz sparowany komputer (Odśwież listę)."
            return
        }
        persistChoices(addr)
        val interval = binding.interval.text.toString().toLongOrNull() ?: 30L
        CaptureScheduler.schedule(
            context = this,
            intervalMinutes = interval,
            flash = selectedFlash(),
            maxResolution = binding.maxRes.isChecked,
        )
        binding.status.text = "Harmonogram: co $interval min (min. 15). " +
            "Po każdym zdjęciu wysłka po Bluetooth do komputera. " +
            if (binding.maxRes.isChecked) "108 MP." else "12 MP."
    }
}
