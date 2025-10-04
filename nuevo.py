import customtkinter as ctk
import fitz # Importa la librería PyMuPDF para trabajar con archivos PDF.
import re # Importa la librería 're' para usar expresiones regulares.
import tkinter as tk # Importa la librería Tkinter para crear la interfaz gráfica.
from tkinter import filedialog, messagebox, simpledialog, ttk # Importa módulos específicos de Tkinter.
from PIL import Image, ImageTk, ImageOps # Importa módulos de la librería PIL (Pillow) para manipular imágenes.
from docx import Document # Importa la clase Document de python-docx para trabajar con archivos de Word.
import os # Importa la librería 'os' para interactuar con el sistema operativo.
import sys # Importa la librería 'sys' para interactuar con el entorno de Python.
from datetime import datetime # Importa la clase datetime para manejar fechas y horas.
import webbrowser # Importa la librería webbrowser para abrir URL's en el navegador.
from tkinter import font # Importa la clase font para trabajar con fuentes en Tkinter.
import time
from tkinter import ttk
from customtkinter import CTkLabel, CTkImage
from customtkinter import CTkTextbox  # Este import debe ir al inicio del archivo


tooltip_label = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
# Ruta de la imagen/logo

def obtener_ruta_recurso(nombre_archivo):
    """
    Obtiene la ruta de un recurso empaquetado por PyInstaller o en desarrollo.
    
    Esta función verifica si el programa se está ejecutando como un ejecutable
    de PyInstaller. Si es así, busca el archivo en el directorio temporal _MEIPASS.
    De lo contrario, lo busca en el mismo directorio del script.
    """
    if hasattr(sys, '_MEIPASS'): # Verifica si el programa fue empaquetado.
        return os.path.join(sys._MEIPASS, nombre_archivo) # Retorna la ruta en el entorno de PyInstaller.
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo) # Retorna la ruta en el entorno de desarrollo.


# Ruta de la imagen/logo
ruta_logo = obtener_ruta_recurso("cygnusCARGA.png")

def mostrar_ventana_carga():
    ventana_carga = ctk.CTk(fg_color="#000000")
    ventana_carga.title("By Pinky")
    ventana_carga.geometry("230x240")
    ventana_carga.resizable(False, False)

    # Texto principal
    label_texto = ctk.CTkLabel(
        ventana_carga,
        text="APP CYGNUS",


        font=("Comic Sans MS", 19, "bold"), fg_color="#000000",
        anchor="center",
        justify="center"
    )
    label_texto.pack(pady=(13, 5))  # Más espacio arriba # antes era (10, 5)

        # Imagen/logo

    if os.path.exists(ruta_logo):
        img = Image.open(ruta_logo)
        img = img.resize((100, 100), Image.Resampling.LANCZOS)

        # Crear imagen compatible con CTk
        img_ctk = CTkImage(light_image=img, dark_image=img, size=(100, 100))

        # Usar CTkLabel en lugar de ctk.CTkLabel
        label_img = CTkLabel(ventana_carga, image=img_ctk, text="", fg_color="black")
        label_img.pack(pady=(5, 5))


    # Texto dinámico
    label_dinamico = ctk.CTkLabel(ventana_carga, text="Inicializando módulos...", font=("Arial", 11))
    label_dinamico.pack(pady=(5, 5))

    # Barra de progreso
    frame_progress = ctk.CTkFrame(ventana_carga, fg_color="black")
    frame_progress.pack(pady=(5, 5))
    progress = ttk.Progressbar(frame_progress, orient="horizontal", length=200, mode="determinate")
    progress.pack(pady=(5, 5))
    progress["maximum"] = 100
    progress["value"] = 0

    # Simulación de llenado progresivo con mensajes
    for i in range(101):
        progress["value"] = i

        if i == 30:
            label_dinamico.configure(text="Cargando recursos...")
        elif i == 60:
            label_dinamico.configure(text="Configurando entorno...")
        elif i == 80:
            label_dinamico.configure(text="Iniciando")

        ventana_carga.update()
        time.sleep(0.05)  # Ajusta la velocidad de llenado

    ventana_carga.destroy()

# Ejecutar antes de iniciar la app principal
mostrar_ventana_carga()


# Lista para almacenar las referencias de las ventanas secundarias
ventanas_hijas = []

# --- CONFIGURACIÓN GLOBAL DE BOTONES y VENTANAS---
# Define una variable para la altura uniforme de los botones
BUTTON_HEIGHT = 20
# Define el tamaño para las ventanas secundarias
VENTANA_SECUNDARIA_ANCHO = 220
VENTANA_SECUNDARIA_ALTO = 460

# Configurar salida estándar para UTF-8 en Windows
# sys.stdout.reconfigure(encoding='utf-8')

# Lista para almacenar los contactos de cada pestaña
contactos_por_pestana = {
    "Principal": [],
    "Telefonos": [],
    "Generador": []
}


def limpiar_texto(texto):
    """
    Limpia caracteres problemáticos en el texto extraído del PDF.
    
    Reemplaza caracteres especiales o no deseados, a menudo generados por la extracción
    de texto de PDFs, y se asegura de que el texto sea compatible con UTF-8.
    """
    reemplazos = {'�': '', '\ue603': '', '\ue616': '', '\ue657': '', '\ue643': '', '\ue6a1': '', '\ue688': ''}
    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo) # Itera sobre el diccionario y reemplaza los caracteres.
    return texto.encode('utf-8', 'ignore').decode('utf-8') # Codifica y decodifica para limpiar caracteres problemáticos.

def extraer_texto_pdf(pdf_path):
    """
    Extrae todo el texto del PDF y lo devuelve como una sola cadena.
    
    Abre el archivo PDF, itera a través de cada página para extraer su texto,
    elimina los saltos de línea y concatena todo en una sola cadena.
    """
    doc = fitz.open(pdf_path) # Abre el documento PDF.
    texto_completo = " ".join([pagina.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES).replace("\n", " ") for pagina in doc]) # Extrae el texto de cada página y lo une en una sola cadena.
    return limpiar_texto(texto_completo) # Llama a la función limpiar_texto para procesar el texto extraído.

def extraer_datos(texto_completo):
    """
    Extrae todos los datos clave del documento utilizando expresiones regulares.
    
    Define un diccionario de patrones de expresiones regulares para cada dato
    que se desea extraer y luego busca esas coincidencias en el texto completo
    del PDF.
    """
    patrones = {
        "ID del evento": r"(CRQ\d+)", # Expresión regular para el ID del evento.
        "Título": r"CRQ\d+ Template\s*(.*?)\s*Nivel de riesgo", # Patrón para el título.
        "Fecha de creación": r"Fecha de creación.*?(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})", # Patrón para la fecha de creación.
        "Departamento": r"Departamento\s*(.*?)\s*FACT", # Patrón para el departamento.
        "Solicitado por": r"Cliente*([A-ZÁÉÍÓÚÑ ]+)\b", # Patrón para el solicitante.
        "Correo": r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", # Patrón para el correo electrónico.
        "Manager del cambio": r"Gestor de cambios*([A-ZÁÉÍÓÚÑ ]+)\b", # Patrón para el gestor de cambios.
        "Fechas programadas": r"Fechas programadas*(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})\s*(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})", # Patrón para las fechas programadas.
        "Nombre EVC": r"1\. Nombre EVC:\s*(.*?)\s*2\.", # Patrón para el nombre EVC.
        "Nombre Aplicación Banco": r"2\. Nombre Aplicación Banco:\s*(.*?)\s*3\.", # Patrón para el nombre de la aplicación.
        "Servicio en AWS": r"3\. Servicio en AWS:\s*(.*?)\s*4\.", # Patrón para el servicio en AWS.
        "Cuenta AWS": r"4\. Cuenta AWS:\s*(.*?)\s*5\.", # Patrón para la cuenta de AWS.
        "Recursos en AWS": r"5\. Nombre del Recurso en AWS:\s*(.*?)\s*6\.", # Patrón para los recursos en AWS.
        "Acción y/o Requerimiento": r"6\. Acción y/o Requerimiento:\s*(.*?)\s*7\.", # Patrón para la acción o requerimiento.
        "Justificación": r"7\. Justificación:\s*(.*?)\s*8\.", # Patrón para la justificación.
        "Remediación": r"8\. Remediación.*?:\s*(.*?)\s*9\.", # Patrón para la remediación.
        "Tipo IaC": r"9\. Tipo IaC\s*\(.*?\):\s*([\w\s]+?)\s*(?=10\.)", # Patrón para el tipo de IaC.
        "Analista para Contactar": r"10\. Analista para Contactar:\s*(.*?)\s*11\.", # Patrón para el analista de contacto.
        "Celular Contacto": r"11\. Celular Contacto:\s*([\d\s\+\-]+)" # Patrón para el celular de contacto.
    }
    
    datos_extraidos = {campo: "No encontrado" for campo in patrones} # Inicializa el diccionario de resultados.
    for campo, patron in patrones.items(): # Itera sobre los patrones.
        coincidencia = re.search(patron, texto_completo, re.MULTILINE | re.DOTALL) # Busca el patrón en el texto.
        if coincidencia:
            if campo == "Fechas programadas" and len(coincidencia.groups()) > 1: # Caso especial para fechas programadas.
                datos_extraidos[campo] = f"{coincidencia.group(1)} - {coincidencia.group(2)}" # Formatea las dos fechas.
            else:
                datos_extraidos[campo] = coincidencia.group(1).strip() # Asigna el valor extraído y elimina espacios en blanco.
    return datos_extraidos

