# Manual de Usuario — Prodify

---

## 1. Introducción

Prodify es una aplicación web de gestión de proyectos basada en tableros Kanban. Permite organizar tareas en columnas visuales, colaborar con otros usuarios a través de espacios de trabajo compartidos y hacer seguimiento de toda la actividad del equipo.

**Para qué sirve:**
- Crear espacios de trabajo y tableros para organizar proyectos.
- Dividir el trabajo en columnas (fases) y tarjetas (tareas individuales).
- Invitar a compañeros y asignarles un nivel de acceso.
- Consultar el historial de lo que ha ocurrido en cada proyecto.
- Empezar rápidamente usando una de las 24 plantillas incluidas.

**A quién va dirigido:**
A cualquier persona o equipo que quiera organizar proyectos de forma visual sin necesidad de instalar ningún programa.

---

## 2. Acceso y requisitos

**Requisitos:**
- Un navegador web actualizado (Chrome, Firefox, Edge o Safari).
- Una cuenta registrada en la plataforma.
- Conexión a internet.

No hay que instalar nada. Todo funciona desde el navegador.

**Dirección de acceso:**
Abre el navegador y escribe la dirección que te haya facilitado el administrador de la plataforma.

---

## 3. Descripción de la interfaz

Una vez dentro, la pantalla se divide en tres zonas:

**Barra superior**
Siempre visible en la parte de arriba. Contiene el logo de la aplicación, un campo de búsqueda, el botón Crear, el interruptor de tema oscuro/claro y el avatar con el menú de tu cuenta.

**Barra lateral izquierda**
Muestra los enlaces a las secciones principales: Inicio, Mis tableros, Plantillas, Perfil, Actividad, Tarjetas, Ajustes y Ayuda. Debajo aparecen los espacios de trabajo a los que tienes acceso.

**Zona central**
Es el área principal donde se muestra el contenido de cada sección: el listado de tableros, el tablero Kanban, el catálogo de plantillas, etc.

---

## 4. Funcionalidades

### 4.1 Crear una cuenta

1. Abre la aplicación en el navegador. Aparecerá la pantalla de inicio de sesión.
2. Haz clic en el enlace **Crear cuenta**.
3. Rellena el formulario:
   - **Nombre de usuario** *(opcional)*: el nombre que verán los demás. Si lo dejas vacío, se usará la parte de tu correo antes de la arroba.
   - **Correo electrónico** *(obligatorio)*: dirección válida.
   - **Contraseña** *(obligatoria)*: mínimo 8 caracteres, y debe incluir al menos una letra mayúscula, una minúscula, un número y un carácter especial (por ejemplo: `Proyecto1!`).
   - **Confirmar contraseña** *(obligatoria)*: escribe la misma contraseña otra vez.
   - **Idioma**: elige en qué idioma quieres usar la aplicación.
4. Pulsa **Registrarse**.
5. Recibirás un correo de bienvenida. Tu cuenta queda activada automáticamente.

> Si introduces más de 5 veces datos incorrectos en el registro, el sistema te bloqueará temporalmente durante unos minutos.

---

### 4.2 Iniciar sesión

1. Introduce tu correo electrónico y contraseña.
2. Pulsa **Iniciar sesión**.
3. Si es la primera vez que entras, verás una pantalla de bienvenida con información sobre la aplicación. A partir de la segunda vez, irás directamente al panel de tableros.

> Si introduces mal los datos más de 8 veces seguidas en 10 minutos, el acceso quedará bloqueado temporalmente.

---

### 4.3 Cerrar sesión

1. Haz clic en tu avatar en la esquina superior derecha.
2. En el menú que aparece, pulsa **Cerrar sesión**.

---

### 4.4 Recuperar la contraseña

