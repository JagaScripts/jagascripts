package es.jaga.fastfoodcompany.modelo.entidades;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Clase que corresponde al modelo de datos de tipo Venta de la aplicación.
 * @author Jose Antonio González Alcántara
 */
public class Venta {
    
    private float total;
    private int numeroDeVenta;
    private String fecha;
    private int cliente;
    private final DateFormat formatoFecha =  new SimpleDateFormat("dd/MM/yyyy");
    
    /**
     * Constructor que recibe dos parámetros del formulario.
     * @param total
     * @param cliente
     */
    public Venta(float total, int cliente){
        this.total = total;
        this.cliente = cliente;
        this.fecha = this.formatoFecha.format(new Date());
    }

    /**
     * Constructor que recibe todos los parámetros del formulario.
     * @param numeroDeVenta
     * @param total
     * @param cliente
     * @param fecha
     */
    public Venta(int numeroDeVenta, float total, int cliente, String fecha){
        this.numeroDeVenta = numeroDeVenta;
        this.total = total;
        this.cliente = cliente;
        this.fecha = fecha;
    }
    
    /**
     * Constructor que unparámetro del formulario.
     * @param total
     */
    public Venta(float total){
        this.cliente = 0;
        this.total = total;
        this.fecha = this.formatoFecha.format(new Date());
    } 
    
    /**
     * Getter del total.
     * @return total.
     */
    public float getTotal() {
        return total;
    }

    /**
     * Setter del total.
     * @param total
     */
    public void setTotal(float total) {
        this.total = total;
    }

    /**
     * Getter del numero d venta
     * @return numero de venta
     */
    public int getNumeroDeVenta() {
        return numeroDeVenta;
    }

    /**
     * Setter numero de venta.
     * @param numeroDeVenta
     */
    public void setNumeroDeVenta(int numeroDeVenta) {
        this.numeroDeVenta = numeroDeVenta;
    }

    /**
     * Getter de la fecha.
     * @return fecha.
     */
    public String getFecha() {
        return fecha;
    }

    /**
     * Setter de la fecha.
     * @param fecha
     */
    public void setFecha(String fecha) {
        this.fecha = fecha;
    }

    /**
     * Getter del cliente.
     * @return cliente
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
    
    
}
