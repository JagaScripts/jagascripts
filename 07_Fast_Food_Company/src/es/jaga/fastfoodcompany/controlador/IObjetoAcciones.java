package es.jaga.fastfoodcompany.controlador;

/**
* Interfaz que define las operaciones logícas de la aplicación con la base de datos.
*
* @param <T> Tipo de datos que manejará.
* @author Jose Antonio González Alcántara.
*
*/
public interface IObjetoAcciones<T> {
    
    /**
     * Método para controlar la inserción de objetos.
     * @return si la operación se ha realizado correctamente.
     */
    public Boolean insertar();
    
    /**
     * Método para controlar la busqueda de objetos.
     * @param criterio
     * @return si la operación se ha realizado correctamente.
     */
    public Boolean buscar(String criterio);
    
    /**
     * Método para controlar la actualización de objetos.
     * @return si la operación se ha realizado correctamente.
     */
    public Boolean actualizar();
    
    /**
     * Método para controlar la eliminación de objetos.
     * @return si la operación se ha realizado correctamente.
     */
    public Boolean borrar();
    
    /**
     * Método que devuelve un objeto de tipo T.
     * @return un objeto si la operación se ha realizado correctamente.
     */
    T obtener();
    
    /**
     * Función para establecer el elemento.
     * @param elemento a establecer
     */
    void establecer(T elemento);
}
