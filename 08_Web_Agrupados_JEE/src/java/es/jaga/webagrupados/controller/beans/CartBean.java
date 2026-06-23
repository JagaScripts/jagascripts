package es.jaga.webagrupados.controller.beans;

import es.jaga.webagrupados.controller.util.JsfUtil;
import es.jaga.webagrupados.model.entities.CartOffer;
import es.jaga.webagrupados.model.entities.Coupons;
import es.jaga.webagrupados.model.entities.Offers;
import es.jaga.webagrupados.model.facades.CouponsFacade;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
import java.util.ResourceBundle;
import javax.ejb.EJB;
import javax.enterprise.context.SessionScoped;
import javax.inject.Inject;
import javax.inject.Named;

/**
 * Clase con el bean de sesión que almacena las ofertas compradas.
 * @author Jose Antonio González Alcántara
 */
@Named("cartBean")
@SessionScoped
public class CartBean implements Serializable{
    
    @Inject
    private UserBean userBean;
    private Offers offer;
    private List<Coupons> coupons;
    private HashMap<Offers,Integer> offerMap;
    private List<CartOffer> cartOffers;
    private float total = 0;
    @EJB private CouponsFacade couponsFacade;
    
    /**
     * Getter del bean de usuario
     * @return bean de usuario
     */
    public UserBean getUserBean() {
        return userBean;
    }

    /**
     * Setter del ben de usuario
     * @param userBean
     */
    public void setUserBean(UserBean userBean) {
        this.userBean = userBean;
    }

    /**
     * Getter de una oferta
     * @return oferta
     */
    public Offers getOffer() {
        return offer;
    }

    /**
     * Setter de una oferta
     * @param offer
     */
    public void setOffer(Offers offer) {
        this.offer = offer;
    }

    /**
     * Método que agrega una oferta al carrito
     * @param offer
     */
    public void addOfferToCart(Offers offer){
        offerMap = getOfferMap();
        if (!offerMap.containsKey(offer)) {
            offerMap.put(offer, 1);
        } else {
            int cant = offerMap.get(offer);
            cant++;
            offerMap.remove(offer);
            offerMap.put(offer,cant);
        }
        String msg = ResourceBundle.getBundle("/es/jaga/webagrupados/es_bundle").getString("AgregateCart");
        JsfUtil.addSuccessMessage(msg);
    }
    
    /**
     * Método que elimina la oferta del carrito
     * @param offer
     */
    public void removeOfferToCart(Offers offer){
        offerMap = getOfferMap();
        offerMap.remove(offer);
    }
    
    /**
     * Método que finaliza la compra del carrito
     * @return cadena
     */
    public String finalizarCompra(){
        String buy = new String();
        if (!userBean.isRegisteredUser()) {
            buy = "failure";
            JsfUtil.addErrorMessage("Debes registrarte para poder comprar");
        } else {
            for (Iterator<CartOffer> iterator = cartOffers.iterator(); iterator.hasNext();) {
                CartOffer next = iterator.next();
                for (int i = 0; i < next.getQuantiti(); i++) {
                    Coupons coupon = new Coupons();
                    coupon.setApplicationUsersId(userBean.getUser());
                    coupon.setOffersId(next.getOffer());
                    getCouponsFacade().create(coupon);                  
                }      
            }
            if (!JsfUtil.isValidationFailed()) {
                    JsfUtil.addSuccessMessage("Gracias por comprar en agrupados");
            }
            cartOffers = null;
            offerMap = null;
            buy = "success";
        }
        return buy;
    }

    /**
     * Getter del total
     * @return
     */
    public float getTotal() {
        return total;
    }

    /**
     * Setter del total
     * @param total
     */
    public void setTotal(float total) {
        this.total = total;
    }   

    /**
     * Getter de mapa de oferta
     * @return
     */
    public HashMap<Offers, Integer> getOfferMap() {
        if (offerMap == null) {
            offerMap = new HashMap();
        }
        return offerMap;
    }

    /**
     * Setter de Mapa de offerta
     * @param offerMap
     */
    public void setOfferMap(HashMap<Offers, Integer> offerMap) {
        this.offerMap = offerMap;
    }

    /**
     * Getter del CArrito de la oferta
     * @return
     */
    public List<CartOffer> getCartOffersFromMap(){
         offerMap = getOfferMap();
        if (offerMap != null) {
            cartOffers = null;
            cartOffers = getCartOffers();
            total = 0;
            for (Entry<Offers, Integer> entrySet : offerMap.entrySet()) {
                CartOffer elementOffer = new CartOffer();
                elementOffer.setOffer(entrySet.getKey());
                elementOffer.setQuantiti(entrySet.getValue());
                cartOffers.add(elementOffer);
                total = total + entrySet.getValue()*entrySet.getKey().getOfferPrice();
            }
        }
        return cartOffers;
    }
    
    /**
     * Getter del carrito de la oferta
     * @return lista de ofertas
     */
    public List<CartOffer> getCartOffers() {
        if (cartOffers == null) {
            cartOffers = new ArrayList<>();
        }
        return cartOffers;
    }

    /**
     * Setter de la lista de ofertas
     * @param cartOffers
     */
    public void setCartOffers(List<CartOffer> cartOffers) {
        this.cartOffers = cartOffers;
    }

    /**
     * Getter de los cupones
     * @return lista de cupones
     */
    public List<Coupons> getCoupons() {
        return coupons;
    }

    /**
     * Setter de los cupones
     * @param coupons
     */
    public void setCoupons(List<Coupons> coupons) {
        this.coupons = coupons;
    }

    /**
     * Getter de la Facade de cupones
     * @return
     */
    public CouponsFacade getCouponsFacade() {
        return couponsFacade;
    }

    /**
     * Setter de la facade de cupones
     * @param couponsFacade
     */
    public void setCouponsFacade(CouponsFacade couponsFacade) {
        this.couponsFacade = couponsFacade;
    }
    
    
    
}
