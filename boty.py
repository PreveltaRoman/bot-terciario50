import logging
import os

from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import gspread

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("boty")

app = Flask(__name__)

# Memoria de sesiones: {numero: {"paso": "..."}}
sesiones = {}

URL_SITIO = "https://sites.google.com/superior50.com.ar/nivelterciario/inicio"
URL_OFERTA = "https://sites.google.com/superior50.com.ar/nivelterciario/oferta-acad%C3%A9mica"
URL_INFO = "https://sites.google.com/superior50.com.ar/nivelterciario/informaci%C3%B3n?authuser=0"
URL_REGIMEN = "https://sites.google.com/superior50.com.ar/nivelterciario/estudiantes/sistema-de-calificaci%C3%B3n?authuser=0"
URL_GUIA = "https://guiadelestudiante.superior50.com.ar/home"

oferta_academica = {
    "1": {
        "nombre": "📋 Técnico superior en Recursos Humanos",
        "detalle": "📋 *Técnico Superior en Recursos Humanos*\nDuración: 3 años.\nEl Técnico Superior en Recursos Humanos es un profesional con formación técnica y estratégica en el campo de la gestión de personal y el desarrollo organizacional.",
        "link": f"{URL_OFERTA}/rrhh?authuser=0",
    },
    "2": {
        "nombre": "🛋️ Técnico superior en Ambientación y decoración de interiores",
        "detalle": "🛋️ *Técnico Superior en Ambientación y Decoración de Interiores*\nDuración: 3 años.\nEl Técnico Superior en Ambientación y Decoración de Interiores es un profesional con formación integral, creativo y técnico-operativa, capaz de intervenir en la concepción, diseño y ejecución de proyectos ambientales y de interiores, respondiendo a necesidades funcionales, estéticas y culturales de distintos tipos de espacios.",
        "link": f"{URL_OFERTA}/amb-y-dec-de-interiores?authuser=0",
    },
    "3": {
        "nombre": "📊 Técnico superior en Gestión de las organizaciones",
        "detalle": "📊 *Técnico Superior en Gestión de las Organizaciones*\nDuración: 3 años.\nEl Técnico Superior en Gestión de las Organizaciones está capacitado para planificar, organizar y coordinar las distintas áreas de una organización, considerando normas de higiene y seguridad laboral.\nInteractúa con los diferentes sectores mediante el trabajo en equipo, con capacidad para negociar propuestas y necesidades organizacionales.",
        "link": f"{URL_OFERTA}/gestión-de-las-organizaciones?authuser=0",
    },
    "4": {
        "nombre": "📢 Técnico superior en Publicidad",
        # TODO: reemplazar por la descripción oficial del sitio
        "detalle": "📢 *Técnico Superior en Publicidad*\nDuración: 3 años.\nEstrategias de comunicación, marketing y creatividad visual.",
        "link": f"{URL_OFERTA}/publicidad?authuser=0",
    },
    "5": {
        "nombre": "🏥 Técnico superior en Enfermería",
        # TODO: reemplazar por la descripción oficial del sitio
        "detalle": "🏥 *Técnico Superior en Enfermería*\nDuración: 3 años.\nSalud integral, atención comunitaria y prácticas asistenciales.",
        "link": f"{URL_OFERTA}/enfermería?authuser=0",
    },
    "6": {
        "nombre": "🤝 Técnico superior en Acompañamiento Terapéutico",
        # TODO: reemplazar por la descripción oficial del sitio
        "detalle": "🤝 *Técnico Superior en Acompañamiento Terapéutico*\nDuración: 3 años.\nSalud mental, integración social y abordaje clínico interdisciplinario.",
        "link": f"{URL_OFERTA}/acompañamiento-terapéutico?authuser=0",
    },
    "7": {
        "nombre": "🛠️ Técnico superior en Soporte de infraestructura de tecnología de la información",
        "detalle": "🛠️ *Técnico Superior en Soporte e Infraestructura de TI*\nDuración: 3 años.\nEl Técnico Superior en Soporte e Infraestructura de Tecnología de la Información está capacitado para implementar, mantener, actualizar y administrar infraestructuras tecnológicas en organizaciones, garantizando la disponibilidad, seguridad y continuidad de los sistemas informáticos.",
        "link": f"{URL_OFERTA}/soporte-de-infraestructura-de-ti?authuser=0",
    },
    "8": {
        "nombre": "💻 Técnico superior en Desarrollo de Software",
        "detalle": "💻 *Técnico Superior en Desarrollo de Software*\nDuración: 3 años.\nEl Técnico Superior en Desarrollo de Software está capacitado para diseñar, construir, verificar, optimizar y mantener aplicaciones informáticas, trabajando en el marco de proyectos organizados.",
        "link": f"{URL_OFERTA}/desarrollador-de-software?authuser=0",
    },
}


