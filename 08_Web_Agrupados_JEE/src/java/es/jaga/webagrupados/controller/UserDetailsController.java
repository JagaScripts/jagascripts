package es.jaga.webagrupados.controller;

import es.jaga.webagrupados.controller.beans.LoginBean;
import es.jaga.webagrupados.controller.beans.MapBean;
import es.jaga.webagrupados.controller.beans.UserBean;
import es.jaga.webagrupados.model.entities.UserDetails;
import es.jaga.webagrupados.controller.util.JsfUtil;
import es.jaga.webagrupados.controller.util.JsfUtil.PersistAction;
import es.jaga.webagrupados.model.facades.UserDetailsFacade;

import java.io.Serializable;
import java.util.List;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.ejb.EJB;
import javax.ejb.EJBException;
import javax.faces.bean.ManagedBean;
import javax.faces.bean.SessionScoped;
import javax.faces.component.UIComponent;
import javax.faces.context.FacesContext;
import javax.faces.convert.Converter;
import javax.faces.convert.FacesConverter;
import javax.inject.Inject;

@ManagedBean(name = "userDetailsController")
@SessionScoped
public class UserDetailsController implements Serializable {

    @EJB
    private es.jaga.webagrupados.model.facades.UserDetailsFacade ejbFacade;
    private List<UserDetails> items = null;
    private UserDetails selected;
    private MapBean mapBean;

    public UserDetailsController() {
    }

    public UserDetails getSelected() {
        return selected;
    }

    public void setSelected(UserDetails selected) {
        this.selected = selected;
    }

    protected void setEmbeddableKeys() {
    }

    protected void initializeEmbeddableKey() {
    }

    private UserDetailsFacade getFacade() {
        return ejbFacade;
    }

    public UserDetails prepareCreate() {
        selected = new UserDetails();
        initializeEmbeddableKey();
        return selected;
    }

    public void create() {
        setAdress();
        persist(PersistAction.CREATE, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("UserDetailsCreated"));
        if (!JsfUtil.isValidationFailed()) {
            items = null;    // Invalidate list of items to trigger re-query.
        }
    }

    public void update() {
        setAdress();
        persist(PersistAction.UPDATE, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("UserDetailsUpdated"));
    }

    public void destroy() {
        persist(PersistAction.DELETE, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("UserDetailsDeleted"));
        if (!JsfUtil.isValidationFailed()) {
            selected = null; // Remove selection
            items = null;    // Invalidate list of items to trigger re-query.
        }
    }

    public List<UserDetails> getItems() {
        if (items == null) {
            items = getFacade().findAll();
            mapBean = new MapBean();
            retrieveCoordinates();
        }
        return items;
    }

    private void persist(PersistAction persistAction, String successMessage) {
        if (selected != null) {
            setEmbeddableKeys();
            try {
                if (persistAction != PersistAction.DELETE) {
                    getFacade().edit(selected);
                } else {
                    getFacade().remove(selected);
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

    public List<UserDetails> getItemsAvailableSelectMany() {
        return getFacade().findAll();
    }

    public List<UserDetails> getItemsAvailableSelectOne() {
        return getFacade().findAll();
    }

    @FacesConverter(forClass = UserDetails.class)
    public static class UserDetailsControllerConverter implements Converter {

        @Override
        public Object getAsObject(FacesContext facesContext, UIComponent component, String value) {
            if (value == null || value.length() == 0) {
                return null;
            }
            UserDetailsController controller = (UserDetailsController) facesContext.getApplication().getELResolver().
                    getValue(facesContext.getELContext(), null, "userDetailsController");
            return controller.getFacade().find(getKey(value));
        }

        java.lang.Integer getKey(String value) {
            java.lang.Integer key;
            key = Integer.valueOf(value);
            return key;
        }

        String getStringKey(java.lang.Integer value) {
            StringBuilder sb = new StringBuilder();
            sb.append(value);
            return sb.toString();
        }

        @Override
        public String getAsString(FacesContext facesContext, UIComponent component, Object object) {
            if (object == null) {
                return null;
            }
            if (object instanceof UserDetails) {
                UserDetails o = (UserDetails) object;
                return getStringKey(o.getId());
            } else {
                Logger.getLogger(this.getClass().getName()).log(Level.SEVERE, "object {0} is of type {1}; expected type: {2}", new Object[]{object, object.getClass().getName(), UserDetails.class.getName()});
                return null;
            }
        }

    }

    public MapBean getMapBean() {
        if (mapBean == null) {
            mapBean = new MapBean();
        }
        return mapBean;
    }

    public void setMapBean(MapBean mapBean) {
        this.mapBean = mapBean;
    }

    public void retrieveCoordinates(){
        mapBean.retrieveCoordinates();
        if (selected != null) {
            mapBean.getAddress().setAddress(selected.getAddress());
            mapBean.getAddress().setCity(selected.getCity());
            mapBean.getAddress().setCountry(selected.getCountry());
            mapBean.getAddress().setProvince(selected.getProvince());           
        }
    }
    
    private void setAdress(){
        mapBean.retrieveCoordinates();
        selected.setAddress(mapBean.getAddress().getAddress());
        selected.setCity(mapBean.getAddress().getCity());
        selected.setCountry(mapBean.getAddress().getCountry());
        selected.setProvince(mapBean.getAddress().getProvince());
        selected.setLatitude(mapBean.getAddress().getLatitude());
        selected.setLongitude(mapBean.getAddress().getLongitude());
    }
 
}