def iniciar_proceso():
    """
    Ejecuta la selección de PDF, extrae datos y genera el documento.
    
    Esta función abre un diálogo para seleccionar un archivo PDF, extrae su texto,
    luego extrae los datos clave y, finalmente, abre un diálogo para guardar
    un archivo de Word generado con la plantilla.
    """
    ruta_pdf = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")]) # Abre un diálogo para seleccionar un archivo.

    if not ruta_pdf:
        messagebox.showwarning("Aviso", "No seleccionaste un PDF.") # Muestra un aviso si no se selecciona un archivo.
        return

    texto_completo = extraer_texto_pdf(ruta_pdf) # Extrae el texto del PDF.
    datos_completos = extraer_datos(texto_completo) # Extrae los datos clave del texto.

    plantilla_path = obtener_ruta_recurso("Plantilla CYGNUS CRQ.docx") # Obtiene la ruta de la plantilla.

    if not os.path.exists(plantilla_path):
        messagebox.showerror("Error", f"No se encontró la plantilla en {plantilla_path}") # Muestra un error si la plantilla no existe.
        return

    nombre_pdf = os.path.splitext(os.path.basename(ruta_pdf))[0] # Obtiene el nombre del archivo PDF sin la extensión.
    datos_completos["Fecha de Proceso"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S") # Añade la fecha de proceso.

    salida_path = filedialog.asksaveasfilename(
        initialfile=f"{nombre_pdf}.docx",
        defaultextension=".docx",
        filetypes=[("Archivos Word", "*.docx")],
        title="Guardar documento Word"
    ) # Abre un diálogo para guardar el archivo de Word.

    if not salida_path:
        messagebox.showwarning("Aviso", "No se guardó el documento.") # Muestra un aviso si el usuario cancela el guardado.
        return

    if salida_path:
        llenar_plantilla(datos_completos, plantilla_path, salida_path) # Llama a la función para llenar la plantilla.

def generar_evento_incidente():
    """
    Crea un Word con la plantilla de evento/incidente con la fecha actual y el nombre del archivo.
    
    Esta función localiza la plantilla de evento/incidente, genera un nombre de archivo
    basado en la fecha y la hora, y abre un diálogo para guardar el documento.
    """
    plantilla_path = obtener_ruta_recurso("Plantilla CYGNUS EVENTO-INCIDENTE.docx") # Obtiene la ruta de la plantilla de evento.

    if not os.path.exists(plantilla_path):
        messagebox.showerror("Error", f"No se encontró la plantilla en {plantilla_path}") # Muestra un error si la plantilla no existe.
        return

    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S") # Obtiene la fecha y hora actuales.
    nombre_archivo = f"Evento_Incidente_{datetime.now().strftime('%d-%m-%Y_%H_%M_%S')}.docx" # Genera un nombre de archivo único.

    salida_path = filedialog.asksaveasfilename(
        initialfile=nombre_archivo,
        defaultextension=".docx",
        filetypes=[("Archivos Word", "*.docx")],
        title="Guardar documento Word"
    ) # Abre un diálogo para guardar el archivo.

    if not salida_path:
        messagebox.showwarning("Aviso", "No se guardó el documento.") # Muestra un aviso si el usuario cancela el guardado.
        return

    id_evento_incidente = os.path.splitext(os.path.basename(salida_path))[0] # Obtiene el ID del archivo.
    datos = {
        "Fecha de Proceso": fecha_actual,
        "ID del EVENTO/INCIDENTE": id_evento_incidente
    } # Crea un diccionario con los datos a llenar.
    llenar_plantilla(datos, plantilla_path, salida_path) # Llama a la función para llenar la plantilla.

# Esta es la función corregida.
def generar_respuesta_ciber():
    id_ingresado = simpledialog.askstring("ID de la CRQ", "Ingresa el ID de la CRQ o ID que corresponda:", parent=root)
    if id_ingresado:
        frase = f"Cordial saludo, se revela el secreto para validaciones sobre el ID: {id_ingresado}"
        root.clipboard_clear()
        root.clipboard_append(frase)
        root.update()
        messagebox.showinfo("CIBER", "✅ Respuesta generada y copiada al portapapeles.")
    else:
        messagebox.showwarning("Aviso", "No se ingresó ningún ID. No se copió nada al portapapeles.")

def mostrar_cloudshell():
    x = root.winfo_x()
    y = root.winfo_y()
    ancho_principal = root.winfo_width()
    nueva_x = x + ancho_principal

    ventana_cloudshell = ctk.CTkToplevel(root)
    ventana_cloudshell.title("CLOUDSHELL")
    ventana_cloudshell.geometry(f"230x300+{nueva_x}+{y}")
    ventana_cloudshell.configure(fg_color="black")
    ventanas_hijas.append(ventana_cloudshell)
    ventana_cloudshell.transient(root)

    frame_botones = ctk.CTkFrame(ventana_cloudshell, fg_color="black")
    frame_botones.pack(pady=10, padx=10, fill="both", expand=True)

    for i in range(1, 10 + 1):
        btn = ctk.CTkButton(
            frame_botones,
            text=str(i),
            command=lambda n=i: messagebox.showinfo("CLOUDSHELL", f"Botón {n} presionado"),
            font=("Arial", 11, "bold"),
            height=BUTTON_HEIGHT,
            corner_radius=10
        )
        btn.pack(pady=2, fill="x")
# Botón MONGO
def mostrar_mongo():
    x = root.winfo_x()
    y = root.winfo_y()
    ancho_principal = root.winfo_width()
    nueva_x = x + ancho_principal

    ventana_mongo = ctk.CTkToplevel(root)
    ventana_mongo.title("EXTENSIONES MONGO")
    ventana_mongo.geometry(f"230x160+{nueva_x}+{y}")
    ventana_mongo.configure(fg_color="black")  # ← Aquí se cierra correctamente
    ventanas_hijas.append(ventana_mongo)
    ventana_mongo.transient(root)

    label_titulo = ctk.CTkLabel(ventana_mongo, text="EXTENSIONES", font=("Arial", 12, "bold"), fg_color="#000000")
    label_titulo.pack(pady=(3, 0))

    comando_validar = """aws cloudformation list-types --visibility PUBLIC --region us-east-1 | jq '.TypeSummaries[] | select(.TypeName == "MongoDB::Atlas::APIKey" or 
  .TypeName == "MongoDB::Atlas::AccessListAPIKey" or 
  .TypeName == "MongoDB::Atlas::AlertConfiguration" or 
  .TypeName == "MongoDB::Atlas::CloudBackUpRestoreJobs" or 
  .TypeName == "MongoDB::Atlas::CloudBackupSchedule" or 
  .TypeName == "MongoDB::Atlas::CloudBackupSnapshot" or 
  .TypeName == "MongoDB::Atlas::Cluster" or 
  .TypeName == "MongoDB::Atlas::CustomDBRole" or 
  .TypeName == "MongoDB::Atlas::DatabaseUser" or 
  .TypeName == "MongoDB::Atlas::EncryptionAtRest" or 
  .TypeName == "MongoDB::Atlas::MaintenanceWindow" or 
  .TypeName == "MongoDB::Atlas::PrivateEndpointAWS" or 
  .TypeName == "MongoDB::Atlas::PrivateEndpointService" or 
  .TypeName == "MongoDB::Atlas::Project" or 
  .TypeName == "MongoDB::Atlas::ProjectIpAccessList" or 
  .TypeName == "MongoDB::Atlas::ServerlessInstance" or 
  .TypeName == "MongoDB::Atlas::ServerlessPrivateEndpoint") | {TypeName, LatestPublicVersion, IsActivated}'"""

    def copiar_comando_mongo(comando):
        ventana_mongo.clipboard_clear()
        ventana_mongo.clipboard_append(comando)
        ventana_mongo.update()
        messagebox.showinfo("Copiado", "Comando copiado al portapapeles, pega el comando en la CLI de AWS para validar las extensiones y su estado")

    def activar_mongo():
        arn_personalizado = simpledialog.askstring("ARN personalizado", "Ingresa el ARN para --execution-role-arn:", parent=root)
        if not arn_personalizado:
            messagebox.showwarning("Advertencia", "No se ingresó ningún ARN.")
            return

        comandos_base = [
            ("MongoDB::Atlas::APIKey", "MongoDB-Atlas-APIKey", 2),
            ("MongoDB::Atlas::AccessListAPIKey", "MongoDB-Atlas-AccessListAPIKey", 2),
            ("MongoDB::Atlas::AlertConfiguration", "MongoDB-Atlas-AlertConfiguration", 2),
            ("MongoDB::Atlas::CloudBackUpRestoreJobs", "MongoDB-Atlas-CloudBackUpRestoreJobs", 2),
            ("MongoDB::Atlas::CloudBackupSchedule", "MongoDB-Atlas-CloudBackupSchedule", 2),
            ("MongoDB::Atlas::CloudBackupSnapshot", "MongoDB-Atlas-CloudBackupSnapshot", 2),
            ("MongoDB::Atlas::Cluster", "MongoDB-Atlas-Cluster", 2),
            ("MongoDB::Atlas::CustomDBRole", "MongoDB-Atlas-CustomDBRole", 2),
            ("MongoDB::Atlas::DatabaseUser", "MongoDB-Atlas-DatabaseUser", 2),
            ("MongoDB::Atlas::EncryptionAtRest", "MongoDB-Atlas-EncryptionAtRest", 2),
            ("MongoDB::Atlas::MaintenanceWindow", "MongoDB-Atlas-MaintenanceWindow", 2),
            ("MongoDB::Atlas::PrivateEndpointAWS", "MongoDB-Atlas-PrivateEndpointAWS", 1),
            ("MongoDB::Atlas::PrivateEndpointService", "MongoDB-Atlas-PrivateEndpointService", 1),
            ("MongoDB::Atlas::Project", "MongoDB-Atlas-Project", 2),
            ("MongoDB::Atlas::ProjectIpAccessList", "MongoDB-Atlas-ProjectIpAccessList", 2),
            ("MongoDB::Atlas::ServerlessInstance", "MongoDB-Atlas-ServerlessInstance", 2),
            ("MongoDB::Atlas::ServerlessPrivateEndpoint", "MongoDB-Atlas-ServerlessPrivateEndpoint", 2)
        ]

        comandos = []
        for alias, public_suffix, version in comandos_base:
            comando = f"""aws cloudformation activate-type \\
--region us-east-1 \\
--type RESOURCE \\
--type-name-alias {alias} \\
--public-type-arn arn:aws:cloudformation:us-east-1::type/resource/bb989456c78c398a858fef18f2ca1bfc1fbba082/{public_suffix} \\
--execution-role-arn {arn_personalizado} \\
--major-version {version}"""
            comandos.append(comando)

        mostrar_comando("\\n\\n".join(comandos), "Activar MONGO")
        
    
    btn_validar_arn = ctk.CTkButton(
    ventana_mongo,
    text="VALIDAR ARN DE ROL 'MONGODB'",
    command=lambda: copiar_comando_mongo("aws iam get-role --role-name OPS0001001-mongodb-atlas-extensions-role"),
    font=("Arial", 11, "bold"),
    width=9
    )
    btn_validar_arn.pack(pady=5)
    btn_validar_arn.bind("<Enter>", on_enter)
    btn_validar_arn.bind("<Leave>", on_leave)
        
    
    
    btn_validar = ctk.CTkButton(
        ventana_mongo,
        text="VALIDAR ESTADO DE EXTENSIONES",
        command=lambda: copiar_comando_mongo(comando_validar),


        font=("Arial", 11, "bold"),
        width=9
    )
    btn_validar.pack(pady=5)
    btn_validar.bind("<Enter>", on_enter)
    btn_validar.bind("<Leave>", on_leave)

    btn_activar = ctk.CTkButton(
        ventana_mongo,
        text="ACTIVAR EXTENSIONES",
        command=activar_mongo,


        font=("Arial", 11, "bold"),
        width=9
    )
    btn_activar.pack(pady=5)
    btn_activar.bind("<Enter>", on_enter)
    btn_activar.bind("<Leave>", on_leave)


    
def generar_ha_info():
    texto = """Cordial saludo. A continuación, se detalla el procedimiento para ambientes productivos:

1. En Helix, crear una Petición de Cambio usando la plantilla:
   Cambio en Producción.Manual.Estandar.Administrativo_Nube AWS - GIOTI.Riesgo = 1

2. Llenar la información obligatoria en el apartado de descripción.

3. Seleccionar los grupos correspondientes:
   - Coordinador de cambios: quien solicita el proceso.
   - Gestores de cambios: OC INTEGRADA OPERACION TI 2 CYGNUS APROBADORES CAMBIOS TI

4. Editar las fechas programadas (no modificar las fechas reales).

5. Guardar la petición y cambiar su estado de 'Borrador' a 'Programado para aprobación'.

Muchas gracias.
"""
    root.clipboard_clear()
    root.clipboard_append(texto)
    root.update()
    messagebox.showinfo("INFO CRQs", "✅ Plantilla para CRQ's copiada al portapapeles.")
    
    

def llenar_plantilla(datos, plantilla_path, salida_path):
    """
    Llena una plantilla de Word con los datos extraídos.
    
    Abre la plantilla de Word, itera a través de sus párrafos y reemplaza
    los marcadores de posición (ej. `{{ID del evento}}`) con los datos
    proporcionados. Luego, guarda y abre el nuevo documento.
    """
    try:
        doc = Document(plantilla_path) # Abre la plantilla de Word.
        for parrafo in doc.paragraphs: # Itera sobre cada párrafo del documento.
            for campo, valor in datos.items(): # Itera sobre cada campo y valor del diccionario de datos.
                marcador = f"{{{{{campo}}}}}" # Crea el marcador de posición a buscar.
                if marcador in parrafo.text: # Verifica si el marcador está en el texto del párrafo.
                    for run in parrafo.runs: # Itera sobre las "runs" (fragmentos de texto) del párrafo.
                        run.text = run.text.replace(marcador, valor) # Reemplaza el marcador con el valor.
        doc.save(salida_path) # Guarda el documento en la ruta de salida.
        os.startfile(salida_path) # Abre el archivo con el programa predeterminado del sistema.
        messagebox.showinfo("Éxito", f"Documento generado correctamente:\n{salida_path}") # Muestra un mensaje de éxito.
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el documento.\nDetalles: {str(e)}") # Maneja y muestra errores si la generación falla.

def iniciar_proceso_crq():
    """Inicia el proceso para la plantilla CRQ."""
    iniciar_proceso()

def iniciar_proceso_task():
    """Inicia el proceso para la plantilla TASK."""
    plantilla_path = obtener_ruta_recurso("Plantilla CYGNUS TAREA CYGNUS.docx") # Obtiene la ruta de la plantilla TASK.
    if not os.path.exists(plantilla_path):
        messagebox.showerror("Error", f"No se encontró la plantilla en {plantilla_path}") # Muestra un error si la plantilla no existe.
        return
    nombre_archivo = f"TASK_{datetime.now().strftime('%d-%m-%Y_%H_%M_%S')}.docx" # Genera el nombre del archivo.
    salida_path = filedialog.asksaveasfilename(
        initialfile=nombre_archivo,
        defaultextension=".docx", # Extensión predeterminada.
        filetypes=[("Archivos Word", "*.docx")],
        title="Guardar documento Word"
    )
    if not salida_path:
        messagebox.showwarning("Aviso", "No se guardó el documento.")
        return
    id_task = os.path.splitext(os.path.basename(salida_path))[0] # Obtiene el ID del archivo.
    datos = {
    "Fecha de Proceso": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    "ID del TASK": id_task
    }
    llenar_plantilla(datos, plantilla_path, salida_path)

def iniciar_proceso_pods():
    """Inicia el proceso para la plantilla PODs."""
    plantilla_path = obtener_ruta_recurso("Plantilla CYGNUS PODs.docx") # Obtiene la ruta de la plantilla PODs.
    if not os.path.exists(plantilla_path):
        messagebox.showerror("Error", f"No se encontró la plantilla en {plantilla_path}")
        return
    nombre_archivo = f"PODs_{datetime.now().strftime('%d-%m-%Y_%H_%M_%S')}.docx" # Genera el nombre del archivo.
    salida_path = filedialog.asksaveasfilename(
        initialfile=nombre_archivo,
        defaultextension=".docx",
        filetypes=[("Archivos Word", "*.docx")],
        title="Guardar documento Word"
    )
    if not salida_path:
        messagebox.showwarning("Aviso", "No se guardó el documento.") # Muestra un aviso si el usuario cancela.
        return
    id_pod = os.path.splitext(os.path.basename(salida_path))[0] # Obtiene el ID del archivo.
    datos = {
        "Fecha de Proceso": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "ID del POD": id_pod,
        "ID del EVENTO/INCIDENTE": id_pod
    }
    llenar_plantilla(datos, plantilla_path, salida_path)

# Funciones de hover
# Función: al pasar el mouse por encima
def on_enter(event):
    """Cambia el color de fondo de un widget al pasar el mouse por encima."""
    widget = event.widget
    if not hasattr(widget, 'original_fg_color'):
        widget.original_fg_color = widget.cget("fg_color")
    widget.configure(fg_color="#9C9C9C")  # color dorado

# Función: al salir el mouse
def on_leave(event):
    """Restaura el color de fondo de un widget al salir el mouse."""
    widget = event.widget
    if hasattr(widget, 'original_fg_color'):
        widget.configure(fg_color=widget.original_fg_color)

# Función: hover sobre imagen
def on_enter_image(event):
    global tooltip_label
    event.widget.configure(border_color="white", border_width=2)  # activa el borde
    tooltip_label = ctk.CTkLabel(master=frame_img, text="Haz clic para ver enlaces Cygnus",
                                 font=("Arial", 10), fg_color="#333333", text_color="white")
    tooltip_label.place(relx=0.5, rely=0.95, anchor="s")  # posición centrada abajo

def on_leave_image(event):
    global tooltip_label
    event.widget.configure(border_color="gray", border_width=0)  # desactiva el borde
    if tooltip_label:
        tooltip_label.destroy()
        tooltip_label = None



def mostrar_telefonos():
    # Obtener la posición actual de la ventana principal
    x = root.winfo_x()
    y = root.winfo_y()
    ancho_principal = root.winfo_width()
    nueva_x = x + ancho_principal

    # Verificar si la ventana ya está abierta
    for ventana in ventanas_hijas:
        if ventana.winfo_exists() and ventana.title() == "Contactos Telefónicos":
            ventana.geometry(f"+{nueva_x}+{y}")
            ventana.lift()
            ventana.focus_force()
            return

    # Crear nueva ventana
    ventana_tel = ctk.CTkToplevel(root)
    ventana_tel.title("Contactos Telefónicos")
    ventanas_hijas.append(ventana_tel)
    ventana_tel.transient(root)
    ventana_tel.geometry(f"530x520+{nueva_x}+{y}")
    ventana_tel.configure(fg_color="black")

    # Crear tabla
    columnas = ("Nombre", "Correo", "Teléfono")
    tabla = ttk.Treeview(ventana_tel, columns=columnas, show="headings")
    tabla.pack(expand=True, fill="both", padx=10, pady=5)
    
    

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, anchor="w")


    # Copiar contacto al hacer doble clic
    def copiar_contacto(event):
        item = tabla.selection()
        if item:
            valores = tabla.item(item, "values")
            if "---" in valores[0] or all(v == "" for v in valores):
                return
            texto = f"{valores[0]} ({valores[1]}) - {valores[2]}"
            ventana_tel.clipboard_clear()
            ventana_tel.clipboard_append(texto)
            ventana_tel.update()
            messagebox.showinfo("Copiado", f"Contacto copiado:\n\n{texto}")

    tabla.bind("<Double-1>", copiar_contacto)


    for col in columnas:
        tabla.heading(col, text=col)
        max_width = max(
            [len(str(tabla.set(item, col))) for item in tabla.get_children()] + [len(col)]
        )
        tabla.column(col, anchor="w", width=max_width * 8)  # El ancho se ajustará automáticamente

    # Definir listas de contactos
    contactos_emma = sorted([
        ("Ana Marcela Noreña Ramirez", "amnorena@bancolombia.com.co", "310-468-1239"),
        ("Luis Orlando Monsalve Uribe", "luimonsa@bancolombia.com.co", "300-601-9457"),
        ("Doreliz Coromoto Graffe Toledo", "dgraffe@bancolombia.com.co", "301-362-9499"),
        ("Luis Eduardo Aviles Argel", "laviles@bancolombia.com.co", "312-779-0482"),
        ("Yony Alejandro Castaneda Ramirez", "ycastane@bancolombia.com.co", "301-362-9499"),
        ("Brahyan Francisco Galvan Alvarez", "bgalvan@bancolombia.com.co", "320-568-3984"),
        ("Luiggy Andres Arrieta Moreno", "larrita@bancolombia.com.co", "301-470-2350"),
        ("Juan Diego Gomez Vasquez", "juadigom@bancolombia.com.co", "313-600-9646"),
        ("Albert Moscoso Orrego", "amoscoso@bancolombia.com.co", "321-848-2601"),
    ], key=lambda x: x[0])

    contactos_tam_aws = sorted([
        ("Jose Luis Caro", "crojose@amazon.com", "300-814-6068"),
        ("Fernando Pelaez", "fpelaezt@amazon.com", "300-518-0900"),
    ], key=lambda x: x[0])

    contactos_skillfullers = sorted([
        ("Nilson Jahir Gonzalez Larrota", "nelgonza@bancolombia.com.co", "300-463-6684"),
        ("Yonier Manuel Asprilla Gómez", "yasprill@bancolombia.com.co", "315-484-4692"),
        ("Javier Fernando Camacho Duarte", "jacamach@bancolombia.com.co", "300-489-1128"),
        ("Juan Pablo Reyes Negrette", "jpreyes@bancolombia.com.co", "315-067-5677"),
        ("Ricardo Leon Pelaez Perez", "rpelaez@bancolombia.com.co", "310-279-2585"),
        ("Monica Alexandra Vasquez Ochoa", "moavasqu@bancolombia.com.co", "305-283-6119"),
        ("Mauricio Bohorquez Orozco", "maubohor@bancolombia.com.co", "322-369-3310"),
        ("Wilson Hernán Salazar Herrera", "wsalazar@bancolombia.com.co", "305-305-6917 - 305-895-1001"),
        ("Juan David Valencia Toro", "juvalenc@bancolombia.com.co", "301-797-9089"),
        ("Fernando Ordoñez Bravo", "fordonez@bancolombia.com.co", "315-059-1936"),
    ], key=lambda x: x[0])

    # Insertar contactos por categoría
    def insertar_categoria(nombre_categoria, lista_contactos):
        # Insertar subtítulo con estilo
        tabla.insert("", "end", values=(f"--- {nombre_categoria} ---", "", ""), tags=(nombre_categoria,))

        # Aplicar estilo visual según la categoría
        if nombre_categoria == "EMMA":
            tabla.tag_configure(nombre_categoria, font=("Arial", 13, "bold"), background="#e28080", foreground="#000000")
        elif nombre_categoria == "TAM AWS":
            tabla.tag_configure(nombre_categoria, font=("Arial", 13, "bold"), background="#e6b459", foreground="#000000")
        elif nombre_categoria == "SKILLFULLERS":
            tabla.tag_configure(nombre_categoria, font=("Arial", 13, "bold"), background="#668aec", foreground="#000000")




        # Insertar contactos
        for contacto in lista_contactos:
            tabla.insert("", "end", values=contacto)

        # Separador visual
        tabla.insert("", "end", values=("", "", ""))

    insertar_categoria("EMMA", contactos_emma)
    insertar_categoria("TAM AWS", contactos_tam_aws)
    insertar_categoria("SKILLFULLERS", contactos_skillfullers)