# ---------------------------------------------------------------------
# TEXTOS
# ---------------------------------------------------------------------
def mensaje_volver_menu():
    return "----------------------------------\n👉 *Escribe 0 para volver al menú principal.*"


def mensaje_opcion_invalida(detalle=""):
    if detalle:
        return f"❌ Opción no válida.\n\n{detalle}"
    return "❌ Opción no válida.\n\n" + mensaje_volver_menu()


def mostrar_menu():
    return (
        "\n 📌*Opciones y trámites disponibles* \n\n"
        "1. Oferta académica (carreras)\n"
        "2. Inscripción y requisitos (ingresantes)\n"
        "3. Mesas de examen y turnos de finales\n"
        "4. Calendario académico y eventos del año\n"
        "5. Guía del estudiante y enlaces\n"
        "6. Contacto, dirección y teléfono\n"
        "7. Sitio web oficial (más información)\n"
        "8. Glosario y términos académicos (FAQ)\n\n"
        "👇 *Escribe el NÚMERO de la opción deseada (ejemplo: 1):*"
    )


def obtener_lista_carreras():
    """Genera el texto con el listado completo de carreras."""
    texto = "📋 *OFERTA ACADÉMICA - CARRERAS*:\n\n"
    for clave, info in oferta_academica.items():
        texto += f"{clave}. {info['nombre']}\n"
    texto += f"\n👉 *Escribe ÚNICAMENTE el NÚMERO (del 1 al {len(oferta_academica)}) de la carrera que te interesa:*"
    texto += "\n\n🔙 *Escribe 0 para volver al menú principal.*"
    return texto


