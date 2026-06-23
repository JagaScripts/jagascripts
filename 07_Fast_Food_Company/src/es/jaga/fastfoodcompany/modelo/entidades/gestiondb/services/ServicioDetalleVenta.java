package es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services;

import es.jaga.fastfoodcompany.modelo.entidades.DetalleVenta;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core.GestionSql;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core.IObjetoAccesoDatos;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core.SQLErrores;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.ArrayList;

/**
 *
 * @author Jose Antonio González Alcántara
 */
public class ServicioDetalleVenta implements IObjetoAccesoDatos<DetalleVenta>{
    //Sentencia CRUD SQL
    //Selecciona todos los detalleVentas de la tabla detalleVentas.
    private final String SELECT_ALL = "SELECT * FROM detalle_venta_producto";
    //Selecciona un detalleVenta de la tabla detalleVentas con un determinado DNI.
    private final String SELECT_BY_NUMERO_DE_VENTA = "SELECT * FROM detalle_venta_producto WHERE venta_numero_venta = ?";
    private final String SELECT_BY_NUMERO_DE_VENTA_AND_IDPRODUCT = "SELECT * FROM detalle_venta_producto WHERE venta_numero_venta = ? AND "
            + "producto_id_producto = ?";
    //Actualiza un detalleVenta de la tabla detalleVentas con determinados parametros.
    private final String UPDATE = "UPDATE detalle_venta_producto SET cantidad = ?,"
            + " precio_venta = ? WHERE venta_numero_venta = ? AND producto_id_producto = ?";
    //Inserta un detalleVenta de la tabla detalleVentas con determinados parametros.
    private final String INSERT = "INSERT INTO detalle_venta_producto (cantidad, producto_id_producto,"
            + " precio_venta, venta_numero_venta)" + 
            "VALUES (?, ?, ?, ?)";
    //Elimina un detalleVenta de la tabla detalleVentas con un determinado DNI.
    private final String DELETE = "DELETE FROM detalle_venta_producto WHERE venta_numero_venta = ?";
    
    /**
     * Constructor base.
     */
    public ServicioDetalleVenta() {
        super();
    }

