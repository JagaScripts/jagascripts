package es.jaga.fastfoodcompany.vista;

import es.jaga.fastfoodcompany.controlador.AccionCategoriaProducto;
import es.jaga.fastfoodcompany.controlador.AccionCategorias;
import es.jaga.fastfoodcompany.controlador.AccionClientes;
import es.jaga.fastfoodcompany.controlador.AccionDescuentos;
import es.jaga.fastfoodcompany.controlador.AccionDetalleVenta;
import es.jaga.fastfoodcompany.controlador.AccionProductos;
import es.jaga.fastfoodcompany.controlador.AccionVentas;
import es.jaga.fastfoodcompany.modelo.entidades.Categoria;
import es.jaga.fastfoodcompany.modelo.entidades.Descuento;
import es.jaga.fastfoodcompany.modelo.entidades.DetalleVenta;
import es.jaga.fastfoodcompany.modelo.entidades.Producto;
import es.jaga.fastfoodcompany.modelo.entidades.Venta;
import es.jaga.fastfoodcompany.principal.FFCJFrame;
import java.awt.FlowLayout;
import java.awt.Image;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.DateFormat;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Iterator;
import java.util.List;
import java.util.Vector;
import javax.swing.ImageIcon;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import static javax.swing.SwingConstants.BOTTOM;
import static javax.swing.SwingConstants.CENTER;
import javax.swing.Timer;
import javax.swing.event.TableModelEvent;
import javax.swing.event.TableModelListener;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableModel;

/**
 * Classe del panel de gestion de la pantalla del TPV.
 * @author Jose Antonio González Alcántara
 */
public class PantallaTPV extends javax.swing.JPanel {

    private final FFCJFrame frame;
    private final DateFormat formatoHora = new SimpleDateFormat("HH:mm:ss");
    private final DateFormat formatoFecha =  new SimpleDateFormat("dd/MM/yyyy");
    private final Timer temporizador;
    private final ActionListener accionActualizarHora;
    private final AccionCategorias accionesCategorias;
    private final AccionProductos accionesProductos;
    private final AccionCategoriaProducto accionesCategoriaProducto;
    private final AccionVentas accionesVentas;
    private final AccionDetalleVenta accionesDetalleVenta;
    private final AccionClientes accionesClientes;
    private final AccionDescuentos accionesDescuentos;
    private Venta venta;
    private DetalleVenta detalleVenta;
    private List<Producto> listaDeProductos;
    private List<DetalleVenta> listaDeDetalleVentas;
    private List<Categoria> listaDeCategorias;
    private List<Producto> listaPrecioProducto;
    private int idCategoria;
    private ArrayList<JLabel> arrayListLabelsCategoria;
    private ArrayList<JLabel> arrayListLabelsProductos;
    private DefaultTableModel tablaPedido;
    private static final String[] NOMBRE_COLUMNAS_TABLA = {"Cantidad","Nombre producto","Precio €"};
    private float precioTotal;
    private int nVenta;
    private DecimalFormat formatoDecimales;
    private boolean descuentoAplicado = false;
    private int posicionSeleccion = 0;
    
