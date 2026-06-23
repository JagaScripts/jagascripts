package es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services;

import es.jaga.fastfoodcompany.modelo.entidades.Descuento;
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
public class ServicioDescuento implements IObjetoAccesoDatos<Descuento>{
    //Sentencia CRUD SQL
    //Selecciona todos los descuentos de la tabla descuentos.
    private final String SELECT_ALL = "SELECT * FROM descuento";
    //Selecciona un descuento de la tabla descuentos con un determinado DNI.
    private final String SELECT_ONE = "SELECT * FROM descuento WHERE cliente_id_cliente = ?";
    private final String SELECT_ONE_CLAVE = "SELECT * FROM descuento WHERE clave = ?";
    //Actualiza un descuento de la tabla descuentos con determinados parametros.
    private final String UPDATE = "UPDATE descuento SET cantidad = ?, clave = ?, caducidad = ? WHERE cliente_id_cliente = ?";
    //Inserta un descuento de la tabla descuentos con determinados parametros.
    private final String INSERT = "INSERT INTO descuento (cantidad, cliente_id_cliente, caducidad, clave)" + 
            "VALUES (?, ?, ?, ?)";
    //Elimina un descuento de la tabla descuentos con un determinado DNI.
    private final String DELETE = "DELETE FROM descuento WHERE clave = ?";
    
    /**
     * Constructor base.
     */
    public ServicioDescuento() {
        super();
    }

    /**
     * Función para insertar un descuento.
     * 
     * @param descuento con los datos a insertar. 
     */
    @Override
    public void insertar(Descuento descuento) {
        Connection conexionDescuento = null;
        PreparedStatement consultaDescuento = null;
        try {
            conexionDescuento = GestionSql.openConnection();
            consultaDescuento = conexionDescuento.prepareStatement(INSERT);
            consultaDescuento.setInt(1, descuento.getCantidad());
            consultaDescuento.setInt(2, descuento.getCliente());
            consultaDescuento.setString(3, descuento.getCaducidad());
            consultaDescuento.setString(4, descuento.getClave());
            consultaDescuento.execute();
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDescuento.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }

    /**
     * Función para actualizar un descuento.
     *
     * @param descuento con los datos a actualizar. 
     */
    @Override
    public void actualizar(Descuento descuento) {
        Connection conexionDescuento = null;
        PreparedStatement consultaDescuento = null;
        try {
            conexionDescuento = GestionSql.openConnection();
            consultaDescuento = conexionDescuento.prepareStatement(UPDATE);
            consultaDescuento.setInt(1, descuento.getCantidad());
            consultaDescuento.setInt(4, descuento.getCliente());
            consultaDescuento.setString(3, descuento.getCaducidad());
            consultaDescuento.setString(2, descuento.getClave());
            consultaDescuento.executeUpdate();
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDescuento.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }

    /**
     * Función para eliminar un descuento.
     *
     * @param clave String valor de búsqueda. 
     */
    @Override
    public void eliminar(String clave) {
        Connection conexionDescuento = null;
        PreparedStatement consultaDescuento = null;
        try {
            conexionDescuento = GestionSql.openConnection();
            consultaDescuento = conexionDescuento.prepareStatement(DELETE);
            consultaDescuento.setString(1, clave);
            consultaDescuento.executeUpdate();
        }   catch (SQLException ex) {
            Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDescuento.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }

    /**
     * Método para listar Descuentos.
     * 
     * @return Lista de Descuentos
     */
    @Override
    public List<Descuento> listarTodos() {
        List<Descuento> descuento = new ArrayList<>();
         Connection conexionDescuento = null;
         PreparedStatement consultaDescuento = null;
        try {
            conexionDescuento = GestionSql.openConnection();
            consultaDescuento = conexionDescuento.prepareStatement(SELECT_ALL);
            ResultSet rsDescuento = consultaDescuento.executeQuery();
            while(rsDescuento.next()){
                descuento.add(enlazar(rsDescuento));
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDescuento.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return descuento;
    }

    /**
     * Método de búsqueda.
     *
     * @param idCliente
     * @return Descuento encontrado con los datos.
     */
    @Override
    public Descuento obtener(String idCliente) {
        Descuento descuento = null;
        Connection conexionDescuento = null;
        PreparedStatement consultaDescuento = null;
        try {
            conexionDescuento = GestionSql.openConnection();
            consultaDescuento = conexionDescuento.prepareStatement(SELECT_ONE);
            consultaDescuento.setInt(1, Integer.parseInt(idCliente));
            ResultSet rsDescuento = consultaDescuento.executeQuery();
            while(rsDescuento.next()){
                descuento = enlazar(rsDescuento);
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDescuento.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return descuento;
    }
    
    /**
     * Obtiene un descuento por clave.
     * @param clave
     * @return Descuento
     */
    public Descuento obtenerPorClave(String clave) {
        Descuento descuento = null;
        Connection conexionDescuento = null;
        PreparedStatement consultaDescuento = null;
        try {
            conexionDescuento = GestionSql.openConnection();
            consultaDescuento = conexionDescuento.prepareStatement(SELECT_ONE_CLAVE);
            consultaDescuento.setString(1, clave);
            ResultSet rsDescuento = consultaDescuento.executeQuery();
            while(rsDescuento.next()){
                descuento = enlazar(rsDescuento);
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDescuento.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return descuento;
    }
    
    /**
     * Método que comprueba la existencia de un descuento
     * @param clave
     * @return truo o false
     */
    public boolean existeClave(String clave) {
        Connection conexionDescuento = null;
        PreparedStatement consultaDescuento = null;
        try {
            conexionDescuento = GestionSql.openConnection();
            consultaDescuento = conexionDescuento.prepareStatement(SELECT_ONE_CLAVE);
            consultaDescuento.setString(1, clave);
            ResultSet rsDescuento = consultaDescuento.executeQuery();
            while(rsDescuento.next()){
                return true;
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaDescuento.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return false;
    }

    /**
     * Método para enlazar un ResultSet con un objeto Descuento.
     *
     * @param resultSet ResultSet con la consulta.
     * @return Descuento descuento con los datos enlazados.
     */
    @Override
    public Descuento enlazar(ResultSet resultSet) {
        try {
            Descuento descuento = new Descuento(resultSet.getInt("cantidad"), resultSet.getInt("cliente_id_cliente"),
                                             resultSet.getString("caducidad"),resultSet.getString("clave"));
            return descuento;
        } catch (SQLException ex) {
            Logger.getLogger(ServicioDescuento.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_ENLACE, ex);
        }
        return null;
    }
    
}
