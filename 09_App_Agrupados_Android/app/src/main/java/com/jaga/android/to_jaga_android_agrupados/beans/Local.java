package com.jaga.android.to_jaga_android_agrupados.beans;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

public class Local {
	
	private String localName;
	private String localDescription;
	private String localLongitud;
	private String localLatitud;
	private String urlImagen;

	private final static String NOMBRE = "NOMBRE";
	private final static String LONGITUD = "LONGITUD";
	private final static String LATITUD = "LATITUD";
	private final static String DESCRIPCION = "DESCRIPCION";
	private final static String IMAGEN = "IMAGEN";

	public String getLocalDescription() {
		return localDescription;
	}

	public void setLocalDescription(String localDescription) {
		this.localDescription = localDescription;
	}

	public String getLocalLatitud() {
		return localLatitud;
	}

	public void setLocalLatitud(String localLatitud) {
		this.localLatitud = localLatitud;
	}

	public String getLocalLongitud() {
		return localLongitud;
	}

	public void setLocalLongitud(String localLongitud) {
		this.localLongitud = localLongitud;
	}

	public String getUrlImagen() {
		return urlImagen;
	}

	public void setUrlImagen(String urlImagen) {
		this.urlImagen = urlImagen;
	}

	public String getLocalName() {
		return localName;
	}
	public void setLocalName(String localName) {
		this.localName = localName;
	}


	public static ArrayList<Local> getArrayListFromJSon(JSONArray datos){
		ArrayList<Local> lista = null;
		Local local = null;
		try {
			if(datos!=null && datos.length() > 0 ){
				lista = new ArrayList<Local>();
			}
			for (int i = 0; i < datos.length(); i++) {
				JSONObject json_data = datos.getJSONObject(i);
				local = new Local();
				local.setLocalName(json_data.getString(NOMBRE));
				local.setLocalDescription(json_data.getString(DESCRIPCION));
				local.setLocalLongitud(json_data.getString(LONGITUD));
				local.setLocalLatitud(json_data.getString(LATITUD));
				local.setUrlImagen(json_data.getString(IMAGEN));
				lista.add(local);
			}
		} catch (JSONException e) {
			e.printStackTrace();
		}
		return lista;

	}
}
