package es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services;

import es.jaga.fastfoodcompany.modelo.entidades.Venta;
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
public class ServicioVenta implements IObjetoAccesoDatos<Venta>{
    //Sentencia CRUD SQL
    //Selecciona todos los ventaVentas de la tabla Ventas.
    private final String SELECT_ALL = "SELECT * FROM venta";
    //Selecciona un Venta de la tabla Ventas con un determinado DNI.
    private final String SELECT_ONE = "SELECT * FROM venta WHERE numero_venta = ?";
    private final String SELECT_BY_FECHA = "SELECT * FROM venta WHERE fecha = ?";
    private final String SELECT_BY_ID = "SELECT * FROM venta WHERE cliente_id_cliente = ?";
    private final String SELECT_BY_ID_NULL = "SELECT * FROM venta WHERE cliente_id_cliente IS NULL";
    private final String SELECT_LAST_ID = "SELECT max(numero_venta) FROM venta";
    //Actualiza un Venta de la tabla Ventas con determinados parametros.
    private final String UPDATE = "UPDATE venta SET total = ?, fecha = ?,"
            + " cliente_id_cliente = ? WHERE numero_venta = ?";
    //Inserta un Venta de la tabla Ventas con determinados parametros.
    private final String INSERT = "INSERT INTO venta (total, fecha,"
            + " cliente_id_cliente) VALUES (?, ?, ?)";
    //Elimina un Venta de la tabla Ventas con un determinado DNI.
    private final String DELETE = "DELETE FROM venta WHERE numero_venta = ?";
    
    /**
     * Constructor base.
     */
    public ServicioVenta() {
        super();
    }

