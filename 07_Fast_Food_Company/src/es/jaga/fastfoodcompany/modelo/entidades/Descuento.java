package es.jaga.fastfoodcompany.modelo.entidades;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.security.SecureRandom;
import java.math.BigInteger;

/**
 * Clase que corresponde al modelo de datos de tipo Descuento de la aplicación.
 * @author Jose Antonio González Alcántara
 */
public class Descuento {
    
    private String clave;
    private int cantidad;
    private int cliente;
    private String caducidad;
    private final DateFormat formatoFecha =  new SimpleDateFormat("dd/MM/yyyy");
    
    /**
     * Constructor que recibe dos parametros del formulario.
     * @param cantidad
     * @param cliente
     */
    public Descuento(int cantidad, int cliente){
        this.cantidad = cantidad;
        this.cliente = cliente;
        this.cantidad = cantidad;
        this.clave = null;
        if (cantidad != 0) {
            this.caducidad = sumarDiasAFecha(new Date(), 15);
            this.clave = generarClave();
        }   
    }
    
    /**
     * Constructor que recibe todos los parámetros del formulario.
     * @param cantidad
     * @param cliente
     * @param caducidad
     * @param clave
     */
    public Descuento(int cantidad, int cliente, String caducidad, String clave){
        this.cantidad = cantidad;
        this.cliente = cliente;
        this.caducidad = caducidad;
        this.clave = clave;
    }
        
    /**
     * Getter de la clave.
     * @return String clave.
     */
    public String getClave() {
        return clave;
    }

    /**
     * Setter de la cantidad.
     * @param clave
     */
    public void setClave(String clave) {
        this.clave = clave;
    }

    /**
     * Getter de la cantidad.
     * @return int cantidad.
     */
    public int getCantidad() {
        return cantidad;
    }

    /**
     * Setter de la cantidad.
     * @param cantidad
     */
    public void setCantidad(int cantidad) {
        this.cantidad = cantidad;
    }

    /**
     * Getter del cliente.
     * @return int cliente
     */
    public int getCliente() {
        return cliente;
    }

    /**
     * Setter del cliente.
     * @param cliente
     */
    public void setCliente(int cliente) {
        this.cliente = cliente;
    }

    /**
     * Getter de la caducidad.
     * @return String caducidad
     */
    public String getCaducidad() {
        return caducidad;
    }

    /**
     * Setter de la caducidad.
     * @param caducidad
     */
    public void setCaducidad(String caducidad) {
        this.caducidad = caducidad;
    }
    
    private String sumarDiasAFecha(Date fecha, int dias){
      if (dias==0) return this.formatoFecha.format(fecha);
      Calendar calendar = Calendar.getInstance();
      calendar.setTime(fecha); 
      calendar.add(Calendar.DAY_OF_YEAR, dias);  
      return this.formatoFecha.format(calendar.getTime()); 
    }
    
    private String generarClave(){
        SecureRandom aleatorio = new SecureRandom();
        String nuevaClave = new BigInteger(130, aleatorio).toString(32);
        return nuevaClave;
    }
    
}
