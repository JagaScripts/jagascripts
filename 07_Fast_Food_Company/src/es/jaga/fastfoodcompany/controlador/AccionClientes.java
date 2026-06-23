package es.jaga.fastfoodcompany.controlador;

import es.jaga.fastfoodcompany.modelo.entidades.Cliente;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services.ServicioCliente;
import javax.swing.JOptionPane;

/**
 *
 * @author Jose Antonio González Alcántara
 */
public class AccionClientes implements IObjetoAcciones<Cliente>{
    
    private final ServicioCliente servicioDB;
    private Cliente cliente;
        
    /**
     * Constructor que instacia el servicio a la base de datos.
     */
    public AccionClientes(){
        this.servicioDB = new ServicioCliente();
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * inserta los datos del cliente en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean insertar(){
        if (this.servicioDB.obtener(this.cliente.getDni().getDNI()) == null && existeDNIValido()){
            this.servicioDB.insertar(this.cliente);
            JOptionPane.showMessageDialog(null, "Cliente Insertado correctamente" + " su id es:" + cliente.getId());
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "Ya existe en la base de datos un cliente con "
                    + "el mismo DNI, presione actualizar lo desea", "Atención",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * borra los datos del cliente en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean borrar(){
        if (this.servicioDB.obtener(this.cliente.getDni().getDNI()) != null && existeDNIValido()){
            this.servicioDB.eliminar(this.cliente.getDni().getDNI());
            JOptionPane.showMessageDialog(null, "Cliente borrado correctamente");
            return true;
         } else {
            JOptionPane.showMessageDialog(null, "El cliente con el DNI no existe "
                    + "en la base de datos", "Alerta",JOptionPane.WARNING_MESSAGE);
            return false;
         }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * actualiza los datos del cliente en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean actualizar(){
        if (existeDNIValido()){
            this.servicioDB.actualizar(this.cliente);
            JOptionPane.showMessageDialog(null, "Cliente Actualizado correctamente");
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "Ya existe en la base de datos "
                    + "un cliente con el mismo DNI", "Alerta",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * busca los datos del cliente en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @param dni del cliente
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean buscar(String dni){
        this.cliente = this.servicioDB.obtener(dni);
        if (this.cliente != null) {
            JOptionPane.showMessageDialog(null, "El nombre cliente con el DNI: "
                    + "" + this.obtener().getDni() + " es " + this.obtener().toString());
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "El cliente no existe en la base de datos", ""
                    + "Atención",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Metodo que devuelve true si el cliente exite.
     * @param id
     * @return boolean
     */
    public Boolean buscarID(int id){
        this.cliente = this.servicioDB.obtenerID(id);
        return this.cliente != null;
    }
    
    /**
     * Método getter que devuelve un cliente.
     * 
     * @return cliente
     */
    @Override
    public Cliente obtener(){
        return this.cliente;
    }  

    /**
     * Método setter que establece un cliente.
     * 
     * @param cliente
     */
    @Override
    public void establecer(Cliente cliente) {
        this.cliente = cliente;
    }
    
    
    
    /**
     * Método que comprueba la adecuación de los datos introducidos
     * en los campos del DNI, su validez e informa
     * al usuario de las incidencias.
     * @return valor booleano.
     */
    public boolean existeDNIValido(){  
        if (this.cliente.getDni().esValido(this.cliente.getDni().getDNI())) {
            return true;
        }
        JOptionPane.showMessageDialog(null, "El campo DNI es obligatorio"
                    + " y debe ser válido", "Atención",JOptionPane.WARNING_MESSAGE);
        return false;
    }

}
