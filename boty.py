from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import gspread

app = Flask(__name__)

# Definimos la máquina de estados y variables globales de memoria
sesiones = {}

oferta_academica = {
    "1": {
        "nombre": "📋 Técnico superior en Recursos Humanos", 
        "detalle": "📋 *Técnico Superior en Recursos Humanos*\nDuración: 3 años.\nEl Técnico Superior en Recursos Humanos es un profesional con formación técnica y estratégica en el campo de la gestión de personal y el desarrollo organizacional.",
        "link": "https://sites.google.com/superior50.com.ar/nivelterciario/oferta-acad%C3%A9mica/rrhh?authuser=0"
    },
    "2": {
        "nombre": "🛋️ Técnico superior en Ambientación y decoración de interiores",
        "detalle": "🛋️ *Técnico Superior en Ambientación y Decoración de Interiores*\nDuración: 3 años.\nEl Técnico Superior en Ambientación y Decoración de Interiores es un profesional con formación integral, creativo y técnico-operativa, capaz de intervenir en la concepción, diseño y ejecución de proyectos ambientales y de interiores, respondiendo a necesidades funcionales, estéticas y culturales de distintos tipos de espacios.",
        "link": "https://sites.google.com/superior50.com.ar/nivelterciario/oferta-acad%C3%A9mica/amb-y-dec-de-interiores?authuser=0"
    },
    "3": {
        "nombre": "📊 Técnico superior en Gestión de las organizaciones",
        "detalle": "📊 *Técnico Superior en Gestión de las Organizaciones*\nDuración: 3 años.\nEl Técnico Superior en Gestión de las Organizaciones está capacitado para planificar, organizar y coordinar las distintas áreas de una organización, considerando normas de higiene y seguridad laboral.\nInteractúa con los diferentes sectores mediante el trabajo en equipo, con capacidad para negociar propuestas y necesidades organizacionales.",
        "link": "https://sites.google.com/superior50.com.ar/nivelterciario/oferta-acad%C3%A9mica/gesti%C3%B3n-de-las-organizaciones?authuser=0"
    },
    "4": {
        "nombre": "📢 Técnico superior en Publicidad",
        "detalle": "📢 *Técnico Superior en Publicidad*\nDuración: 3 años.\nEstrategias de comunicación, marketing y creatividad visual.",
        "link": "https://sites.google.com/superior50.com.ar/nivelterciario/oferta-acad%C3%A9mica/publicidad?authuser=0"
    },
    "5": {
        "nombre": "🏥 Técnico superior en Enfermería", 
        "detalle": "🏥 *Técnico Superior en Enfermería*\nDuración: 3 años.\nSalud integral, atención comunitaria y prácticas asistenciales.",
        "link": "https://sites.google.com/superior50.com.ar/nivelterciario/oferta-acad%C3%A9mica/enfermer%C3%ADa?authuser=0"
    },
    "6": {
        "nombre": "🤝 Técnico superior en Acompañamiento Terapéutico",
        "detalle": "🤝 *Técnico Superior en Acompañamiento Terapéutico*\nDuración: 3 años.\nSalud mental, integración social y abordaje clínico interdisciplinario.",
        "link": "https://sites.google.com/superior50.com.ar/nivelterciario/oferta-acad%C3%A9mica/acompa%C3%B1amiento-terapeutico?authuser=0"
    },
    "7": {
        "nombre": "🛠️ Técnico superior en Soporte de infraestructura de tecnología de la información",
        "detalle": "🛠️ *Técnico Superior en Soporte e Infraestructura de TI*\nDuración: 3 años.\nEl Técnico Superior en Soporte e Infraestructura de Tecnología de la Información está capacitado para implementar, mantener, actualizar y administrar infraestructuras tecnológicas en organizaciones, garantizando la disponibilidad, seguridad y continuidad de los sistemas informáticos.",
        "link": "https://sites.google.com/superior50.com.ar/nivelterciario/oferta-acad%C3%A9mica/soporte-de-infraestructura-de-ti?authuser=0"
    },
    "8": {
        "nombre": "💻 Técnico superior en Desarrollo de Software",
        "detalle": "💻 *Técnico Superior en Desarrollo de Software*\nDuración: 3 años.\nEl Técnico Superior en Desarrollo de Software está capacitado para diseñar, construir, verificar, optimizar y mantener aplicaciones informáticas, trabajando en el marco de proyectos organizados.",
        "link": "https://sites.google.com/superior50.com.ar/nivelterciario/oferta-acad%C3%A9mica/desarrollador-de-software?authuser=0"
    }
}

