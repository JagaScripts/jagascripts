package es.jaga.fastfoodcompany.controlador;

import es.jaga.fastfoodcompany.modelo.entidades.DetalleVenta;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services.ServicioDetalleVenta;
import java.util.List;
import javax.swing.JOptionPane;

/**
 *
 * @author Jose Antonio González Alcántara
 */
public class AccionDetalleVenta implements IObjetoAcciones<DetalleVenta>{
    
    private final ServicioDetalleVenta servicioDB;
    private DetalleVenta venta;
    
    /**
     * Constructor que instacia el servicio a la base de datos.
     */
    public AccionDetalleVenta(){
        this.servicioDB = new ServicioDetalleVenta();
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
            JOptionPane.showMessageDialog(null, "DetalleVenta borrado correctamente");
            return true;
         } else {
            JOptionPane.showMessageDialog(null, "La venta con el nombre no existe "
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
            JOptionPane.showMessageDialog(null, "DetalleVenta Actualizado correctamente");
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "PAra actualizar un detalle venta "
                    + "tiene que existir", "Alerta",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * busca los datos de la venta en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @param numeroDeVenta nuero de la venta.
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean buscar(String numeroDeVenta){
        this.venta = this.servicioDB.obtener(String.valueOf(this.venta.getNumeroDeVenta()));
        if (this.venta != null) {
            JOptionPane.showMessageDialog(null, "La nombre venta con el nombre: "
                    + "" + this.obtener().getNumeroDeVenta() + " es " + this.obtener().toString());
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "La venta no existe en la base de datos", ""
                    + "Atención",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método getter que devuelve una venta.
     * 
     * @return venta
     */
    @Override
    public DetalleVenta obtener(){
        return this.venta;
    }  

    /**
     * Método setter que establece una venta.
     * 
     * @param venta
     */
    @Override
    public void establecer(DetalleVenta venta) {
        this.venta = venta;
    }
        
    /**
     * Metodo que obtiene los detalles de venta de una venta determinada.
     * @param numeroDeVenta
     * @return lista de detalles venta
     */
    public List<DetalleVenta> obtenerDetallesVenta(int numeroDeVenta) {
        List<DetalleVenta> listaDetalleVentas = this.servicioDB.obtenerDetallesVenta(numeroDeVenta);
        return listaDetalleVentas;
    }
}