# 
    ajustar_columnas1(tabla)
# tar columnas automáticamente ignorando separadores
def ajustar_columnas1(tabla):
    multiplicadores = {
        "Nombre": 9,
        "Correo": 9,
        "Teléfono": 3
    }
    for col in tabla["columns"]:
        valores_validos = [
            str(tabla.set(item, col))
            for item in tabla.get_children()
            if "---" not in tabla.item(item, "values")[0] and tabla.item(item, "values")[0].strip() != ""
        ]
        max_width = max([len(v) for v in valores_validos] + [len(col)])
        tabla.column(col, width=max_width * multiplicadores.get(col, 7))  # 7 por defecto si no está en el dict

    # Estilo visual con más espacio vertical
    estilo = ttk.Style()
    estilo.theme_use("default")
    estilo.configure("Treeview", background="white", foreground="black", rowheight=28, fieldbackground="white")
    estilo.map("Treeview", background=[("selected", "gray")])



    # Ordena alfabéticamente las listas de contactos antes de insertarlas.
    contactos_emma = sorted([
        ("Ana Marcela Noreña Ramirez", "amnorena@bancolombia.com.co", "310-468-1239"),
        ("Luis Orlando Monsalve Uribe", "luimonsa@bancolombia.com.co", "300-601-9457"),
        ("Doreliz Coromoto Graffe Toledo", "dgraffe@bancolombia.com.co", "301-362-9499"),
        ("Luis Eduardo Aviles Argel", "laviles@bancolombia.com.co", "312-779-0482"),
        ("Yony Alejandro Castaneda Ramirez", "ycastane@bancolombia.com.co", "301-362-9499"), #
        ("Brahyan Francisco Galvan Alvarez", "bgalvan@bancolombia.com.co", "320-568-3984"),
        ("Luiggy Andres Arrieta Moreno", "larrita@bancolombia.com.co", "301-470-2350"),
        ("Juan Diego Gomez Vasquez", "juadigom@bancolombia.com.co", "313-600-9646"),
        ("Albert Moscoso Orrego", "amoscoso@bancolombia.com.co", "321-848-2601"),
    ], key=lambda x: x[0])
    
    contactos_tam_aws = sorted([
        ("Jose Luis Caro", "crojose@amazon.com", "300-814-6068"),
        ("Fernando Pelaez", "fpelaezt@amazon.com", "300-518-0900"),
    ], key=lambda x: x[0])
    
    contactos_skillfullers = sorted([
        ("Nilson Jahir Gonzalez Larrota", "nelgonza@bancolombia.com.co", "300-463-6684"), #
        ("Yonier Manuel Asprilla Gómez", "yasprill@bancolombia.com.co", "315-484-4692"),
        ("Javier Fernando Camacho Duarte", "jacamach@bancolombia.com.co", "300-489-1128"),
        ("Juan Pablo Reyes Negrette", "jpreyes@bancolombia.com.co", "315-067-5677"),
        ("Ricardo Leon Pelaez Perez", "rpelaez@bancolombia.com.co", "310-279-2585"),
        ("Monica Alexandra Vasquez Ochoa", "moavasqu@bancolombia.com.co", "305-283-6119"),
        ("Mauricio Bohorquez Orozco", "maubohor@bancolombia.com.co", "322-369-3310"),
        ("Wilson Hernán Salazar Herrera", "wsalazar@@bancolombia.com.co", "305-305-6917 - 305-895-1001"), #
        ("Juan David Valencia Toro", "juvalenc@bancolombia.com.co", "301-797-9089"),
        ("Fernando Ordoñez Bravo", "fordonez@bancolombia.com.co", "315-059-1936"),
    ], key=lambda x: x[0])

    tabla.insert("", "end", values=(f"--- {nombre_categoria} ---", "", ""))
    for contacto in lista_contactos:
        tabla.insert("", "end", values=contacto)
    # Separador visual más limpio
    tabla.insert("", "end", values=(" ", " ", " "))
        

    insertar_categoria("EMMA", contactos_emma)
    insertar_categoria("TAM AWS", contactos_tam_aws)
    insertar_categoria("SKILLFULLERS", contactos_skillfullers)

    # Estilo visual
    estilo = ttk.Style()
    estilo.theme_use("default")
    estilo.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
    estilo.map("Treeview", background=[("selected", "gray")])


