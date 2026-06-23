package es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services;

import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core.GestionSql;
import es.jaga.fastfoodcompany.modelo.entidades.Cliente;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core.IObjetoAccesoDatos;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core.SQLErrores;
import java.sql.PreparedStatement;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Clase que interacciona con la base de datos del objeto Cliente.
 * 
 * @author Jose Antonio González Alcántara
 */
public class ServicioCliente implements IObjetoAccesoDatos<Cliente>{
    //Sentencia CRUD SQL
    //Selecciona todos los clientes de la tabla clientes.
    private final String SELECT_ALL = "SELECT * FROM cliente";
    //Selecciona un cliente de la tabla clientes con un determinado DNI.
    private final String SELECT_ONE = "SELECT * FROM cliente WHERE dni = ?";
    private final String SELECT_ONE_BY_ID = "SELECT * FROM cliente WHERE id_cliente = ?";
    //Actualiza un cliente de la tabla clientes con determinados parametros.
    private final String UPDATE = "UPDATE cliente SET nombre = ?, " +
            "primer_apellido = ?, segundo_apellido = ?, direccion = ?, habitual = ? WHERE dni = ?";
    //Inserta un cliente de la tabla clientes con determinados parametros.
    private final String INSERT = "INSERT INTO cliente (id_cliente, dni, nombre, primer_apellido, segundo_apellido," + 
            " direccion, habitual) VALUES (? ,?, ?, ?, ?, ?, ?)";
    //Elimina un cliente de la tabla clientes con un determinado DNI.
    private final String DELETE = "DELETE FROM cliente WHERE dni = ?";
    
    /**
     * Constructor base.
     */
    public ServicioCliente() {
        super();
    }
    /**
     * Método para listar Clientes.
     * 
     * @return Lista de Clientes
     */
    @Override
    public List<Cliente> listarTodos(){
         List<Cliente> clientes = new ArrayList<>();
         Connection conexionClientes = null;
         PreparedStatement consultaClientes = null;
        try {
            conexionClientes = GestionSql.openConnection();
            consultaClientes = conexionClientes.prepareStatement(SELECT_ALL);
            ResultSet rsClientes = consultaClientes.executeQuery();
            while(rsClientes.next()){
                clientes.add(enlazar(rsClientes));
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaClientes.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return clientes;
    }
    
   /**
     * Método de búsqueda.
     *
     * @param dni String valor de búsqueda.
     * @return Cliente cliente encontrado con los datos.
     */
    @Override
    public Cliente obtener(String dni){
        Cliente cliente = null;
        Connection conexionClientes = null;
        PreparedStatement consultaClientes = null;
        try {
            conexionClientes = GestionSql.openConnection();
            consultaClientes = conexionClientes.prepareStatement(SELECT_ONE);
            consultaClientes.setString(1, dni);
            ResultSet rsCliente = consultaClientes.executeQuery();
            while(rsCliente.next()){
                cliente = enlazar(rsCliente);
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaClientes.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return cliente;
    }
    
    /**
     * Método para obtener un cliente según id.
     * @param id
     * @return cliente
     */
    public Cliente obtenerID(int id){
        Cliente cliente = null;
        Connection conexionClientes = null;
        PreparedStatement consultaClientes = null;
        try {
            conexionClientes = GestionSql.openConnection();
            consultaClientes = conexionClientes.prepareStatement(SELECT_ONE_BY_ID);
            consultaClientes.setInt(1, id);
            ResultSet rsCliente = consultaClientes.executeQuery();
            while(rsCliente.next()){
                cliente = enlazar(rsCliente);
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaClientes.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
        return cliente;
    }
   
    /**
     * Función para insertar un cliente.
     * 
     * @param cliente con los datos a insertar.
     */
    @Override
    public void insertar(Cliente cliente){
        Connection conexionClientes = null;
        PreparedStatement consultaClientes = null;
        try {
            conexionClientes = GestionSql.openConnection();
            consultaClientes = conexionClientes.prepareStatement(INSERT,PreparedStatement.RETURN_GENERATED_KEYS);
            consultaClientes.setInt(1, cliente.getId());
            consultaClientes.setString(2, cliente.getDni().getDNI());
            consultaClientes.setString(3, cliente.getNombre());
            consultaClientes.setString(4, cliente.getPrimerApellido());
            consultaClientes.setString(5, cliente.getSegundoApellido());
            consultaClientes.setString(6, cliente.getDireccion().toString());
            consultaClientes.setBoolean(7, cliente.isHabitual());
            consultaClientes.executeUpdate();
            ResultSet rsCliente = consultaClientes.getGeneratedKeys();
            while (rsCliente.next()) {
                cliente.setId(rsCliente.getInt("id_cliente"));
            }
        } catch (SQLException ex) {
            Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaClientes.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }
    
    /**
     * Función para eliminar un cliente.
     *
     * @param dni String valor de búsqueda.
     */
    @Override
    public void eliminar(String dni){
        Connection conexionClientes = null;
        PreparedStatement consultaClientes = null;
        try {
            conexionClientes = GestionSql.openConnection();
            consultaClientes = conexionClientes.prepareStatement(DELETE);
            consultaClientes.setString(1, dni);
            consultaClientes.executeUpdate();
        }   catch (SQLException ex) {
            Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaClientes.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }
    
    /**
     * Función para actualizar un cliente.
     *
     * @param cliente con los datos a actualizar.
     */
    @Override
    public void actualizar(Cliente cliente){
        Connection conexionClientes = null;
        PreparedStatement consultaClientes = null;
        try {
            conexionClientes = GestionSql.openConnection();
            consultaClientes = conexionClientes.prepareStatement(UPDATE);
            consultaClientes.setString(1, cliente.getNombre());
            consultaClientes.setString(2, cliente.getPrimerApellido());
            consultaClientes.setString(3, cliente.getSegundoApellido());
            consultaClientes.setString(4, cliente.getDireccion().toString());
            consultaClientes.setBoolean(5, cliente.isHabitual());
            consultaClientes.setString(6, cliente.getDni().getDNI());
            consultaClientes.executeUpdate();
        } catch (SQLException ex) {
            Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_SENTENCIA, ex);
        } finally {
            try {
                consultaClientes.close();
                GestionSql.closeConnection();
            } catch (SQLException e) {
                Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
            }
        }
    }

     /**
     * Método para enlazar un ResultSet con un objeto cliente.
     *
     * @param resultSet ResultSet con la consulta.
     * @return Cliente cliente con los datos enlazados.
     */
    @Override
    public Cliente enlazar(ResultSet resultSet) {
        try {
            Cliente cliente = new Cliente(resultSet.getInt("id_Cliente"), resultSet.getString("dni"), resultSet.getString("nombre"),
                    resultSet.getString("primer_apellido"), resultSet.getString("segundo_apellido"),
                    resultSet.getString("direccion"), resultSet.getBoolean("habitual"));
            return cliente;
        } catch (SQLException ex) {
            Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_ENLACE, ex);
        }
        return null;
    }
  
}
