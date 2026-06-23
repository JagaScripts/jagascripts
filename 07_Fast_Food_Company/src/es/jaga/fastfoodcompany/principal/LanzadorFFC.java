package es.jaga.fastfoodcompany.principal;

/**
 * Classe principal lanzadora del proyecto FastFooCompany.
 * @author Jose Antonio González Alcántara
 */
public class LanzadorFFC {
    
    /**
     * Método principal.
     *
     * @param args String[] parámetros.
     */
    public static void main(String[] args) {
        try {
            javax.swing.UIManager.setLookAndFeel(javax.swing.UIManager.getSystemLookAndFeelClassName());
            FFCJFrame frame = FFCJFrame.getInstancia();
            frame.setVisible(true);
        } catch (ClassNotFoundException ex) {
            java.util.logging.Logger.getLogger(FFCJFrame.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
        } catch (InstantiationException ex) {
            java.util.logging.Logger.getLogger(FFCJFrame.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
        } catch (IllegalAccessException ex) {
            java.util.logging.Logger.getLogger(FFCJFrame.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
        } catch (javax.swing.UnsupportedLookAndFeelException ex) {
            java.util.logging.Logger.getLogger(FFCJFrame.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
        }
    }
}
