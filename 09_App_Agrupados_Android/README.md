# 09. App Agrupados (Android Nativo)

La contraparte móvil (App) de la plataforma Agrupados, permitiendo a los usuarios consumir los servicios nativamente desde sus smartphones.

## 🎯 Contexto del Negocio
Para que un portal de ofertas sea exitoso, la principal vía de interacción de los clientes debe ser a través del móvil. Se requería una aplicación nativa que aprovechara las características del hardware del dispositivo (GPS, Localización) para mostrar las ofertas más relevantes cercanas al usuario.

## 🛠️ Arquitectura y Stack
*   **Lenguaje:** Java para Android (Android SDK).
*   **Interfaz:** XML Layouts, Material Design.
*   **Servicios:** Consumo de APIs y Google Maps API para Android.

## 🧠 Retos Técnicos
*   **Ciclo de Vida (Activities/Fragments):** Gestionar eficientemente la memoria y los cambios de estado (como la rotación de pantalla o paso a segundo plano) sin perder la información del usuario.
*   **Consumo Asíncrono de APIs:** Realizar peticiones de red fuera del Hilo Principal (Main/UI Thread) mediante procesos en segundo plano para evitar bloqueos (ANR) en la interfaz gráfica.
*   **Mapas y Geolocalización:** Implementar la solicitud de permisos en tiempo de ejecución (Location) de forma segura y renderizar fragmentos de mapas interactivos.

## 📈 Impacto y Resultados
*   *(Sección en edición)* Expansión del ecosistema al canal móvil, demostrando capacidad para desarrollar software integral end-to-end.
