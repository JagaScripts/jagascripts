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
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Jose Antonio González Alcántara
 */
public class ServicioCategoria implements IObjetoAccesoDatos<Categoria>{
    //Sentencia CRUD SQL
    //Selecciona todos los categorias de la tabla categorias.
    private final String SELECT_ALL = "SELECT * FROM categoria";
    private final String SELECT_ALL_PRODUCTS_CAT_PRO = "SELECT * FROM producto_pertenece_categoria WHERE "
            + "categoria_id_categoria = ?";
    private final String SELECT_PRODUCTS = "SELECT * FROM producto WHERE id_producto = ?";
    //Selecciona un categoria de la tabla categorias con un determinado DNI.
    private final String SELECT_ONE = "SELECT * FROM categoria WHERE nombre = ?";
    //Actualiza un categoria de la tabla categorias con determinados parametros.
    private final String UPDATE = "UPDATE categoria SET nombre = ?, imagen = ? WHERE id_categoria = ?";
    //private final Sring UPDATE = "UPDATE producto_pertenece_categoria SET "
    //Inserta un categoria de la tabla categorias con determinados parametros.
    private final String INSERT = "INSERT INTO categoria (id_categoria, nombre, imagen)" + 
            "VALUES (?, ?, ?)";
    private final String INSERT_CAT_PRO = "INSERT INTO producto_pertenece_categoria (producto_id_producto, categoria_id_categoria)" + 
            "VALUES (?, ?)";
    //Elimina un categoria de la tabla categorias con un determinado DNI.
    private final String DELETE = "DELETE FROM categoria WHERE nombre = ?";
    private final String DELETE_CAT_PRO_BY_CATEGORIA = "DELETE producto_pertenece_categoria FROM producto_pertenece_categoria WHERE categoria_id_categoria = ?";
    //private final String DELETE_PRODUCT_CAT_PRO = "DELETE FROM producto_pertenece_categoria WHERE categoria_id_categoria = ? AND"
           // + "producto_id_producto = ?";
    private final ServicioCategoriaProducto categoriaProducto;
    
    /**
     * Constructor base.
     */
    public ServicioCategoria() {
        super();
        this.categoriaProducto = new ServicioCategoriaProducto();
    }

