package es.jaga.fastfoodcompany.controlador;
import es.jaga.fastfoodcompany.modelo.entidades.CategoriaProducto;
import es.jaga.fastfoodcompany.modelo.entidades.Producto;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services.ServicioCategoriaProducto;
import java.util.ArrayList;
import java.util.List;
/**
 *
 * @author Jose Antonio González Alcántara
 */
public class AccionCategoriaProducto implements IObjetoAcciones<CategoriaProducto>{
    
    private final ServicioCategoriaProducto servicioDB;
    private List<CategoriaProducto> listaCategoriaProducto = new ArrayList<>();
    
    /**
     * Constructor que instacia el servicio a la base de datos.
     */
    public AccionCategoriaProducto(){
        this.servicioDB = new ServicioCategoriaProducto();
    }

    /**
     * "Not supported yet."
     * @return
     */
    @Override
    public Boolean insertar() {
         throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    /**
     * "Not supported yet."
     * @param criterio
     * @return
     */
    @Override
    public Boolean buscar(String criterio) {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    /**
     * "Not supported yet."
     * @return
     */
    @Override
    public Boolean actualizar() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    /**
     * "Not supported yet."
     * @return
     */
    @Override
    public Boolean borrar() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    /**
     * "Not supported yet."
     * @return
     */
    @Override
    public CategoriaProducto obtener() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    /**
     * Función que añade un elemento a la listad de pares Categoria-Producto.
     * @param elemento
     */
    @Override
    public void establecer(CategoriaProducto elemento) {
        this.listaCategoriaProducto.add(elemento);
    }
    
    /**
     * Metodo que devuelve una lista de todods losproductos.
     * @return lista de productos
     */
    public List<Producto> listarTodosProductos(){
        return this.servicioDB.listarTodosProductos();
    }
    
    /**
     * Metodo que devuelve una lista de todods los productos de una categoria.
     * @param idCategoria
     * @return lista de productos.
     */
    public List<Producto> listarProductos(int idCategoria){
        return this.servicioDB.listarProductos(idCategoria);
    }
    
    /**
     * Metodo que devuelve un producto.
     * @param nombre
     * @return Producto
     */
    public Producto obtenerProductoNombre(String nombre){
        return this.servicioDB.obtenerProductoNombre(nombre);
    }
    
}
