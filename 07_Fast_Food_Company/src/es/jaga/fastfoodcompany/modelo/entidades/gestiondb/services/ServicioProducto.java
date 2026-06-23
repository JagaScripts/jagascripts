package es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services;

import es.jaga.fastfoodcompany.modelo.entidades.Categoria;
import es.jaga.fastfoodcompany.modelo.entidades.Producto;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core.GestionSql;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core.IObjetoAccesoDatos;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core.SQLErrores;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jose Antonio González Alcántara
 */
public class ServicioProducto implements IObjetoAccesoDatos<Producto>{
    //Sentencia CRUD SQL
    //Selecciona todos los productos de la tabla productos.
    private final String SELECT_ALL = "SELECT * FROM producto";
    private final String SELECT_ALL_PRODUCTS_CAT_PRO = "SELECT * FROM producto_pertenece_categoria WHERE "
            + "producto_id_producto = ?";
    private final String SELECT_CATEGORIS = "SELECT * FROM categoria WHERE id_categoria = ?";
    //Selecciona un producto de la tabla productos con un determinado DNI.
    private final String SELECT_ONE = "SELECT * FROM producto WHERE nombre = ?";
    //Actualiza un producto de la tabla productos con determinados parametros.
    private final String UPDATE = "UPDATE producto SET nombre = ?, precio = ?, imagen = ? WHERE id_producto = ?";
    //Inserta un producto de la tabla productos con determinados parametros.
    private final String INSERT = "INSERT INTO producto (nombre, precio, imagen)" + 
            "VALUES (?, ?, ?)";
    //Elimina un producto de la tabla productos con un determinado DNI.
    private final String DELETE = "DELETE FROM producto WHERE nombre = ?";
    
    /**
     * Constructor base.
     */
    public ServicioProducto() {
        super();
    }
    
     /**
     * Función para insertar un producto.
     * 
     * @param producto con los datos a insertar.
     */
    @Override
    public void insertar(Producto producto) {
        Connection conexionProducto = null;
        PreparedStatement consultaProducto = null;
        try {
            conexionProducto = GestionSql.openConnection();
            consultaProducto = conexionProducto.prepareStatement(INSERT,PreparedStatement.RETURN_GENERATED_KEYS);
            consultaProducto.setString(1, producto.getNombre());
            consultaProducto.setFloat(2, producto.getPrecio());
            consultaProducto.setString(3, producto.getImagen());
            consultaProducto.executeUpdate();
            ResultSet rsProducto = consultaProducto.getGeneratedKeys();
            while (rsProducto.next()) {
                producto.setId(rsProducto.getInt(1));
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
    }

    /**
     * Función para actualizar un producto.
     *
     * @param producto con los datos a actualizar. 
     */
    @Override
    public void actualizar(Producto producto) {
        Connection conexionProducto = null;
        PreparedStatement consultaProducto = null;
        try {
            conexionProducto = GestionSql.openConnection();
            consultaProducto = conexionProducto.prepareStatement(UPDATE);
            consultaProducto.setString(1, producto.getNombre());
            consultaProducto.setFloat(2, producto.getPrecio());
            consultaProducto.setString(3, producto.getImagen());
            consultaProducto.setInt(4, producto.getId());
            consultaProducto.executeUpdate();
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
    }

    /**
     * Función para eliminar un producto.
     *
     * @param nombre String valor de búsqueda. 
     */
    @Override
    public void eliminar(String nombre) {
        Connection conexionProducto = null;
        PreparedStatement consultaProducto = null;
        try {
            conexionProducto = GestionSql.openConnection();
            consultaProducto = conexionProducto.prepareStatement(DELETE);
            consultaProducto.setString(1, nombre);
            consultaProducto.executeUpdate();
        }   catch (SQLException ex) {
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
    }

     /**
     * Método para listar Producto.
     * 
     * @return Lista de Producto.
     */
    @Override
    public List<Producto> listarTodos() {
        List<Producto> producto = new ArrayList<>();
         Connection conexionProducto = null;
         PreparedStatement consultaProducto = null;
        try {
            conexionProducto = GestionSql.openConnection();
            consultaProducto = conexionProducto.prepareStatement(SELECT_ALL);
            ResultSet rsProducto = consultaProducto.executeQuery();
            while(rsProducto.next()){
                producto.add(enlazar(rsProducto));
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
     * Método de búsqueda.
     *
     * @param nombre
     * @return Producto encontrado con los datos.
     */
    @Override
    public Producto obtener(String nombre) {
        Producto producto = null;
        Connection conexionProducto = null;
        PreparedStatement consultaProducto = null;
        try {
            conexionProducto = GestionSql.openConnection();
            consultaProducto = conexionProducto.prepareStatement(SELECT_ONE);
            consultaProducto.setString(1, nombre);
            ResultSet rsProducto = consultaProducto.executeQuery();
            while(rsProducto.next()){
                producto = enlazar(rsProducto);
                consultaProducto = conexionProducto.prepareStatement(SELECT_ALL_PRODUCTS_CAT_PRO);
                consultaProducto.setInt(1, producto.getId());
                ResultSet rsCategoriaProducto = consultaProducto.executeQuery();
                while (rsCategoriaProducto.next()) {
                    consultaProducto = conexionProducto.prepareStatement(SELECT_CATEGORIS);
                    consultaProducto.setInt(1, rsCategoriaProducto.getInt("categoria_id_categoria"));
                    ResultSet rsProductos = consultaProducto.executeQuery();
                    while (rsProductos.next()) {
                        Categoria categoria = new Categoria(rsProductos.getInt("id_categoria"),rsProductos.getString("nombre"),
                                                            rsProductos.getString("imagen"));
                        producto.incluirCategoria(categoria);
                    }
                }
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
     * Método para enlazar un ResultSet con un objeto Producto.
     *
     * @param resultSet ResultSet con la consulta.
     * @return Producto producto con los datos enlazados.
     */
    @Override
    public Producto enlazar(ResultSet resultSet) {
        try {
            Producto producto = new Producto(resultSet.getInt("id_producto"),resultSet.getString("nombre"), resultSet.getFloat("precio"), 
                                             resultSet.getString("imagen"));
            return producto;
        } catch (SQLException ex) {
            Logger.getLogger(ServicioProducto.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_ENLACE, ex);
        }
        return null;
    }
 
}
