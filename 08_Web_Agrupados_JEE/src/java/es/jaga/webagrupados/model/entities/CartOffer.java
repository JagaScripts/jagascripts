package es.jaga.webagrupados.model.entities;

/**
 * Envoltorio para el carrito
 * @author Jose Antonio González Alcántara
 */
public class CartOffer {
    
    private Offers offer;
    private Integer quantiti;
    private float offerPrice;

    /**
     * Getter de la oferta
     * @return
     */
    public Offers getOffer() {
        return offer;
    }

    /**
     * Setter de la oferta
     * @param offer
     */
    public void setOffer(Offers offer) {
        this.offer = offer;
    }

    /**
     * Getter de la cantidad
     * @return cantidad
     */
    public Integer getQuantiti() {
        return quantiti;
    }

    /**
     * Setter de la cantidad
     * @param quantiti
     */
    public void setQuantiti(Integer quantiti) {
        this.quantiti = quantiti;
    }

    /**
     * Getter de precio de la oferta
     * @return precio de la oferta
     */
    public float getOfferPrice() {
        offerPrice = offer.getOfferPrice()*quantiti;
        return offerPrice;
    }

    /**
     * Setter del precio de la oferta
     * @param offerPrice
     */
    public void setOfferPrice(float offerPrice) {
        this.offerPrice = offerPrice;
    }
    
    
    
}