def ingresar_a_cluster():
    """
    Pide un nombre de cluster, genera un comando de AWS CLI y lo copia al portapapeles.
    """
    nombre_cluster = simpledialog.askstring("Nombre del Cluster", "Ingresa el nombre del cluster:", parent=root) # Muestra un diálogo de entrada.
    if not nombre_cluster: # Si se cancela, sale de la función.
        return
    comando = f"aws eks update-kubeconfig --name {nombre_cluster} --region us-east-1"
    copiar_comando(comando)

def listar_cluster():
    """Genera y copia el comando para listar clusters."""
    comando = "aws eks list-clusters --region us-east-1"
    root.clipboard_clear()
    root.clipboard_append(comando)
    root.update()
    messagebox.showinfo("Copiado", "El comando ha sido copiado al portapapeles.")


def mostrar_comando(comando, titulo):
    """Muestra un cuadro de texto con un comando y lo copia automáticamente al portapapeles."""
    
    ventana_comando = ctk.CTkToplevel(root)
    ventana_comando.title(f"Comando {titulo}")
    ventana_comando.geometry("800x400")
    ventana_comando.configure(fg_color="black")
    ventana_comando.transient(root)  # ← Ayuda a mantenerla en primer plano

    # Cuadro de texto
    cuadro_texto = CTkTextbox(ventana_comando, wrap="word", font=("Arial", 10))
    cuadro_texto.pack(expand=True, fill="both", padx=10, pady=5)
    cuadro_texto.insert("1.0", comando)
    cuadro_texto.configure(state="normal")

    # Copiar automáticamente al portapapeles
    ventana_comando.clipboard_clear()
    ventana_comando.clipboard_append(comando)
    ventana_comando.update()
    messagebox.showinfo("Copiado", "El comando ha sido copiado al portapapeles.")

    # Botón para copiar manualmente
    boton_copiar = ctk.CTkButton(
        ventana_comando,
        text="Copiar al portapapeles",
        command=lambda: copiar_comando(comando),  # Asegúrate de tener esta función definida
        font=("Arial", 11, "bold")
    )
    boton_copiar.pack(pady=1)

def copiar_comando(comando):
    """Copia un comando al portapapeles y muestra un mensaje de confirmación."""
    root.clipboard_clear()
    root.clipboard_append(comando)
    root.update()
    messagebox.showinfo("Copiado", "El comando ha sido copiado al portapapeles.")

