package es.jaga.fastfoodcompany.modelo.entidades;

/**
 * Clase que corresponde al modelo de datos de tipo Cliente de la aplicación.
 *
 * @author Jose Antonio González Alcántara
 */
public class Cliente {

    private String nombre;
    private String primerApellido;
    private String segundoApellido;
    private boolean habitual;
    private DNI dni;
    private Direccion direccion;
    private int id;

    /**
     * Constructor que recibe todos los parámetros del formulario.
     *
     * @param id
     * @param dni
     * @param nombre String nombre del cliente.
     * @param primerApellido String primerApellido del cliente.
     * @param segundoApellido String segundoApellido del cliente.
     * @param direccion String direccion del cliente.
     * @param habitual Boolean habitual del cliente.
     */
    
    public Cliente(int id, String dni, String nombre, String primerApellido, String segundoApellido,
            String direccion, Boolean habitual) {
        this.id = id;
        this.nombre = nombre;
        this.primerApellido = primerApellido;
        this.segundoApellido = segundoApellido;
        this.dni = new DNI(dni);
        this.direccion = new Direccion(direccion);
        this.habitual = habitual;
    }
     /**
     * Constructor de cliente vacio.
     */
    public Cliente(){
     
    }

    /**
     * Clase que corresponde al modelo de datos de tipo DNI de la aplicación.
     */
    public class DNI {

        
        private Integer numeros;
        private char letra;
       
        /**
         * Constructor que recibe un dni.
         * @param dni
         */
        public DNI(String dni){
            if (dni != null) {
                this.letra = dni.charAt(8);
                this.numeros = Integer.parseInt(dni.substring(0, 8));
            }
        }
        
        /**
         * Constructor que recibe todos las partes de un del DNI.
         * @param numeros
         * @param letra
         */
        public DNI(Integer numeros, char letra) {
            this.numeros = numeros;
            this.letra = letra;
        }
    