# Respuestas fijas del menú principal (opción -> texto). Se les agrega
# automáticamente el mensaje de "volver al menú" al final.
RESPUESTAS_ESTATICAS = {
    "2": (
        "📝 *INSCRIPCIÓN Y REQUISITOS (INGRESANTES)*:\n\n"
        "Para anotarte como alumno regular a cualquier carrera, necesitas presentar la siguiente documentación:\n\n"
        "• 📄 *Título secundario* (o constancia de título en trámite / certificado de alumno regular si estás cursando el último año).\n"
        "• 🪪 *Fotocopia de DNI* (anverso y reverso).\n"
        "• 📜 *Partida de nacimiento* actualizada.\n"
        "• 🖼️ *Fotos carnet* (actuales).\n"
        "• 🩺 *Ficha médica* / certificado de salud.\n\n"
        "🔗 La preinscripción online y los formularios correspondientes se habilitan en fechas específicas a través de nuestro sitio web:\n"
        f"{URL_SITIO}\n\n"
    ),
    "4": (
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
    ),
    "5": (
        "🔗 *GUÍA DEL ESTUDIANTE Y ENLACES*:\n\n"
        "Puedes acceder a la guía oficial de estudiantes aquí:\n"
        f"{URL_GUIA}\n\n"
    ),
    "6": (
        "📍 *CONTACTO Y DIRECCIÓN*:\n\n"
        "• 🏢 *Dirección*: Domingo Ferrari 480 - Rufino, Santa Fe.\n"
        "• 📞 *Teléfono*: (03382) 428570\n"
        "• ✉️ *Email*: nivel_terciario@superior50.com.ar\n\n"
    ),
    "7": (
        "🌐 *SITIO WEB OFICIAL*:\n\n"
        "Visítanos en:\n"
        f"{URL_SITIO}\n\n"
    ),
    "8": (
        "📖 *GLOSARIO Y PREGUNTAS FRECUENTES (FAQ)*:\n\n"
        "• 🏆 *Promoción directa*: Permite aprobar sin final. Requisitos: 75% de asistencia (o 50% justificado), 100% de TPs y promedio de 8 o más en parciales.\n\n"
        "• 🗣️ *Coloquio*: Instancia de evaluación oral integradora previa a la mesa final para alumnos regulares o promocionados.\n\n"
        "• 📜 *Alumno Regular*: Se mantiene con el 75% de asistencia (o hasta 50% por salud/trabajo) y aprobación de parciales y TPs. La regularidad tiene una duración de 3 años consecutivos.\n\n"
        "• 👥 *Cursado Semi-presencial*: Requiere cumplir al menos con el 40% de asistencia presencial.\n\n"
        "• 🔓 *Condición Libre*: Rinde todo el programa en mesa final sin cursada. Válido solo para formato *materia*.\n\n"
        "• 🔄 *Homologaciones y Equivalencias*: Trámite para acreditar materias de otra institución.\n"
        f"🔗 Info: {URL_INFO}\n\n"
        "• 🎓 *Mesas Especiales*: Llamados para alumnos con 1 o 2 materias pendientes para recibirse.\n\n"
        "• 🔗 *Materias Correlativas*: Asignaturas que exigen tener cursadas/aprobadas otras previas.\n\n"
        "🌐 *Régimen de cursado completo*:\n"
        f"{URL_REGIMEN}\n\n"
    ),
}


# ---------------------------------------------------------------------
# GOOGLE SHEETS
# ---------------------------------------------------------------------
def obtener_mesas_desde_sheets():
    """Se conecta a Google Sheets y arma el texto de mesas de examen e inscripciones."""
    try:
        gc = gspread.service_account(filename="credentials.json")
        sh = gc.open("Bot_Datos_Terciario50")
        worksheet = sh.worksheet("MesasExamen")
        filas = worksheet.get_all_values()

        datos = {fila[0]: fila[1] for fila in filas if len(fila) >= 2}

        return (
            "📝 *MESAS DE EXAMEN Y TURNOS DE FINALES*:\n\n"
            "🗓️ *Fechas de Inscripción Generales*:\n"
            f"• {datos.get('InscripciónIngresantes', 'Consultar en plataforma oficial.')}\n\n"
            "📌 *Turnos de Exámenes Finales*:\n"
            f"• *1.º turno*: {datos.get('Turno 1', 'No disponible')}\n\n"
            f"• *2.º turno*: {datos.get('Turno 2', 'No disponible')}\n\n"
            f"• *3.º turno*: {datos.get('Turno 3', 'No disponible')}\n\n"
            "🎓 *Mesas Especiales (Materias Pendientes)*:\n"
            f"• {datos.get('Mesas Especiales', 'No disponible')}\n\n"
            f"{datos.get('EstadoMesa', '')}\n\n"
            "🔗 Las inscripciones se realizan a través de la página oficial:\n"
            f"{URL_SITIO}\n\n"
            + mensaje_volver_menu()
        )
    except Exception:
        log.exception("No se pudo leer la hoja de Google Sheets")
        return (
            "⚠️ En este momento no podemos acceder a la información actualizada de mesas de examen. "
            "Por favor, intenta más tarde o visita nuestra web oficial.\n\n"
            + mensaje_volver_menu()
        )