def generar_comando_kubectl():
    """
    Muestra la ventana del generador de comandos de kubectl.
    """
    # Obtener la posición actual de la ventana principal
    x = root.winfo_x()
    y = root.winfo_y()
    ancho_principal = root.winfo_width()
    
    # Calcular la nueva posición de la ventana hija
    nueva_x = x + ancho_principal
    
    # Verificar si la ventana ya está abierta
    for ventana in ventanas_hijas:
        if ventana.winfo_exists() and ventana.title() == "GENERADOR DE COMANDOS":
            # Reposicionar la ventana
            ventana.geometry(f"+{nueva_x}+{y}") #
            # Enfocarla
            ventana.lift()
            ventana.focus_force()
            return
            
    # Si no existe, crear una nueva ventana
    # Crear la ventana
    ventana_opciones = ctk.CTkToplevel(root)
    ventana_opciones.title("GENERADOR DE COMANDOS")
    ventanas_hijas.append(ventana_opciones)
    ventana_opciones.transient(root)
    ventana_opciones.geometry(f"230x540+{nueva_x}+{y}")
    ventana_opciones.configure(fg_color="#000000")  # ← Aquí estaba el error

    # Crear el frame principal
    frame_kubectl = ctk.CTkFrame(ventana_opciones, fg_color="#000000")
    frame_kubectl.pack(pady=1, fill="x", padx=20)
    frame_kubectl.columnconfigure(0, weight=1)
    frame_kubectl.columnconfigure(1, weight=1)



    def generar_comando_ns():
        namespace = simpledialog.askstring("Namespace", "Ingresa el namespace:", parent=root)
        if namespace:
            comando = f"kubectl get events --sort-by=.metadata.creationTimestamp -n {namespace} | grep -e Warning"
            root.clipboard_clear()
            root.clipboard_append(comando)
            root.update()
            messagebox.showinfo("Copiado", "El comando ha sido copiado al portapapeles.")
        
        
    def eliminar_pods():
        pods_input = simpledialog.askstring("Pods", "Ingresa los nombres de los pods (puedes pegar la salida de 'kubectl get pods'):", parent=root) # Pide los nombres de los pods.
        if not pods_input:
            return
        namespace_input = simpledialog.askstring("Namespace", "Ingresa el namespace:", parent=root) # Pide el namespace.
        if not namespace_input:
            return
        pod_lines = pods_input.strip().splitlines()
        pods = [line.split()[0] for line in pod_lines if line.strip()] # Extrae los nombres de los pods.
        namespace = namespace_input.strip()
        comandos = "\n".join([f"kubectl delete pod -n {namespace} {pod}" for pod in pods])
        mostrar_comando(comandos, "Eliminar PODs")

    def generar_logs():
        pods_input = simpledialog.askstring("Pods", "Ingresa los nombres de los pods (puedes pegar la salida de 'kubectl get pods'):", parent=root)
        if not pods_input:
            return
        namespace_input = simpledialog.askstring("Namespace", "Ingresa el namespace:", parent=root) # Pide el namespace.
        if not namespace_input:
            return
        pod_lines = pods_input.strip().splitlines()
        pods = [line.split()[0] for line in pod_lines if line.strip()]
        namespace = namespace_input.strip()
        comando = "for pod in \\\n" # Construye el comando de logs.
        for pod in pods:
            comando += f"     {pod} \\\n" #
        comando += f";\ndo\n"
        comando += f'    echo "Logs for pod: $pod"\n'
        comando += f"    kubectl logs -n {namespace} $pod |\n"
        comando += f"    grep -i -E 'error|failed|Failed|Exception|stopped|exception|statuscode|ready|peering|undefined|url|messageid|database|ssl|detected|unable|Unable|certificate|certificado|certificates|unknown|status|504|500|GATEWAY_TIMEOUT|rejected|fatal|GATEWAY|TIMEOUT|KEYSTORE|null|RBAC|denied|SSL|ssl|INVALIDA|invalida|secret|Error|error|ERROR|conficts|refused|REFUSED|jwt|JWT|Server Error|not found|invalid|ready'\n"
        comando += "done"
        mostrar_comando(comando, "Logs")
            

    def pods_no_running():
        comando = "kubectl get po -A | grep -v Running" #
        copiar_comando(comando)

    def pods_live_monitor():
        pods_input = simpledialog.askstring("Pods", "Ingresa los nombres de los pods (puedes pegar la salida de 'kubectl get pods'):", parent=root)
        if not pods_input:
            return
        namespace_input = simpledialog.askstring("Namespace", "Ingresa el namespace:", parent=root)
        if not namespace_input:
            return
        pod_lines = pods_input.strip().splitlines() #
        pods = [line.split()[0] for line in pod_lines if line.strip()]
        namespace = namespace_input.strip()
        grep_pods = " |grep " + " ".join([f"-e {pod}" for pod in pods])
        comando = f"while true; do kubectl get po -n {namespace}{grep_pods}; echo \"\"; echo \"Actualizando...\"; echo \"\"; sleep 5; done" #
        mostrar_comando(comando, "LIVE")


    
    label_eks = ctk.CTkLabel(frame_kubectl, text="EKS", font=("Arial", 12, "bold"), fg_color="#000000")
    label_eks.grid(row=0, column=0, columnspan=2,   pady=(3, 0), sticky="ew")

    # 🔹 PODs LIVE y TOP POD    
    frame_pods = ctk.CTkFrame(frame_kubectl, fg_color="#000000")
    frame_pods.grid(row=1, column=0, columnspan=2, pady=1, sticky="ew")


    # Configurar 3 columnas
    frame_pods.columnconfigure(0, weight=1)
    frame_pods.columnconfigure(1, weight=1)
    frame_pods.columnconfigure(2, weight=1)



    # Botón LIVE
    btn_pods_live = ctk.CTkButton(
        frame_pods,
        text="LIVE",
        command=pods_live_monitor,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold"),
        width=10
    )
    btn_pods_live.grid(row=0, column=0, padx=5, pady=0)



    # Botón TOP
    def generar_comando_top():
        namespace = simpledialog.askstring("Namespace", "Ingresa el namespace:", parent=root)
        if namespace:
            comando = f"kubectl.exe top pod -n {namespace}"
            copiar_comando(comando)

    btn_top_pod = ctk.CTkButton(
        frame_pods,
        text="TOP",
        command=generar_comando_top,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold"),
        width=20
    )
    btn_top_pod.grid(row=0, column=1, padx=5, pady=0)



    

    # Botón EVENTOS
    btn_ns = ctk.CTkButton(
        frame_pods,
        text="EVENTOS",
        command=generar_comando_ns,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold"),
        width=10
    )
    btn_ns.grid(row=0, column=2, padx=5, pady=0)




    # Frame contenedor para los botones
    frame_pods_logs = ctk.CTkFrame(frame_kubectl, fg_color="#000000")
    frame_pods_logs.grid(row=2, column=0, columnspan=2, pady=1, sticky="ew")

    # Configurar 3 columnas para centrar los botones
    frame_pods_logs.columnconfigure(0, weight=1)
    frame_pods_logs.columnconfigure(1, weight=1)



    # Botón DELETE
    btn_eliminar_pods = ctk.CTkButton(
        frame_pods_logs,
        text="DELETE",
        command=eliminar_pods,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold"),
        width=20
    )
    btn_eliminar_pods.grid(row=0, column=0, padx=5, pady=0)





    # Botón LOGs GREP
    btn_logs = ctk.CTkButton(
        frame_pods_logs,
        text="LOGs GREP",
        command=generar_logs,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold"),
        width=20
    )
    btn_logs.grid(row=0, column=1, padx=5, pady=0)



    # Botón PODs NO RUNNING
    btn_pods_no_running = ctk.CTkButton(
        frame_pods_logs,
        text="PODs NO RUNNING",
        command=pods_no_running,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold"),
        width=10
    )
    btn_pods_no_running.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")



    # Inicio de la reubicación
    # Frame para el título y los botones de CLUSTER


    frame_cluster = ctk.CTkFrame(frame_kubectl, fg_color="#000000")
    frame_cluster.grid(row=3, column=0, columnspan=2, pady=1, sticky="ew")
    
    frame_cluster.columnconfigure(0, weight=1)
    frame_cluster.columnconfigure(1, weight=1)

    label_cluster = ctk.CTkLabel(frame_cluster, text="CLUSTER", font=("Arial", 12, "bold"), fg_color="#000000")
    label_cluster.grid(row=0, column=0, columnspan=2,   pady=(3, 0), sticky="ew")
    
    


    # Botón LISTAR
    btn_listar_cluster = ctk.CTkButton(
        frame_cluster,
        text="LISTAR",
        command=listar_cluster,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold")
    )
    btn_listar_cluster.grid(row=1, column=0, padx=5, pady=(0, 5))

    # Botón INGRESAR
    btn_cluster = ctk.CTkButton(
        frame_cluster,
        text="INGRESAR",
        command=ingresar_a_cluster,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold")
    )
    btn_cluster.grid(row=1, column=1, padx=5, pady=(0, 5))



    # Título de la sección
    label_deployment = ctk.CTkLabel(frame_kubectl, text="DEPLOYMENT", font=("Arial", 12, "bold"), fg_color="#000000")
    label_deployment.grid(row=8, column=0, columnspan=2,   pady=(3, 0), sticky="ew")
    

    frame_deployment = ctk.CTkFrame(frame_kubectl, fg_color="#000000")
    frame_deployment.grid(row=9, column=0, columnspan=2, pady=1, sticky="ew")

    # Configurar columnas para centrar los botones
    frame_deployment.columnconfigure(0, weight=1)
    frame_deployment.columnconfigure(1, weight=1)

    
    # Botón LISTAR
    def listar_deployment():
        ns = simpledialog.askstring("Namespace", "Ingresa el namespace:", parent=root)
        if ns:
            copiar_comando(f"kubectl get deployment -n {ns}")
    

    # Botón LISTAR
    btn_listar_d = ctk.CTkButton(
        frame_deployment,
        text="LISTAR",
        command=listar_deployment,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold")
    )
    btn_listar_d.grid(row=0, column=0, padx=5, pady=5)

    
    # Botón DESCRIBIR
    def describir_deployment():
        ns = simpledialog.askstring("Namespace", "Enter the namespace:", parent=root)
        name = simpledialog.askstring("Deployment", "Enter the deployment name:", parent=root)
        if ns and name:
            copiar_comando(f"kubectl describe deployment -n {ns} {name}")
    

    # Botón DESCRIBIR
    btn_describir_d = ctk.CTkButton(
        frame_deployment,
        text="DESCRIBIR",
        command=describir_deployment,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold")
    )
    btn_describir_d.grid(row=0, column=1, padx=5, pady=5)

    
    # Título de la sección CONFIG MAP
    label_configmap = ctk.CTkLabel(frame_kubectl, text="CONFIG MAP", font=("Arial", 12, "bold"), fg_color="#000000")
    label_configmap.grid(row=10, column=0, columnspan=2,   pady=(3, 0), sticky="ew")
    

    # Frame contenedor para los botones
    frame_configmap = ctk.CTkFrame(frame_kubectl, fg_color="#000000")
    frame_configmap.grid(row=11, column=0, columnspan=2, pady=1, sticky="ew")

    # Configurar columnas para centrar los botones
    frame_configmap.columnconfigure(0, weight=1)
    frame_configmap.columnconfigure(1, weight=1)

    
    # Botón LISTAR CONFIG MAP
    def listar_configmap():
        ns = simpledialog.askstring("Namespace", "Enter the namespace:", parent=root)
        if ns:
            copiar_comando(f"kubectl.exe get configmaps -n {ns}")
    

    # Botón LISTAR
    btn_listar_c = ctk.CTkButton(
        frame_configmap,
        text="LISTAR",
        command=listar_configmap,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold")
    )
    btn_listar_c.grid(row=0, column=0, padx=5, pady=5)

    
    # Botón DESCRIBIR CONFIG MAP
    def describir_configmap():
        ns = simpledialog.askstring("Namespace", "Enter the namespace:", parent=root)
        name = simpledialog.askstring("ConfigMap", "Enter the configmap name:", parent=root)
        if ns and name:
            copiar_comando(f"kubectl.exe describe configmap {name} -n {ns}")
    

    # Botón DESCRIBIR
    btn_describir_c = ctk.CTkButton(
        frame_configmap,
        text="DESCRIBIR",
        command=describir_configmap,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold")
    )
    btn_describir_c.grid(row=0, column=1, padx=5, pady=5)


    






    
    # Crear un frame contenedor centrado en el grid
    frame_cmds = ctk.CTkFrame(frame_kubectl, fg_color="#000000")
    frame_cmds.grid(row=15, column=0, columnspan=2, pady=1, sticky="ew")

    # Centrar el contenido dentro del frame
    frame_cmds.columnconfigure(0, weight=1)
    frame_cmds.columnconfigure(1, weight=1)


    # Título EXPORTAR LOGS
    label_exportlogs = ctk.CTkLabel(frame_kubectl, text="EXPORTAR LOGS", font=("Arial", 12, "bold"), fg_color="#000000")
    label_exportlogs.grid(row=12, column=0, columnspan=2, pady=(3, 0), sticky="ew")
    

    # Frame contenedor para los botones
    frame_cmds = ctk.CTkFrame(frame_kubectl, fg_color="#000000")
    frame_cmds.grid(row=13, column=0, columnspan=2, pady=(5, 10), sticky="ew")

    # Configurar columnas para centrar los botones
    frame_cmds.columnconfigure(0, weight=1)
    frame_cmds.columnconfigure(1, weight=1)


    
    
    def generar_bash_logs_grep():
        pods_input = simpledialog.askstring("Pods", "Pega la salida de 'kubectl get pods':", parent=root)
        if not pods_input:
            return
        namespace_input = simpledialog.askstring("Namespace", "Ingresa el namespace:", parent=root)
        if not namespace_input:
            return

        pod_lines = pods_input.strip().splitlines()
        namespace = namespace_input.strip()

        nombres_pods = []
        for line in pod_lines:
            partes = line.strip().split()
            if partes:
                nombres_pods.append(partes[0])

        pods_str = " \\\n    ".join(nombres_pods)
        grep_expr = (
            "error|failed|Failed|Exception|stopped|exception|statuscode|ready|peering|undefined|url|messageid|database|ssl|"
            "detected|unable|Unable|certificate|certificado|certificates|unknown|status|504|500|GATEWAY_TIMEOUT|rejected|"
            "fatal|GATEWAY|TIMEOUT|KEYSTORE|null|RBAC|denied|SSL|ssl|INVALIDA|invalida|secret|Error|error|ERROR|conficts|"
            "refused|REFUSED|jwt|JWT|Server Error|not found|invalid|ready"
        )

        bash_script = f"""for pod in {pods_str} ; do
        echo "Logs for pod: $pod"
        kubectl logs -n {namespace} $pod | grep -i -E '{grep_expr}' > $pod.txt
    done"""


        ventana_bash = ctk.CTkToplevel(root)
        ventana_bash.transient(root)
        ventana_bash.lift()
        ventana_bash.focus_force()
        ventana_bash.title("Script Bash para Logs con GREP")
        ventana_bash.geometry("800x400")
        ventana_bash.configure(fg_color="black")  # ← fondo negro visible

        text_widget = CTkTextbox(ventana_bash, wrap="word", font=("Consolas", 10))
        text_widget.pack(expand=True, fill="both", padx=10, pady=5)
        text_widget.insert("1.0", bash_script)
        text_widget.configure(state="normal")

        boton_copiar = ctk.CTkButton(
            ventana_bash,
            text="Copiar al portapapeles",
            command=lambda: copiar_comando(bash_script),
            font=("Arial", 11, "bold")
        )
        boton_copiar.pack(pady=5)


        # Copiar al portapapeles automáticamente
        ventana_bash.clipboard_clear()
        ventana_bash.clipboard_append(bash_script)
        ventana_bash.update()
        messagebox.showinfo("Copiado", "El script ha sido copiado al portapapeles.")


    
    
    
    
    
    def exportar_logs_kubectl():
        pods_input = simpledialog.askstring("Pods", "Pega la salida de 'kubectl get pods':", parent=root)
        if not pods_input:
            return
        namespace_input = simpledialog.askstring("Namespace", "Ingresa el namespace:", parent=root)
        if not namespace_input:
            return

        pod_lines = pods_input.strip().splitlines()
        namespace = namespace_input.strip()
        comandos = []

        for line in pod_lines:
            partes = line.strip().split()
            if partes:
                nombre_pod = partes[0]
                comando = f"kubectl logs -n {namespace} {nombre_pod} > {nombre_pod}.txt"
                comandos.append(comando)

        comandos_final = "\n".join(comandos) + "\n"

        ventana_comandos = ctk.CTkToplevel(root)
        ventana_comandos.transient(root)
        ventana_comandos.lift()
        ventana_comandos.focus_force()
        ventana_comandos.title("Comandos Generados")
        ventana_comandos.geometry("800x400")
        ventana_comandos.configure(fg_color="black")

        text_widget = CTkTextbox(ventana_comandos, wrap="word", font=("Consolas", 10))
        text_widget.pack(expand=True, fill="both", padx=10, pady=5)
        text_widget.insert("1.0", comandos_final)
        text_widget.configure(state="normal")

        boton_copiar = ctk.CTkButton(
            ventana_comandos,
            text="Copiar al portapapeles",
            command=lambda: copiar_comando(comandos_final),
            font=("Arial", 11, "bold")
        )
        boton_copiar.pack(pady=5)


        # Insertar el contenido del script
        text_widget.insert("1.0", comandos_final)

        # Copiar al portapapeles automáticamente
        copiar_comando(comandos_final)


        # Configurar columnas del frame para que se distribuyan equitativamente
    frame_cmds.columnconfigure(0, weight=1)
    frame_cmds.columnconfigure(1, weight=1)


    #Botón CON GREP
    btn_cmd3 = ctk.CTkButton(
        frame_cmds,
        text="CON GREP",
        command=generar_bash_logs_grep,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold")
    )
    btn_cmd3.grid(row=0, column=0, padx=5, pady=0)

    # Botón SIN GREP
    btn_cmd4 = ctk.CTkButton(
        frame_cmds,
        text="SIN GREP",
        command=exportar_logs_kubectl,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold")
    )
    btn_cmd4.grid(row=0, column=1, padx=5, pady=0)



    label_cloudwatch = ctk.CTkLabel(frame_kubectl, text="EKS LOGs INSIGHTS", font=("Arial", 12, "bold"), fg_color="#000000")
    label_cloudwatch.grid(row=14, column=0, columnspan=2, pady=(3, 0), sticky="ew")
    
    # Frame contenedor para los botones
    frame_cloudwatch = ctk.CTkFrame(frame_kubectl, fg_color="#000000")
    frame_cloudwatch.grid(row=15, column=0, columnspan=2, pady=1, sticky="ew")

    # Configurar columnas para centrar los botones
    frame_cloudwatch.columnconfigure(0, weight=1)
    frame_cloudwatch.columnconfigure(1, weight=1)
    
    def generar_query_cloudwatch():
        pods_input = simpledialog.askstring("Pods", "Ingresa los nombres de los pods (puedes pegar la salida de 'kubectl get pods'):", parent=root)
        if not pods_input:
            return
        namespace_input = simpledialog.askstring("Namespace", "Ingresa el namespace:", parent=root)
        if not namespace_input:
            return
        pod_lines = pods_input.strip().splitlines()
        pods = [f'"{line.split()[0]}"' for line in pod_lines if line.strip()]
        namespace = namespace_input.strip()
        pods_string = ", ".join(pods)
        query = f"""
fields @timestamp, @message, kubernetes.pod_name
| filter kubernetes.namespace_name = "{namespace}"
| filter kubernetes.pod_name in [{pods_string}] and log like /error|failed|Failed|Exception|exception|statuscode|ready|peering|undefined|url|messageid|database|ssl|detected|unable|Unable|certificate|certificado|certificates|unknown|status|504|500|GATEWAY_TIMEOUT|rejected|fatal|GATEWAY|TIMEOUT|KEYSTORE|null|RBAC|denied|SSL|ssl|INVALIDA|invalida|secret|Error|error|ERROR|conficts|refused|REFUSED|jwt|JWT|Server Error|not found|invalid|ready/
| sort @timestamp desc
| limit 2000
"""
        mostrar_comando(query.strip(), "CloudWatch Query")
    # Botón LOGs CON GREP
    btn_logs_grep = ctk.CTkButton(
        frame_cloudwatch,
        text="CONGREP",
        command=generar_query_cloudwatch,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold"),
        #width=10
    )
    btn_logs_grep.grid(row=0, column=0, padx=5, pady=5)


    def generar_query_cloudwatch_conteo():
        query_conteo = """
filter log like /(?i)error|failed/
| stats count(*) as Error by kubernetes.pod_name, kubernetes.namespace_name
| sort Error desc
"""
        mostrar_comando(query_conteo.strip(), "CloudWatch Conteo")
        
    # Botón CONTEO ERRORES
    btn_conteo_errores = ctk.CTkButton(
        frame_cloudwatch,
        text="CONTEO",
        command=generar_query_cloudwatch_conteo,
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold"),
        #width=10
    )
    btn_conteo_errores.grid(row=0, column=1, padx=5, pady=5)

        
            
