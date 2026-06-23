package es.jaga.webagrupados.model.entities;

import java.io.Serializable;
import java.util.Date;
import javax.persistence.Basic;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.ManyToOne;
import javax.persistence.NamedQueries;
import javax.persistence.NamedQuery;
import javax.persistence.Table;
import javax.persistence.Temporal;
import javax.persistence.TemporalType;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;
import javax.xml.bind.annotation.XmlRootElement;

/**
 *
 * @author Jose Antonio González Alcántara
 */
@Entity
@Table(name = "application_user_details")
@XmlRootElement
@NamedQueries({
    @NamedQuery(name = "UserDetails.findAll", query = "SELECT u FROM UserDetails u"),
    @NamedQuery(name = "UserDetails.findById", query = "SELECT u FROM UserDetails u WHERE u.id = :id"),
    @NamedQuery(name = "UserDetails.findByName", query = "SELECT u FROM UserDetails u WHERE u.name = :name"),
    @NamedQuery(name = "UserDetails.findByDniCif", query = "SELECT u FROM UserDetails u WHERE u.dniCif = :dniCif"),
    @NamedQuery(name = "UserDetails.findByAddress", query = "SELECT u FROM UserDetails u WHERE u.address = :address"),
    @NamedQuery(name = "UserDetails.findByCity", query = "SELECT u FROM UserDetails u WHERE u.city = :city"),
    @NamedQuery(name = "UserDetails.findByProvince", query = "SELECT u FROM UserDetails u WHERE u.province = :province"),
    @NamedQuery(name = "UserDetails.findByCountry", query = "SELECT u FROM UserDetails u WHERE u.country = :country"),
    @NamedQuery(name = "UserDetails.findByLatitude", query = "SELECT u FROM UserDetails u WHERE u.latitude = :latitude"),
    @NamedQuery(name = "UserDetails.findByLongitude", query = "SELECT u FROM UserDetails u WHERE u.longitude = :longitude"),
    @NamedQuery(name = "UserDetails.findByDateOfRegistration", query = "SELECT u FROM UserDetails u WHERE u.dateOfRegistration = :dateOfRegistration"),
    @NamedQuery(name = "UserDetails.findByLeavingDate", query = "SELECT u FROM UserDetails u WHERE u.leavingDate = :leavingDate")})
public class UserDetails implements Serializable {
    private static final long serialVersionUID = 1L;
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Basic(optional = false)
    @Column(name = "id")
    private Integer id;
    @Basic(optional = false)
    @NotNull
    @Size(min = 1, max = 200)
    @Column(name = "name")
    private String name;
    @Basic(optional = false)
    @NotNull
    @Size(min = 1, max = 12)
    @Column(name = "dni_cif")
    private String dniCif;
    @Basic(optional = false)
    @NotNull
    @Size(min = 1, max = 150)
    @Column(name = "address")
    private String address;
    @Basic(optional = false)
    @NotNull
    @Size(min = 1, max = 150)
    @Column(name = "city")
    private String city;
    @Basic(optional = false)
    @NotNull
    @Size(min = 1, max = 80)
    @Column(name = "province")
    private String province;
    @Basic(optional = false)
    @NotNull
    @Size(min = 1, max = 80)
    @Column(name = "country")
    private String country;
    // @Max(value=?)  @Min(value=?)//if you know range of your decimal fields consider using these annotations to enforce field validation
    @Column(name = "latitude")
    private Double latitude;
    @Column(name = "longitude")
    private Double longitude;
    @Basic(optional = false)
    @NotNull
    @Column(name = "date_of_registration")
    @Temporal(TemporalType.DATE)
    private Date dateOfRegistration;
    @Column(name = "leaving_date")
    @Temporal(TemporalType.DATE)
    private Date leavingDate;
    @JoinColumn(name = "application_users_id", referencedColumnName = "id")
    @ManyToOne(optional = false)
    private Users applicationUsersId;

    public UserDetails() {
        this.id = 0;
        this.dateOfRegistration = new Date();
    }

    public UserDetails(Integer id) {
        this.id = id;
        this.dateOfRegistration = new Date();
    }

    public UserDetails(Integer id, String name, String dniCif, String address, String city, String province, String country, Date dateOfRegistration) {
        this.id = id;
        this.name = name;
        this.dniCif = dniCif;
        this.address = address;
        this.city = city;
        this.province = province;
        this.country = country;
        this.dateOfRegistration = dateOfRegistration;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDniCif() {
        return dniCif;
    }

    public void setDniCif(String dniCif) {
        this.dniCif = dniCif;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getProvince() {
        return province;
    }

    public void setProvince(String province) {
        this.province = province;
    }

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
    }

    public Double getLatitude() {
        return latitude;
    }

    public void setLatitude(Double latitude) {
        this.latitude = latitude;
    }

    public Double getLongitude() {
        return longitude;
    }

    public void setLongitude(Double longitude) {
        this.longitude = longitude;
    }

    public Date getDateOfRegistration() {
        return dateOfRegistration;
    }

    public void setDateOfRegistration(Date dateOfRegistration) {
        this.dateOfRegistration = dateOfRegistration;
    }

    public Date getLeavingDate() {
        return leavingDate;
    }

    public void setLeavingDate(Date leavingDate) {
        this.leavingDate = leavingDate;
    }

    public Users getApplicationUsersId() {
        return applicationUsersId;
    }

    public void setApplicationUsersId(Users applicationUsersId) {
        this.applicationUsersId = applicationUsersId;
    }

    @Override
    public int hashCode() {
        int hash = 0;
        hash += (id != null ? id.hashCode() : 0);
        return hash;
    }

    @Override
    public boolean equals(Object object) {
        // TODO: Warning - this method won't work in the case the id fields are not set
        if (!(object instanceof UserDetails)) {
            return false;
        }
        UserDetails other = (UserDetails) object;
        if ((this.id == null && other.id != null) || (this.id != null && !this.id.equals(other.id))) {
            return false;
        }
        return true;
    }

    @Override
    public String toString() {
         return "Nombre " + name + "dirección: " + address + ", " + city + ", " + province + ", " + country + 
                ", DNI/CIF: " + dniCif ;
    }
    
}