# ---------------------------------------------------------------------
# LÓGICA DEL BOT
# ---------------------------------------------------------------------
def procesar_mensaje(numero, texto):
    """Recibe el número y el texto del usuario y devuelve el texto de respuesta.

    Está separada de Twilio a propósito: cuando se reemplace Twilio, solo
    cambia la ruta de entrada/salida, no esta función.
    """
    sesion = sesiones.setdefault(numero, {"paso": "inicio"})
    paso = sesion["paso"]

    # FASE 1: BIENVENIDA
    if paso == "inicio":
        sesion["paso"] = "menu_principal"
        return (
            "¡Hola! Bienvenido/a al asistente virtual del Colegio Superior N°50 - GENERAL DON JOSÉ DE SAN MARTÍN.\n"
            f"{mostrar_menu()}"
        )

    # FASE 2: MENÚ PRINCIPAL
    if paso == "menu_principal":
        if texto == "1":
            sesion["paso"] = "viendo_carreras"
            return obtener_lista_carreras()
        if texto == "3":
            sesion["paso"] = "volver_menu"
            return obtener_mesas_desde_sheets()
        if texto in RESPUESTAS_ESTATICAS:
            sesion["paso"] = "volver_menu"
            return RESPUESTAS_ESTATICAS[texto] + mensaje_volver_menu()
        return mensaje_opcion_invalida(mostrar_menu())

    # FASE 3: VIENDO CARRERAS
    if paso == "viendo_carreras":
        if texto == "0":
            sesion["paso"] = "menu_principal"
            return mostrar_menu()
        if texto in oferta_academica:
            carrera = oferta_academica[texto]
            sesion["paso"] = "decidiendo_post_carrera"
            return (
                f"{carrera['detalle']}\n\n"
                f"🔗 *Plan de estudios y más info:* {carrera['link']}\n\n"
                "----------------------------------\n"
                "1️⃣ Escribe *1* para ver otra carrera\n"
                "0️⃣ Escribe *0* para volver al menú principal"
            )
        return mensaje_opcion_invalida(
            f"👉 *Por favor, escribe un NÚMERO del 1 al {len(oferta_academica)} para elegir una carrera.*\n"
            "🔙 *O escribe 0 para volver al menú principal.*"
        )

    # FASE 4: DECISIÓN POST-CARRERA
    if paso == "decidiendo_post_carrera":
        if texto == "0":
            sesion["paso"] = "menu_principal"
            return mostrar_menu()
        if texto == "1":
            sesion["paso"] = "viendo_carreras"
            return obtener_lista_carreras()
        return mensaje_opcion_invalida(
            "👉 *Responde con un número:*\n"
            "1️⃣ Para ver otra carrera\n"
            "0️⃣ Para volver al menú principal"
        )

    # AUXILIAR: VOLVER AL MENÚ
    if paso == "volver_menu":
        if texto == "0":
            sesion["paso"] = "menu_principal"
            return mostrar_menu()
        return mensaje_opcion_invalida(mensaje_volver_menu())

    # Estado desconocido: se reinicia la sesión
    sesion["paso"] = "inicio"
    return procesar_mensaje(numero, texto)


# ---------------------------------------------------------------------
# ENTRADA/SALIDA (Twilio, por ahora)
# ---------------------------------------------------------------------
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    numero = request.values.get("From", "")
    texto = request.values.get("Body", "").lower().strip()

    respuesta_twilio = MessagingResponse()
    respuesta_twilio.message().body(procesar_mensaje(numero, texto))
    return Response(str(respuesta_twilio), mimetype="text/xml")


if __name__ == "__main__":
    if os.environ.get("BOT_DEBUG") == "1":
        # Desarrollo: servidor de Flask con recarga automática
        app.run(port=5000, debug=True)
    else:
        # Producción (Windows): waitress
        from waitress import serve
        log.info("Bot escuchando en http://0.0.0.0:5000")
        serve(app, host="0.0.0.0", port=5000, threads=4)