    /**
     * Creates new form PanelVentas
     * @param frame
     */
    public PantallaTPV(FFCJFrame frame) {
        initComponents();
        this.accionActualizarHora = new ActionListener() {
            
            @Override
            public void actionPerformed(ActionEvent ae) {
                txtHora.setText(formatoHora.format(new Date()));
            }
        };
        this.frame = frame;
        this.txtFecha.setText(formatoFecha.format(new Date()));
        this.temporizador = new Timer(1000, accionActualizarHora);
        this.temporizador.start();
        this.accionesProductos = new AccionProductos();
        this.accionesCategorias = new AccionCategorias();
        this.accionesCategoriaProducto = new AccionCategoriaProducto();
        this.accionesVentas = new AccionVentas();
        this.accionesDetalleVenta = new AccionDetalleVenta();
        this.accionesClientes = new AccionClientes();
        this.accionesDescuentos = new AccionDescuentos();
        this.nVenta = this.accionesVentas.obtenerUltimoNumeroDeVenta() + 1;
        this.txtNTicket.setText(String.valueOf(this.nVenta));
        this.arrayListLabelsCategoria = new ArrayList();
        this.listaDeDetalleVentas = new ArrayList<DetalleVenta>();
        this.listaDeCategorias = this.accionesCategorias.listarTodas();
        this.listaPrecioProducto  = new ArrayList();
        this.cargarEtiquetasCategoria();
        this.cargarEtiquetasProductos(this.listaDeCategorias.get(0).getId());
        this.tablaPedido = (new DefaultTableModel(NOMBRE_COLUMNAS_TABLA,0){
            Class[] types = new Class [] {
                java.lang.Integer.class, java.lang.String.class, java.lang.Integer.class
            };
            boolean[] canEdit = new boolean [] {
                true, false, false
            };

            @Override
            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            @Override
            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        this.precioTotal = 0;
        this.btnFinalizar.setEnabled(false);
        this.formatoDecimales = new DecimalFormat("#.00");
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        pnlSuperior = new javax.swing.JPanel();
        lblNTicket = new javax.swing.JLabel();
        txtNTicket = new javax.swing.JTextField();
        rdbClienteHabitual = new javax.swing.JRadioButton();
        idCliente = new javax.swing.JLabel();
        txtIdCliente = new javax.swing.JTextField();
        lbClientelHabitual = new javax.swing.JLabel();
        txtNumeroDescuento = new javax.swing.JTextField();
        btnAplicarDescuento = new javax.swing.JButton();
        jLabel1 = new javax.swing.JLabel();
        txtFecha = new javax.swing.JTextField();
        lblHora = new javax.swing.JLabel();
        txtHora = new javax.swing.JTextField();
        pnlIzquierdo = new javax.swing.JPanel();
        tblTicket = new javax.swing.JScrollPane();
        tblPedido = new javax.swing.JTable();
        pnlNumeros = new javax.swing.JPanel();
        btnSiete = new javax.swing.JButton();
        btnOcho = new javax.swing.JButton();
        btnNueve = new javax.swing.JButton();
        btnCuatro = new javax.swing.JButton();
        btnCinco = new javax.swing.JButton();
        btnSeis = new javax.swing.JButton();
        btnUno = new javax.swing.JButton();
        btnDos = new javax.swing.JButton();
        btnTres = new javax.swing.JButton();
        btnC = new javax.swing.JButton();
        btnCero = new javax.swing.JButton();
        btnPunto = new javax.swing.JButton();
        pnlNavegar = new javax.swing.JPanel();
        btnArriba = new javax.swing.JButton();
        btnEliminar = new javax.swing.JButton();
        btnAbajo = new javax.swing.JButton();
        pnlTotal = new javax.swing.JPanel();
        lblTotal = new javax.swing.JLabel();
        txtTotal = new javax.swing.JTextField();
        btnFinalizar = new javax.swing.JButton();
        jLabel2 = new javax.swing.JLabel();
        pnlDerecho = new javax.swing.JPanel();
        pnlCategorias = new javax.swing.JPanel();
        pnlInferior = new javax.swing.JPanel();
        lblAvíso = new javax.swing.JLabel();
        pnlCentral = new javax.swing.JPanel();
        pnlProductos = new javax.swing.JPanel();

        setPreferredSize(new java.awt.Dimension(800, 600));
        setLayout(new java.awt.BorderLayout(5, 5));

        java.awt.FlowLayout flowLayout1 = new java.awt.FlowLayout(java.awt.FlowLayout.LEFT);
        flowLayout1.setAlignOnBaseline(true);
        pnlSuperior.setLayout(flowLayout1);

        lblNTicket.setText("Nº de Ticket :");
        pnlSuperior.add(lblNTicket);

        txtNTicket.setEditable(false);
        txtNTicket.setFocusable(false);
        txtNTicket.setPreferredSize(new java.awt.Dimension(25, 20));
        pnlSuperior.add(txtNTicket);

        rdbClienteHabitual.setText("Cliente Habitual");
        rdbClienteHabitual.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                rdbClienteHabitualActionPerformed(evt);
            }
        });
        pnlSuperior.add(rdbClienteHabitual);

        idCliente.setText("IDCliente :");
        pnlSuperior.add(idCliente);

        txtIdCliente.setEditable(false);
        txtIdCliente.setPreferredSize(new java.awt.Dimension(20, 20));
        pnlSuperior.add(txtIdCliente);

        lbClientelHabitual.setText("Nº Descuento :");
        pnlSuperior.add(lbClientelHabitual);

        txtNumeroDescuento.setEditable(false);
        txtNumeroDescuento.setPreferredSize(new java.awt.Dimension(20, 20));
        pnlSuperior.add(txtNumeroDescuento);

