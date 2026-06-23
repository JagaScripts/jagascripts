package es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services;

import es.jaga.fastfoodcompany.modelo.entidades.Categoria;
import es.jaga.fastfoodcompany.modelo.entidades.CategoriaProducto;
import es.jaga.fastfoodcompany.modelo.entidades.Producto;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core.GestionSql;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core.IObjetoAccesoDatos;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core.SQLErrores;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jose Antonio González Alcántara
 */
public class ServicioCategoriaProducto implements IObjetoAccesoDatos<CategoriaProducto>{
   
    //private final String SELECT_ONE_PR = "SELECT * FROM producto_pertenece_categoria WHERE "
           // + "producto_id_producto = ?";
    private final String SELECT_ALL_PRODUCTOS_CATEGORIA = "SELECT * FROM producto_pertenece_categoria WHERE "
            + "categoria_id_categoria = ?";
    private final String SELECT_ALL_PRODUCTOS = "SELECT * FROM producto";
    private final String SELECT_ONE_PRODUCTO = "SELECT * FROM producto WHERE id_producto = ?";
    private final String SELECT_ONE_PRODUCTO_NOMBRE = "SELECT * FROM producto WHERE nombre = ?";
    private final String SELECT_PRODUCTO_BY_ID = "SELECT * FROM producto_pertenece_categoria WHERE categoria_id_categoria = ?";
    private final String INSERT = "INSERT INTO producto_pertenece_categoria (producto_id_producto, categoria_id_categoria)" + 
            "VALUES (?, ?)";
    private final String DELETE = "DELETE FROM producto_pertenece_categoria WHERE producto_id_producto = ? AND categoria_id_categoria = ?";
    
    /**
     * Constructor base.
     */
    public ServicioCategoriaProducto() {
        super();
    }

    @Override
    public void insertar(CategoriaProducto categoria) {
         throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public void actualizar(CategoriaProducto categoria) {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public void eliminar(String id) {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }
    
    /**
     * Excluye un producto de la base de datos.
     * @param idProducto
     * @param idCategoria
     */
    public void excluirProducto(int idProducto, int idCategoria) {
        Connection conexionCategoria = null;
        PreparedStatement consultaCategoria = null;
        try {
            conexionCategoria = GestionSql.openConnection();
            consultaCategoria = conexionCategoria.prepareStatement(DELETE);
            consultaCategoria.setInt(1, idProducto);
            consultaCategoria.setInt(2, idCategoria);
            consultaCategoria.executeUpdate();
        }   catch (SQLException ex) {
            Logger.getLogger(ServicioCategoria.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaCategoria.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioCategoria.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }

    @Override
    public List<CategoriaProducto> listarTodos() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }
    
    /**
     * lista los productos.
     * @return lista de productos.
     */
    public List<Producto> listarTodosProductos() {
        List<Producto> listaProductos = new ArrayList<>();
        Connection conexionProducto = null;
        PreparedStatement consultaProducto = null;
        try {
            conexionProducto = GestionSql.openConnection();
            consultaProducto = conexionProducto.prepareStatement(SELECT_ALL_PRODUCTOS);
            ResultSet rsProducto = consultaProducto.executeQuery();
            while(rsProducto.next()){
                listaProductos.add(enlazarProducto(rsProducto));
            }
            return listaProductos;
        } catch (SQLException ex) {
            Logger.getLogger(ServicioProducto.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
            return null;
        } finally {
            try {
                consultaProducto.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioProducto.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
                return null;
            }
        }
    }
    
    /**
     * lista las categorias
     * @param idCategoria
     * @return lista de categorias
     */
    public List<Producto> listarProductos(int idCategoria) {
        List<Producto> listaProductos = new ArrayList<>();
        Connection conexionProducto = null;
        PreparedStatement consultaProducto = null;
        try {
            conexionProducto = GestionSql.openConnection();
            consultaProducto = conexionProducto.prepareStatement(SELECT_PRODUCTO_BY_ID);
            consultaProducto.setInt(1, idCategoria);
            ResultSet rsCategoriaProdutos = consultaProducto.executeQuery();
            while(rsCategoriaProdutos.next()){
                consultaProducto = conexionProducto.prepareStatement(SELECT_ONE_PRODUCTO);
                consultaProducto.setInt(1, rsCategoriaProdutos.getInt("producto_id_producto"));
                ResultSet rsProducto = consultaProducto.executeQuery();
                while (rsProducto.next()) {
                    listaProductos.add(enlazarProducto(rsProducto));
                }
            }
            return listaProductos;
        } catch (SQLException ex) {
            Logger.getLogger(ServicioProducto.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
            return null;
        } finally {
            try {
                consultaProducto.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioProducto.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
                return null;
            }
        }
    }
    
    /**
     * obtiene un producto
     * @param id
     * @return producto
     */
    public Producto obtenerProducto(int id){
        Producto producto = null;
        Connection conexionProducto = null;
        PreparedStatement consultaProducto = null;
        try {
            conexionProducto = GestionSql.openConnection();
            consultaProducto = conexionProducto.prepareStatement(SELECT_ONE_PRODUCTO);
            consultaProducto.setInt(1, id);
            ResultSet rsProducto = consultaProducto.executeQuery();
            while(rsProducto.next()){
                producto = enlazarProducto(rsProducto);
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioProducto.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaProducto.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioProducto.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return producto;
    }

    /**
     * obtiene un producto por nombre
     * @param nombre
     * @return producto
     */
    public Producto obtenerProductoNombre(String nombre){
        Producto producto = null;
        Connection conexionProducto = null;
        PreparedStatement consultaProducto = null;
        try {
            conexionProducto = GestionSql.openConnection();
            consultaProducto = conexionProducto.prepareStatement(SELECT_ONE_PRODUCTO_NOMBRE);
            consultaProducto.setString(1, nombre);
            ResultSet rsProducto = consultaProducto.executeQuery();
            while(rsProducto.next()){
                producto = enlazarProducto(rsProducto);
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioProducto.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaProducto.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioProducto.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return producto;
    }
    
    @Override
    public CategoriaProducto obtener(String id) {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }
    
    /**
     * obtiene un producto por id y categoria
     * @param id
     * @param categoria
     */
    public void obtenerProductos(int id, Categoria categoria){
        Connection conexionCategoria = null;
        PreparedStatement consultaCategoria = null;
        try {
            conexionCategoria = GestionSql.openConnection();
            consultaCategoria = conexionCategoria.prepareStatement(SELECT_ALL_PRODUCTOS_CATEGORIA);
            consultaCategoria.setInt(1, id);
            ResultSet rsCategoria = consultaCategoria.executeQuery();
            while(rsCategoria.next()){
                categoria.incluirProducto(obtenerProducto(rsCategoria.getInt("producto_id_producto")));
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioCategoria.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaCategoria.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioCategoria.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }

    @Override
    public CategoriaProducto enlazar(ResultSet resultSet) {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }
    
    /**
     * Método para enlazar un ResultSet con un objeto Producto.
     * @param resultSet
     * @return
     */
    public Producto enlazarProducto(ResultSet resultSet){
        try {
            Producto producto = new Producto(resultSet.getInt("id_producto"), resultSet.getString("nombre"), resultSet.getFloat("precio"), 
                                             resultSet.getString("imagen"));
            return producto;
        } catch (SQLException ex) {
            Logger.getLogger(ServicioProducto.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_ENLACE, ex);
        }
        return null;
    }
}