def obtener_lista_carreras():
    """Genera y retorna el texto con la lista de carreras disponibles para enviar por WhatsApp.

    Recorre el diccionario `oferta_academica` y arma un menú con cada carrera numerada.
    El usuario debe responder con el número de la carrera que quiere consultar.
    """
    # Inicializa el texto que se va a mostrar en WhatsApp.
    texto = "📋 *OFERTA ACADÉMICA - CARRERAS*:\n\n"

    # Recorre todas las carreras guardadas en el diccionario.
    for clave, info in oferta_academica.items():
        texto += f"{clave}. {info['nombre']}\n"

    # Agrega la instrucción final para que el usuario elija una opción.
    texto += "\nResponde con el número de la carrera que te interesa:"
    return texto

def obtener_mesas_desde_sheets():
    """Se conecta a Google Sheets y extrae los datos de mesas de examen para mostrarlos al usuario.

    La función:
    1) inicia la autenticación con la cuenta de servicio de Google,
    2) abre la planilla de Google Sheets,
    3) lee la hoja 'MesasExamen',
    4) transforma los datos en un diccionario clave-valor,
    5) arma un texto listo para enviar por WhatsApp.
    """
    try:
        # Crea el cliente de Google Sheets usando el archivo de credenciales JSON.
        gc = gspread.service_account(filename="credentials.json")

        # Abre la planilla pública/correspondiente a la institución.
        sh = gc.open("Bot_Datos_Terciario50")

        # Accede a la hoja específica que contiene la información de mesas de examen.
        worksheet = sh.worksheet("MesasExamen")

        # Lee todas las filas de la hoja y las guarda como listas de texto.
        filas = worksheet.get_all_values()

        # Convierte la información en un diccionario donde la clave es la primera columna
        # y el valor es la segunda columna, por ejemplo: {'Turno 1': '10/05'}.
        # Solo incluye filas que tengan al menos 2 columnas.
        datos = {fila[0]: fila[1] for fila in filas if len(fila) >= 2}

        # Arma el texto final para responder por WhatsApp.
        # Se usan los valores 'Turno 1', 'Turno 2', 'Turno 3' y 'EstadoMesa' en la hoja.
        texto = (
            "📝 *INSCRIPCIONES A LAS MESAS DE EXAMEN*:\n\n"
            f"📌 *Turnos de Exámenes Finales*:\n"
            f"• *1 - Turno*: {datos.get('Turno 1', 'No disponible')}\n\n"
            f"• *2 - Turno*: {datos.get('Turno 2', 'No disponible')}\n\n"
            f"• *3 - Turno*: {datos.get('Turno 3', 'No disponible')}\n\n"
            f"🎓 *Mesas Especiales (Materias Pendientes)*:\n"
            f"• Inscripción y mesas: {datos.get('Mesas Especiales', 'No disponible')}\n\n"
            f"{datos.get('EstadoMesa', '')}\n\n"
            "Las inscripciones se realizan a través de la página oficial:\n"
            "https://sites.google.com/superior50.com.ar/nivelterciario/inicio \n\n"
            "Envía cualquier mensaje para volver al menú principal."
        )

        # Devuelve el mensaje formateado para que el bot lo envíe al usuario.
        return texto
    except Exception as e:
        # Si falla la conexión o la lectura de Google Sheets, se devuelve un mensaje alternativo.
        return (
            "⚠️ En este momento no podemos acceder a la información actualizada de mesas de examen. "
            "Por favor, intenta más tarde o visita nuestra web oficial.\n\n"
            "Envía cualquier mensaje para volver al menú principal."
        )

