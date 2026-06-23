/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package es.jaga.webagrupados.model.facades;

import es.jaga.webagrupados.model.entities.Offers;
import es.jaga.webagrupados.model.entities.Users;
import java.util.List;
import javax.ejb.Stateless;
import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.persistence.TypedQuery;

/**
 *
 * @author Jose Antonio González Alcántara
 */
@Stateless
public class OffersFacade extends AbstractFacade<Offers> {
    @PersistenceContext(unitName = "EF_JAGA_JEE_WebAgrupadosPU")
    private EntityManager em;

    @Override
    protected EntityManager getEntityManager() {
        return em;
    }

    public OffersFacade() {
        super(Offers.class);
    }
    
    /**
     * Método para buscar las oferta activas
     * @return
     */
    public List<Offers> findActive(){
        List<Offers> offers = null;
        TypedQuery<Offers> query = getEntityManager().createNamedQuery("Offers.findByActive", Offers.class);
        query.setParameter("active", true);
        offers = query.getResultList();
        return offers;
    }
    
    /**
     * Método para buscar las ofertas de un solo negocio
     * @param business
     * @return
     */
    public List<Offers> findBusiness(Users business){
        List<Offers> offers = null;
        TypedQuery<Offers> query = getEntityManager().createNamedQuery("Offers.findByBusiness", Offers.class);
        query.setParameter("aplicationUserId", business);
        offers = query.getResultList();
        return offers;
    }
}
