package es.jaga.webagrupados.controller;

import es.jaga.webagrupados.controller.beans.UserBean;
import es.jaga.webagrupados.model.entities.Offers;
import es.jaga.webagrupados.controller.util.JsfUtil;
import es.jaga.webagrupados.controller.util.JsfUtil.PersistAction;
import es.jaga.webagrupados.model.facades.OffersFacade;

import java.io.Serializable;
import java.util.Date;
import java.util.List;
import java.util.Locale;
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

@ManagedBean(name = "offersController")
@SessionScoped
public class OffersController implements Serializable {

    @EJB
    private es.jaga.webagrupados.model.facades.OffersFacade ejbFacade;
    private List<Offers> items = null;
    private List<Offers> itemsActive = null;
    private Offers selected;
    private List<Offers> filteredItems = null;
    private List<Offers> businessItems = null;
    @Inject
    private UserBean userBean;

    public OffersController() {
    }

    public Offers getSelected() {
        return selected;
    }

    public void setSelected(Offers selected) {
        this.selected = selected;
    }

    protected void setEmbeddableKeys() {
    }

    protected void initializeEmbeddableKey() {
    }

    private OffersFacade getFacade() {
        return ejbFacade;
    }

    public Offers prepareCreate() {
        selected = new Offers();
        initializeEmbeddableKey();
        return selected;
    }

    public void create() {
        persist(PersistAction.CREATE, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("OffersCreated"));
        if (!JsfUtil.isValidationFailed()) {
            items = null;    // Invalidate list of items to trigger re-query.
        }
    }

    public void update() {
        if (selected.getActive() == true) {
            Offers tempOffer = selected;
            setActiveOffer(selected);
            persist(PersistAction.UPDATE, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("OffersUpdated"));
            for (Offers item : businessItems) {
                selected = item;
                if (tempOffer.getId() != selected.getId()) {
                    persist(PersistAction.UPDATE, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("OffersUpdated"));
                }
            }
            selected = tempOffer;
        } else {
            persist(PersistAction.UPDATE, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("OffersUpdated"));
        }
        
        
        
    }

    public void destroy() {
        persist(PersistAction.DELETE, ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("OffersDeleted"));
        if (!JsfUtil.isValidationFailed()) {
            selected = null; // Remove selection
            items = null;    // Invalidate list of items to trigger re-query.
        }
    }

    public List<Offers> getItems() {
        if (items == null) {
                items = getFacade().findAll();
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

    public List<Offers> getItemsAvailableSelectMany() {
        return getFacade().findAll();
    }

    public List<Offers> getItemsAvailableSelectOne() {
        return getFacade().findAll();
    }

    @FacesConverter(forClass = Offers.class)
    public static class OffersControllerConverter implements Converter {

        @Override
        public Object getAsObject(FacesContext facesContext, UIComponent component, String value) {
            if (value == null || value.length() == 0) {
                return null;
            }
            OffersController controller = (OffersController) facesContext.getApplication().getELResolver().
                    getValue(facesContext.getELContext(), null, "offersController");
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
            if (object instanceof Offers) {
                Offers o = (Offers) object;
                return getStringKey(o.getId());
            } else {
                Logger.getLogger(this.getClass().getName()).log(Level.SEVERE, "object {0} is of type {1}; expected type: {2}", new Object[]{object, object.getClass().getName(), Offers.class.getName()});
                return null;
            }
        }

    }

    public List<Offers> getFilteredItems() {
        if (filteredItems == null) {
            filteredItems = getFacade().findActive();
        }
        return filteredItems;
    }

    public void setFilteredItems(List<Offers> filteredItems) {
        this.filteredItems = filteredItems;
    }
    
    public boolean filterByPriceLte(Object value, Object filter, Locale locale) {
        String filterText = (filter == null) ? null : filter.toString().trim();
        if(filterText == null||filterText.equals("")) {
            return true;
        }
         
        if(value == null) {
            return false;
        }
        return ((Comparable) value).compareTo(Float.valueOf(filterText)) < 0;
    }

     public boolean filterByPriceGte(Object value, Object filter, Locale locale) {
        String filterText = (filter == null) ? null : filter.toString().trim();
        if(filterText == null||filterText.equals("")) {
            return true;
        }
         
        if(value == null) {
            return false;
        }
         
        return ((Comparable) value).compareTo(Float.valueOf(filterText)) > 0;
    }
     
    public boolean filterByDateBefore(Object value, Object filter, Locale locale) {
        if (filter == null || filter.toString().isEmpty()) {
            return true;
        }
        
        if(value == null) {
            return false;
        }
        Date valueDate = (Date) value;
        Date filterDate = (Date) filter;
       
        return filterDate.before(valueDate);
    }
    
    public boolean filterByDateAfter(Object value, Object filter, Locale locale) {
        if (filter == null || filter.toString().isEmpty()) {
            return true;
        }
        
        if(value == null) {
            return false;
        }
        Date valueDate = (Date) value;
        Date filterDate = (Date) filter;
        
        return filterDate.after(valueDate);
    }
    
    public boolean filterByActive(Object value, Object filter, Locale locale){
        return (boolean) value;
    }

    public List<Offers> getItemsActive() {
        return itemsActive == null ? getFacade().findActive() : itemsActive;
    }

    public void setItemsActive(List<Offers> itemsActive) {
        this.itemsActive = itemsActive;
    }

    public List<Offers> getBusinessItems() {
        return businessItems == null || userBean.getUser() != null ? businessItems = getFacade().findBusiness(userBean.getUser()) : businessItems;
    }

    public void setBusinessItems(List<Offers> businessItems) {
        this.businessItems = businessItems;
    }

    public UserBean getUserBean() {
        return userBean;
    }

    public void setUserBean(UserBean userBean) {
        this.userBean = userBean;
    }

    public void setActiveOffer(Offers active){
        for (Offers item : businessItems) {
            if (item.getId() != active.getId()) {
                item.setActive(false);
            }
        }
    }
}