        btnAplicarDescuento.setText("Aplicar Descuento");
        btnAplicarDescuento.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAplicarDescuentoActionPerformed(evt);
            }
        });
        pnlSuperior.add(btnAplicarDescuento);

        jLabel1.setText("Fecha :");
        pnlSuperior.add(jLabel1);

        txtFecha.setEditable(false);
        txtFecha.setHorizontalAlignment(javax.swing.JTextField.CENTER);
        txtFecha.setFocusable(false);
        txtFecha.setPreferredSize(new java.awt.Dimension(50, 20));
        pnlSuperior.add(txtFecha);

        lblHora.setText("Hora :");
        pnlSuperior.add(lblHora);

        txtHora.setEditable(false);
        txtHora.setHorizontalAlignment(javax.swing.JTextField.CENTER);
        txtHora.setPreferredSize(new java.awt.Dimension(53, 20));
        pnlSuperior.add(txtHora);

        add(pnlSuperior, java.awt.BorderLayout.NORTH);

        tblPedido.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Cantidad", "Descripción", "Precio"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.Integer.class, java.lang.String.class, java.lang.Integer.class
            };
            boolean[] canEdit = new boolean [] {
                true, false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        tblTicket.setViewportView(tblPedido);

        pnlNumeros.setLayout(new java.awt.GridLayout(4, 3, 5, 5));

        btnSiete.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnSiete.setText("7");
        btnSiete.setToolTipText("Funcionalidad no implementada");
        btnSiete.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSieteActionPerformed(evt);
            }
        });
        pnlNumeros.add(btnSiete);

        btnOcho.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnOcho.setText("8");
        btnOcho.setToolTipText("Funcionalidad no implementada");
        btnOcho.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnOchoActionPerformed(evt);
            }
        });
        pnlNumeros.add(btnOcho);

        btnNueve.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnNueve.setText("9");
        btnNueve.setToolTipText("Funcionalidad no implementada");
        btnNueve.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnNueveActionPerformed(evt);
            }
        });
        pnlNumeros.add(btnNueve);

        btnCuatro.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnCuatro.setText("4");
        btnCuatro.setToolTipText("Funcionalidad no implementada");
        btnCuatro.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnCuatroActionPerformed(evt);
            }
        });
        pnlNumeros.add(btnCuatro);

        btnCinco.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnCinco.setText("5");
        btnCinco.setToolTipText("Funcionalidad no implementada");
        btnCinco.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnCincoActionPerformed(evt);
            }
        });
        pnlNumeros.add(btnCinco);

        btnSeis.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnSeis.setText("6");
        btnSeis.setToolTipText("Funcionalidad no implementada");
        btnSeis.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSeisActionPerformed(evt);
            }
        });
        pnlNumeros.add(btnSeis);

        btnUno.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnUno.setText("1");
        btnUno.setToolTipText("Funcionalidad no implementada");
        btnUno.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnUnoActionPerformed(evt);
            }
        });
        pnlNumeros.add(btnUno);

        btnDos.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnDos.setText("2");
        btnDos.setToolTipText("Funcionalidad no implementada");
        btnDos.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnDosActionPerformed(evt);
            }
        });
        pnlNumeros.add(btnDos);

        btnTres.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnTres.setText("3");
        btnTres.setToolTipText("Funcionalidad no implementada");
        btnTres.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnTresActionPerformed(evt);
            }
        });
        pnlNumeros.add(btnTres);

        btnC.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnC.setText("C");
        btnC.setToolTipText("Funcionalidad no implementada");
        pnlNumeros.add(btnC);

        btnCero.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnCero.setText("0");
        btnCero.setToolTipText("Funcionalidad no implementada");
        pnlNumeros.add(btnCero);

        btnPunto.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnPunto.setText(".");
        btnPunto.setToolTipText("Funcionalidad no implementada");
        btnPunto.setEnabled(false);
        pnlNumeros.add(btnPunto);

        pnlNavegar.setLayout(new java.awt.GridLayout(0, 1));

        btnArriba.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnArriba.setIcon(new javax.swing.ImageIcon(getClass().getResource("/img/FlechaArriba.png"))); // NOI18N
        btnArriba.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnArribaActionPerformed(evt);
            }
        });
        pnlNavegar.add(btnArriba);

        btnEliminar.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnEliminar.setIcon(new javax.swing.ImageIcon(getClass().getResource("/img/waste-bin.png"))); // NOI18N
        btnEliminar.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnEliminarActionPerformed(evt);
            }
        });
        pnlNavegar.add(btnEliminar);

        btnAbajo.setFont(new java.awt.Font("Tahoma", 1, 36)); // NOI18N
        btnAbajo.setIcon(new javax.swing.ImageIcon(getClass().getResource("/img/FlechaAbajo.png"))); // NOI18N
        btnAbajo.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAbajoActionPerformed(evt);
            }
        });
        pnlNavegar.add(btnAbajo);

        lblTotal.setText("TOTAL :");

        txtTotal.setEditable(false);
        txtTotal.setHorizontalAlignment(javax.swing.JTextField.RIGHT);

        btnFinalizar.setText("Finalizar pedido");
        btnFinalizar.setEnabled(false);
        btnFinalizar.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnFinalizarActionPerformed(evt);
            }
        });

        jLabel2.setText("  €");

        javax.swing.GroupLayout pnlTotalLayout = new javax.swing.GroupLayout(pnlTotal);
        pnlTotal.setLayout(pnlTotalLayout);
        pnlTotalLayout.setHorizontalGroup(
            pnlTotalLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, pnlTotalLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(pnlTotalLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(btnFinalizar, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addGroup(pnlTotalLayout.createSequentialGroup()
                        .addComponent(lblTotal, javax.swing.GroupLayout.PREFERRED_SIZE, 48, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(txtTotal)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jLabel2, javax.swing.GroupLayout.PREFERRED_SIZE, 14, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap())
        );
        pnlTotalLayout.setVerticalGroup(
            pnlTotalLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(pnlTotalLayout.createSequentialGroup()
                .addGroup(pnlTotalLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(lblTotal, javax.swing.GroupLayout.PREFERRED_SIZE, 25, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(txtTotal, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jLabel2))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(btnFinalizar, javax.swing.GroupLayout.DEFAULT_SIZE, 34, Short.MAX_VALUE))
        );

        javax.swing.GroupLayout pnlIzquierdoLayout = new javax.swing.GroupLayout(pnlIzquierdo);
        pnlIzquierdo.setLayout(pnlIzquierdoLayout);
        pnlIzquierdoLayout.setHorizontalGroup(
            pnlIzquierdoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(pnlIzquierdoLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(pnlIzquierdoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(tblTicket, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                    .addComponent(pnlTotal, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, pnlIzquierdoLayout.createSequentialGroup()
                        .addGap(0, 0, Short.MAX_VALUE)
                        .addComponent(pnlNumeros, javax.swing.GroupLayout.PREFERRED_SIZE, 193, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(pnlNavegar, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap())
        );
        pnlIzquierdoLayout.setVerticalGroup(
            pnlIzquierdoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(pnlIzquierdoLayout.createSequentialGroup()
                .addComponent(tblTicket, javax.swing.GroupLayout.PREFERRED_SIZE, 92, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(pnlTotal, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(pnlIzquierdoLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(pnlNumeros, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(pnlNavegar, javax.swing.GroupLayout.PREFERRED_SIZE, 271, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap(67, Short.MAX_VALUE))
        );

        add(pnlIzquierdo, java.awt.BorderLayout.WEST);

        pnlDerecho.setPreferredSize(new java.awt.Dimension(175, 491));
        pnlDerecho.setLayout(new java.awt.BorderLayout());

        pnlCategorias.setBorder(javax.swing.BorderFactory.createTitledBorder("Selección de categoría"));
        pnlCategorias.setPreferredSize(new java.awt.Dimension(175, 491));
        pnlDerecho.add(pnlCategorias, java.awt.BorderLayout.CENTER);

        add(pnlDerecho, java.awt.BorderLayout.EAST);

        pnlInferior.setPreferredSize(new java.awt.Dimension(1066, 50));
        pnlInferior.setLayout(new java.awt.CardLayout());

        lblAvíso.setBorder(javax.swing.BorderFactory.createTitledBorder("Información"));
        pnlInferior.add(lblAvíso, "card2");

        add(pnlInferior, java.awt.BorderLayout.SOUTH);

        pnlCentral.setPreferredSize(new java.awt.Dimension(281, 491));
        pnlCentral.setLayout(new java.awt.BorderLayout());

        pnlProductos.setBorder(javax.swing.BorderFactory.createTitledBorder("Selección de Productos"));
        pnlProductos.setCursor(new java.awt.Cursor(java.awt.Cursor.DEFAULT_CURSOR));
        pnlProductos.setPreferredSize(new java.awt.Dimension(281, 491));
        pnlCentral.add(pnlProductos, java.awt.BorderLayout.CENTER);

        add(pnlCentral, java.awt.BorderLayout.CENTER);
    }// </editor-fold>//GEN-END:initComponents

    private void btnFinalizarActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnFinalizarActionPerformed
        this.establecerVenta();
        this.accionesVentas.insertar();
        this.insertarVentaDetalle();
        this.nVenta = this.nVenta + 1;
        this.txtNTicket.setText(String.valueOf(this.nVenta));
        this.txtIdCliente.setText("");
        this.txtNumeroDescuento.setText("");
        this.txtTotal.setText("");
        this.precioTotal = 0;
        this.vaciarTablaPedido();
        this.descuentoAplicado = false;
        this.btnFinalizar.setEnabled(false);
    }//GEN-LAST:event_btnFinalizarActionPerformed

    private void btnAplicarDescuentoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnAplicarDescuentoActionPerformed
        this.aplicarDescuento();
        this.txtNumeroDescuento.setText("");
        this.txtIdCliente.setText("");
        this.txtIdCliente.setEditable(false);
        this.txtNumeroDescuento.setEditable(false);
        this.rdbClienteHabitual.setSelected(false);
    }//GEN-LAST:event_btnAplicarDescuentoActionPerformed

    private void btnEliminarActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnEliminarActionPerformed
        int[] filasSeleccionadas = this.tblPedido.getSelectedRows();
        if (filasSeleccionadas.length > 0) {
            this.eliminarProductosPedido(filasSeleccionadas);
            this.txtTotal.setText(String.valueOf(this.formatoDecimales.format(this.precioTotal)));
            if (this.precioTotal != 0) {
                this.btnFinalizar.setEnabled(true);
            }
        }
        
    }//GEN-LAST:event_btnEliminarActionPerformed

    private void btnArribaActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnArribaActionPerformed
        int numerofilas = this.tblPedido.getRowCount();
        if (numerofilas > 0) {
            int[] filasSeleccionadas = this.tblPedido.getSelectedRows();
            if (filasSeleccionadas.length > 0) {
                int indiceFila = filasSeleccionadas.length - 1;
                this.posicionSeleccion = filasSeleccionadas[indiceFila] - 1;
                if (this.posicionSeleccion >= 0) {
                    this.tblPedido.setRowSelectionInterval(this.posicionSeleccion, this.posicionSeleccion);
                }
            } else {
                this.posicionSeleccion = numerofilas - 1;
                this.tblPedido.setRowSelectionInterval(this.posicionSeleccion, this.posicionSeleccion);
            }
        }
    }//GEN-LAST:event_btnArribaActionPerformed

    private void btnAbajoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnAbajoActionPerformed
        int numerofilas = this.tblPedido.getRowCount();
        if (numerofilas > 0) {
            int[] filasSeleccionadas = this.tblPedido.getSelectedRows();
            if (filasSeleccionadas.length > 0) {
                int indiceFila = filasSeleccionadas.length - 1;
                this.posicionSeleccion = filasSeleccionadas[indiceFila] + 1;
                if (this.posicionSeleccion < numerofilas) {
                    this.tblPedido.setRowSelectionInterval(this.posicionSeleccion, this.posicionSeleccion);
                }
            } else {
                this.posicionSeleccion = 0;
                this.tblPedido.setRowSelectionInterval(this.posicionSeleccion, this.posicionSeleccion);
            }
        }
    }//GEN-LAST:event_btnAbajoActionPerformed

    private void rdbClienteHabitualActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_rdbClienteHabitualActionPerformed
        if (!this.rdbClienteHabitual.isSelected()) {
            this.txtNumeroDescuento.setEditable(false);
            this.txtIdCliente.setEditable(false);
        } else {
            this.txtIdCliente.setEditable(true);
            this.txtNumeroDescuento.setEditable(true);
        }
    }//GEN-LAST:event_rdbClienteHabitualActionPerformed

    private void btnUnoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnUnoActionPerformed
        this.cambiarCantidad(1);
    }//GEN-LAST:event_btnUnoActionPerformed

    private void btnDosActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnDosActionPerformed
        this.cambiarCantidad(2);
    }//GEN-LAST:event_btnDosActionPerformed

    private void btnTresActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnTresActionPerformed
        this.cambiarCantidad(3);
    }//GEN-LAST:event_btnTresActionPerformed

    private void btnCuatroActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnCuatroActionPerformed
        this.cambiarCantidad(4);
    }//GEN-LAST:event_btnCuatroActionPerformed

    private void btnCincoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnCincoActionPerformed
        this.cambiarCantidad(5);
    }//GEN-LAST:event_btnCincoActionPerformed

    private void btnSeisActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnSeisActionPerformed
        this.cambiarCantidad(6);
    }//GEN-LAST:event_btnSeisActionPerformed

    private void btnSieteActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnSieteActionPerformed
        this.cambiarCantidad(7);
    }//GEN-LAST:event_btnSieteActionPerformed

    private void btnOchoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnOchoActionPerformed
        this.cambiarCantidad(8);
    }//GEN-LAST:event_btnOchoActionPerformed

    private void btnNueveActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnNueveActionPerformed
        this.cambiarCantidad(9);
    }//GEN-LAST:event_btnNueveActionPerformed

    private void lblCategoriaMouseClicked(java.awt.event.MouseEvent evt) {
        int etiquetClicada = this.arrayListLabelsCategoria.indexOf(evt.getComponent());
        this.cargarEtiquetasProductos(this.listaDeCategorias.get(etiquetClicada).getId());
    }
    
    private void lblProductoMouseClicked(java.awt.event.MouseEvent evt) {                                        
        int etiquetClicada = this.arrayListLabelsProductos.indexOf(evt.getComponent());
        this.insertarProductoPedido(etiquetClicada);
    }
   
    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnAbajo;
    private javax.swing.JButton btnAplicarDescuento;
    private javax.swing.JButton btnArriba;
    private javax.swing.JButton btnC;
    private javax.swing.JButton btnCero;
    private javax.swing.JButton btnCinco;
    private javax.swing.JButton btnCuatro;
    private javax.swing.JButton btnDos;
    private javax.swing.JButton btnEliminar;
    private javax.swing.JButton btnFinalizar;
    private javax.swing.JButton btnNueve;
    private javax.swing.JButton btnOcho;
    private javax.swing.JButton btnPunto;
    private javax.swing.JButton btnSeis;
    private javax.swing.JButton btnSiete;
    private javax.swing.JButton btnTres;
    private javax.swing.JButton btnUno;
    private javax.swing.JLabel idCliente;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel lbClientelHabitual;
    private javax.swing.JLabel lblAvíso;
    private javax.swing.JLabel lblHora;
    private javax.swing.JLabel lblNTicket;
    private javax.swing.JLabel lblTotal;
    private javax.swing.JPanel pnlCategorias;
    private javax.swing.JPanel pnlCentral;
    private javax.swing.JPanel pnlDerecho;
    private javax.swing.JPanel pnlInferior;
    private javax.swing.JPanel pnlIzquierdo;
    private javax.swing.JPanel pnlNavegar;
    private javax.swing.JPanel pnlNumeros;
    private javax.swing.JPanel pnlProductos;
    private javax.swing.JPanel pnlSuperior;
    private javax.swing.JPanel pnlTotal;
    private javax.swing.JRadioButton rdbClienteHabitual;
    private javax.swing.JTable tblPedido;
    private javax.swing.JScrollPane tblTicket;
    private javax.swing.JTextField txtFecha;
    private javax.swing.JTextField txtHora;
    private javax.swing.JTextField txtIdCliente;
    private javax.swing.JTextField txtNTicket;
    private javax.swing.JTextField txtNumeroDescuento;
    private javax.swing.JTextField txtTotal;
    // End of variables declaration//GEN-END:variables

    private void cargarEtiquetasCategoria(){
        int i = 0;
        ArrayList<Categoria> categorias = new ArrayList(this.listaDeCategorias);
        Iterator<Categoria> iteradorCategorias = categorias.iterator();
        this.pnlCategorias.setLayout(new FlowLayout(FlowLayout.LEFT));
        while (iteradorCategorias.hasNext()) {
            Categoria categoria = iteradorCategorias.next();
            this.idCategoria = categoria.getId();
            Image imageLabelCategoria = new ImageIcon(this.frame.getRutaImagenes() + categoria.getImagen()).getImage();
            ImageIcon imageIconCategoria = new ImageIcon(imageLabelCategoria.getScaledInstance(80, 80, Image.SCALE_SMOOTH));
            this.arrayListLabelsCategoria.add(new JLabel(imageIconCategoria));
            this.arrayListLabelsCategoria.get(i).addMouseListener(new java.awt.event.MouseAdapter() {
                @Override
                public void mouseClicked(java.awt.event.MouseEvent evt) {
                    lblCategoriaMouseClicked(evt);
                }
            });
            this.arrayListLabelsCategoria.get(i).setHorizontalTextPosition(CENTER);
            this.arrayListLabelsCategoria.get(i).setVerticalTextPosition(BOTTOM);
            this.arrayListLabelsCategoria.get(i).setText(categoria.getNombre());
            this.arrayListLabelsCategoria.get(i).setVisible(true);
            this.pnlCategorias.add(this.arrayListLabelsCategoria.get(i));
            i++;
        }
    }
    
    private void cargarEtiquetasProductos(int idCategoria){
        if (this.arrayListLabelsProductos == null) {
            this.arrayListLabelsProductos = new ArrayList();
        }
        if (!this.arrayListLabelsProductos.isEmpty()) {
            this.arrayListLabelsProductos.removeAll(this.arrayListLabelsProductos);
            this.pnlProductos.removeAll();
            this.pnlCentral.add(pnlProductos, java.awt.BorderLayout.CENTER);
            this.add(pnlCentral, java.awt.BorderLayout.CENTER);
        }
        int i = 0;
        this.listaDeProductos = this.accionesCategoriaProducto.listarProductos(idCategoria);
        ArrayList<Producto> productos = new ArrayList(this.listaDeProductos);
        Iterator<Producto> iteradorProductos = productos.iterator();
        this.pnlProductos.setLayout(new FlowLayout(FlowLayout.LEFT));
        while (iteradorProductos.hasNext()) {
            Producto producto = iteradorProductos.next();
            Image imageLabelProducto = new ImageIcon(this.frame.getRutaImagenes() + producto.getImagen()).getImage();
            ImageIcon imageIconProducto = new ImageIcon(imageLabelProducto.getScaledInstance(80, 80, Image.SCALE_SMOOTH));
            this.arrayListLabelsProductos.add(new JLabel(imageIconProducto));
            this.arrayListLabelsProductos.get(i).addMouseListener(new java.awt.event.MouseAdapter() {
                @Override
                public void mouseClicked(java.awt.event.MouseEvent evt) {
                    lblProductoMouseClicked(evt);
                }
            });
            this.arrayListLabelsProductos.get(i).setHorizontalTextPosition(CENTER);
            this.arrayListLabelsProductos.get(i).setVerticalTextPosition(BOTTOM);
            this.arrayListLabelsProductos.get(i).setText(producto.getNombre());
            this.arrayListLabelsProductos.get(i).setVisible(true);
            this.pnlProductos.add(this.arrayListLabelsProductos.get(i));
            this.pnlProductos.updateUI();
            i++;
        }
    }
    
    private void insertarProductoPedido(int indiceProducto){
        float precioProducto = this.listaDeProductos.get(indiceProducto).getPrecio();
        Vector filaTabla = new Vector(NOMBRE_COLUMNAS_TABLA.length);
        filaTabla.add(1);
        filaTabla.add(this.listaDeProductos.get(indiceProducto).getNombre());
        filaTabla.add(this.formatoDecimales.format(precioProducto));
        this.detalleVenta = new DetalleVenta(this.nVenta, 
                this.listaDeProductos.get(indiceProducto).getId(), 1, this.listaDeProductos.get(indiceProducto).getPrecio());
        this.listaPrecioProducto.add(this.listaDeProductos.get(indiceProducto));
        this.listaDeDetalleVentas.add(this.detalleVenta);
        this.tablaPedido.addRow(filaTabla);
        this.tblPedido.setModel(this.tablaPedido);
        this.tblPedido.getModel().addTableModelListener(new TableModelListener() {

            @Override
            public void tableChanged(TableModelEvent evt) {
                multiplicarCantidad(evt);
            }
        });
        this.tblTicket.setViewportView(this.tblPedido);
        this.precioTotal = this.precioTotal + precioProducto;
        this.txtTotal.setText(String.valueOf(this.formatoDecimales.format(this.precioTotal)));
        if (this.precioTotal != 0) {
            this.btnFinalizar.setEnabled(true);
        }
    }
    
    private void eliminarProductosPedido(int[] filasSelecionadas){
        int arrayIndex = filasSelecionadas.length - 1;
        while (arrayIndex >= 0) {
            int listIndex = filasSelecionadas[arrayIndex];
            DetalleVenta eliminarDetalleVenta = this.listaDeDetalleVentas.remove(listIndex);
            this.listaPrecioProducto.remove(listIndex);
            this.tablaPedido.removeRow(listIndex);
            this.precioTotal = this.precioTotal - eliminarDetalleVenta.getPrecioVenta();
            arrayIndex--;
        }
    }
    
    private void vaciarTablaPedido(){
        int i = this.tablaPedido.getRowCount();
        while (i >= 1) {
            i--;
            this.tablaPedido.removeRow(i);
        }
    }
    
     private boolean camposTiposCorrectos(){
        if (this.esNumero(txtIdCliente.getText())) {
            return true;
        } else {
            JOptionPane.showMessageDialog(null, "El campo idCliente debe ser numeros"
            , "Atención",JOptionPane.WARNING_MESSAGE);
            return false;
        }
    }
      
    private boolean esNumero(String texto){
        try {
            Integer.parseInt(texto);
            return true;
        } catch (Exception ex) {
            return false;
        }
    }
    
    private boolean existeCliente(){
        if (txtIdCliente.getText().isEmpty()) {
            txtIdCliente.setText("0");
        }
        if (camposTiposCorrectos()){
            return this.accionesClientes.buscarID(Integer.parseInt(this.txtIdCliente.getText()));
        }
        return false;
    }
    
    private void establecerVenta(){
        if (!this.existeCliente()) {
                this.venta = new Venta(this.precioTotal);
        } else {
                this.venta = new Venta(this.precioTotal,Integer.parseInt(this.txtIdCliente.getText()));
        }
        this.accionesVentas.establecer(this.venta);
    }
    
    private void insertarVentaDetalle(){
        if (this.existeDetalle()) {
            Iterator<DetalleVenta> iteradorDetalleVentas = this.listaDeDetalleVentas.iterator();
            while (iteradorDetalleVentas.hasNext()) {
                this.accionesDetalleVenta.establecer(iteradorDetalleVentas.next());
                this.accionesDetalleVenta.insertar();
            }
        }
    }
    
    private boolean existeDetalle(){
        if (this.listaDeDetalleVentas.isEmpty()) {
            JOptionPane.showMessageDialog(null, "No hay productos en el pedido inserta"
            , "Atención",JOptionPane.WARNING_MESSAGE);
            return false;
        } else  {
            return true;
        }
    }
    
    private void aplicarDescuento(){
        String clave = this.txtNumeroDescuento.getText();
        String idStringCliente = this.txtIdCliente.getText();
        if (!this.listaDeDetalleVentas.isEmpty() && !clave.isEmpty() && !idStringCliente.isEmpty()) {
            int idIntCliente = Integer.parseInt(idStringCliente);
            if (this.accionesDescuentos.esDescuentoCliente(clave, idIntCliente) && this.descuentoAplicado == false) {
                Descuento descuento = this.accionesDescuentos.obtenerDescuento(clave);
                float cantidadDescuento = descuento.getCantidad();
                float porcentajeDescuento = cantidadDescuento / 100;
                float totalDescuento = (1 - porcentajeDescuento) * this.precioTotal;
                this.precioTotal = totalDescuento;
                this.txtTotal.setText(this.formatoDecimales.format(this.precioTotal));
                this.descuentoAplicado = true;
            } else {
                JOptionPane.showMessageDialog(null, "El descuento no existe en la base de datos o es para otro cliente", ""
                    + "Atención",JOptionPane.WARNING_MESSAGE);
            }
        }
    }
    
    private void multiplicarCantidad(TableModelEvent evt){
        if (evt.getType() == TableModelEvent.UPDATE) {
            TableModel modelo = ((TableModel) (evt.getSource()));
            int fila = evt.getFirstRow();
            int columna = evt.getColumn();
            if (columna == 0) {
                int cantidad = Integer.parseInt(modelo.getValueAt(fila,columna).toString());
                float precioProducto = this.listaPrecioProducto.get(fila).getPrecio();
                float precio = cantidad * precioProducto;
                this.listaDeDetalleVentas.get(fila).setPrecioVenta(precio);
                 this.listaDeDetalleVentas.get(fila).setCantidad(cantidad);
                modelo.setValueAt(this.formatoDecimales.format(precio),fila, 2);
                int nFilas = modelo.getRowCount();
                this.precioTotal = 0;
                for (int i = 0; i < nFilas; i++) {
                    float precioVenta = Float.parseFloat(modelo.getValueAt(i, 2).toString().replace(",", "."));
                    this.precioTotal = this.precioTotal + precioVenta;
                }
                this.txtTotal.setText(this.formatoDecimales.format(this.precioTotal));
            }
        }
    }
    
    private void cambiarCantidad(int numero){
        int numerofilas = this.tblPedido.getRowCount();
        if (numerofilas > 0) {
            int[] filasSeleccionadas = this.tblPedido.getSelectedRows();
            if (filasSeleccionadas.length > 0) {
                int indiceFila = filasSeleccionadas.length - 1;
                this.posicionSeleccion = filasSeleccionadas[indiceFila];
                this.tblPedido.setRowSelectionInterval(this.posicionSeleccion, this.posicionSeleccion);
                this.tblPedido.setValueAt(numero, this.posicionSeleccion, 0);
            } else {
                this.posicionSeleccion = 0;
                this.tblPedido.setRowSelectionInterval(this.posicionSeleccion, this.posicionSeleccion);
                this.tblPedido.setValueAt(numero, this.posicionSeleccion, 0);
            }
        }
    }
}