    @Override
    public void insertar(Categoria categoria) {
        Connection conexionCategoria = null;
        PreparedStatement consultaCategoria = null;
        try {
            conexionCategoria = GestionSql.openConnection();
            conexionCategoria.setAutoCommit(false);
            consultaCategoria = conexionCategoria.prepareStatement(INSERT,PreparedStatement.RETURN_GENERATED_KEYS);
            consultaCategoria.setInt(1, categoria.getId());
            consultaCategoria.setString(2, categoria.getNombre());
            consultaCategoria.setString(3, categoria.getImagen());
            consultaCategoria.executeUpdate();
            ResultSet rsCategoria = consultaCategoria.getGeneratedKeys();
            while (rsCategoria.next()) {
                categoria.setId(rsCategoria.getInt(1));
            }
            if (categoria.getProductos() != null) {
                Iterator<Producto> iteradorProcuctos = categoria.getProductos().iterator();
                consultaCategoria = conexionCategoria.prepareStatement(INSERT_CAT_PRO);
                while (iteradorProcuctos.hasNext()) {           
                    consultaCategoria.setInt(1, iteradorProcuctos.next().getId());
                    consultaCategoria.setInt(2, categoria.getId());
                    consultaCategoria.execute();
                }      
            }
            conexionCategoria.commit();
        } catch (SQLException ex) {
            try {
                conexionCategoria.rollback();
            } catch (SQLException ex1) {
                 Logger.getLogger(ServicioCategoria.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
            }
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
    public void actualizar(Categoria categoria) {
        Connection conexionCategoria = null;
        PreparedStatement consultaCategoria = null;
        try {
            conexionCategoria = GestionSql.openConnection();
            conexionCategoria.setAutoCommit(false);
            consultaCategoria = conexionCategoria.prepareStatement(UPDATE);
            consultaCategoria.setString(1, categoria.getNombre());
            consultaCategoria.setString(2, categoria.getImagen());
            consultaCategoria.setInt(3, categoria.getId());
            consultaCategoria.executeUpdate();
            consultaCategoria = conexionCategoria.prepareStatement(SELECT_ALL_PRODUCTS_CAT_PRO);
            consultaCategoria.setInt(1, categoria.getId());
            ResultSet rsCategoria = consultaCategoria.executeQuery(); 
            boolean productosDbVacio = rsCategoria.getRow() == 0;
            boolean prodcutosBeanVacio = categoria.getProductos() == null;
            if (!productosDbVacio ||  !prodcutosBeanVacio) {
                consultaCategoria = conexionCategoria.prepareStatement(DELETE_CAT_PRO_BY_CATEGORIA);
                consultaCategoria.setInt(1, categoria.getId());
                consultaCategoria.executeUpdate();
                if (!prodcutosBeanVacio) {
                    Iterator<Producto> iteradorCatProcuctos = categoria.getProductos().iterator();
                    while (iteradorCatProcuctos.hasNext()) {
                        int idProducto = iteradorCatProcuctos.next().getId();
                        consultaCategoria = conexionCategoria.prepareStatement(INSERT_CAT_PRO);
                        consultaCategoria.setInt(1, idProducto);
                        consultaCategoria.setInt(2, categoria.getId());
                        consultaCategoria.executeUpdate();            
                    }
                }
            }
            conexionCategoria.commit();
        } catch (SQLException ex) {
            Logger.getLogger(ServicioCategoria.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
            try {
                conexionCategoria.rollback();
            } catch (SQLException ex1) {
                Logger.getLogger(ServicioCategoria.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
            }
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
    public void eliminar(String nombre) {
        Categoria categoria = this.obtener(nombre);
        Connection conexionCategoria = null;
        PreparedStatement consultaCategoria = null;
        try {
            conexionCategoria = GestionSql.openConnection();
            conexionCategoria.setAutoCommit(false);
            consultaCategoria = conexionCategoria.prepareStatement(DELETE_CAT_PRO_BY_CATEGORIA);
            consultaCategoria.setInt(1, categoria.getId());
            consultaCategoria.executeUpdate();
            consultaCategoria = conexionCategoria.prepareStatement(DELETE);
            consultaCategoria.setString(1, nombre);
            consultaCategoria.executeUpdate();
            conexionCategoria.commit();
        }   catch (SQLException ex) {
            try {
                conexionCategoria.rollback();
            } catch (SQLException ex1) {
                Logger.getLogger(ServicioCategoria.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
            }
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
    public List<Categoria> listarTodos() {
        List<Categoria> categoria = new ArrayList<>();
        Connection conexionCategoria = null;
        PreparedStatement consultaCategoria = null;
        try {
            conexionCategoria = GestionSql.openConnection();
            consultaCategoria = conexionCategoria.prepareStatement(SELECT_ALL);
            ResultSet rsCategoria = consultaCategoria.executeQuery();
            while(rsCategoria.next()){
                categoria.add(enlazar(rsCategoria));
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
        return categoria;
    }

    @Override
    public Categoria obtener(String nombre) {
        Categoria categoria = null;
        Connection conexionCategoria = null;
        PreparedStatement consultaCategoria = null;
        try {
            conexionCategoria = GestionSql.openConnection();
            conexionCategoria.setAutoCommit(false);
            consultaCategoria = conexionCategoria.prepareStatement(SELECT_ONE);
            consultaCategoria.setString(1, nombre);
            ResultSet rsCategoria = consultaCategoria.executeQuery();
            while(rsCategoria.next()){
                categoria = enlazar(rsCategoria);
                consultaCategoria = conexionCategoria.prepareStatement(SELECT_ALL_PRODUCTS_CAT_PRO);
                consultaCategoria.setInt(1, categoria.getId());
                ResultSet rsCategoriaProducto = consultaCategoria.executeQuery();
                while (rsCategoriaProducto.next()) {
                    consultaCategoria = conexionCategoria.prepareStatement(SELECT_PRODUCTS);
                    consultaCategoria.setInt(1, rsCategoriaProducto.getInt("producto_id_producto"));
                    ResultSet rsProductos = consultaCategoria.executeQuery();
                    while (rsProductos.next()) {
                        Producto producto = new Producto(rsProductos.getInt("id_producto"),rsProductos.getString("nombre"),
                                                         rsProductos.getFloat("precio"),rsProductos.getString("imagen"));
                        categoria.incluirProducto(producto);
                    }
                }
            }
            conexionCategoria.commit();
        } catch (SQLException ex) {
            try {
                conexionCategoria.rollback();
            } catch (SQLException ex1) {
                Logger.getLogger(ServicioCategoria.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
            }
        } finally {
            try {
                consultaCategoria.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioCategoria.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return categoria;
    }

    @Override
    public Categoria enlazar(ResultSet resultSet) {
        try {
            Categoria categoria = new Categoria(resultSet.getInt("id_categoria"),resultSet.getString("nombre"),
                                             resultSet.getString("imagen"));
            return categoria;
        } catch (SQLException ex) {
            Logger.getLogger(ServicioCategoria.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_ENLACE, ex);
        }
        return null;
    }
    
}
