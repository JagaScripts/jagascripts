package es.jaga.fastfoodcompany.controlador;

import es.jaga.fastfoodcompany.modelo.entidades.Venta;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services.ServicioVenta;
import java.util.List;
import javax.swing.JOptionPane;

/**
 *
 * @author Jose Antonio González Alcántara
 */
public class AccionVentas implements IObjetoAcciones<Venta>{
    
    private final ServicioVenta servicioDB;
    private Venta venta;
    
    /**
     * Constructor que instacia el servicio a la base de datos.
     */
    public AccionVentas(){
        this.servicioDB = new ServicioVenta();
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * inserta los datos de la venta en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean insertar(){
        this.servicioDB.insertar(this.venta);
        return true;
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * borra los datos de la venta en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean borrar(){
        if (this.servicioDB.obtener(String.valueOf(this.venta.getNumeroDeVenta())) != null){
            this.servicioDB.eliminar(String.valueOf(this.venta.getNumeroDeVenta()));
            JOptionPane.showMessageDialog(null, "Venta borrado correctamente");
            return true;
         } else {
            JOptionPane.showMessageDialog(null, "La venta con el este numero no existe "
                    + "en la base de datos", "Alerta",JOptionPane.WARNING_MESSAGE);
            return false;
         }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * actualiza los datos de la venta en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean actualizar(){
        if (this.servicioDB.obtener(String.valueOf(this.venta.getNumeroDeVenta())) != null){
            this.servicioDB.actualizar(this.venta);
            JOptionPane.showMessageDialog(null, "Venta Actualizado correctamente");
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "La venta con el este numero no existe "
                    + "en la base de datos", "Alerta",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * busca los datos de la venta en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @param numeroDeVenta numero de la venta
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean buscar(String numeroDeVenta){
        this.venta = this.servicioDB.obtener(String.valueOf(numeroDeVenta));
        if (this.venta != null) {
            JOptionPane.showMessageDialog(null, "El total con numero de venta: "
                    + "" + this.venta.getNumeroDeVenta() + " es " + this.venta.getTotal());
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "La venta no existe en la base de datos", ""
                    + "Atención",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método getter que devuelve un venta.
     * 
     * @return venta
     */
    @Override
    public Venta obtener(){
        return this.venta;
    }  

    /**
     * Método setter que establece un venta.
     * 
     * @param venta
     */
    @Override
    public void establecer(Venta venta) {
        this.venta = venta;
    }
    
    /**
     * Metodó que obtiene Ventas de una fecha determinada;
     * @param fecha
     * @return lista de ventas
     */
    public List<Venta> obtenerVentasFecha(String fecha) {
        List<Venta> listaVentas = this.servicioDB.obtenerPorFecha(fecha);
        if (listaVentas == null) {
            JOptionPane.showMessageDialog(null, "No existen ventas en la base de datos con la fecha: " + fecha, ""
                    + "Atención",JOptionPane.WARNING_MESSAGE);
        } else {
            JOptionPane.showMessageDialog(null, "Hay un total de ventas: "
                    + "" + listaVentas.size() + " de la fecha " + fecha);
        }
        return listaVentas;
    }
    
    /**
     * Método que obtiene las ventas segun un id de cliente.
     * @param idCliente
     * @return lista de ventas
     */
    public List<Venta> obtenerVentasIdCliente(int idCliente) {
        List<Venta> listaVentas = this.servicioDB.obtenerPorIdCliente(idCliente);
        if (listaVentas == null) {
            JOptionPane.showMessageDialog(null, "No existen ventas en la base de datos del cliente: " + idCliente, ""
                    + "Atención",JOptionPane.WARNING_MESSAGE);
        } else {
            JOptionPane.showMessageDialog(null, "Hay un total de ventas: "
                    + "" + listaVentas.size() + " del cliente " + idCliente);
        }
        return listaVentas;
    }
    
    /**
     * Método que obtiene el Ultimo Numero de Venta.
     * @return int ultimo número de venta.
     */
    public int obtenerUltimoNumeroDeVenta(){
        return this.servicioDB.obtenerUltimoNumeroDeVenta();
    }
    
}
