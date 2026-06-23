package es.jaga.fastfoodcompany.modelo.entidades;

/**
 * Clase que corresponde al modelo de datos de tipo DetalleVenta de la aplicación.
 * @author Jose Antonio González Alcántara
 */
public class DetalleVenta {
    
    private int numeroDeVenta;
    private int idProducto;
    private int cantidad;
    private float precioVenta;
    
    /**
     * Constructor que recibe todos los parámetros del formulario.
     * @param numeroDeVenta
     * @param idProducto
     * @param cantidad
     * @param precioVenta
     */
    public DetalleVenta(int numeroDeVenta, int idProducto, int cantidad, float precioVenta){
        this.numeroDeVenta = numeroDeVenta;
        this.idProducto = idProducto;
        this.cantidad = cantidad;
        this.precioVenta = precioVenta;
    }

    /**
     * Getter del número de venta.
     * @return número de venta.
     */
    public int getNumeroDeVenta() {
        return numeroDeVenta;
    }

    /**
     * Setter del número de venta.
     * @param numeroDeVenta
     */
    public void setNumeroDeVenta(int numeroDeVenta) {
        this.numeroDeVenta = numeroDeVenta;
    }

    /**
     * Getter del id del Producto.
     * @return idProducto
     */
    public int getIdProducto() {
        return idProducto;
    }

    /**
     * Setter del id del producto.
     * @param idProducto
     */
    public void setIdProducto(int idProducto) {
        this.idProducto = idProducto;
    }

    /**
     * Getter de la cantidad del detalle.
     * @return cantidad
     */
    public int getCantidad() {
        return cantidad;
    }

    /**
     * Setter de la cantidad del detalle.
     * @param cantidad
     */
    public void setCantidad(int cantidad) {
        this.cantidad = cantidad;
    }

    /**
     * Getter de precio de venta.
     * @return float precio de venta
     */
    public float getPrecioVenta() {
        return precioVenta;
    }

    /**
     * Setter del predio de venta.
     * @param precioVenta
     */
    public void setPrecioVenta(float precioVenta) {
        this.precioVenta = precioVenta;
    }

}