1. En la pantalla de inicio de sesión, pulsa **¿Olvidaste tu contraseña?**
2. Escribe tu correo electrónico y pulsa **Enviar enlace**.
3. Abre el correo que recibirás y haz clic en el enlace que contiene.
4. Escribe una contraseña nueva (debe cumplir los mismos requisitos que al crear la cuenta) y confírmala.
5. Pulsa **Restablecer contraseña**. Serás redirigido al inicio de sesión.

> El enlace del correo tiene una validez de 1 hora. Pasado ese tiempo tendrás que pedir uno nuevo.

---

### 4.5 Crear un espacio de trabajo

Un espacio de trabajo es el contenedor que agrupa los tableros de un equipo o proyecto.

1. Haz clic en el botón **Crear** en la barra superior.
2. Selecciona **Crear tablero**.
3. En el cuadro de diálogo que aparece:
   - Escribe el **nombre del espacio de trabajo**.
   - Escribe el **nombre del primer tablero** (si lo dejas vacío, se llamará "Tablero principal").
4. Pulsa **Crear**.

El espacio se creará con un tablero que ya incluye tres columnas por defecto: **Pendiente**, **En progreso** y **Listo**.

---

### 4.6 Renombrar un espacio de trabajo

Solo pueden hacerlo los usuarios con rol Propietario o Admin en ese espacio.

1. Accede al espacio de trabajo desde la barra lateral.
2. Haz clic en el botón de edición junto al nombre del espacio.
3. Escribe el nuevo nombre (máximo 120 caracteres).
4. Confirma el cambio.

---

### 4.7 Eliminar un espacio de trabajo

Solo puede hacerlo el Propietario del espacio.

1. Accede al espacio de trabajo.
2. Haz clic en el botón **Eliminar espacio** (aparece en rojo).
3. Confirma la eliminación en el cuadro de diálogo.

> Esta acción es permanente. Se borrarán también todos los tableros, columnas y tarjetas que contenga el espacio. No se puede deshacer.

---

### 4.8 Crear un tablero dentro de un espacio

Requiere rol Propietario o Admin en el espacio.

1. Accede al espacio de trabajo desde la barra lateral.
2. Haz clic en la tarjeta **+ Nuevo tablero**.
3. Escribe el nombre del tablero (máximo 120 caracteres).
4. Pulsa **Crear**.

---

### 4.9 Abrir un tablero

1. Desde el panel principal, haz clic sobre la tarjeta del tablero.
2. También puedes acceder directamente desde la barra lateral, pulsando el nombre del espacio y luego el tablero.

---

### 4.10 Eliminar un tablero

Requiere rol Propietario o Admin.

1. Abre el tablero.
2. Haz clic en el icono de engranaje ⚙ en la esquina superior derecha del tablero.
3. Ve a la pestaña **Zona peligrosa**.
4. Pulsa el botón **Eliminar tablero**.
5. Confirma la acción.

> Se borrarán todas las columnas y tarjetas del tablero. No se puede deshacer.

---

### 4.11 Personalizar el fondo del tablero

Requiere rol Propietario o Admin.

1. Abre el tablero y haz clic en el icono ⚙.
2. Ve a la pestaña **Fondo**.
3. Para cambiar el color, haz clic en uno de los 12 colores disponibles.
4. Para subir una imagen de portada, haz clic en el botón de cámara 📷, selecciona un archivo y pulsa **Guardar**.
   - Formatos admitidos: JPG, JPEG, PNG, SVG, WebP.
   - Tamaño máximo: 1 MB.
5. Si ya tienes una imagen y quieres quitarla, haz clic en el icono de papelera 🗑 que aparece junto a ella.
6. Pulsa **Guardar** para aplicar los cambios.

---

### 4.12 Crear una columna

Requiere rol Editor, Admin o Propietario.

1. Abre el tablero.
2. Haz clic en el botón **+ Crear columna** en la cabecera del tablero.
3. Escribe el nombre de la columna (máximo 120 caracteres).
4. Confirma pulsando el botón de crear.