    /**
     * Función para insertar un detalleVenta.
     * 
     * @param detalleVenta con los datos a insertar.  
     */
    @Override
    public void insertar(DetalleVenta detalleVenta) {
        Connection conexionDetalleVenta = null;
        PreparedStatement consultaDetalleVenta = null;
        try {
            conexionDetalleVenta = GestionSql.openConnection();
            consultaDetalleVenta = conexionDetalleVenta.prepareStatement(SELECT_BY_NUMERO_DE_VENTA_AND_IDPRODUCT);
            consultaDetalleVenta.setInt(1, detalleVenta.getNumeroDeVenta());
            consultaDetalleVenta.setInt(2, detalleVenta.getIdProducto());
            ResultSet rsDetalleVenta = consultaDetalleVenta.executeQuery();
            if(rsDetalleVenta.next()){
                DetalleVenta dbDetalleVenta = enlazar(rsDetalleVenta);
                detalleVenta.setCantidad(dbDetalleVenta.getCantidad() + detalleVenta.getCantidad());
                detalleVenta.setPrecioVenta(dbDetalleVenta.getPrecioVenta() + detalleVenta.getPrecioVenta());
                this.actualizar(detalleVenta);
            } else {
                consultaDetalleVenta = conexionDetalleVenta.prepareStatement(INSERT);
                consultaDetalleVenta.setInt(1, detalleVenta.getCantidad());
                consultaDetalleVenta.setInt(2, detalleVenta.getIdProducto());
                consultaDetalleVenta.setFloat(3, detalleVenta.getPrecioVenta());
                consultaDetalleVenta.setInt(4, detalleVenta.getNumeroDeVenta());
                consultaDetalleVenta.execute();
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDetalleVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }

    /**
     * Función para actualizar un detalleVenta.
     *
     * @param detalleVenta con los datos a actualizar.  
     */
    @Override
    public void actualizar(DetalleVenta detalleVenta) {
        Connection conexionDetalleVenta = null;
        PreparedStatement consultaDetalleVenta = null;
        try {
            conexionDetalleVenta = GestionSql.openConnection();
            consultaDetalleVenta = conexionDetalleVenta.prepareStatement(UPDATE);
            consultaDetalleVenta.setInt(1, detalleVenta.getCantidad());
            consultaDetalleVenta.setFloat(2, detalleVenta.getPrecioVenta());
            consultaDetalleVenta.setInt(3, detalleVenta.getNumeroDeVenta());
            consultaDetalleVenta.setInt(4, detalleVenta.getIdProducto());
            consultaDetalleVenta.executeUpdate();
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDetalleVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }

    /**
     * Función para eliminar un DetalleVenta.
     *
     * @param numeroVenta String valor de búsqueda.  
     */
    @Override
    public void eliminar(String numeroVenta) {
        Connection conexionDetalleVenta = null;
        PreparedStatement consultaDetalleVenta = null;
        try {
            conexionDetalleVenta = GestionSql.openConnection();
            consultaDetalleVenta = conexionDetalleVenta.prepareStatement(DELETE);
            consultaDetalleVenta.setString(1, numeroVenta);
            consultaDetalleVenta.executeUpdate();
        }   catch (SQLException ex) {
            Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDetalleVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }

    /**
     * Método para listar DetalleVenta.
     * 
     * @return Lista de DetalleVenta
     */
    @Override
    public List<DetalleVenta> listarTodos() {
        List<DetalleVenta> detalleVenta = new ArrayList<>();
        Connection conexionDetalleVenta = null;
        PreparedStatement consultaDetalleVenta = null;
        try {
            conexionDetalleVenta = GestionSql.openConnection();
            consultaDetalleVenta = conexionDetalleVenta.prepareStatement(SELECT_ALL);
            ResultSet rsDetalleVenta = consultaDetalleVenta.executeQuery();
            while(rsDetalleVenta.next()){
                detalleVenta.add(enlazar(rsDetalleVenta));
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDetalleVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return detalleVenta;
    }

    /**
     * Método de búsqueda.
     *
     * @param numeroVenta encontrado con los datos.
     * @return DetalleVenta encontrado con los datos.
     */
    @Override
    public DetalleVenta obtener(String numeroVenta) {
        DetalleVenta detalleVenta = null;
        Connection conexionDetalleVenta = null;
        PreparedStatement consultaDetalleVenta = null;
        try {
            conexionDetalleVenta = GestionSql.openConnection();
            consultaDetalleVenta = conexionDetalleVenta.prepareStatement(SELECT_BY_NUMERO_DE_VENTA);
            consultaDetalleVenta.setString(1, numeroVenta);
            ResultSet rsDetalleVenta = consultaDetalleVenta.executeQuery();
            while(rsDetalleVenta.next()){
                detalleVenta = enlazar(rsDetalleVenta);
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDetalleVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return detalleVenta;
    }
    
    /**
     * Obtine lista de detalles de venta
     * @param numeroVenta
     * @return lista de detalles de venta.
     */
    public List<DetalleVenta> obtenerDetallesVenta(int numeroVenta) {
        List<DetalleVenta> listaDetalleVenta = null;
        DetalleVenta detalleVenta = null;
        Connection conexionDetalleVenta = null;
        PreparedStatement consultaDetalleVenta = null;
        try {
            conexionDetalleVenta = GestionSql.openConnection();
            consultaDetalleVenta = conexionDetalleVenta.prepareStatement(SELECT_BY_NUMERO_DE_VENTA);
            consultaDetalleVenta.setInt(1, numeroVenta);
            ResultSet rsDetalleVenta = consultaDetalleVenta.executeQuery();
            while(rsDetalleVenta.next()){
                detalleVenta = enlazar(rsDetalleVenta);
                if (listaDetalleVenta == null) {
                    listaDetalleVenta = new ArrayList<>();
                }
                listaDetalleVenta.add(detalleVenta);
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDetalleVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return listaDetalleVenta;
    }

    /**
     * Método para enlazar un ResultSet con un objeto DetalleVenta.
     *
     * @param resultSet ResultSet con la consulta.
     * @return DetalleVenta detalleVenta con los datos enlazados.
     */
    @Override
    public DetalleVenta enlazar(ResultSet resultSet) {
        try {
            DetalleVenta detalleVenta = new DetalleVenta(resultSet.getInt("venta_numero_venta"), resultSet.getInt("producto_id_producto"),
                                             resultSet.getInt("cantidad"),resultSet.getFloat("precio_venta"));
            return detalleVenta;
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDetalleVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_ENLACE, ex);
        }
        return null;
    }
    
}
