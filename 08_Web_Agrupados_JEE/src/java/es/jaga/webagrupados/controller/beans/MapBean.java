package es.jaga.webagrupados.controller.beans;

import es.jaga.webagrupados.model.entities.Address;
import es.jaga.webagrupados.services.CoordinatesService;
import java.io.Serializable;
import javax.enterprise.context.SessionScoped;
import javax.faces.application.FacesMessage;
import javax.faces.context.FacesContext;
import javax.inject.Named;
import org.primefaces.model.map.DefaultMapModel;
import org.primefaces.model.map.LatLng;
import org.primefaces.model.map.MapModel;
import org.primefaces.model.map.Marker;

/**
 * Clase con el bean que controla la vista del mapa.
 * 
 * @author Jose Antonio González Alcántara
 */
@Named(value = "mapBean")
@SessionScoped
public class MapBean implements Serializable {

    private Address address;
    private MapModel model;
    private Marker marker;

    /**
     * Creates a new instance of MapBean.
     */
    public MapBean() {
        model = new DefaultMapModel();
        address = new Address();
    }

    /**
     * Método que añade un marcador al modelo del mapa.
     */
    public void addMarker() {
        model.addOverlay(new Marker(new LatLng(address.getLatitude(), address.getLongitude()), address.getFullAddress()));
        //addMessage(new FacesMessage(FacesMessage.SEVERITY_INFO, "Marker Added", address.getCoordinatesForMap()));
    }

    /**
     * Método para mostrar un mensaje al contexto.
     *
     * @param message String.
     */
    public void addMessage(FacesMessage message) {
        FacesContext.getCurrentInstance().addMessage(null, message);
    }

    /**
     * Getter del modelo del mapa.
     *
     * @return MapModel modelo.
     */
    public MapModel getModel() {
        return model;
    }

    /**
     * Setter del modelo del mapa.
     *
     * @param model MapModel.
     */
    public void setModel(MapModel model) {
        this.model = model;
    }

    /**
     * Método que recupera las coordenadas del API de Google Maps para una
     * dirección determinada.
     */
    public void retrieveCoordinates() {
        CoordinatesService service = new CoordinatesService();
        double[] coords = service.getLatitudeLongitude(getAddress().getFullAddress());
        getAddress().setLatitude(coords[0]);
        getAddress().setLongitude(coords[1]);
        resetModel();
        addMarker();
    }

    /**
     * Getter del marcador del mapa.
     *
     * @return Marker marcador del mapa.
     */
    public Marker getMarker() {
        return marker;
    }

    /**
     * Método que reinicia el modelo del mapa.
     */
    private void resetModel() {
        model = new DefaultMapModel();
    }

    /**
     * Getter de la dirección.
     *
     * @return Address dirección por la que consulta.
     */
    public Address getAddress() {
        return address;
    }

    /**
     * Setter de la dirección.
     *
     * @param defaultAddress Address dirección.
     */
    public void setAddress(Address defaultAddress) {
        this.address = defaultAddress;
    }

    /**
     * Método que muestra la dirección en la interfaz gráfica y que podríamos
     * aprovechar para almacenar en base de datos.
     */
    public void save() {
        String msg = getAddress().getFullAddress() + " " + getAddress().getCoordinatesForMap();
        addMessage(new FacesMessage(FacesMessage.SEVERITY_INFO, msg, msg));
    }
}
