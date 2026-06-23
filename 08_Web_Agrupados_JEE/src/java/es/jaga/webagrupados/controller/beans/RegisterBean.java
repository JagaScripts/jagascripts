package es.jaga.webagrupados.controller.beans;

import es.jaga.webagrupados.controller.util.JsfUtil;
import es.jaga.webagrupados.model.entities.Roles;
import es.jaga.webagrupados.model.entities.UserDetails;
import es.jaga.webagrupados.model.entities.Users;
import es.jaga.webagrupados.model.facades.UserDetailsFacade;
import es.jaga.webagrupados.model.facades.UsersFacade;
import java.io.Serializable;
import java.util.Date;
import java.util.List;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.ejb.EJB;
import javax.ejb.EJBException;
import javax.enterprise.context.SessionScoped;
import javax.faces.context.FacesContext;
import javax.inject.Inject;
import javax.inject.Named;
import org.hibernate.validator.constraints.Email;

/**
 *
 * @author Jose Antonio González Alcántara
 */
@Named("registerBean")
@SessionScoped
public class RegisterBean implements Serializable{
    
    @Inject
    private UserBean userBean;
    private Users user;
    private UserDetails userDetails;
    private String username;
    @Email
    private String email;
    private String password;
    private MapBean coordenates;
    @EJB UsersFacade usersFacade;
    @EJB UserDetailsFacade usersDetailsFacade;
    private boolean comprobate = false;

    /**
     * Getter del usuario
     * @return usuario
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
     * Getter de los detalles de usuario
     * @return
     */
    public UserDetails getUserDetails() {
        return userDetails;
    }

    /**
     * Setter de los detalles de ussuario
     * @param userDetails
     */
    public void setUserDetails(UserDetails userDetails) {
        this.userDetails = userDetails;
    }

    /**
     * Función que comprueba la combinacion de ususario y el email ya existe en la base de datos
     * 
     */
    public void comprobateUsernameAndEmail(){
        if (userBean.getUser() == null && !email.isEmpty() && !username.isEmpty()) {
            Users uEmail = usersFacade.isEmailExist(email);
            Users uUsername = usersFacade.isUsernameExist(username);
            if (uEmail != null) {
                JsfUtil.addErrorMessage("El email: " + email + " ya existe");
            }
            if (uUsername != null){
                JsfUtil.addErrorMessage("El nombre de usuario: " + username + " ya existe");
            }
            if (uUsername == null && uEmail == null){
                prepareCreate();
                user.setUsername(username);
                user.setEmail(email);
                coordenates = new MapBean();
                comprobate = true;
            }
        }
    }
    
    /**
     * Método que valida el registro del usuario
     * @return stado de la validación
     */
    public String registerUser(){
        String register = null;
        coordenates.retrieveCoordinates();
        userDetails.setLatitude(getCoordenates().getAddress().getLatitude());
        userDetails.setLongitude(getCoordenates().getAddress().getLongitude());
        userDetails.setAddress(coordenates.getAddress().getAddress());
        userDetails.setCity(coordenates.getAddress().getCity());
        userDetails.setProvince(coordenates.getAddress().getProvince());
        userDetails.setCountry(coordenates.getAddress().getCountry());
        userDetails.setDateOfRegistration(new Date());
        user.setActive(true);
        user.setRole(new Roles(3));
        userDetails.setApplicationUsersId(user);
        user.getUserDetailsCollection().add(userDetails);
        create();
        if (!JsfUtil.isValidationFailed()) {
            userBean.setUser(user);
            register = "success";
            comprobate = false;
            user = null;
            userDetails = null;
            return register;
        }
        register = "failure";
        return register;
    }

    /**
     * Getter de la comprobacion
     * @return
     */
    public boolean isComprobate() {
        return comprobate;
    }

    /**
     * Setter de la comprobación    
     * @param comprobate
     */
    public void setComprobate(boolean comprobate) {
        this.comprobate = comprobate;
    }

