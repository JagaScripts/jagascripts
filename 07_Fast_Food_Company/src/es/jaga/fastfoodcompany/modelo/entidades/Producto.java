package es.jaga.fastfoodcompany.modelo.entidades;

import java.util.ArrayList;
import java.util.List;

/**
 * Clase que corresponde al modelo de datos de tipo Producto de la aplicación.
 * 
 * @author Jose Antonio González Alcántara
 */
public class Producto {
    
    private String nombre;
    private float precio;
    private int id;
    private String imagen;
    private List<Categoria> categorias;
    
    /**
     * Constructor que recibe todos lo parametros del formulario.
     * 
     * @param id
     * @param nombre
     * @param precio
     * @param imagen
     */
   
    public Producto(int id, String nombre, float precio, String imagen){
        this.id = id;
        this.nombre = nombre;
        this.precio = precio;
        this.imagen = imagen;        
    }
   
    /**
     * Getter del nombre del Producto.
     * 
     * @return String nombre del producto.
     */
    public String getNombre() {
        return nombre;
    }

    /**
     * Setter del nombre del producto.
     * 
     * @param nombre String nombre del producto.
     */
    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    /**
     * Getter del precio del Producto.
     * 
     * @return String precio del producto.
     */
    public float getPrecio() {
        return precio;
    }

    /**
     * Setter del precio del producto.
     * 
     * @param precio String precio del producto.
     */
    public void setPrecio(float precio) {
        this.precio = precio;
    }

    /**
     * Getter de la id del Producto.
     * 
     * @return String id del producto.
     */
    public int getId() {
        return id;
    }

   /**
     * Setter de la id del producto.
     * 
     * @param id String id del producto.
     */
    public void setId(int id) {
        this.id = id;
    }

    /**
     * Getter de la imagen del Producto.
     * 
     * @return String nombre del producto.
     */
    public String getImagen() {
        return imagen;
    }

    /**
     * Setter de la imagen del producto.
     * 
     * @param imagen String imagen del producto.
     */
    public void setImagen(String imagen) {
        this.imagen = imagen;
    }

    /**
     * Getter de la lista de categorias del producto.
     * 
     * @return lista de las categorias del producto.
     */
    public List getCategorias() {
        return categorias;
    }

    /**
     * Setter de las categorias del producto.
     * 
     * @param categorias List de las categorias del producto.
     */
    public void setCategorias(List categorias) {
        this.categorias = categorias;
    }
    
    /**
     * Método incluye una categoría en la lista de categorias.
     * @param categoria
     */
    public void incluirCategoria(Categoria categoria){
        if (this.categorias == null) {
            this.categorias = new ArrayList<>();
        }
        this.categorias.add(categoria);
    }
    
    /**
     * Método excluye un producto segun id.
     * @param idCategoria
     */
    public void excluirCategoria(int idCategoria){
        if (this.categorias != null) {
            this.categorias.remove(idCategoria);
        }
    }
    
    /**
     * Sobre escritura del metodo.
     * @return String nombre del producto
     */
    @Override
    public String toString(){
        return getNombre();
    }
    
}
