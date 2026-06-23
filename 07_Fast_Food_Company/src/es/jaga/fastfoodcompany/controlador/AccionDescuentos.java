package es.jaga.fastfoodcompany.controlador;

import es.jaga.fastfoodcompany.modelo.entidades.Descuento;
import es.jaga.fastfoodcompany.modelo.entidades.gestiondb.services.ServicioDescuento;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JOptionPane;

/**
 *
 * @author Jose Antonio González Alcántara
 */
public class AccionDescuentos implements IObjetoAcciones<Descuento>{
    
    private final ServicioDescuento servicioDB;
    private Descuento descuento;
    
    /**
     * Constructor que instacia el servicio a la base de datos.
     */
    public AccionDescuentos(){
        this.servicioDB = new ServicioDescuento();
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * inserta los datos del descuento en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean insertar(){
        if (this.servicioDB.obtener(String.valueOf(this.descuento.getCliente())) == null){
            this.servicioDB.insertar(this.descuento);
            JOptionPane.showMessageDialog(null, "Descuento Insertado correctamente");
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "Ya existe en la base de datos un descuento con "
                    + "el mismo clave, presione actualizar lo desea", "Atención",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * borra los datos del descuento en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean borrar(){
        this.descuento = this.servicioDB.obtener(String.valueOf(this.descuento.getCliente()));
        if (this.descuento != null){
            this.servicioDB.eliminar(this.descuento.getClave());
            JOptionPane.showMessageDialog(null, "Descuento borrado correctamente");
            return true;
         } else {
            JOptionPane.showMessageDialog(null, "El descuento con el clave no existe "
                    + "en la base de datos", "Alerta",JOptionPane.WARNING_MESSAGE);
            return false;
         }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * actualiza los datos del descuento en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean actualizar(){
        if (!this.servicioDB.existeClave(this.descuento.getClave()) && fechaCorrecta(this.descuento.getCaducidad())){
            this.servicioDB.actualizar(this.descuento);
            JOptionPane.showMessageDialog(null, "Descuento Actualizado correctamente");
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "Ya existe en la base de datos "
                    + "un descuento con la misma clave", "Alerta",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método que comprueba la adecuación de los datos introducidos,
     * busca los datos del descuento en la base de datos e informa
     * al usuario de las incidencias.
     * 
     * @param idCliente del descuento.
     * @return Boolean true para operacion realizada correctamente false
     * para operacion realizada incorrectamente.
     */
    @Override
    public Boolean buscar(String idCliente){
        this.descuento = this.servicioDB.obtener(idCliente);
        if (this.descuento != null) {
            JOptionPane.showMessageDialog(null, "Descuento del cliente " + descuento.getCliente() + " con la clave: "
                    + "" + this.descuento.getClave() + " es " + this.descuento.getCantidad());
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "El descuento no existe en la base de datos", ""
                    + "Atención",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
    
    /**
     * Método getter que devuelve un descuento.
     * 
     * @return descuento
     */
    @Override
    public Descuento obtener(){
        return this.descuento;
    }  

    /**
     * Método setter que establece un descuento.
     * 
     * @param descuento
     */
    @Override
    public void establecer(Descuento descuento) {
        this.descuento = descuento;
    }
    
    /**
     * Metodo que que comprueba si la fecha es correcta:
     * @param fecha
     * @return boolean
     */
    public boolean fechaCorrecta(String fecha){
        try {
            SimpleDateFormat formatoFecha =  new SimpleDateFormat("dd/MM/yyyy");
            Date hoy = new Date();
            Date caducidad = formatoFecha.parse(fecha);
            if (hoy.before(caducidad)) {
                return true;
            }
        } catch (ParseException ex) {
            Logger.getLogger(AccionDescuentos.class.getName()).log(Level.SEVERE, null, ex);
        }
        JOptionPane.showMessageDialog(null, "La fecha de caducidad no puede ser anterior al dia de hoy", ""
                    + "Atención",JOptionPane.WARNING_MESSAGE);
        return false;
    }
    
    /**
     * Método que comprueva si exite una clave.
     * @param clave
     * @return boolean
     */
    public boolean existeClave(String clave){
        return this.servicioDB.existeClave(clave);
    }
    
    /**
     * Método que devuele un decuento si existe si no no devuelve null.
     * @param clave
     * @return null o Descuento
     */
    public Descuento obtenerDescuento(String clave){
        return this.servicioDB.obtenerPorClave(clave);
    }
    
    /**
     * Método que compprueba si el descuento es del cliente.
     * @param clave
     * @param idCliente
     * @return boolean
     */
    public boolean esDescuentoCliente(String clave, int idCliente){
        if (this.existeClave(clave)) {
            Descuento descuento = this.obtenerDescuento(clave);
            if (descuento.getCliente() == idCliente) {
                return true;
            }
        }
        return false;
    }
}