    /**
     * Getter del email
     * @return email
     */
    public String getEmail() {
        return email;
    }

    /**
     * Setter del email
     * @param email
     */
    public void setEmail(String email) {
        this.email = email;
    }

    /**
     * Getter del nombre de  usuario
     * @return nombre de usuario
     */
    public String getUsername() {
        return username;
    }

    /**
     * Setter del nombre de usuario 
     * @param username
     */
    public void setUsername(String username) {
        this.username = username;
    }

    /**
     * Getter del password
     * @return password
     */
    public String getPassword() {
        return password;
    }

    /**
     * Setter del password
     * @param Password
     */
    public void setPassword(String Password) {
        this.password = Password;
    }

    /**
     * Getter de las cordenadas
     * @return
     */
    public MapBean getCoordenates() {
        return coordenates;
    }

    /**
     * Setter de las cordenadas
     * @param coordenates
     */
    public void setCoordenates(MapBean coordenates) {
        this.coordenates = coordenates;
    }

    private UsersFacade getFacade() {
        return usersFacade;
    }
    
  
    public Users prepareCreate() {
       user = new Users();
       userDetails = new UserDetails();
       initializeEmbeddableKey();
       return user;
    }
    
    public void create() {
        persist(JsfUtil.PersistAction.CREATE, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("UsersCreated"));
    }
    
    private void persist(JsfUtil.PersistAction persistAction, String successMessage) {
        if (user != null) {
            setEmbeddableKeys();
            try {
                if (persistAction == JsfUtil.PersistAction.DELETE) {
                    getFacade().remove(user);
                } else if (persistAction == JsfUtil.PersistAction.UPDATE)    {
                    getFacade().edit(user);                    
                } else if (persistAction == JsfUtil.PersistAction.CREATE) {
                    getFacade().create(user);
                }
                JsfUtil.addSuccessMessage(successMessage);
            } catch (EJBException ex) {
                String msg = "";
                Throwable cause = ex.getCause();
                if (cause != null) {
                    msg = cause.getLocalizedMessage();
                }
                if (msg.length() > 0) {
                    JsfUtil.addErrorMessage(msg);
                } else {
                    JsfUtil.addErrorMessage(ex, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("PersistenceErrorOccured"));
                }
            } catch (Exception ex) {
                Logger.getLogger(this.getClass().getName()).log(Level.SEVERE, null, ex);
                JsfUtil.addErrorMessage(ex, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("PersistenceErrorOccured"));
            }
        }
    }
    
       
    public List<Users> getItemsAvailableSelectMany() {
        return getFacade().findAll();
    }

    public List<Users> getItemsAvailableSelectOne() {
        return getFacade().findAll();
    }
    
    protected void setEmbeddableKeys() {
    }

    protected void initializeEmbeddableKey() {
    }
    
    public void update() {
        persist(JsfUtil.PersistAction.UPDATE, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("UsersUpdated"));
    }

    public void destroy() {
        persist(JsfUtil.PersistAction.DELETE, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("UsersDeleted"));
        if (!JsfUtil.isValidationFailed()) {
            user = null; // Remove selection
            userDetails = null;
        }
    }
    
    /**
     * Método para dar de baja
     * @return estado de la baja
     */
    public String unSuscribe(){
        getUsersDetailsFacade().remove(userBean.getUser().getUserDetailsCollection().iterator().next());
        destroy();
        LoginBean login = new LoginBean();
        return login.logout();
    }

    public UserBean getUserBean() {
        return userBean;
    }

    public void setUserBean(UserBean userBean) {
        this.userBean = userBean;
    }

    public UserDetailsFacade getUsersDetailsFacade() {
        return usersDetailsFacade;
    }

    public void setUsersDetailsFacade(UserDetailsFacade usersDetailsFacade) {
        this.usersDetailsFacade = usersDetailsFacade;
    }
    
     
}
