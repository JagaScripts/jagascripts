package com.jaga.android.to_jaga_android_agrupados.data;

import com.jaga.android.to_jaga_android_agrupados.beans.Local;


import java.util.ArrayList;


public class AgrupadosData {
	private static ArrayList<Local> lstLocales;
	private static Local localSeleccionado;

	public static ArrayList<Local> getLstLocales() {
		return lstLocales;
	}

	public static void setLstLocales(ArrayList<Local> lstLocales) {
		AgrupadosData.lstLocales = lstLocales;
	}

	public static Local getLocalSeleccionado() {
		return localSeleccionado;
	}

	public static void setLocalSeleccionado(Local localSeleccionado) {
		AgrupadosData.localSeleccionado = localSeleccionado;
	}
}

