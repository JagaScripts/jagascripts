package es.jaga.fastfoodcompany.controlador;

import es.jaga.fastfoodcompany.modelo.entidades.Producto;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services.ServicioProducto;
import javax.swing.JOptionPane;

/**
 *
 * @author Jose Antonio González Alcántara
 */
public class AccionProductos implements IObjetoAcciones<Producto>{
    
    private final ServicioProducto servicioDB;
    private Producto producto;
    
    /**
     * Constructor que instacia el servicio a la base de datos.
     */
    public AccionProductos(){
        this.servicioDB = new ServicioProducto();
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * inserta los datos del producto en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean insertar(){
        if (this.servicioDB.obtener(this.producto.getNombre()) == null){
            this.servicioDB.insertar(this.producto);
            JOptionPane.showMessageDialog(null, "Producto Insertado correctamente" + " el id del producto es: " + producto.getId());
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "Ya existe en la base de datos un producto con "
                    + "el mismo nombre y no puede haber dos productos con el mismo nombre", "Atención",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * borra los datos del producto en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean borrar(){
        if (this.servicioDB.obtener(this.producto.getNombre()) != null){
            this.servicioDB.eliminar(this.producto.getNombre());
            JOptionPane.showMessageDialog(null, "Producto borrado correctamente");
            return true;
         } else {
            JOptionPane.showMessageDialog(null, "El producto con el nombre no existe "
                    + "en la base de datos", "Alerta",JOptionPane.WARNING_MESSAGE);
            return false;
         }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * actualiza los datos del producto en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean actualizar(){
        if (this.servicioDB.obtener(this.producto.getNombre()) != null){
            this.servicioDB.actualizar(this.producto);
            JOptionPane.showMessageDialog(null, "Producto Actualizado correctamente");
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "Ya existe en la base de datos "
                    + "un producto con el mismo nombre", "Alerta",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * busca los datos del producto en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @param nombre del producto
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean buscar(String nombre){
        this.producto = this.servicioDB.obtener(nombre);
        if (this.producto != null) {
            JOptionPane.showMessageDialog(null, "El id del producto con el nombre: "
                    + "" + this.obtener().getNombre()+ " es " + this.obtener().getId());
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "El producto no existe en la base de datos", ""
                    + "Atención",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método getter que devuelve un producto.
     * 
     * @return producto
     */
    @Override
    public Producto obtener(){
        return this.producto;
    }  

    /**
     * Método setter que establece un producto.
     * 
     * @param producto
     */
    @Override
    public void establecer(Producto producto) {
        this.producto = producto;
    }
    
}