La columna se añadirá al final del tablero.

---

### 4.13 Renombrar una columna

Requiere rol Editor, Admin o Propietario.

1. En el tablero, haz doble clic sobre el nombre de la columna.
2. Escribe el nuevo nombre.
3. Pulsa **Enter** o haz clic fuera del campo para guardar.

---

### 4.14 Mover columnas

Requiere rol Editor, Admin o Propietario.

1. En el tablero, haz clic y mantén pulsado sobre el icono de arrastre (⠿) que aparece en la cabecera de la columna.
2. Arrastra la columna a la posición deseada. Verás un indicador de dónde se colocará.
3. Suelta el botón del ratón para confirmar.

El nuevo orden se guarda automáticamente.

---

### 4.15 Eliminar una columna

Requiere rol Editor, Admin o Propietario.

1. En el pie de la columna, haz clic en el icono de papelera.
2. Confirma la eliminación.

> Se borrarán también todas las tarjetas que contenga esa columna.

---

### 4.16 Crear una tarjeta (tarea)

Requiere rol Editor, Admin o Propietario.

1. Dentro de la columna donde quieres añadir la tarea, haz clic en el botón **+ Agregar tarea**.
2. Escribe el título de la tarea (máximo 200 caracteres).
3. Pulsa **Crear** para confirmar.

---

### 4.17 Mover una tarjeta

Requiere rol Editor, Admin o Propietario.

1. Haz clic y mantén pulsado sobre la tarjeta.
2. Arrástrala hasta la columna y la posición donde quieras colocarla. Una línea indicará el punto de inserción exacto.
3. Suelta para confirmar. El cambio se guarda automáticamente y queda registrado en la actividad.

---

### 4.18 Eliminar una tarjeta

Requiere rol Editor, Admin o Propietario.

1. Pasa el cursor por encima de la tarjeta.
2. Aparecerá un botón de eliminar (×) en la esquina.
3. Haz clic en ese botón.
4. Confirma la eliminación en el cuadro de diálogo.

---

### 4.19 Usar una plantilla de tablero

Las plantillas son estructuras de tablero prediseñadas con columnas ya configuradas. Hay 24 disponibles.

**Desde el catálogo de plantillas:**
1. Haz clic en **Plantillas** en la barra lateral izquierda.
2. Explora el catálogo. Puedes navegar por categorías en la parte izquierda.
3. Cuando encuentres la plantilla que quieras, haz clic en **Usar plantilla**.
4. En el cuadro de diálogo, elige si quieres crear un nuevo espacio o usar uno existente.
5. Escribe el nombre del tablero.
6. Pulsa **Crear**.

**Desde el botón Crear:**
1. Haz clic en **Crear** en la barra superior.
2. Selecciona **Empezar con una plantilla**.
3. En el cuadro de diálogo, elige la pestaña **Plantilla**, selecciona la que quieras y escribe el nombre del tablero.
4. Pulsa **Crear**.

**Categorías de plantillas disponibles:**

| Categoría | Plantillas |
|---|---|
| Producto | Lanzamiento de producto, Sprint de desarrollo, Roadmap de producto |
| Calidad | Seguimiento de bugs |
| Marketing | Campaña de marketing, Calendario editorial, Contenido para redes |
| Ventas | Pipeline de ventas, Plan comercial |
| Clientes | CRM ligero, Onboarding de clientes, Gestión de clientes |
| Soporte | Mesa de soporte, Gestión de incidencias |
| Operaciones | Operaciones semanales, Mejora de procesos |
| Recursos Humanos | Proceso de selección, Onboarding de empleados |
| Proyectos | Gestión de proyecto |
| Eventos | Planificación de eventos |
| Creativo | Producción creativa |
| Agencia | Flujo de agencia |
| Finanzas | Cierre financiero |
| Personal | Productividad personal |

---

### 4.20 Gestionar miembros de un espacio de trabajo

