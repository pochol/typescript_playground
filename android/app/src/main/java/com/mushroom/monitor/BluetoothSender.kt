package com.mushroom.monitor

import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import android.content.Context
import android.util.Log
import java.io.DataOutputStream
import java.io.File
import java.util.UUID

/**
 * Wysyła plik do sparowanego komputera przez Bluetooth (RFCOMM / SPP).
 *
 * Protokół (odbierany przez relay/bt_receiver.py):
 *   [int32 BE: długość nazwy][nazwa UTF-8][int64 BE: rozmiar pliku][bajty pliku]
 *
 * Bluetooth, nie USB — zgodnie z wymaganiami (REQUIREMENTS.md). Telefon łączy
 * się jako klient do komputera, który wystawia serwis SPP.
 */
class BluetoothSender(private val context: Context) {

    companion object {
        private const val TAG = "BluetoothSender"
        /** Standardowy UUID Serial Port Profile — ten sam wystawia komputer. */
        val SPP_UUID: UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
    }

    private fun adapter(): BluetoothAdapter =
        BluetoothAdapter.getDefaultAdapter()
            ?: throw IllegalStateException("Ten telefon nie ma Bluetooth")

    /** Lista sparowanych urządzeń (komputer musi być wcześniej sparowany w ustawieniach). */
    @SuppressLint("MissingPermission") // BLUETOOTH_CONNECT sprawdzane w MainActivity
    fun pairedDevices(): List<BluetoothDevice> =
        adapter().bondedDevices?.toList() ?: emptyList()

    /** Łączy się z [deviceAddress] i przesyła [file]. Blokujące — wołaj z wątku IO. */
    @SuppressLint("MissingPermission")
    fun send(deviceAddress: String, file: File) {
        val adapter = adapter()
        if (!adapter.isEnabled) throw IllegalStateException("Włącz Bluetooth")
        val device = adapter.getRemoteDevice(deviceAddress)
        // Skanowanie spowalnia połączenie RFCOMM — wyłącz na czas transferu.
        adapter.cancelDiscovery()

        var socket: BluetoothSocket? = null
        try {
            socket = device.createRfcommSocketToServiceRecord(SPP_UUID)
            socket.connect()
            DataOutputStream(socket.outputStream).use { out ->
                val nameBytes = file.name.toByteArray(Charsets.UTF_8)
                out.writeInt(nameBytes.size)        // int32 BE
                out.write(nameBytes)
                out.writeLong(file.length())        // int64 BE
                file.inputStream().use { input ->
                    val buf = ByteArray(8192)
                    while (true) {
                        val n = input.read(buf)
                        if (n < 0) break
                        out.write(buf, 0, n)
                    }
                }
                out.flush()
            }
            Log.i(TAG, "Wysłano ${file.name} (${file.length() / 1024} KB) -> $deviceAddress")
        } finally {
            try {
                socket?.close()
            } catch (_: Exception) {
            }
        }
    }
}