def mostrar_menu():
    """Devuelve el texto del menú principal del bot.

    Este menú se muestra al inicio y cada vez que el usuario vuelve al inicio.
    Cada opción dirige a una sección diferente del asistente institucional.
    """
    # Retorna el contenido del menú principal en formato legible para WhatsApp.
    return (
        "\n 🏛️ *TERCIARIO SUPERIOR N° 50* 🏛️\n\n"
        "1. Oferta académica (carreras)\n"
        "2. Inscripción y requisitos (ingresantes)\n"
        "3. Sobre las mesas de examen\n"
        "4. Calendario académico y eventos del año\n"
        "5. Guía del estudiante y enlaces\n"
        "6. Contacto, dirección y teléfono\n"
        "7. Sitio web oficial (más información)\n"
        "8. Glosario y términos académicos (FAQ)\n"
    )

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    """Procesa los mensajes entrantes de WhatsApp y dirige la conversación por etapas.

    La lógica usa un diccionario `sesiones` para guardar el estado de cada contacto.
    Así, cada usuario conserva su propio flujo de conversación y no se mezclan con otros.
    """
    # Obtenemos el número del usuario para identificarlo de forma única.
    from_numero = request.values.get('From', '')

    # Tomamos el texto del mensaje y lo normalizamos para comparar de forma segura.
    mensaje_usuario = request.values.get('Body', '').lower().strip()

    # Creamos la respuesta que Twilio va a devolver al usuario.
    respuesta_twilio = MessagingResponse()
    msg = respuesta_twilio.message()

    # Si es la primera vez que este número nos escribe, le creamos su sesión en "inicio".
    if from_numero not in sesiones:
        sesiones[from_numero] = {"paso": "inicio"}

    # Obtenemos el paso actual correspondiente EXCLUSIVAMENTE a este usuario.
    paso_actual = sesiones[from_numero]["paso"]

    # -----------------------------------------------------------------
    # FASE 1: BIENVENIDA Y MENÚ DIRECTO
    # -----------------------------------------------------------------
    if paso_actual == "inicio":
        msg.body(
            "¡Hola! Bienvenido/a al asistente virtual automático del Colegio Superior N°50 - GENERAL DON JOSÉ DE SAN MARTÍN.\n\n"
            "Escribe el número de la opción que te interesa:\n"
            f"{mostrar_menu()}"
        )
        sesiones[from_numero]["paso"] = "menu_principal"
        return Response(str(respuesta_twilio), mimetype='text/xml')

    # -----------------------------------------------------------------
    # FASE 2: MENÚ PRINCIPAL INSTITUCIONAL
    # -----------------------------------------------------------------
    if paso_actual == "menu_principal":
        if mensaje_usuario == "1":
            msg.body(obtener_lista_carreras())
            sesiones[from_numero]["paso"] = "viendo_carreras"

        elif mensaje_usuario == "2":
            # SECCIÓN: REQUISITOS DE INSCRIPCIÓN PARA INGRESANTES
            msg.body(
                "📝 *INSCRIPCIÓN Y REQUISITOS (INGRESANTES)*:\n\n"
                "Para anotarte como alumno regular a cualquier carrera, necesitas presentar la siguiente documentación:\n\n"
                "• 📄 *Título secundario* (o constancia de título en trámite / certificado de alumno regular si estás cursando el último año).\n"
                "• 🪪 *Fotocopia de DNI* (anverso y reverso).\n"
                "• *Partida de nacimiento* actualizada.\n"
                "• *Fotos carnet* (actuales).\n"
                "• *Ficha médica* / certificado de salud.\n\n"
                "🔗 La preinscripción online y los formularios correspondientes se habilitan en fechas específicas a través de nuestro sitio web:\n"
                "https://sites.google.com/superior50.com.ar/nivelterciario/inicio\n\n"
                "Envía cualquier mensaje para volver al menú principal."
            )
            sesiones[from_numero]["paso"] = "volver_menu"   
        
        elif mensaje_usuario == "3":
            # Cuando el usuario elige la opción 3 del menú, se ejecuta esta función.
            # La función lee la hoja de Google Sheets y devuelve un texto con la información
            # actualizada de mesas de examen para enviárselo al usuario por WhatsApp.
            msg.body(obtener_mesas_desde_sheets())
            sesiones[from_numero]["paso"] = "volver_menu"
            
        elif mensaje_usuario == "4":
            # SECCIÓN 2: CALENDARIO ACADÉMICO Y EVENTOS ANUALES
            msg.body(
                "📅 *CALENDARIO ACADÉMICO Y EVENTOS*:\n\n"
                "• 🟢 *Curso introductorio (obligatorio)*: Inicio de actividades para ingresantes.\n"
                "- Fecha: del 9 al 20 de marzo.\n\n"

                "• 📚 *Inicio del ciclo lectivo*: Apertura oficial de clases.\n"
                "- Fecha: 23 de marzo.\n\n"

                "• ⏱️ *Cierre del 1.er cuatrimestre*: Finalización de cursadas.\n"
                "- Fecha: 3 de julio.\n\n"

                "• ❄️ *Receso escolar*: Vacaciones de invierno (según el receso provincial).\n"
                "- Fecha: del 6 al 17 de julio.\n\n"

                "• 🔄 *Inicio del segundo cuatrimestre*: Posterior al receso.\n"
                "- Fecha: 3 de agosto.\n\n"

                "• 🏁 *Cierre del 2.º cuatrimestre*: Finalización de clases del año.\n"
                "- Fecha: 13 de noviembre.\n\n"

                "• 📝 *Inscripción de estudiantes ingresantes a primer año 2027*: Primera convocatoria.\n"
                "- Fecha: del 23 de noviembre al 14 de diciembre.\n\n"

                "• 🎓 *Finalización del ciclo lectivo*.\n"
                "- Fecha: 11 de diciembre.\n\n"
                "Envía cualquier mensaje para volver al menú principal."
            )
            sesiones[from_numero]["paso"] = "volver_menu"
            
        elif mensaje_usuario == "5":
            msg.body(
                "🔗 *Guía del Estudiante*:\n\n"
                "Puedes acceder a la guía oficial de estudiantes aquí:\n"
                "https://guiadelestudiante.superior50.com.ar/home \n\n"
                "Envía cualquier mensaje para volver al menú principal."
            )
            sesiones[from_numero]["paso"] = "volver_menu"
            
        elif mensaje_usuario == "6":
            msg.body(
                "📍 *Contacto y Dirección*:\n\n"
                "• Dirección: Domingo Ferrari 480 - Rufino, Santa Fe.\n"
                "• Teléfono: (03382) 428570\n"
                "• Email: nivel_terciario@superior50.com.ar\n\n"
                "Envía cualquier mensaje para volver al menú principal."
            )
            sesiones[from_numero]["paso"] = "volver_menu"
            
        elif mensaje_usuario == "7":
            msg.body(
                "🌐 *Sitio Web Oficial*:\n\n"
                "Visítanos en:\n"
                "https://sites.google.com/superior50.com.ar/nivelterciario/inicio \n\n"
                "Envía cualquier mensaje para volver al menú principal."
            )
            sesiones[from_numero]["paso"] = "volver_menu"

        elif mensaje_usuario == "8":
            # SECCIÓN: GLOSARIO Y TÉRMINOS ACADÉMICOS
            msg.body(
                "📖 *GLOSARIO Y PREGUNTAS FRECUENTES*:\n\n"
                "• *Materias correlativas*: Materias que, según el plan de estudios, requieren haber cursado o aprobado otras previamente para poder inscribirte.\n\n"

                "• *Materias cuatrimestrales y anuales*: Las cuatrimestrales se cursan durante un cuatrimestre, mientras que las anuales se extienden a lo largo de todo el ciclo lectivo.\n\n"

                "• *Homologaciones y equivalencias*: Trámite para solicitar el reconocimiento de materias aprobadas previamente en otra institución o carrera de nivel superior.\n\n"

                "• *Alumno regular*: Condición del estudiante que cumple con el porcentaje de asistencia y con la aprobación de los trabajos prácticos y parciales requeridos.\n\n"
                "Envía cualquier mensaje para volver al menú principal."
            )
            sesiones[from_numero]["paso"] = "volver_menu"
        else:
            msg.body(f"❌ Opción no válida.\n\n{mostrar_menu()}")
            
        return Response(str(respuesta_twilio), mimetype='text/xml')

    # -----------------------------------------------------------------
    # FASE 3: VIENDO CARRERAS (Detalle + Link web)
    # -----------------------------------------------------------------
    if paso_actual == "viendo_carreras":
        if mensaje_usuario in oferta_academica:
            carrera = oferta_academica[mensaje_usuario]
            msg.body(
                f"{carrera['detalle']}\n\n"
                f"🔗 *Plan de estudios y más info:* {carrera['link']}\n\n"
                "----------------------------------\n"
                "1️⃣ Volver al menú principal\n"
                "2️⃣ Ver otra carrera"
            )   
            sesiones[from_numero]["paso"] = "decidiendo_post_carrera"
        else:
            msg.body("❌ Opción no válida. Por favor, elige un número de carrera del 1 al 8.")

        return Response(str(respuesta_twilio), mimetype='text/xml')

   # -----------------------------------------------------------------
    # FASE 4: DECISIÓN POST-CARRERA (Menú principal vs Seguir viendo)
    # -----------------------------------------------------------------
    if paso_actual == "decidiendo_post_carrera":
        if mensaje_usuario == "1":
            msg.body(mostrar_menu())
            sesiones[from_numero]["paso"] = "menu_principal"
            
        elif mensaje_usuario == "2":
            msg.body(obtener_lista_carreras())
            sesiones[from_numero]["paso"] = "viendo_carreras"
            
        else:
            msg.body(
                "❌ Opción no válida. Por favor, responde:\n"
                "1️⃣ Para volver al menú principal\n"
                "2️⃣ Para ver otra carrera"
            )
            
        return Response(str(respuesta_twilio), mimetype='text/xml')

    # -----------------------------------------------------------------
    # AUXILIAR: VOLVER AL MENÚ
    # -----------------------------------------------------------------
    if paso_actual == "volver_menu":
        msg.body(mostrar_menu())
        sesiones[from_numero]["paso"] = "menu_principal"
        return Response(str(respuesta_twilio), mimetype='text/xml')

    return Response(str(respuesta_twilio), mimetype='text/xml')

if __name__ == "__main__":
    app.run(port=5000)
