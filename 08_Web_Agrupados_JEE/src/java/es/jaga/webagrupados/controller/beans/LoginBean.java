package es.jaga.webagrupados.controller.beans;

import es.jaga.webagrupados.controller.util.JsfUtil;
import es.jaga.webagrupados.model.entities.Users;
import es.jaga.webagrupados.model.facades.UserDetailsFacade;
import es.jaga.webagrupados.model.facades.UsersFacade;
import javax.ejb.EJB;
import javax.enterprise.context.RequestScoped;
import javax.faces.context.FacesContext;
import javax.inject.Inject;
import javax.inject.Named;
/**
 * Clase que controla las peticiones de login.
 * @author Jose Antonio González Alcántara
 */
@Named("loginBean")
@RequestScoped
public class LoginBean {

    @Inject
    private UserBean userBean;
    private String username;
    private String password;
    @EJB private UsersFacade userFacade;
    @EJB private UserDetailsFacade userDetailsFacade;

    /**
     * Creates a new instance of LoginBean.
     */
    public LoginBean() {
    }

    /**
     * Setter del password asociado al formulario.
     *
     * @param password String password.
     */
    public void setPassword(String password) {
        this.password = password;
    }

    /**
     * Getter del password.
     *
     * @return String password.
     */
    public String getPassword() {
        if (password == null) {
            password = "";
        }
        return password;
    }

    /**
     * Setter del usuario asociado al formulario.
     *
     * @param username String usuario.
     */
    public void setUsername(String username) {
        this.username = username;
    }

    /**
     * Getter del nombre de usuario.
     *
     * @return String username.
     */
    public String getUsername() {
        if (username == null) {
            username = "";
        }
        return username;
    }

    /**
     * Método que comprueba que los valores del formulario son correctos y, en
     * caso de que el usuario sea admin, añade los permisos correspondientes.
     *
     * @return String con la cadena asociada al resultado de la operación que se
     * utiliza en los casos de navegación.
     */
    public String login() {
        if (!getUsername().isEmpty() && !getPassword().isEmpty()) {
            Users user = userFacade.login(getUsername(), getPassword());
            if (user != null) {
                userBean.setUser(user);
                JsfUtil.addSuccessMessage("Logeado correctamente");
                return "success";
            }
        }
        JsfUtil.addErrorMessage("La combinación usuario y contraseña no existen en nuestra base de datos");
        return "failure";
    }
    
 

    /**
     * Método que elimina el usuario y la sesión reiniciando los valores.
     *
     * @return String resultado de la operación.
     */
    public String logout() {
        userBean.setUser(null);
        FacesContext.getCurrentInstance().getExternalContext().invalidateSession();
        return "success";
    }

    /**
     * Método que comprueba que el usuario en la sesión existe y tiene usuario.
     *
     * @return boolean true si hay usuario y tiene nombre de usuario distinto de
     * cadena vacía, false si no.
     */
    public boolean isLoggedIn() {
        return userBean.getUser() != null;
    }
    
    /**
     * Método para dar de bja a un usuario y desloguearlo;
     * @return
     */
    public String unSuscribe(){
        userDetailsFacade.remove(userBean.getDetails());
        userFacade.remove(userBean.getUser());
        return logout();
    }
   
    public String cancel(){
        return "failure";
    }
}
