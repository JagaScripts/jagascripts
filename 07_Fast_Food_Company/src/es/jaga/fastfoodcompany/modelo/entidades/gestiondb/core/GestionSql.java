package es.jaga.fastfoodcompany.modelo.entidades.gestiondb.core;

import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services.ServicioCliente;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Clase para para la conectar con MySQL.
 * 
 * @author Jose Antonio González Alcántara
 */
public class GestionSql {
    private static final String DRIVER = "com.mysql.jdbc.Driver";
    private static final String SERVER = "jdbc:mysql://sql309.main-hosting.eu:3306/";//"jdbc:mysql://localhost:3306/";
    private static final String DATABASE = "u110269477_fastfoodcompan";
    private static final String USERNAME = "u110269477_joseagalcan";//"root";
<<<<<<< HEAD
    private static final String PASSWORD = "DB_PASSWORD_HIDDEN";
=======
    private static final String PASSWORD = "0Fastfoodcompany";
>>>>>>> 662fea9baedbad13a03f8e1cae961a8019150a86
    private static Connection connection = null;
    
    /**
     * Constructor mínimo.
     */
    public GestionSql() {
        super();
    }
    
    /**
     * Método para abrir una conexión a la base de datos.
     *
     * @return java.sql.Connection conexión o null.
     */
    public static Connection openConnection(){
        try {
            Class.forName(DRIVER);
            connection = DriverManager.getConnection(SERVER + DATABASE, USERNAME, PASSWORD);
            return connection;
        } catch (ClassNotFoundException ex) {
            Logger.getLogger(GestionSql.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_DRIVER, ex);
        } catch (SQLException ex) {
            Logger.getLogger(GestionSql.class.getName()).log(Level.SEVERE, 
                    SQLErrores.ERROR_SQL_ABRIR_CONEXION, ex);
        }
        return null;
    }
    
    /**
     * Función para cerrar una conexión a la base de datos.
     *
     */
    public static void closeConnection(){
        try {
            connection.close();
        } catch (SQLException e) {
             Logger.getLogger(ServicioCliente.class.getName()).log(Level.SEVERE,
                        SQLErrores.ERROR_SQL_CERRAR_CONEXION, e);
        }
   }
    
}
