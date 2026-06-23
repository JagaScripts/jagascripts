package es.jaga.fastfoodcompany.controlador;


import es.jaga.fastfoodcompany.modelo.entidades.Categoria;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services.ServicioCategoria;
import java.util.List;
import javax.swing.JOptionPane;


/**
 *
 * @author Jose Antonio González Alcántara
 */
public class AccionCategorias implements IObjetoAcciones<Categoria>{
    
    private final ServicioCategoria servicioDB;
    private Categoria categoria;
    
    
    /**
     * Constructor que instacia el servicio a la base de datos.
     */
    public AccionCategorias(){
        this.servicioDB = new ServicioCategoria();
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * inserta los datos de la categoria en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean insertar(){
        if (this.servicioDB.obtener(this.categoria.getNombre()) == null){
            this.servicioDB.insertar(this.categoria);
            JOptionPane.showMessageDialog(null, "Categoria Insertado correctamente");
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "Ya existe en la base de datos un categoria con "
                    + "el mismo nombre, presione actualizar lo desea", "Atención",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * borra los datos de la categoria en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean borrar(){
        if (this.servicioDB.obtener(this.categoria.getNombre()) != null){
            this.servicioDB.eliminar(this.categoria.getNombre());
            JOptionPane.showMessageDialog(null, "Categoria borrado correctamente");
            return true;
         } else {
            JOptionPane.showMessageDialog(null, "El categoria con el nombre no existe "
                    + "en la base de datos", "Alerta",JOptionPane.WARNING_MESSAGE);
            return false;
         }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * actualiza los datos de la categoria en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean actualizar(){
        if (this.servicioDB.obtener(this.categoria.getNombre()) != null){
            this.servicioDB.actualizar(this.categoria);
            JOptionPane.showMessageDialog(null, "Categoria Actualizado correctamente");
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "No existe en la base de datos "
                    + "esta categoria para actualizar primero insertar", "Alerta",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * busca los datos de la categoria en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @param nombre de la categoría.
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean buscar(String nombre){
        this.categoria = this.servicioDB.obtener(nombre);
        if (this.categoria != null) {
            JOptionPane.showMessageDialog(null, "Se ha encontrado la categoria con el id: " + this.categoria.getId());
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "El categoria no existe en la base de datos", ""
                    + "Atención",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método getter que devuelve un categoria.
     * 
     * @return categoria
     */
    @Override
    public Categoria obtener(){
        return this.categoria;
    }  

    /**
     * Método setter que establece un categoria.
     * 
     * @param categoria
     */
    @Override
    public void establecer(Categoria categoria) {
        this.categoria = categoria;
    }

    /**
     * Metodo que devuelve una lista de todas las categorias.
     * @return lista de categorias.
     */
    public List<Categoria> listarTodas() {
        return this.servicioDB.listarTodos();
    }

    
}