def copiar_script(texto):
    """Copia el texto dado al portapapeles y muestra un mensaje."""
    root.clipboard_clear()
    root.clipboard_append(texto)
    root.update()
    messagebox.showinfo("Comando Copiado", "El comando fué copiado.", parent=root)

def mostrar_script():
    """
    Muestra la ventana de scripts. Si ya está abierta, la enfoca y la reposiciona.
    """
    x = root.winfo_x()
    y = root.winfo_y()
    ancho_principal = root.winfo_width()
    nueva_x = x + ancho_principal
    
    for ventana in ventanas_hijas:
        if ventana.winfo_exists() and ventana.title() == "NUEVOS SCRIPTS":
            ventana.geometry(f"+{nueva_x}+{y}")
            ventana.lift()
            ventana.focus_force()
            return #

    ventana_script = ctk.CTkToplevel(root)
    ventana_script.title("NUEVOS SCRIPTS")
    ventanas_hijas.append(ventana_script)
    ventana_script.transient(root)
    ventana_script.geometry(f"230x470+{nueva_x}+{y}")
    ventana_script.configure(fg_color="#000000")  # ← ahora sí está completa

    # Crear el frame contenedor
    frame_script = ctk.CTkFrame(ventana_script, fg_color="black")
    frame_script.pack(expand=True, padx=5, pady=5)

    # Lista de textos para los botones
    button_texts = [("GOKU", "~/Documents/goku"),
                    ("INICIO", "~/Documents/inicio"), 
                    ("SCRIPT2", "SCRIPT2"), 
                    ("SCRIPT3", "SCRIPT3"), 
                    ("SCRIPT4", "SCRIPT4"), 
                    ("SCRIPT5", "SCRIPT5")]

    for text, texto_a_copiar in button_texts:
        btn = ctk.CTkButton(
            frame_script,
            text=text,
            command=lambda t=texto_a_copiar: copiar_script(t),
            height=BUTTON_HEIGHT, corner_radius=10,
            font=("Arial", 11, "bold")
        )
        btn.pack(pady=1, fill="x")
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

# Configuración de la ventana principal
root = ctk.CTk()
root.title("by PINKY")
root.geometry("220x520")
root.configure(fg_color="black")  # Un gris oscuro uniforme
root.resizable(False, False)

def actualizar_posicion_ventanas_hijas(event):
    """Actualiza la posición de las ventanas hijas cuando la ventana principal se mueve."""
    global ventanas_hijas
    for ventana_hija in ventanas_hijas:
        if ventana_hija.winfo_exists():
            # Obtiene la posición de la ventana principal
            x = root.winfo_x()
            y = root.winfo_y()
            # Calcula la nueva posición de la ventana hija (a la derecha de la principal)
            ancho_principal = root.winfo_width() #
            nueva_x = x + ancho_principal
            # Ajusta la geometría de la ventana hija
            ventana_hija.geometry(f"+{nueva_x}+{y}")
    # Limpia la lista de ventanas que ya no existen
    ventanas_hijas = [v for v in ventanas_hijas if v.winfo_exists()]

# Vincula el evento de configuración de la ventana principal a la función de actualización
root.bind("<Configure>", actualizar_posicion_ventanas_hijas)

# Estilo para los botones
style = ttk.Style()
style.configure("TButton", background="white", foreground="black", font=("Arial", 11, "bold"))

# Frame para el título y los botones de DOCUMENTACIÓN
frame_documentacion = ctk.CTkFrame(root, fg_color="#000000")  # azul oscuro
frame_documentacion.pack(pady=0)

label_titulo = ctk.CTkLabel(frame_documentacion, text="DOCUMENTACIÓN", font=("Arial", 12, "bold"), fg_color="#000000")
label_titulo.pack(pady=0)

frame_botones_doc = ctk.CTkFrame(frame_documentacion, fg_color="#000000")
frame_botones_doc.pack(pady=(1, 5))

btn_crq = ctk.CTkButton(frame_botones_doc, text="CRQ", command=iniciar_proceso_crq, height=BUTTON_HEIGHT, width=55, corner_radius=10, font=("Arial", 11, "bold"))
btn_crq.pack(side=tk.LEFT, padx=5)

btn_task = ctk.CTkButton(frame_botones_doc, text="TASK", command=iniciar_proceso_task, height=BUTTON_HEIGHT, width=55, corner_radius=10, font=("Arial", 11, "bold"))
btn_task.pack(side=tk.LEFT, padx=5)

btn_pods = ctk.CTkButton(frame_botones_doc, text="PODS", command=iniciar_proceso_pods, height=BUTTON_HEIGHT, width=55, corner_radius=10, font=("Arial", 11, "bold"))
btn_pods.pack(side=tk.LEFT, padx=5)
btn_pods.bind("<Enter>", on_enter)
btn_pods.bind("<Leave>", on_leave)

# Frame agrupado para EVENTO / INCIDENTE, MONGO, CIBER e INFO CRQs , fg_color="#000000")
frame_evento = ctk.CTkFrame(root, fg_color="#000000")
frame_evento.pack(pady=1)

# Botón EVENTO / INCIDENTE (se mantiene igual)
btn_evento = ctk.CTkButton(frame_evento, text="EVENTO / INCIDENTE", command=generar_evento_incidente, font=("Arial", 11, "bold"), height=BUTTON_HEIGHT, width=100, corner_radius=10)
btn_evento.pack(pady=1)

# Nuevo título "OTROS"
label_otros = ctk.CTkLabel(frame_evento, text="OTROS", font=("Arial", 12, "bold"), fg_color="#000000")
label_otros.pack(pady=(3, 0))

# Nuevo frame para agrupar MONGO, CIBER e INFO CRQs
frame_otros = ctk.CTkFrame(frame_evento, fg_color="#000000")
frame_otros.pack(pady=1)

frame_mongo_cloud = ctk.CTkFrame(frame_otros, fg_color="#000000")
frame_mongo_cloud.pack(pady=1)

btn_mongo = ctk.CTkButton(frame_mongo_cloud, text="MONGO", command=mostrar_mongo,
                          font=("Arial", 11, "bold"), height=BUTTON_HEIGHT, width=65, corner_radius=10)
btn_mongo.pack(side=tk.LEFT, padx=5)

btn_cloudshell = ctk.CTkButton(frame_mongo_cloud, text="CLOUDSHELL", command=mostrar_cloudshell,
                               font=("Arial", 11, "bold"), height=BUTTON_HEIGHT, width=85, corner_radius=10)
btn_cloudshell.pack(side=tk.LEFT, padx=5)

# Subframe para CIBER e INFO CRQs
frame_ciber_info = ctk.CTkFrame(frame_otros, fg_color="#000000")
frame_ciber_info.pack(pady=1)

btn_respuesta_ciber = ctk.CTkButton(frame_ciber_info, text="CIBER", command=generar_respuesta_ciber, font=("Arial", 11, "bold"), height=BUTTON_HEIGHT, width=70, corner_radius=10)
btn_respuesta_ciber.pack(side=tk.LEFT, padx=5)

btn_ha_info = ctk.CTkButton(frame_ciber_info, text="INFO CRQs", command=generar_ha_info, font=("Arial", 11, "bold"), height=BUTTON_HEIGHT, width=70, corner_radius=10)
btn_ha_info.pack(side=tk.LEFT, padx=5)
btn_ha_info.bind("<Enter>", on_enter)
btn_ha_info.bind("<Leave>", on_leave)






# Frame para el título y el botón de KUBECTL
frame_kubectl = ctk.CTkFrame(root, fg_color="#000000")
frame_kubectl.pack(pady=1, fill="x", padx=20)
frame_kubectl.columnconfigure(0, weight=1)

label_kubectl = ctk.CTkLabel(frame_kubectl, text="KUBECTL", font=("Arial", 12, "bold"), fg_color="#000000")
label_kubectl.grid(row=0, column=0,   pady=(3, 0), sticky="ew")

btn_kubectl = ctk.CTkButton(
    frame_kubectl,
    text="GENERADOR COMANDOS",
    command=generar_comando_kubectl,
    height=BUTTON_HEIGHT,
    corner_radius=10,
    width=38,
    font=("Arial", 11, "bold")
)
btn_kubectl.grid(row=1, column=0, padx=10, pady=0)
btn_kubectl.bind("<Enter>", on_enter)
btn_kubectl.bind("<Leave>", on_leave)

btn_script = ctk.CTkButton(
    frame_kubectl,
    text="SCRIPTS",
    command=mostrar_script,
    height=BUTTON_HEIGHT,
    corner_radius=10,
    width=8,
    font=("Arial", 11, "bold")
)
btn_script.grid(row=2, column=0, padx=40, pady=1)
btn_script.bind("<Enter>", on_enter)
btn_script.bind("<Leave>", on_leave)




# Frame para el título y los botones de CONTACTOS
# Frame para el título y los botones de CONTACTOS
frame_contactos = ctk.CTkFrame(root, fg_color="#000000")
frame_contactos.pack(pady=0, fill="x")
frame_contactos.columnconfigure(0, weight=1)
frame_contactos.columnconfigure(1, weight=1)

label_contactos = ctk.CTkLabel(frame_contactos, text="CONTACTOS", font=("Arial", 12, "bold"), fg_color="#000000")
label_contactos.grid(row=0, column=0, columnspan=2,   pady=(3, 0), sticky="ew")



# Sub-frame centrado para los botones TEL y NUESTROS
subframe_botones_contactos = ctk.CTkFrame(frame_contactos, fg_color="#000000")
subframe_botones_contactos.grid(row=1, column=0, columnspan=2,   pady=(3, 0))

btn_tel = ctk.CTkButton(subframe_botones_contactos, text="VARIOS", command=mostrar_telefonos,
                    width=8, font=("Arial", 11, "bold"),
 height=BUTTON_HEIGHT, corner_radius=10 )
btn_tel.pack(side=tk.LEFT, padx=5)
btn_tel.bind("<Enter>", on_enter)
btn_tel.bind("<Leave>", on_leave)


#cygnussssss

def ajustar_columnas(tabla):
    multiplicadores = {
        "Nombre": 5,
        "Correo": 6,
        "Teléfono": 3
    }

    for col in tabla["columns"]:
        valores_validos = [
            str(tabla.set(item, col))
            for item in tabla.get_children()
            if "---" not in tabla.item(item, "values")[0] and tabla.item(item, "values")[0].strip() != ""
        ]
        max_width = max([len(v) for v in valores_validos] + [len(col)])
        tabla.column(col, width=max_width * multiplicadores.get(col, 7))  # 7 por defecto si no está en el dict  # 7 por defecto si no está en el dict  # Ajusta el multiplicador si usas otra fuente