**Niveles de acceso en un espacio:**

| Rol | Qué puede hacer |
|---|---|
| Propietario | Todo, incluido eliminar el espacio |
| Admin | Gestionar miembros, tableros y configuración |
| Editor | Crear y editar columnas y tarjetas |
| Lector | Solo ver el tablero |

**Añadir un miembro:**

Requiere rol Propietario o Admin.

1. Accede al espacio de trabajo.
2. Haz clic en el botón **Miembros**.
3. En el formulario de la parte superior, escribe el correo electrónico del nuevo miembro.
4. Selecciona el rol que tendrá: Admin, Editor o Lector.
5. Pulsa **Añadir miembro**.

> El usuario debe tener ya una cuenta creada en la plataforma para poder añadirlo.

**Cambiar el rol de un miembro:**

1. En la página de miembros, localiza al usuario.
2. Cambia el rol en el selector desplegable de su fila.
3. Pulsa **Guardar**.

**Eliminar un miembro:**

1. En la página de miembros, localiza al usuario.
2. Pulsa el botón **Eliminar** en su fila.

**Abandonar un espacio:**

Si eres miembro (no propietario) y quieres salir del espacio:

1. Ve a la página de miembros del espacio.
2. Pulsa el botón **Abandonar** en tu propia fila.

---

### 4.21 Invitar a alguien a un tablero concreto

Requiere rol Propietario o Admin en el tablero.

1. Abre el tablero.
2. Haz clic en el icono ⚙.
3. Ve a la pestaña **Miembros**.
4. En el formulario de invitación, escribe el correo del usuario y selecciona su rol.
5. Pulsa **Invitar**.

El usuario recibirá un correo con un enlace. Al hacer clic en ese enlace:
- Si ya tiene cuenta, accederá directamente al tablero.
- Si no tiene cuenta, se le redirigirá al formulario de registro con el correo ya rellenado.

**Cancelar una invitación pendiente:**

1. En la pestaña Miembros del panel de configuración del tablero, localiza la sección de invitaciones pendientes.
2. Haz clic en el botón de cancelar junto a la invitación.

**Cambiar el rol de un miembro del tablero:**

1. En la pestaña Miembros, localiza al usuario.
2. Cambia el rol en el selector desplegable.
3. Pulsa **Guardar**.

---

### 4.22 Editar el perfil

1. Haz clic en tu avatar en la esquina superior derecha.
2. Selecciona **Mi perfil**, o accede desde la barra lateral → **Perfil**.
3. Para cambiar el nombre visible: modifica el campo **Nombre de usuario** y pulsa **Guardar**.
4. Para cambiar la foto: haz clic en **Elegir archivo**, selecciona una imagen (JPG, JPEG, PNG, SVG o WebP; máximo 1 MB) y pulsa **Guardar**.
5. Para eliminar la foto actual: activa la opción **Eliminar avatar** y guarda.

---

### 4.23 Cambiar el correo electrónico

1. Haz clic en tu avatar → **Cuenta**, o ve a la barra lateral → **Cuenta**.
2. Busca la sección de correo electrónico y haz clic en el botón de editar.
3. Escribe el nuevo correo en el cuadro de diálogo.
4. Confirma el cambio.

> No puedes usar un correo que ya esté registrado por otro usuario.

---

### 4.24 Cambiar la contraseña desde la cuenta

1. Ve a la barra lateral → **Cuenta**.
2. Haz clic en el botón **Cambiar contraseña**.
3. Recibirás un correo con un enlace para establecer la nueva contraseña.
4. Abre el correo, haz clic en el enlace y sigue el proceso de restablecimiento.

---

### 4.25 Cambiar el idioma

La aplicación está disponible en cinco idiomas: Español, Inglés, Francés, Alemán y Portugués.

**Desde los ajustes:**
1. Ve a la barra lateral → **Ajustes**.
2. En la sección de idioma, selecciona el que prefieras.
3. El cambio se aplica de inmediato.

