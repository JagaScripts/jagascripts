package es.jaga.webagrupados.filters;

import es.jaga.webagrupados.controller.beans.UserBean;
import java.io.IOException;
import javax.inject.Inject;
import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.annotation.WebFilter;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Clase que capturará las peticiones antes de servirlas para permitir o denegar
 * accesos basándonos en roles.
 *
 * @author Jose Antonio González Alcántara
 */
@WebFilter(filterName = "loginFilter", urlPatterns = {"/*"})
public class LoginFilter implements Filter {
    
    @Inject
    private UserBean userBean;
    private FilterConfig config;

    /**
     * Método de inicialización del filtro.
     *
     * @param filterConfig FilterConfig objeto con la configuración del filtro.
     * @throws ServletException Excepción lanzada en caso de fallo en el
     * servlet.
     */
    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
        config = filterConfig;
    }

    /**
     * Método que implementa el filtrado operando sobre las peticiones y
     * respuestas.
     *
     * @param request HttpServletRequest petición.
     * @param response HttpServletResponse respuesta.
     * @param chain FilterChain cadena/secuencia de filtros.
     * @throws IOException Excepción de escritura/lectura.
     * @throws ServletException Excepción de servlet.
     */
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        String uri = ((HttpServletRequest) request).getRequestURI();
        String contextPath = ((HttpServletRequest) request).getContextPath();
        if (!userBean.isAdmin() && uri.contains("/administrator/")) {
            ((HttpServletResponse) response).sendRedirect(contextPath + "/faces/error/401.xhtml");
        } else if ((!userBean.isRegisteredUser() && !userBean.isAdmin() && !userBean.isBusiness()) && uri.contains("/client/")) {
            ((HttpServletResponse) response).sendRedirect(contextPath + "/faces/error/401.xhtml");
        } else if ((!userBean.isAdmin() && !userBean.isBusiness()) && uri.contains("/business/")) {
            ((HttpServletResponse) response).sendRedirect(contextPath + "/faces/error/401.xhtml");
        }
        chain.doFilter(request, response);
    }

    /**
     * Método que destruye el filtro.
     */
    @Override
    public void destroy() {
    }
    
    
}