def mostrar_nuestros():
    # Obtener posición de la ventana principal
    x = root.winfo_x()
    y = root.winfo_y()
    ancho_principal = root.winfo_width()
    nueva_x = x + ancho_principal



    # Verificar si la ventana ya está abierta
    for ventana in ventanas_hijas:
        if ventana.winfo_exists() and ventana.title() == "Contactos Nuestros":
            ventana.geometry(f"+{nueva_x}+{y}")
            ventana.lift()
            ventana.focus_force()
            return



    # Crear nueva ventana
    ventana_nuestros = ctk.CTkToplevel(root)
    ventana_nuestros.title("Contactos Nuestros")
    ventanas_hijas.append(ventana_nuestros)
    ventana_nuestros.transient(root)
    ventana_nuestros.geometry(f"530x180+{nueva_x}+{y}")
    ventana_nuestros.configure(fg_color="black")


    # Definir columnas y crear tabla
    columnas = ("Nombre", "Correo", "Teléfono")
    tabla = ttk.Treeview(ventana_nuestros, columns=columnas, show="headings")
    tabla.pack(expand=True, fill="both", padx=10, pady=5)

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, anchor="w")  # El ancho se ajustará automáticamente

    # Insertar encabezado de categoría y contactos
    tabla.insert("", "end", values=("", "", ""))
    for contacto in contactos_nuestros:
        tabla.insert("", "end", values=contacto)
    tabla.insert("", "end", values=("", "", ""))  # Separador visual

    # Ajustar columnas automáticamente
    ajustar_columnas(tabla)


    # Estilo visual
    estilo = ttk.Style()
    estilo.theme_use("default")
    estilo.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
    estilo.map("Treeview", background=[("selected", "gray")])


    # Copiar contacto al hacer doble clic
    def copiar_contacto(event):
        item = tabla.selection()
        if item:
            valores = tabla.item(item, "values")
            if "---" in valores[0] or all(v == "" for v in valores):
                return
            texto = f"{valores[0]} ({valores[1]}) - {valores[2]}"
            ventana_nuestros.clipboard_clear()
            ventana_nuestros.clipboard_append(texto)
            ventana_nuestros.update()
            messagebox.showinfo("Copiado", f"Contacto copiado:\n\n{texto}")

    tabla.bind("<Double-1>", copiar_contacto)

    
# Define the list of contacts for "NUESTROS"
contactos_nuestros = sorted([
    ("Avaro León Henao", "alhenao@bancolombia.com.co", "312-739-7096"),
    ("Claudia Yaneth Uribe Mora", "cyuribe@bancolombia.com.co", "300-368-1375"),
    ("Eduer Ferney Quintero Arbelaez", "efquinte@bancolombia.com.co", "319-295-6941"),
    ("Edwin Fernando Rua", "edrua@bancolombia.com.co", "318-275-4726"),
    ("Jonatan Fernando Rojas Marin", "jofrojas@bancolombia.com.co", "302-416-6912"),
    ("Juan Pablo Rosero", "jurosero@bancolombia.com.co", "301-488-4056"),
    ("Mauricio Cardona Acosta", "macacost@bancolombia.com.co", "300-651-7017"),
], key=lambda x: x[0])




# Botón NUESTROS

btn_nuestros = ctk.CTkButton(subframe_botones_contactos, text="CYGNUS", command=mostrar_nuestros,
                         width=8, font=("Arial", 11, "bold"),
 height=BUTTON_HEIGHT, corner_radius=10 )
btn_nuestros.pack(side=tk.LEFT, padx=5)
btn_nuestros.bind("<Enter>", on_enter)
btn_nuestros.bind("<Leave>", on_leave)





# Frame para el título y los botones de TURNOS
frame_turnos = ctk.CTkFrame(root, fg_color="#000000")
frame_turnos.pack(pady=1, fill="x")

label_turnos = ctk.CTkLabel(frame_turnos, text="TURNOS", font=("Arial", 12, "bold"), fg_color="#000000")
label_turnos.pack(  pady=(3, 0))


# Lista de integrantes
integrantes = [
    "Alvaro León Henao",
    "Claudia Yaneth Uribe Mora",
    "Edwin Fernando Rua",
    "Eduer Ferney Quintero",
    "Jonatan Fernando Rojas Marin",
    "Juan Pablo Rosero",
    "Mauricio Cardona Acosta"
]

# Función para seleccionar integrantes y copiar texto

def seleccionar_integrantes(turno):
    def mover_arriba():
        indices = listbox_seleccionados.curselection()
        if not indices: return
        for i in indices:
            if i > 0:
                texto = listbox_seleccionados.get(i)
                listbox_seleccionados.delete(i)
                listbox_seleccionados.insert(i - 1, texto)
                listbox_seleccionados.selection_set(i - 1)

    def mover_abajo():
        indices = listbox_seleccionados.curselection()
        if not indices: return
        for i in reversed(indices):
            if i < listbox_seleccionados.size() - 1:
                texto = listbox_seleccionados.get(i)
                listbox_seleccionados.delete(i)
                listbox_seleccionados.insert(i + 1, texto)
                listbox_seleccionados.selection_set(i + 1)



    def quitar_seleccionados():
        listbox_seleccionados.delete(0, tk.END)
        
    def confirmar_seleccion():
        seleccionados = listbox_seleccionados.get(0, tk.END)
        if len(seleccionados) < 1:
            messagebox.showwarning("Advertencia", "Selecciona al menos un integrante.")
            return

        if len(seleccionados) == 1:
            verbo = "continúo"
            nombres = ""
        else:
            verbo = "continuamos"
            if len(seleccionados) == 2:
                nombres = " y ".join(seleccionados)
            else:
                nombres = ", ".join(seleccionados[:-1]) + " y " + seleccionados[-1]

        if turno == "6-2":
            texto = f"Buenos Días, {verbo} por parte de Operación Cloud COES en el turno 06:00 am - 02:00 pm {nombres}"
        elif turno == "2-10":
            texto = f"Buenas Tardes, {verbo} por parte de Operación Cloud COES en el turno 02:00 pm - 10:00 pm {nombres}"
        else:
            texto = f"Buenas Noches, {verbo} por parte de Operación Cloud COES en el turno 10:00 pm - 06:00 am {nombres}"

        root.clipboard_clear()
        root.clipboard_append(texto)
        root.update()
        messagebox.showinfo("Copiado", "El texto ha sido copiado correctamente al portapapeles.")
        ventana_seleccion.destroy()

    def copiar_turno_individual():
        if turno == "6-2":
            texto = "Buenos Días, continúo por parte de Operación Cloud COES en el turno 06:00 am - 02:00 pm"
        elif turno == "2-10":
            texto = "Buenas Tardes, continúo por parte de Operación Cloud COES en el turno 02:00 pm - 10:00 pm"
        else:
            texto = "Buenas Noches, continúo por parte de Operación Cloud COES en el turno 10:00 pm - 06:00 am"

        root.clipboard_clear()
        root.clipboard_append(texto)
        root.update()
        messagebox.showinfo("Copiado", "Copiado correctamente al portapapeles.")

    ventana_seleccion = ctk.CTkToplevel(root)
    ventana_seleccion.transient(root)
    ventanas_hijas.append(ventana_seleccion)

    x = root.winfo_x()
    y = root.winfo_y()
    ancho_principal = root.winfo_width()
    nueva_x = x + ancho_principal
    ventana_seleccion.geometry(f"230x470+{nueva_x}+{y}")
    ventana_seleccion.title("Seleccionar y Ordenar")
    ventana_seleccion.configure(fg_color="#000000")

    frame_contenido = ctk.CTkFrame(ventana_seleccion, fg_color="#000000")
    frame_contenido.pack(padx=10, pady=10, fill="both", expand=True)

    integrantes = [
        "Alvaro León Henao",
        "Claudia Yaneth Uribe Mora",
        "Edwin Fernando Rua",
        "Eduer Ferney Quintero",
        "Jonatan Fernando Rojas Marin",
        "Juan Pablo Rosero",
        "Mauricio Cardona Acosta"
    ]

    label_original = ctk.CTkLabel(frame_contenido, text="1. Selecciona los integrantes:", font=("Arial", 11, "bold"), fg_color="#000000")
    label_original.pack(pady=1)

    frame_listbox = ctk.CTkFrame(frame_contenido, fg_color="black")
    frame_listbox.pack(fill="x", padx=10, pady=1)
    listbox_original = tk.Listbox(frame_listbox, selectmode=tk.MULTIPLE, height=7)
    listbox_original.pack(fill="x", padx=10, pady=1)

    for nombre in integrantes:
        listbox_original.insert(tk.END, nombre)

    def pasar_seleccion():
        seleccionados = [listbox_original.get(i) for i in listbox_original.curselection()]
        if not seleccionados:
            messagebox.showwarning("Advertencia", "Selecciona al menos un integrante de la lista.")
            return
        listbox_seleccionados.delete(0, tk.END)
        for nombre in seleccionados:
            listbox_seleccionados.insert(tk.END, nombre)

    btn_pasar = ctk.CTkButton(frame_contenido, text="Añadir >>", command=pasar_seleccion, font=("Arial", 11, "bold"), height=25, width=70, corner_radius=10 )
    btn_pasar.pack(pady=1)

    label_seleccionados = ctk.CTkLabel(frame_contenido, text="2. Reordena (si es necesario):", font=("Arial", 11, "bold"), fg_color="#000000")
    label_seleccionados.pack(pady=1)

    listbox_seleccionados = tk.Listbox(frame_contenido, selectmode=tk.SINGLE, height=7)
    listbox_seleccionados.pack(fill="x", padx=10, pady=1)

    frame_mover = ctk.CTkFrame(frame_contenido, fg_color="#000000")
    frame_mover.pack(pady=1)

    btn_subir = ctk.CTkButton(frame_mover, text="▲ Subir", command=mover_arriba, font=("Arial", 10, "bold"), height=25, width=40, corner_radius=10)
    btn_subir.pack(side=tk.LEFT, padx=5)

    btn_bajar = ctk.CTkButton(frame_mover, text="▼ Bajar", command=mover_abajo, font=("Arial", 10, "bold"), height=25, width=40, corner_radius=10)
    btn_bajar.pack(side=tk.LEFT, padx=5)

    btn_quitar = ctk.CTkButton(
    frame_mover,
    text="X Borrar",
    command=quitar_seleccionados,
    font=("Arial", 10, "bold"),
    height=25,
    width=40,
    corner_radius=10
    )
    btn_quitar.pack(side=tk.LEFT, padx=5)


    btn_confirmar = ctk.CTkButton(frame_contenido, text="3. Generar", command=confirmar_seleccion, font=("Arial", 11, "bold"), height=25, width=70, corner_radius=10 )
    btn_confirmar.pack(pady=5)

    btn_turno_solo = ctk.CTkButton(frame_contenido, text="4. SOLO EN TURNO", command=copiar_turno_individual, font=("Arial", 11, "bold"), height=25, width=70)
    btn_turno_solo.pack(pady=5)


# Frame para los botones de turnos
frame_botones_turnos = ctk.CTkFrame(frame_turnos, fg_color="#000000")
frame_botones_turnos.pack(pady=1)



for turno in ["6-2", "2-10", "10-6"]:
    btn = ctk.CTkButton(
        frame_botones_turnos,
        text=turno,
        command=lambda t=turno: seleccionar_integrantes(t),
        height=BUTTON_HEIGHT,
        corner_radius=10,
        font=("Arial", 11, "bold"),
        width=4
    )
    btn.pack(side=tk.LEFT, padx=5)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)



frame_img = ctk.CTkFrame(root, fg_color="#000000")
frame_img.pack(pady=1)



def abrir_url(url):
    """Abre la URL dada en una nueva ventana del navegador."""
    try:
        webbrowser.open(url)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la URL:\n{e}")

def imagen_clicada(event):
    """Muestra la ventana de enlaces de Cygnus con scroll funcional y sin espacios blancos."""
    x = root.winfo_x()
    y = root.winfo_y()
    ancho_principal = root.winfo_width()
    nueva_x = x + ancho_principal



    for ventana in ventanas_hijas:
        if ventana.winfo_exists() and ventana.title() == "ENLACES CYGNUS":
            ventana.geometry(f"+{nueva_x}+{y}")
            ventana.lift()
            ventana.focus_force()
            return

    ventana_botones = ctk.CTkToplevel(root)
    ventana_botones.title("Enlaces Cygnus")
    ventanas_hijas.append(ventana_botones)
    ventana_botones.transient(root)
    ventana_botones.geometry(f"230x520+{nueva_x}+{y}")
    ventana_botones.configure(fg_color="black")
    ventana_botones.resizable(False, False)


