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
    """Genera y retorna el texto formateado con el listado completo de carreras."""
    texto = "📋 *OFERTA ACADÉMICA - CARRERAS*:\n\n"
    for clave, info in oferta_academica.items():
        texto += f"{clave}. {info['nombre']}\n"
    texto += "\n👉 *Escribe ÚNICAMENTE el NÚMERO (del 1 al 8) de la carrera que te interesa:*"
    return texto

def obtener_mesas_desde_sheets():
    """Se conecta a Google Sheets y extrae los datos de mesas de examen, inscripciones y mesas especiales."""
    try:
        gc = gspread.service_account(filename="credentials.json")
        sh = gc.open("Bot_Datos_Terciario50")
        worksheet = sh.worksheet("MesasExamen")
        filas = worksheet.get_all_values()
        
        datos = {fila[0]: fila[1] for fila in filas if len(fila) >= 2}
        
        texto = (
            "📝 *INSCRIPCIONES Y MESAS DE EXAMEN*:\n\n"
            f"🗓️ *Fechas de Inscripción Generales*:\n"
            f"• {datos.get('InscripciónIngresantes', 'Consultar en plataforma oficial.')}\n\n"
            f"📌 *Turnos de Exámenes Finales*:\n"
            f"• *1.er turno*: {datos.get('Turno 1', 'No disponible')}\n\n"
            f"• *2.º turno*: {datos.get('Turno 2', 'No disponible')}\n\n"
            f"• *3.er turno*: {datos.get('Turno 3', 'No disponible')}\n\n"
            f"🎓 *Mesas Especiales (Materias Pendientes)*:\n"
            f"• {datos.get('Mesas Especiales', 'No disponible')}\n\n"
            f"{datos.get('EstadoMesa', '')}\n\n"
            "🔗 Las inscripciones se realizan a través de la página oficial:\n"
            "https://sites.google.com/superior50.com.ar/nivelterciario/inicio \n\n"
            + mensaje_volver_menu()
        )
        return texto
    except Exception as e:
        return (
            "⚠️ En este momento no podemos acceder a la información actualizada de mesas de examen. "
            "Por favor, intenta más tarde o visita nuestra web oficial.\n\n"
            + mensaje_volver_menu()
        )

def mostrar_menu():
    return (
        "\n 🏛️ *Opciones y trámites disponibles* 🏛️\n\n"
        "1. Oferta académica (carreras)\n"
        "2. Inscripción y requisitos (ingresantes)\n"
        "3. Sobre las inscripciones y mesas de exámenes\n"
        "4. Calendario académico y eventos del año\n"
        "5. Guía del estudiante y enlaces\n"
        "6. Contacto, dirección y teléfono\n"
        "7. Sitio web oficial (más información)\n"
        "8. Glosario y términos académicos (FAQ)\n\n"
        "👇 *Escribe el NÚMERO de la opción deseada (ejemplo: 1):*"
    )


def mensaje_volver_menu():
    return "----------------------------------\n👉 *Escribe 1 para volver al menú principal.*"