        /**
        * 
        * Método que valida un DNI.
        * 
        * @param dni String que representa un DNI.
        * @return true si el DNI es válido y false el DNI no es válido.
        */
        public boolean esValido(String dni){
            try {
                dni = dni.toUpperCase();
                setDNI(dni.substring(0, 8),dni.charAt(8));
                return (verificarParametros(dni, getLetra()) && verificarLetra(getNumeros(), getLetra()));
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
        public boolean esValido(String numeros, Character letra){
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

        public char getLetra() {
            return letra;
        }

        public void setLetra(char letra) {
            this.letra = letra;
        }

        public Integer getNumeros() {
            return numeros;
        }

        public void setNumeros(Integer numeros) {
            this.numeros = numeros;
        }
        
        public void setDNI(String numeros, char letra){
            setNumeros(Integer.parseInt(numeros));
            setLetra(letra);
        }

        public String getDNI(){
            return getNumeros().toString() + getLetra();
        }

        @Override
        public String toString() {
            return getNumeros() + "-" + getLetra();
        }
    }

    /**
     * Clase que corresponde al modelo de datos de tipo Direccion de la aplicación.
     */
    public class Direccion {

        private String tipoDeVia;
        private String nombreDeVia;
        private int numero;
        private int piso;
        private int puerta;
        private String localidad;
        private int cp;
        private String provincia;
        private String pais;

        public Direccion(String tipoDeVia, String nombreDeVia, int numero,
                int piso, int puerta, String localidad, int cp,
                String provincia, String pais) {
            this.tipoDeVia = tipoDeVia;
            this.nombreDeVia = nombreDeVia;
            this.numero = numero;
            this.piso = piso;
            this.puerta = puerta;
            this.localidad = localidad;
            this.cp = cp;
            this.provincia = provincia;
            this.pais = pais;
        }
        
        public Direccion(String direccion){
            if (direccion != null) {
                String[] splitDireccion = direccion.split(" - ");
                this.tipoDeVia = splitDireccion[0];
                this.nombreDeVia = splitDireccion[1];
                this.numero = Integer.parseInt(splitDireccion[2]);
                this.piso =  Integer.parseInt(splitDireccion[3]);
                this.puerta =  Integer.parseInt(splitDireccion[4]);
                this.localidad = splitDireccion[6];
                this.cp =  Integer.parseInt(splitDireccion[5]);
                this.provincia = splitDireccion[7];
                this.pais = splitDireccion[8];
            }
        }

        @Override
        public String toString() {
            return getTipoVia() + " - " + getNombreVia() + " - " + getNumeroCasa()
                    + " - " + getNumeroPiso() + " - " + getNumeroPuerta() + " - " + getCodigoPostal()
                    + " - " + getLocalidad() + " - " + getProvincia() + " - "
                    + getPais();
        }

        public String getTipoVia() {
            return tipoDeVia;
        }

        public void setTipoVia(String tipoDeVia) {
            this.tipoDeVia = tipoDeVia;
        }

        public String getNombreVia() {
            return nombreDeVia;
        }

        public void setNombreVia(String nombreDeVia) {
            this.nombreDeVia = nombreDeVia;
        }

        public int getNumeroCasa() {
            return numero;
        }

        public void setNumeroCasa(int numero) {
            this.numero = numero;
        }

        public int getNumeroPiso() {
            return piso;
        }

        public void setNumeroPiso(int piso) {
            this.piso = piso;
        }

        public int getNumeroPuerta() {
            return puerta;
        }

        public void setNumeroPuerta(int puerta) {
            this.puerta = puerta;
        }

        public String getLocalidad() {
            return localidad;
        }

        public void setLocalidad(String localidad) {
            this.localidad = localidad;
        }

        public int getCodigoPostal() {
            return cp;
        }

        public void setCp(int cp) {
            this.cp = cp;
        }

        public String getProvincia() {
            return provincia;
        }

        public void setProvincia(String provincia) {
            this.provincia = provincia;
        }

        public String getPais() {
            return pais;
        }

        public void setPais(String pais) {
            this.pais = pais;
        }
    }

    /**
     * Getter del habitualidad del cliente.
     * 
     * @return boolean habitualidad del cliente.
     */
    public boolean isHabitual() {
        return habitual;
    }

    /**
     * Setter de la habitualidad del cliente.
     * 
     * @param habitual del cliente.
     */
    public void setHabitual(boolean habitual) {
        this.habitual = habitual;
    }
    
    /**
     * Getter del nombre del cliente.
     *
     * @return String nombre del cliente.
     */
    public String getNombre() {
        return nombre;
    }

    /**
     * Setter del nombre del cliente.
     *
     * @param nombre String nombre del cliente.
     */
    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    /**
     * Getter del apellido paterno del cliente.
     *
     * @return String primerApellido.
     */
    public String getPrimerApellido() {
        return primerApellido;
    }

    /**
     * Setter del apellido paterno del cliente.
     *
     * @param apellido1 String apellido paterno.
     */
    public void setPrimerApellido(String apellido1) {
        this.primerApellido = apellido1;
    }

    /**
     * Getter del apellido materno del cliente.
     *
     * @return String segundoApellido.
     */
    public String getSegundoApellido() {
        return segundoApellido;
    }

    /**
     * Setter del apellido materno del cliente.
     *
     * @param apellido2 String apellido materno.
     */
    public void setSegundoApellido(String apellido2) {
        this.segundoApellido = apellido2;
    }

    public Direccion getDireccion() {
        return direccion;
    }

    public DNI getDni() {
        return dni;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }
    
    

    /**
     * Método que devuelve el nombre y los dos apellidos del cliente.
     *
     * @return String nombre completo del cliente.
     */
    public String getNombreCompleto() {
        return getNombre() + " " + getPrimerApellido()+ " " + getSegundoApellido();
    }

    /**
     *
     * @return
     */
    @Override
    public String toString() {
        return getDni().toString() + " " + getNombreCompleto() + "\n"
                + getDireccion().toString();
    }
}