**Desde el menú de usuario:**
1. Haz clic en tu avatar en la esquina superior derecha.
2. Usa el selector de idioma que aparece en la parte inferior del menú.

---

### 4.26 Cambiar entre modo oscuro y modo claro

1. Haz clic en el icono ☀ / 🌙 que aparece en la barra superior derecha.

El cambio se aplica al instante en toda la interfaz.

---

### 4.27 Consultar el historial de actividad

1. Ve a la barra lateral → **Actividad**.
2. Verás un listado cronológico de todas las acciones registradas en tu cuenta: creaciones, movimientos, cambios de nombre, invitaciones, etc.
3. Usa los botones de paginación en la parte inferior para navegar por el historial.

La actividad se registra automáticamente para estas acciones: inicio de sesión, creación y eliminación de espacios y tableros, creación, movimiento y eliminación de columnas y tarjetas, cambios de rol, invitaciones enviadas, cambios de correo, contraseña e idioma.

---

### 4.28 Vista de tarjetas

1. Ve a la barra lateral → **Tarjetas**.
2. En la parte superior verás tres cifras: el total de tarjetas, las completadas y las abiertas.
3. Debajo aparece la lista de todas las tarjetas a las que tienes acceso, organizadas por tablero.
4. Usa los botones de filtro para ver solo las de alta prioridad, las más recientes, o todas sin filtrar.

---

### 4.29 Sección de ayuda

1. Ve a la barra lateral → **Ayuda**.
2. Encontrarás información básica sobre el uso de la plataforma y enlaces de referencia.

---

## 5. Preguntas frecuentes

**¿Qué pasa si escribo mal la contraseña varias veces al iniciar sesión?**
Tras 8 intentos fallidos en un intervalo de 10 minutos, el sistema bloqueará temporalmente el acceso desde esa dirección. Espera unos minutos y vuelve a intentarlo.

**¿Puedo recuperar un tablero o una tarjeta que he eliminado?**
No. Las eliminaciones son permanentes y no hay papelera de reciclaje. Confirma siempre antes de eliminar cualquier elemento.

**¿Qué requisitos tiene la contraseña?**
Debe tener al menos 8 caracteres e incluir: una letra mayúscula, una letra minúscula, un número y un carácter especial (como `!`, `@`, `#`, etc.).

**¿Puedo añadir a alguien que no tiene cuenta en Prodify?**
No directamente a un espacio de trabajo. Sin embargo, si le invitas a un tablero concreto, al hacer clic en el enlace del correo se le redirigirá al formulario de registro con su correo ya rellenado.

**¿Cuántos espacios de trabajo puedo tener?**
No hay límite establecido en la aplicación.

**¿Puedo pertenecer a varios espacios de trabajo a la vez?**
Sí, y puedes tener roles distintos en cada uno.

**¿El lector puede mover tarjetas o crear columnas?**
No. El rol Lector solo puede ver el contenido. Para crear o mover elementos se necesita al menos el rol Editor.

**¿Quién puede eliminar un espacio de trabajo?**
Solo el Propietario, que es quien lo creó.

**¿El enlace de recuperación de contraseña caduca?**
Sí, caduca al cabo de 1 hora. Si no lo usas a tiempo, repite el proceso desde la pantalla de inicio de sesión.

**¿La imagen de portada del tablero tiene algún límite de tamaño?**
Sí. El archivo no puede superar 1 MB y debe ser JPG, JPEG, PNG, SVG o WebP.

**¿Puedo cambiar el idioma sin cerrar sesión?**
Sí. El cambio de idioma desde los ajustes o desde el menú de usuario se aplica de inmediato sin necesidad de cerrar sesión.

**¿Dónde veo quién ha hecho qué en mis tableros?**
En la barra lateral → **Actividad**. Se registra toda acción importante de tu cuenta.