    /**
     * Función para insertar un Venta.
     * 
     * @param venta con los datos a insertar.  
     */
    @Override
    public void insertar(Venta venta) {
        Connection conexionVenta = null;
        PreparedStatement consultaVenta = null;
        try {
            conexionVenta = GestionSql.openConnection();
            consultaVenta = conexionVenta.prepareStatement(INSERT);
            consultaVenta.setFloat(1, venta.getTotal());
            consultaVenta.setString(2, venta.getFecha());
            int cliente = venta.getCliente();
            if (cliente == 0) {
                consultaVenta.setString(3,null);
            } else {
                consultaVenta.setInt(3, venta.getCliente());
            }
            consultaVenta.execute();
        } catch (SQLException ex) {
            Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }

    /**
     * Función para actualizar un Venta.
     *
     * @param venta con los datos a actualizar.   
     */
    @Override
    public void actualizar(Venta venta) {
        Connection conexionVenta = null;
        PreparedStatement consultaVenta = null;
        try {
            conexionVenta = GestionSql.openConnection();
            consultaVenta = conexionVenta.prepareStatement(UPDATE);
            consultaVenta.setFloat(1, venta.getTotal());
            consultaVenta.setString(2, venta.getFecha());
            consultaVenta.setInt(3, venta.getCliente());
            consultaVenta.setInt(4, venta.getNumeroDeVenta());
            consultaVenta.executeUpdate();
        } catch (SQLException ex) {
            Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }

    /**
     * Función para eliminar un Venta.
     *
     * @param numeroDeVenta String valor de búsqueda.  
     */
    @Override
    public void eliminar(String numeroDeVenta) {
        Connection conexionVenta = null;
        PreparedStatement consultaVenta = null;
        try {
            conexionVenta = GestionSql.openConnection();
            consultaVenta = conexionVenta.prepareStatement(DELETE);
            consultaVenta.setInt(1, Integer.parseInt(numeroDeVenta));
            consultaVenta.executeUpdate();
        }   catch (SQLException ex) {
            Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }

    /**
     * Método para listar Venta.
     * 
     * @return Lista de Venta
     */
    @Override
    public List<Venta> listarTodos() {
        List<Venta> venta = new ArrayList<>();
        Connection conexionVenta = null;
        PreparedStatement consultaVenta = null;
        try {
            conexionVenta = GestionSql.openConnection();
            consultaVenta = conexionVenta.prepareStatement(SELECT_ALL);
            ResultSet rsVenta = consultaVenta.executeQuery();
            while(rsVenta.next()){
                venta.add(enlazar(rsVenta));
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return venta;
    }

    /**
     * Método de búsqueda.
     *
     * @param numeroDeVenta encontrado con los datos. 
     * @return Venta encontrado con los datos.
     */
    @Override
    public Venta obtener(String numeroDeVenta) {
        Venta venta = null;
        Connection conexionVenta = null;
        PreparedStatement consultaVenta = null;
        try {
            conexionVenta = GestionSql.openConnection();
            consultaVenta = conexionVenta.prepareStatement(SELECT_ONE);
            consultaVenta.setInt(1, Integer.parseInt(numeroDeVenta));
            ResultSet rsVenta = consultaVenta.executeQuery();
            while(rsVenta.next()){
                venta = enlazar(rsVenta);
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return venta;
    }
    
    /**
     * Obtiene el ultmo numero de venta
     * @return int con el numero de venta
     */
    public int obtenerUltimoNumeroDeVenta(){
        int numeroDeVenta = 0;
        Connection conexionVenta = null;
        PreparedStatement consultaVenta = null;
        try {
            conexionVenta = GestionSql.openConnection();
            consultaVenta = conexionVenta.prepareStatement(SELECT_LAST_ID);
            ResultSet rsVenta = consultaVenta.executeQuery();
            while (rsVenta.next()) {
                numeroDeVenta = rsVenta.getInt("max(numero_venta)");
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return numeroDeVenta;
    }
    
    /**
     * Obtiene una lista de ventas por fecha.
     * @param fecha
     * @return lista de ventas
     */
    public List<Venta> obtenerPorFecha(String fecha) {
        Venta venta = null;
        List<Venta> listaVenta = null;
        Connection conexionVenta = null;
        PreparedStatement consultaVenta = null;
        try {
            conexionVenta = GestionSql.openConnection();
            consultaVenta = conexionVenta.prepareStatement(SELECT_BY_FECHA);
            consultaVenta.setString(1, fecha);
            ResultSet rsVenta = consultaVenta.executeQuery();
            while(rsVenta.next()){
                venta = enlazar(rsVenta);
                if (listaVenta == null) {
                    listaVenta = new ArrayList<>();
                }
                listaVenta.add(venta);
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return listaVenta;
    }
    
    /**
     * Obtiene una lista de ventas por idCliente.
     * @param idCliente
     * @return lista de ventas
     */
    public List<Venta> obtenerPorIdCliente(int idCliente) {
        Venta venta = null;
        List<Venta> listaVenta = null;
        Connection conexionVenta = null;
        PreparedStatement consultaVenta = null;
        try {
            conexionVenta = GestionSql.openConnection();
            consultaVenta = conexionVenta.prepareStatement(SELECT_BY_ID);
            if (idCliente == 0) {
                consultaVenta = conexionVenta.prepareStatement(SELECT_BY_ID_NULL);
            } else {
                consultaVenta.setInt(1, idCliente);
            }
            ResultSet rsVenta = consultaVenta.executeQuery();
            while(rsVenta.next()){
                venta = enlazar(rsVenta);
                if (listaVenta == null) {
                    listaVenta = new ArrayList<>();
                }
                listaVenta.add(venta);
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaVenta.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return listaVenta;
    }

    /**
     * Método para enlazar un ResultSet con un objeto Venta.
     *
     * @param resultSet ResultSet con la consulta.
     * @return Venta detalleVenta con los datos enlazados.
     */
    @Override
    public Venta enlazar(ResultSet resultSet) {
        try {
            Venta venta = new Venta(resultSet.getInt("numero_venta"), resultSet.getFloat("total"),
                                    resultSet.getInt("cliente_id_cliente"), resultSet.getString("fecha"));
            return venta;
        } catch (SQLException ex) {
            Logger.getLogger(ServicioVenta.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_ENLACE, ex);
        }
        return null;
    }
    
}
