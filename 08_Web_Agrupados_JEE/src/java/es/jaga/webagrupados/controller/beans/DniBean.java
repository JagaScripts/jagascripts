package es.jaga.webagrupados.controller.beans;

import javax.enterprise.context.RequestScoped;
import javax.faces.application.FacesMessage;
import javax.faces.component.UIComponent;
import javax.faces.context.FacesContext;
import javax.faces.validator.ValidatorException;
import javax.inject.Named;

/**
 * Clase que verifica la validez de un DNI.
 * 
 * @author Jose Antonio González Alcántara
 */
@Named("dniBean")
@RequestScoped
public class DniBean {
    
     /**
     * 
     * Método que valida un DNI.
     * 
     * @param dni String que representa un DNI.
     * @return true si el DNI es válido y false el DNI no es válido.
     */
    private boolean esValido(String dni){
        try {
            dni = dni.toUpperCase();
            Character letra = dni.charAt(8);
            Integer numeros = Integer.parseInt(dni.substring(0, 8));
            return (verificarParametros(dni, letra) && verificarLetra(numeros, letra));
        } catch (Exception e) {
            return false;
        }
    }
   
    /**
     * Método que valida un DNI.
     * 
     * @param numeros String de números.
     * @param letra Character de la letra.
     * @return true si el DNI es válido y false si el DNI no es válido.
     */
    private boolean esValido(String numeros, Character letra){
        try {
            String dni = numeros + letra;
            letra = dni.toUpperCase().charAt(8);
            Integer vNumeros = Integer.parseInt(numeros);
            return (verificarParametros(dni, letra) && verificarLetra(vNumeros, letra));
        } catch (Exception e) {
            return false;
        }
    }
    
    /**
     * Método que verifica los parametros proporcionados.
     * 
     * @param dni String del DNI.
     * @param letra Character de la letra.
     * @return true si los parametros son válido y false si los parametros no son válidos.
     */
    private boolean verificarParametros(String dni, Character letra){
        return (dni.length() == 9 && Character.isLetter(letra));
    }
    
    /**
     * Método que verifica la correspondencia entre los números y la letra del DNI.
     * 
     * @param numeros String de números.
     * @param letra Character de la letra.
     * @return true si la correspondencia es válida y false si la correspondencia no es válida.
     */
    private boolean verificarLetra(Integer numeros, Character letra){
        int resto = numeros % 23;
        String letrasValidas = "TRWAGMYFPDXBNJZSQVHLCKE";
        Character letraValida = letrasValidas.charAt(resto);
        return letraValida.equals(letra);
    }
    
    public void validate(FacesContext arg0, UIComponent arg1, Object arg2)
         throws ValidatorException {
      if (!esValido((String)arg2)) {
         throw new ValidatorException(new FacesMessage(FacesMessage.SEVERITY_ERROR,
                 "El DNI/CIF tiene que ser valido 9 números y 1 letra",
                 "El DNI/CIF tiene que ser valido 9 números y 1 letra"));
      }
   }
    
}
