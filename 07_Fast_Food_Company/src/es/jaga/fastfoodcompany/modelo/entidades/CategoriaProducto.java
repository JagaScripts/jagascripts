package es.jaga.fastfoodcompany.modelo.entidades;

/**
 *
 * @author Jose Antonio González Alcántara
 */
public class CategoriaProducto {
    
    private int idCategoria;
    private int idProdcuto;
    
    /**
     *
     * @param idCategoria
     * @param idProducto
     */
    public CategoriaProducto(int idCategoria, int idProducto){
        this.idCategoria = idCategoria;
        this.idProdcuto = idProducto;
    }

    /**
     *
     * @return
     */
    public int getIdCategoria() {
        return idCategoria;
    }

    /**
     *
     * @param idCategoria
     */
    public void setIdCategoria(int idCategoria) {
        this.idCategoria = idCategoria;
    }

    /**
     *
     * @return
     */
    public int getIdProdcuto() {
        return idProdcuto;
    }

    /**
     *
     * @param idProdcuto
     */
    public void setIdProdcuto(int idProdcuto) {
        this.idProdcuto = idProdcuto;
    }
    
    
}
