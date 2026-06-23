package es.jaga.webagrupados.model.facades;

import es.jaga.webagrupados.model.entities.Users;
import java.util.List;
import javax.ejb.Stateless;
import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.persistence.TypedQuery;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;

/**
 *
 * @author Jose Antonio González Alcántara
 */
@Stateless
@Path("/UsersFacade")
public class UsersFacade extends AbstractFacade<Users> {
    @PersistenceContext(unitName = "EF_JAGA_JEE_WebAgrupadosPU")
    private EntityManager em;

    @Override
    protected EntityManager getEntityManager() {
        return em;
    }

    public UsersFacade() {
        super(Users.class);
    }
    
    /**
     * Método para comprobar las credenciales
     * @param username
     * @param password
     * @return
     */
    @GET
    @Path("/login/{username}/{password}")
    @Produces({"application/xml","application/json"})
    public Users login(@PathParam("username") String username,@PathParam("password") String password) {
        Users user = null;
        TypedQuery<Users> query = getEntityManager().createNamedQuery("Users.login", Users.class);
        query.setParameter("password", password);
        query.setParameter("username", username);
        List<Users> users = query.getResultList();
        if (!users.isEmpty() && users.size() == 1) {
            user = users.get(0);
        }
        return user;
    }
    
    /**
     * Método para comprobar la existencia de un nombre de usuario
     * @param username
     * @return
     */
    public Users isUsernameExist(String username){
        Users user = null;
        TypedQuery<Users> query = getEntityManager().createNamedQuery("Users.findByUsername", Users.class);
        query.setParameter("username", username);
        List<Users> users = query.getResultList();
        if (!users.isEmpty() && users.size() == 1) {
            user = users.get(0);
        }
        return user;
    } 

    /**
     * Método para comprobar la existencia de un email.
     * @param email
     * @return
     */
    public Users isEmailExist(String email){
        Users user = null;
        TypedQuery<Users> query = getEntityManager().createNamedQuery("Users.findByEmail", Users.class);
        query.setParameter("email", email);
        List<Users> users = query.getResultList();
        if (!users.isEmpty() && users.size() == 1) {
            user = users.get(0);
        }
        return user;
    } 
    
    /**
     * Método para combrobar la existencia de combinacion nombre de usuario email
     * @param email
     * @param username
     * @return
     */
    public Users isEmailOrUsernameExist(String email, String username){
        Users user = null;
        TypedQuery<Users> query = getEntityManager().createNamedQuery("Users.findByUsernameOrEmail", Users.class);
        query.setParameter("email", email);
        query.setParameter("username", username);
        List<Users> users = query.getResultList();
        if (!users.isEmpty() && users.size() == 1) {
            user = users.get(0);
        }
        return user;
    }
    
}
