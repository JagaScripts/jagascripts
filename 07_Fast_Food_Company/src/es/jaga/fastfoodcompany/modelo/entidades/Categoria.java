package es.jaga.fastfoodcompany.modelo.entidades;

import java.util.ArrayList;
import java.util.List;

/**
 * Clase que corresponde al modelo de datos de tipo Categoria de la aplicación.
 * @author Jose Antonio González Alcántara
 */
public class Categoria {
    
    private int id;
    private String nombre;
    private String imagen;
    private List<Producto> productos;
    
    /**
     * Constructor que recibe todos los parámetros del formulario.
     * @param id
     * @param nombre
     * @param imagen
     */
    public Categoria(int id, String nombre, String imagen){
        this.id = id;
        this.nombre = nombre;
        this.imagen = imagen;
    }

    /**
     * Getter del Id.
     * @return id
     */
    public int getId() {
        return id;
    }

    /**
     * Setter del id.
     * @param id
     */
    public void setId(int id) {
        this.id = id;
    }

    /**
     * Getter del Nombre.
     * @return nombre
     */
    public String getNombre() {
        return nombre;
    }

    /**
     * Setter del nombre.
     * @param nombre
     */
    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    /**
     * Getter del nombre de la imagen.
     * @return
     */
    public String getImagen() {
        return imagen;
    }

    /**
     * Setter del nombre de la imagen.
     * @param imagen
     */
    public void setImagen(String imagen) {
        this.imagen = imagen;
    }

    /**
     * Getter de la lista de productos.
     * @return lista de productos.
     */
    public List<Producto> getProductos() {
        return productos;
    }

    /**
     * Setter de la lista de productos.
     * @param productos lista de productos.
     */
    public void setProductos(List<Producto> productos) {
        this.productos = productos;
    }
    
    /**
     * Método incluye un producto en la lista de productos.
     * @param producto
     */
    public void incluirProducto(Producto producto){
        if (this.productos == null) {
            this.productos = new ArrayList<>();
        }
        this.productos.add(producto);
    }
    
    /**
     * Método excluye un producto segun id.
     * @param idProducto
     */
    public void excluirProducto(int idProducto){
        if (this.productos != null) {
            this.productos.remove(idProducto);
        }
    }
    
}