def mensaje_opcion_invalida(detalle=""):
    if detalle:
        return f"❌ Opción no válida.\n\n{detalle}"
    return "❌ Opción no válida.\n\n" + mensaje_volver_menu()

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    from_numero = request.values.get('From', '')
    mensaje_usuario = request.values.get('Body', '').lower().strip()

    respuesta_twilio = MessagingResponse()
    msg = respuesta_twilio.message()

    if from_numero not in sesiones:
        sesiones[from_numero] = {"paso": "inicio"}

    paso_actual = sesiones[from_numero]["paso"]

    # -----------------------------------------------------------------
    # FASE 1: BIENVENIDA Y MENÚ DIRECTO
    # -----------------------------------------------------------------
    if paso_actual == "inicio":
        msg.body(
            "¡Hola! Bienvenido/a al asistente virtual del Colegio Superior N°50 - GENERAL DON JOSÉ DE SAN MARTÍN.\n"
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
            msg.body(
                "📝 *INSCRIPCIÓN Y REQUISITOS (INGRESANTES)*:\n\n"
                "Para anotarte como alumno regular a cualquier carrera, necesitas presentar la siguiente documentación:\n\n"
                "• 📄 *Título secundario* (o constancia de título en trámite / certificado de alumno regular si estás cursando el último año).\n"
                "• 🪪 *Fotocopia de DNI* (anverso y reverso).\n"
                "• 📜 *Partida de nacimiento* actualizada.\n"
                "• 🖼️ *Fotos carnet* (actuales).\n"
                "• 🩺 *Ficha médica* / certificado de salud.\n\n"
                "🔗 La preinscripción online y los formularios correspondientes se habilitan en fechas específicas a través de nuestro sitio web:\n"
                "https://sites.google.com/superior50.com.ar/nivelterciario/inicio\n\n"
                + mensaje_volver_menu()
            )
            sesiones[from_numero]["paso"] = "volver_menu"   
        
        elif mensaje_usuario == "3":
            msg.body(obtener_mesas_desde_sheets())
            sesiones[from_numero]["paso"] = "volver_menu"
            
        elif mensaje_usuario == "4":
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

                "• 📝 *Inscripción de estudiantes ingresantes a primer año*: Primera convocatoria.\n"
                "- Fecha: del 23 de noviembre al 14 de diciembre.\n\n"

                "• 🎓 *Finalización del ciclo lectivo*.\n"
                "- Fecha: 11 de diciembre.\n\n"

                + mensaje_volver_menu()
            )
            sesiones[from_numero]["paso"] = "volver_menu"            
        elif mensaje_usuario == "5":
            msg.body(
                "🔗 *GUÍA DEL ESTUDIANTE Y ENLACES*:\n\n"
                "Puedes acceder a la guía oficial de estudiantes aquí:\n"
                "https://guiadelestudiante.superior50.com.ar/home \n\n"
                + mensaje_volver_menu()
            )
            sesiones[from_numero]["paso"] = "volver_menu"
            
        elif mensaje_usuario == "6":
            msg.body(
                "📍 *CONTACTO Y DIRECCIÓN*:\n\n"
                "• 🏢 *Dirección*: Domingo Ferrari 480 - Rufino, Santa Fe.\n"
                "• 📞 *Teléfono*: (03382) 428570\n"
                "• ✉️ *Email*: nivel_terciario@superior50.com.ar\n\n"
                + mensaje_volver_menu()
            )
            sesiones[from_numero]["paso"] = "volver_menu"
            
        elif mensaje_usuario == "7":
            msg.body(
                "🌐 *SITIO WEB OFICIAL*:\n\n"
                "Visítanos en:\n"
                "https://sites.google.com/superior50.com.ar/nivelterciario/inicio \n\n"
                + mensaje_volver_menu()
            )
            sesiones[from_numero]["paso"] = "volver_menu"

        elif mensaje_usuario == "8":
            # SECCIÓN ENRIQUECIDA: GLOSARIO Y FAQ COMPLETO
            msg.body(
                "📖 *GLOSARIO Y PREGUNTAS FRECUENTES (FAQ)*:\n\n"
                "• 🏆 *Promoción directa*: Permite aprobar sin final. Requisitos: 75% de asistencia (o 50% justificado), 100% de TPs y promedio de 8 o más en parciales.\n\n"
                "• 🗣️ *Coloquio*: Instancia de evaluación oral integradora previa a la mesa final para alumnos regulares o promocionados.\n\n"
                "• 📜 *Alumno Regular*: Se mantiene con el 75% de asistencia (o hasta 50% por salud/trabajo) y aprobación de parciales y TPs.\n\n"
                "• 👥 *Cursado Semi-presencial*: Requiere cumplir al menos con el 40% de asistencia presencial.\n\n"
                "• 🔓 *Condición Libre*: Rinde todo el programa en mesa final sin cursada. Válido solo para formato *materia*.\n\n"
                "• 🔄 *Homologaciones y Equivalencias*: Trámite para acreditar materias de otra institución.\n"
                "🔗 Info: https://sites.google.com/superior50.com.ar/nivelterciario/informaci%C3%B3n?authuser=0 \n\n"
                "• 🎓 *Mesas Especiales*: Llamados para alumnos con 1 o 2 materias pendientes para recibirse.\n\n"
                "• 🔗 *Materias Correlativas*: Asignaturas que exigen tener cursadas/aprobadas otras previas.\n\n"
                "🌐 *Régimen de cursado completo*:\n"
                "https://sites.google.com/superior50.com.ar/nivelterciario/estudiantes/sistema-de-calificaci%C3%B3n?authuser=0 \n\n"
                + mensaje_volver_menu()
            )
            sesiones[from_numero]["paso"] = "volver_menu"
        else:
            msg.body(mensaje_opcion_invalida(mostrar_menu()))
            
        return Response(str(respuesta_twilio), mimetype='text/xml')

    # -----------------------------------------------------------------
    # FASE 3: VIENDO CARRERAS
    # -----------------------------------------------------------------
    if paso_actual == "viendo_carreras":
        if mensaje_usuario in oferta_academica:
            carrera = oferta_academica[mensaje_usuario]
            msg.body(
                f"{carrera['detalle']}\n\n"
                f"🔗 *Plan de estudios y más info:* {carrera['link']}\n\n"
                "----------------------------------\n"
                "1️⃣ Escribe *1* para volver al menú principal\n"
                "2️⃣ Escribe *2* para ver otra carrera"
            )   
            sesiones[from_numero]["paso"] = "decidiendo_post_carrera"
        else:
            msg.body(mensaje_opcion_invalida("👉 *Por favor, escribe un NÚMERO del 1 al 8 para elegir una carrera:*"))

        return Response(str(respuesta_twilio), mimetype='text/xml')

    # -----------------------------------------------------------------
    # FASE 4: DECISIÓN POST-CARRERA
    # -----------------------------------------------------------------
    if paso_actual == "decidiendo_post_carrera":
        if mensaje_usuario == "1":
            msg.body(mostrar_menu())
            sesiones[from_numero]["paso"] = "menu_principal"
            
        elif mensaje_usuario == "2":
            msg.body(obtener_lista_carreras())
            sesiones[from_numero]["paso"] = "viendo_carreras"
            
        else:
            msg.body(mensaje_opcion_invalida(
                "👉 *Responde con un número:*\n"
                "1️⃣ Para volver al menú principal\n"
                "2️⃣ Para ver otra carrera"
            ))
            
        return Response(str(respuesta_twilio), mimetype='text/xml')

    # -----------------------------------------------------------------
    # AUXILIAR: VOLVER AL MENÚ (Exige 1 de forma explícita)
    # -----------------------------------------------------------------
    if paso_actual == "volver_menu":
        if mensaje_usuario == "1":
            msg.body(mostrar_menu())
            sesiones[from_numero]["paso"] = "menu_principal"
        else:
            msg.body(mensaje_opcion_invalida(mensaje_volver_menu()))
        return Response(str(respuesta_twilio), mimetype='text/xml')

    return Response(str(respuesta_twilio), mimetype='text/xml')

if __name__ == "__main__":
    app.run(port=5000)