#Canvas y scrollbar
    canvas = tk.Canvas(ventana_botones, bg="black", highlightthickness=0)
    scrollbar = ttk.Scrollbar(ventana_botones, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Frame interno
    frame_botones = ctk.CTkFrame(canvas, fg_color="black")
    canvas_window = canvas.create_window((0, 0), window=frame_botones, anchor="nw")


    # Crear un Frame interior donde irán los botones
    frame_botones = ctk.CTkFrame(canvas, fg_color="black")
    canvas_window = canvas.create_window((0, 0), window=frame_botones, anchor="nw")

    # Ajustar el scroll y el ancho dinámico
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(canvas_window, width=canvas.winfo_width())

    frame_botones.bind("<Configure>", on_frame_configure)

    # Habilitar el desplazamiento con la rueda del mouse
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    def abrir_url(url):
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la URL:\n{e}")

    # Lista de botones con sus colores originales
    botones_coloreados = [
        ("DoR CYGNUS", "https://grupobancolombia.visualstudio.com/Vicepresidencia%20Servicios%20de%20Tecnolog%C3%ADa/_wiki/wikis/Vicepresidencia%20Servicios%20de%20Tecnolog%C3%ADa.wiki/355216/DoR-CYGNUS-(Operaci%C3%B3n-Nube)", "#8297AD"),
        ("EQU0642 - CYGNUS", "https://grupobancolombia.visualstudio.com/Vicepresidencia Servicios de Tecnología/_boards/board/t/EQU0642 - CYGNUS/Lista de producto", "#8297AD"),
        ("HELIX", "https://bancolombia-smartit.onbmc.com/smartit/app/#/ticket-console", "#8297AD"),
        ("CATALOGO DE SERVICIOS", "https://bancolombia-dwp.onbmc.com/dwp/app/#/page/ohpsg1j4", "#8297AD"),
        ("AWS CONSOLA", "https://d-9067080964.awsapps.com/start#/", "#8297AD"),
        ("PLEXO", "https://plexo.apps.bancolombia.com", "#54ADA2"),
        ("KAIZEN", "https://kaizen.apps.bancolombia.com/plexo-view", "#54ADA2"),
        ("VSTS SERVICIOS PLEXO", "https://grupobancolombia.visualstudio.com/Vicepresidencia%20Servicios%20de%20Tecnolog%C3%ADa/_wiki/wikis/Vicepresidencia%20Servicios%20de%20Tecnolog%C3%ADa.wiki/410958/Configuracion-de-servicios", "#54ADA2"),
        ("REPO PLEXO", "https://grupobancolombia.visualstudio.com/Vicepresidencia%20Servicios%20de%20Tecnolog%C3%ADa/_git/Template_Cloud_Operacion", "#54ADA2"),
        ("MAG NUBE", "https://mag.apps.bancolombia.com/admin", "#54ADA2"),
        ("DYNATRACE K8s EKS NODE", "https://lqy04258.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/8e44de1b-bff6-48d6-af5b-f0dab16acc94", "#84b6f4"),
        ("SPOT IO", "https://console.spotinst.com/spt/auth/signIn", "#84b6f4"),
        ("TURNOS", "https://bancolombia.sharepoint.com/:x:/r/teams/Cygnus-AWS/_layouts/15/Doc.aspx?sourcedoc=%7B6296F025-6862-40E7-9F15-B3A957E83C53%7D&file=Turnos%20Cygnus%202025.xlsx&action=default&mobileredirect=true", "#CCB363"),
        ("VACACIONES", "https://bancolombia.sharepoint.com/:x:/r/teams/PlataformasyDisponibilidaddeTI/_layouts/15/Doc.aspx?sourcedoc=%7B3D2AC0FD-DEAD-4AF7-B354-6775428DF4DB%7D&file=Vacaciones%20CYGNUS.xlsx&action=default&mobileredirect=true", "#CCB363"),
        ("PROGRAMACIÓN HAPPY FRIDAY", "https://bancolombia.sharepoint.com/:x:/r/teams/Cygnus-AWS/_layouts/15/Doc.aspx?sourcedoc=%7B7B333C20-3584-4D0B-ACFA-00CDB1263EBE%7D&file=HAPPY%20FRIDAY%20Y%20CUMPLEA%C3%91OS%20CYGNUS.xlsx&action=default&mobileredirect=true", "#CCB363"),
        ("REPORTE HAPPY", "https://bancolombia.sharepoint.com.mcas.ms/sites/co-vgh/SitePages/mis-beneficios-a-tiempo.aspx", "#CCB363"),
        ("CYGNUS HOME", "https://bancolombia.sharepoint.com/teams/Cygnus-AWS/SitePages/TrainingHome.aspx", "#CCB363"),
        ("CARPETA CYGNUS ONE DRIVE", "https://bancolombia.sharepoint.com/teams/PlataformasyDisponibilidaddeTI/Documentos%20compartidos/Forms/AllItems.aspx?id=%2Fteams%2FPlataformasyDisponibilidaddeTI%2FDocumentos%20compartidos%2FGeneral%2F02%2E%20Areas%2FIntegrada%C2%A0Operaci%C3%B3n%20TI%2F2FCYGNUS&viewid=57766697%2D4feb%2D4155%2Daa50%2D7e170cf7663f&csf=1&web=1&e=EkAc8b&FolderCTID=0x0120005E9D7AC01B2F224C9592BE475FCCCF12", "#CCB363"),
        ("CONECTADOS", "https://performancemanager8.successfactors.com/sf/start?_s.crb=aXY4tvGvZ%252bhWEJ65r%252bfyKs1XnEaUsD71QXK3e6RrN%252f8%253d", "#CCB363"),
        ("DIRECTORIO ACTIVO GRUPOS", "https://apps.powerapps.com/play/e/6bdfe354-f250-e0e7-941d-103fc5c5001d/a/903ea87a-6b3a-4311-b962-f96b75e674d6?tenantId=b5e244bd-c492-495b-8b10-61bfd453e423&hint=8bd66a5b-a6b7-43c4-8bdb-7d71972150ca&sourcetime=1757015480085&source=teamsLinkUnfurling", "#B85CCF"),
        ("PORTAL CONTINUIDAD TI", "https://apps.powerapps.com/play/e/6bdfe354-f250-e0e7-941d-103fc5c5001d/a/913bb453-3222-4666-be40-dd026f570605?tenantId=b5e244bd-c492-495b-8b10-61bfd453e423", "#B85CCF"),
        ("PIPELINES", "https://bancolombia-is.onbmc.com/helix/index.html#/Autogestionados.Bancolombia/view/Autogestionados.Bancolombia:Servicios%20autogestionados", "#B85CCF"),
        ("GESTIONAR CAMBIOS TI", "https://bancolombia.sharepoint.com/sites/co-vsti/SitePages/sobre-nosotros_modelo-operativo_procesos_gestionar-cambios.aspx?xsdata=MDV8MDJ8fDdlNmJkODZkZDFiZDRiZDQ4YTgwMDhkZGVmZThjZTFmfGI1ZTI0NGJkYzQ5MjQ0NWI4YjEwNjFiZmQ0NTNlNDIzfDB8MHw2Mzg5MzA1MDUzMjYxMTU2Mjd8VW5rbm93bnxWR1ZoYlhOVFpXTjFjbWwwZVZObGNuWnBZMlY4ZXlKRFFTSTZJbFJsWVcxelgwRlVVRk5sY25acFkyVmZVMUJQVEU5R0lpd2lWaUk2SWpBdU1DNHdNREF3SWl3aVVDSTZJbGRwYmpNeUlpd2lRVTRpT2lKUGRHaGxjaUlzSWxkVUlqb3hNWDA9fDF8TDJOb1lYUnpMekU1T21GaU56bGlOV1ZoTFdVNVl6SXROR1l4TVMxaE16aGxMV000Tm1Oak9USTNZMk5sT1Y5bFlXVXlPVFppTWkwMFlqRmxMVFJoTVdRdFlUQmlZaTFoTVRZd01URmhPVGd3TmpaQWRXNXhMbWRpYkM1emNHRmpaWE12YldWemMyRm5aWE12TVRjMU56UTFNemN6TVRjME13PT18OTYyYWE2ZDdmNTZhNGE1YTNjMDcwOGRkZWZlOGNlMWZ8ZDU4NzVmNjI3OGUwNGU4Y2E5ZjUxNGM3NzE3ZTBhYWQ%3D&sdata=QlJkRWVIQVdLbGU3QWdVcEJENExja3FMQm1NQUZCK3BPaXpPOWFkZGJZdz0%3D&ovuser=b5e244bd-c492-495b-8b10-61bfd453e423%2Cefquinte%40bancolombia.com.co&OR=Teams-HL&CT=1757457468155&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiI0OS8yNTA4MTUwMDcxNyIsIkhhc0ZlZGVlcmF0ZWRVc2VyIOmZhbHNlfQ%3D%3D", "#B85CCF"),
        ("TABLERO HAs", "https://grupobancolombia.visualstudio.com/Vicepresidencia%20Servicios%20de%20Tecnolog%C3%ADa/_dashboards/dashboard/1f9264bd-fee1-48a1-bfd5-a8508c67acfb", "#C44141"),
        ("TABLERO CRQs", "https://bancolombia-ca1.onbmc.com/dashboards/d/b973b7b8-88f5-4201-a124-23f03094d644/tablero-cygnus?orgId=1271008613", "#C44141"),
        ("RESTRICCIÓN CAMBIOS", "https://bancolombia.sharepoint.com/:x:/r/sites/co-vsti/_layouts/15/Doc.aspx?sourcedoc=%7BDEC5F518-F360-4E63-99F6-8DA2FCA926DC%7D&file=Calendario%20Cambios%20Alto%20Impacto%20y%20Fechas%20Restricci%25u00f3n.xlsx&action=default&mobileredirect=true", "#D3DF68"),
        ("STAND BY", "https://bancolombia.sharepoint.com/sites/co-vsti/Lists/Programacin%20Stand%20By/IMes.aspx?viewid=ab3bc15f%2Dcce7%2D45c3%2D9eb4%2D319d54502d52&useFiltersInViewXml=1&OR=Teams%2DHL&CT=1706593136683&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiI0OS8yMzExMzAyODcyNCIsIkhhc0ZlZGVyYXRlZFVzZXIiOmZhbHNlfQ%3D%3D", "#D3DF68")
    ]
    

    for texto_boton, url, color in botones_coloreados:
        btn = ctk.CTkButton(
            frame_botones,
            text=texto_boton,
            command=lambda u=url: abrir_url(u),
            font=("Arial", 11, "bold"),
            fg_color=color,
            text_color="black"
        )
        btn.pack(pady=1, fill="x")
        btn.bind("<Enter>", lambda e, b=btn: b.configure(fg_color="gray"))
        btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(fg_color=c))


# Modificando la ruta de la imagen
# Modificando la ruta de la imagen
ruta_imagen = obtener_ruta_recurso("cygnussssss.png")

if os.path.exists(ruta_imagen):
    try:
        img = Image.open(ruta_imagen)
        img = img.resize((150, 110), Image.Resampling.LANCZOS)

        global imagen_ctk
        imagen_ctk = CTkImage(light_image=img, dark_image=img, size=(190, 150))

        label_img = CTkLabel(master=frame_img, image=imagen_ctk, text="", fg_color="black")
        label_img.pack(side="bottom", pady=5)
        label_img.bind("<Button-1>", imagen_clicada)
        label_img.bind("<Enter>", on_enter_image)
        label_img.bind("<Leave>", on_leave_image)


    except Exception as e:
        print("Error al cargar la imagen:", str(e))
else:
    print("⚠ Imagen no encontrada:", ruta_imagen)




# Inicia el bucle de eventos de Tkinter
root.mainloop() # Inicia el bucle principal de la aplicación.
