package es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core;

import java.sql.ResultSet;
import java.util.List;

/**
 * Interfaz que define las operaciones de interacción con la base de datos.
 *
 * @param <T> Tipo de datos que manejará.
 * @author Jose Antonio González Alcántara.
 *
 */
public interface IObjetoAccesoDatos<T> {

    /**
     * Función para insertar objetos.
     *
     * @param elemento Elemento con los datos que se desean insertar
     */
    void insertar(T elemento);

    /**
     * Función para actualizar un elemento.
     *
     * @param elemento Elemento con los datos que se desean actualizar.
     */
    void actualizar(T elemento);

    /**
     * Función para eliminar un objeto.
     *
     * @param id String valor del filtro.
     */
    void eliminar(String id);

    /**
     * Función para cargar todos los objeto.
     *
     * @return List con los objetos cargados.
     */
    List<T> listarTodos();

    /**
     * Función para buscar por dni.
     *
     * @param id String valor del filtro.
     * @return T elemento con los datos asociados que cumplen el criterio.
     */
    T obtener(String id);

    /**
     * Función que enlaza un ResultSet con un objeto.
     *
     * @param resultSet ResultSet a enlazar
     * @return T elemento con los datos asociados.
     */
    T enlazar(ResultSet resultSet);
}
