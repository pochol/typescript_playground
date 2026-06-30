package com.mushroom.monitor

import android.content.Context

/** Trwałe ustawienia aplikacji (adres sparowanego komputera, parametry zdjęcia). */
object Prefs {
    private const val FILE = "mushroom_prefs"
    private const val KEY_ADDR = "target_bt_address"
    private const val KEY_FLASH = "flash"
    private const val KEY_MAX_RES = "max_res"

    private fun p(c: Context) = c.getSharedPreferences(FILE, Context.MODE_PRIVATE)

    fun targetAddress(c: Context): String? = p(c).getString(KEY_ADDR, null)
    fun setTargetAddress(c: Context, addr: String) =
        p(c).edit().putString(KEY_ADDR, addr).apply()

    fun flash(c: Context): String = p(c).getString(KEY_FLASH, "ON") ?: "ON"
    fun setFlash(c: Context, v: String) = p(c).edit().putString(KEY_FLASH, v).apply()

    fun maxRes(c: Context): Boolean = p(c).getBoolean(KEY_MAX_RES, false)
    fun setMaxRes(c: Context, v: Boolean) = p(c).edit().putBoolean(KEY_MAX_RES, v).apply()
}
