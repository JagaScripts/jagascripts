package es.jaga.webagrupados.model.entities;

import java.io.Serializable;
import java.util.Collection;
import java.util.Date;
import javax.persistence.Basic;
import javax.persistence.CascadeType;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.ManyToOne;
import javax.persistence.NamedQueries;
import javax.persistence.NamedQuery;
import javax.persistence.OneToMany;
import javax.persistence.Table;
import javax.persistence.Temporal;
import javax.persistence.TemporalType;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;
import javax.xml.bind.annotation.XmlRootElement;
import javax.xml.bind.annotation.XmlTransient;

/**
 *
 * @author Jose Antonio González Alcántara
 */
@Entity
@Table(name = "offers")
@XmlRootElement
@NamedQueries({
    @NamedQuery(name = "Offers.findAll", query = "SELECT o FROM Offers o"),
    @NamedQuery(name = "Offers.findById", query = "SELECT o FROM Offers o WHERE o.id = :id"),
    @NamedQuery(name = "Offers.findByTitle", query = "SELECT o FROM Offers o WHERE o.title = :title"),
    @NamedQuery(name = "Offers.findByDescription", query = "SELECT o FROM Offers o WHERE o.description = :description"),
    @NamedQuery(name = "Offers.findByStartPrice", query = "SELECT o FROM Offers o WHERE o.startPrice = :startPrice"),
    @NamedQuery(name = "Offers.findByOfferPrice", query = "SELECT o FROM Offers o WHERE o.offerPrice = :offerPrice"),
    @NamedQuery(name = "Offers.findByImage", query = "SELECT o FROM Offers o WHERE o.image = :image"),
    @NamedQuery(name = "Offers.findByStartDate", query = "SELECT o FROM Offers o WHERE o.startDate = :startDate"),
    @NamedQuery(name = "Offers.findByEndDate", query = "SELECT o FROM Offers o WHERE o.endDate = :endDate"),
    @NamedQuery(name = "Offers.findByBusiness", query = "SELECT o FROM Offers o WHERE o.applicationUsersId = :aplicationUserId"),
    @NamedQuery(name = "Offers.findByActive", query = "SELECT o FROM Offers o WHERE o.active = :active")})

public class Offers implements Serializable {
    private static final long serialVersionUID = 1L;
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Basic(optional = false)
    @Column(name = "id")
    private Integer id;
    @Basic(optional = false)
    @NotNull
    @Size(min = 1, max = 100)
    @Column(name = "title")
    private String title;
    @Size(max = 250)
    @Column(name = "description")
    private String description;
    @Basic(optional = false)
    @NotNull
    @Column(name = "start_price")
    private float startPrice;
    @Basic(optional = false)
    @NotNull
    @Column(name = "offer_price")
    private float offerPrice;
    @Size(max = 100)
    @Column(name = "image")
    private String image;
    @Basic(optional = false)
    @NotNull
    @Column(name = "start_date")
    @Temporal(TemporalType.TIMESTAMP)
    private Date startDate;
    @Basic(optional = false)
    @NotNull
    @Column(name = "end_date")
    @Temporal(TemporalType.TIMESTAMP)
    private Date endDate;
    @Basic(optional = false)
    @NotNull
    @Column(name = "active")
    private boolean active;
    @OneToMany(cascade = CascadeType.ALL, mappedBy = "offersId")
    private Collection<Coupons> couponsCollection;
    @JoinColumn(name = "application_users_id", referencedColumnName = "id")
    @ManyToOne(optional = false)
    private Users applicationUsersId;

    public Offers() {
        this.id = 0;
        this.active = false;
    }

    public Offers(Integer id) {
        this.id = id;
    }

    public Offers(Integer id, String title, float startPrice, float offerPrice, Date startDate, Date endDate, boolean active) {
        this.id = id;
        this.title = title;
        this.startPrice = startPrice;
        this.offerPrice = offerPrice;
        this.startDate = startDate;
        this.endDate = endDate;
        this.active = active;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public float getStartPrice() {
        return startPrice;
    }

    public void setStartPrice(float startPrice) {
        this.startPrice = startPrice;
    }

    public float getOfferPrice() {
        return offerPrice;
    }

    public void setOfferPrice(float offerPrice) {
        this.offerPrice = offerPrice;
    }

    public String getImage() {
        return image;
    }

    public void setImage(String image) {
        this.image = image;
    }

    public Date getStartDate() {
        return startDate;
    }

    public void setStartDate(Date startDate) {
        this.startDate = startDate;
    }

    public Date getEndDate() {
        return endDate;
    }

    public void setEndDate(Date endDate) {
        this.endDate = endDate;
    }

    public boolean getActive() {
        return active;
    }

    public void setActive(boolean active) {
        this.active = active;
    }

    @XmlTransient
    public Collection<Coupons> getCouponsCollection() {
        return couponsCollection;
    }

    public void setCouponsCollection(Collection<Coupons> couponsCollection) {
        this.couponsCollection = couponsCollection;
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
        if (!(object instanceof Offers)) {
            return false;
        }
        Offers other = (Offers) object;
        if ((this.id == null && other.id != null) || (this.id != null && !this.id.equals(other.id))) {
            return false;
        }
        return true;
    }

    @Override
    public String toString() {
        return "Oferta: " + this.title + ", " + this.description;
    }
    
}
