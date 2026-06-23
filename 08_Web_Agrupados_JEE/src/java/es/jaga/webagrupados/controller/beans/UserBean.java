package es.jaga.webagrupados.controller.beans;

import es.jaga.webagrupados.controller.util.JsfUtil;
import es.jaga.webagrupados.model.entities.UserDetails;
import es.jaga.webagrupados.model.entities.Users;
import es.jaga.webagrupados.model.facades.UserDetailsFacade;
import java.io.Serializable;
import java.util.Collection;
import java.util.Iterator;
import javax.ejb.EJB;
import javax.enterprise.context.SessionScoped;
import javax.inject.Named;

/**
 * Clase con el bean de sesión que almacena los datos de usuario.
 * @author Jose Antonio González Alcántara
 */
@Named(value = "userBean")
@SessionScoped
public class UserBean implements Serializable {
    
    private Users user;
    @EJB
    private UserDetailsFacade detailsFacad;

    /**
     * Método que comprueba si el usuario tiene permiso de administrador.
     *
     * @return boolean true si contiene ese rol, false si no.
     */
    public boolean isAdmin() {
        return (getUser() != null) ? getUser().getRole().getRolename().equals("Administrator") : false;
    }
    
    /**
     * Método que comprueba si el usuario tiene permiso de negocio.
     *
     * @return boolean true si contiene ese rol, false si no.
     */
    public boolean isBusiness() {
        return (getUser() != null) ? getUser().getRole().getRolename().equals("Business") : false;
    }
    
    /**
     * Método que comprueba si el usuario tiene permiso de usuario registrado.
     *
     * @return boolean true si contiene ese rol, false si no.
     */
    public boolean isRegisteredUser() {
        return  (getUser() != null) ? getUser().getRole().getRolename().equals("Client") : false;
    }
    
    /**
     * Método que comprueba si el usuario tiene permiso de usuario registrado.
     *
     * @return boolean true si contiene ese rol, false si no.
     */
    public boolean isNotRegistered() {
        return  (getUser() == null) ? true : false;
    }
        
    /**
     * Getter del usuario.
     *
     * @return User usuario.
     */
    public Users getUser() {
        return user;
    }

    /**
     * Setter del usuario
     * @param user
     */
    public void setUser(Users user) {
        this.user = user;
    }
    
    /**
     * Getter de los detalles
     * @return detalles de ussuario
     */
    public UserDetails getDetails(){
        Collection<UserDetails> colDetails = getUser().getUserDetailsCollection();
        Iterator<UserDetails> iterDetails = colDetails.iterator();
        UserDetails details = iterDetails.next();
        return details;
    }
    
    /** 
     * Getter del rol
     * @return cadena del rol
     */
    public String getRol(){
        return  (getUser() != null) ? "/" + getUser().getRole().getRolename().toLowerCase() : "";
    }
    
    /**
     * Metódo para editar un usuario
     * @return cadena
     */
    public String edit(){
        detailsFacad.edit(getDetails());
        JsfUtil.addSuccessMessage("Datos actualizados correctamente");
        return "success";
    }
    
    /**
     * Metódo de cancelacion.
     * @return cadena
     */
    public String cancel(){
        JsfUtil.addErrorMessage("Se ha cancelado la edición");
        return "failure";
    }

    
}
