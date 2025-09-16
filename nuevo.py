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

# Lista para almacenar las referencias de las ventanas secundarias
ventanas_hijas = []

# Configurar salida estándar para UTF-8 en Windows
# sys.stdout.reconfigure(encoding='utf-8')

# Lista para almacenar los contactos de cada pestaña
contactos_por_pestana = {
    "Principal": [],
    "Telefonos": [],
    "Generador": []
}

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

def limpiar_texto(texto):
    """
    Limpia caracteres problemáticos en el texto extraído del PDF.
    
    Reemplaza caracteres especiales o no deseados, a menudo generados por la extracción
    de texto de PDFs, y se asegura de que el texto sea compatible con UTF-8.
    """
    reemplazos = {' ': '', '\ue603': '', '\ue616': '', '\ue657': '', '\ue643': '', '\ue6a1': '', '\ue688': ''}
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
    datos_completos["Fecha de Proceso"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Añade la fecha de proceso.

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

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Obtiene la fecha y hora actuales.
    nombre_archivo = f"Evento_Incidente_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx" # Genera un nombre de archivo único.

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
    nombre_archivo = f"TASK_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx" # Genera el nombre del archivo.
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
    "Fecha de Proceso": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "ID del TASK": id_task
    }
    llenar_plantilla(datos, plantilla_path, salida_path)

def iniciar_proceso_pods():
    """Inicia el proceso para la plantilla PODs."""
    plantilla_path = obtener_ruta_recurso("Plantilla CYGNUS PODs.docx") # Obtiene la ruta de la plantilla PODs.
    if not os.path.exists(plantilla_path):
        messagebox.showerror("Error", f"No se encontró la plantilla en {plantilla_path}")
        return
    nombre_archivo = f"PODs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx" # Genera el nombre del archivo.
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
        "Fecha de Proceso": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ID del POD": id_pod,
        "ID del EVENTO/INCIDENTE": id_pod
    }
    llenar_plantilla(datos, plantilla_path, salida_path)

# Funciones de hover
def on_enter(event):
    """Cambia el color de fondo de un widget al pasar el mouse por encima."""
    widget = event.widget
    # Guarda el color original si no está guardado
    if not hasattr(widget, 'original_bg'):
        widget.original_bg = widget.cget("bg")
    widget.config(bg="#9C9C9C")  # dorado

def on_leave(event):
    """Restaura el color de fondo de un widget al salir el mouse."""
    widget = event.widget
    # Restaura el color original si está guardado
    if hasattr(widget, 'original_bg'):
        widget.config(bg=widget.original_bg)

def on_enter_image(event):
    """Cambia el color del borde de una imagen al pasar el mouse por encima."""
    event.widget.config(highlightbackground="white")

def on_leave_image(event):
    """Restaura el color del borde de una imagen al salir el mouse."""
    event.widget.config(highlightbackground="gray")


def mostrar_telefonos():
    """
    Muestra la ventana de contactos telefónicos. Si ya está abierta, la enfoca y la reposiciona.
    """
    # Obtener la posición actual de la ventana principal
    x = root.winfo_x()
    y = root.winfo_y()
    ancho_principal = root.winfo_width()
    
    # Calcular la nueva posición de la ventana hija
    nueva_x = x + ancho_principal
    
    # Verificar si la ventana ya está abierta
    for ventana in ventanas_hijas:
        if ventana.winfo_exists() and ventana.title() == "Contactos Telefónicos":
            # Reposicionar la ventana
            ventana.geometry(f"+{nueva_x}+{y}") #
            # Enfocarla
            ventana.lift()
            ventana.focus_force()
            return
            
    # Si no existe, crear una nueva ventana
    ventana_tel = tk.Toplevel(root) # Crea una nueva ventana de nivel superior.
    ventana_tel.title("Contactos Telefónicos")
    ventanas_hijas.append(ventana_tel)
    
    # Hacemos la ventana secundaria transitoria de la principal
    ventana_tel.transient(root)
    
    # La nueva ventana aparecerá a la derecha de la principal
    ancho_nueva = 510
    alto_nueva = 400
    ventana_tel.geometry(f"{ancho_nueva}x{alto_nueva}+{nueva_x}+{y}")
    ventana_tel.configure(bg="black")
    
    columnas = ("Nombre", "Correo", "Teléfono")
    tabla = ttk.Treeview(ventana_tel, columns=columnas, show="headings") # Crea el widget de tabla.
    tabla.pack(expand=True, fill="both", padx=10, pady=10)
  
    for col in columnas:        
        tabla.column("Nombre", anchor="w", width=140)
        tabla.column("Correo", anchor="w", width=140)
        tabla.column("Teléfono", anchor="w", width=40)

        
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
    
    def insertar_categoria(nombre_categoria, lista_contactos):
        tabla.insert("", "end", values=(f"--- {nombre_categoria} ---", "", "")) # Inserta una fila de encabezado.
        for contacto in lista_contactos:
            tabla.insert("", "end", values=contacto) # Inserta cada contacto en la tabla.
        tabla.insert("", "end", values=("", "", "")) # Inserta una fila en blanco para separar.
    
    insertar_categoria("EMMA", contactos_emma) #
    insertar_categoria("TAM AWS", contactos_tam_aws)
    insertar_categoria("SKILLFULLERS", contactos_skillfullers)
    
    estilo = ttk.Style()
    estilo.theme_use("default")
    estilo.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
    estilo.map("Treeview", background=[("selected", "gray")])
    
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
    
    tabla.bind("<Double-1>", copiar_contacto) # Asocia la función copiar_contacto al doble clic.

def ingresar_a_cluster():
    """
    Pide un nombre de cluster, genera un comando de AWS CLI y lo copia al portapapeles.
    """
    nombre_cluster = simpledialog.askstring("Nombre del Cluster", "Ingresa el nombre del cluster:") # Muestra un diálogo de entrada.
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
    """
    Muestra un cuadro de texto con un comando y un botón para copiarlo.
    """
    ventana_comando = tk.Toplevel()
    ventana_comando.title(f"Comando {titulo}")
    ventana_comando.geometry("800x400")
    ventana_comando.configure(bg="black")
    cuadro_texto = tk.Text(ventana_comando, wrap="word", bg="#E9E9E9", fg="black", font=("Courier", 10))
    cuadro_texto.pack(expand=True, fill="both", padx=10, pady=10)
    cuadro_texto.insert("1.0", comando) # Inserta el comando en el cuadro de texto.
    cuadro_texto.config(state="normal")
    
    def copiar_al_portapapeles():
        ventana_comando.clipboard_clear()
        ventana_comando.clipboard_append(cuadro_texto.get("1.0", "end-1c"))
        ventana_comando.update()
        messagebox.showinfo("Copiado", "El comando ha sido copiado al portapapeles.")
    
    boton_copiar = tk.Button(ventana_comando, text="Copiar al portapapeles", command=copiar_al_portapapeles,
                             bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"), relief="raised")
    boton_copiar.pack(pady=5)

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
        if ventana.winfo_exists() and ventana.title() == "GENERADOR":
            # Reposicionar la ventana
            ventana.geometry(f"+{nueva_x}+{y}") #
            # Enfocarla
            ventana.lift()
            ventana.focus_force()
            return
            
    # Si no existe, crear una nueva ventana
    ventana_opciones = tk.Toplevel(root)
    ventana_opciones.title("GENERADOR")
    ventanas_hijas.append(ventana_opciones)
    ventana_opciones.transient(root)
    ancho_nueva = 220
    alto_nueva = 290
    ventana_opciones.geometry(f"220x460+{nueva_x}+{y}")

    ventana_opciones.configure(bg="#111111")
    frame_kubectl = tk.Frame(ventana_opciones, bg="#111111")
    frame_kubectl.pack(pady=5, fill="x", padx=20)
    frame_kubectl.columnconfigure(0, weight=1)
    frame_kubectl.columnconfigure(1, weight=1)

    def eliminar_pods():
        pods_input = simpledialog.askstring("Pods", "Ingresa los nombres de los pods (puedes pegar la salida de 'kubectl get pods'):") # Pide los nombres de los pods.
        if not pods_input:
            return
        namespace_input = simpledialog.askstring("Namespace", "Ingresa el namespace:") # Pide el namespace.
        if not namespace_input:
            return
        pod_lines = pods_input.strip().splitlines()
        pods = [line.split()[0] for line in pod_lines if line.strip()] # Extrae los nombres de los pods.
        namespace = namespace_input.strip()
        comandos = "\n".join([f"kubectl delete pod -n {namespace} {pod}" for pod in pods])
        mostrar_comando(comandos, "Eliminar PODs")

    def generar_logs():
        pods_input = simpledialog.askstring("Pods", "Ingresa los nombres de los pods (puedes pegar la salida de 'kubectl get pods'):")
        if not pods_input:
            return
        namespace_input = simpledialog.askstring("Namespace", "Ingresa el namespace:") # Pide el namespace.
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
        pods_input = simpledialog.askstring("Pods", "Ingresa los nombres de los pods (puedes pegar la salida de 'kubectl get pods'):")
        if not pods_input:
            return
        namespace_input = simpledialog.askstring("Namespace", "Ingresa el namespace:")
        if not namespace_input:
            return
        pod_lines = pods_input.strip().splitlines() #
        pods = [line.split()[0] for line in pod_lines if line.strip()]
        namespace = namespace_input.strip()
        grep_pods = " |grep " + " ".join([f"-e {pod}" for pod in pods])
        comando = f"while true; do kubectl get po -n {namespace}{grep_pods}; echo \"\"; echo \"Actualizando...\"; echo \"\"; sleep 5; done" #
        mostrar_comando(comando, "LIVE")

    def generar_query_cloudwatch():
        pods_input = simpledialog.askstring("Pods", "Ingresa los nombres de los pods (puedes pegar la salida de 'kubectl get pods'):")
        if not pods_input:
            return
        namespace_input = simpledialog.askstring("Namespace", "Ingresa el namespace:")
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

    def generar_query_cloudwatch_conteo():
        query_conteo = """
filter log like /(?i)error|failed/
| stats count(*) as Error by kubernetes.pod_name, kubernetes.namespace_name
| sort Error desc
"""
        mostrar_comando(query_conteo.strip(), "CloudWatch Conteo")
        
    label_eks = tk.Label(frame_kubectl, text="EKS", bg="#111111", fg="white", font=("Arial", 12, "bold"))
    label_eks.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="ew")

    # 🔹 PODs LIVE y TOP POD
    frame_pods = tk.Frame(frame_kubectl, bg="#111111")
    frame_pods.grid(row=1, column=0, columnspan=2, pady=(0, 5), sticky="ew")
    frame_pods.columnconfigure(0, weight=1)
    frame_pods.columnconfigure(1, weight=1)

    btn_pods_live = tk.Button(frame_pods, text="LIVE", command=pods_live_monitor,
                              width=20, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_pods_live.grid(row=0, column=0, padx=5, pady=5)
    btn_pods_live.bind("<Enter>", on_enter)
    btn_pods_live.bind("<Leave>", on_leave)

    btn_top_pod = tk.Button(frame_pods, text="TOP", command=lambda: copiar_comando("kubectl.exe top pod -n"),
                            width=20, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_top_pod.grid(row=0, column=1, padx=5, pady=5)
    btn_top_pod.bind("<Enter>", on_enter)
    btn_top_pod.bind("<Leave>", on_leave)


    # 🔹 Eliminar PODs y LOGs
    frame_pods_logs = tk.Frame(frame_kubectl, bg="#111111")
    frame_pods_logs.grid(row=2, column=0, columnspan=2, pady=(0, 5), sticky="ew")
    frame_pods_logs.columnconfigure(0, weight=1)
    frame_pods_logs.columnconfigure(1, weight=1)

    btn_eliminar_pods = tk.Button(frame_pods_logs, text="DELETE", command=eliminar_pods,
                                  width=20, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_eliminar_pods.grid(row=0, column=0, padx=5, pady=5)
    btn_eliminar_pods.bind("<Enter>", on_enter)
    btn_eliminar_pods.bind("<Leave>", on_leave)

    btn_logs = tk.Button(frame_pods_logs, text="LOGs GREP", command=generar_logs,
                         width=20, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_logs.grid(row=0, column=1, padx=5, pady=5)
    btn_logs.bind("<Enter>", on_enter)
    btn_logs.bind("<Leave>", on_leave)




    # Título de la sección
    label_deployment = tk.Label(frame_kubectl, text="DEPLOYMENT", bg="#111111", fg="white", font=("Arial", 12, "bold"))
    label_deployment.grid(row=8, column=0, columnspan=2, pady=(20, 5), sticky="ew")
    
    # Crear un frame contenedor para los botones
    frame_deployment = tk.Frame(frame_kubectl, bg="#111111")
    frame_deployment.grid(row=9, column=0, columnspan=2, pady=(0, 5), sticky="ew")
    frame_deployment.columnconfigure(0, weight=1)
    frame_deployment.columnconfigure(1, weight=1)
    
    # Botón LISTAR
    def listar_deployment():
        ns = simpledialog.askstring("Namespace", "Ingresa el namespace:")
        if ns:
            copiar_comando(f"kubectl get deployment -n {ns}")
    
    btn_listar_d = tk.Button(frame_deployment, text="LIST", command=listar_deployment,
                             width=15, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_listar_d.grid(row=0, column=0, padx=5, pady=5)
    btn_listar_d.bind("<Enter>", on_enter)
    btn_listar_d.bind("<Leave>", on_leave)
    
    # Botón DESCRIBIR
    def describir_deployment():
        ns = simpledialog.askstring("Namespace", "Enter the namespace:")
        name = simpledialog.askstring("Deployment", "Enter the deployment name:")
        if ns and name:
            copiar_comando(f"kubectl describe deployment -n {ns} {name}")
    
    btn_describir_d = tk.Button(frame_deployment, text="DESCRIBE", command=describir_deployment,
                                width=15, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_describir_d.grid(row=0, column=1, padx=5, pady=5)
    btn_describir_d.bind("<Enter>", on_enter)
    btn_describir_d.bind("<Leave>", on_leave)
    
    # Título de la sección CONFIG MAP
    label_configmap = tk.Label(frame_kubectl, text="CONFIG MAP", bg="#111111", fg="white", font=("Arial", 12, "bold"))
    label_configmap.grid(row=10, column=0, columnspan=2, pady=(20, 5), sticky="ew")
    
    # Crear un frame contenedor para los botones
    frame_configmap = tk.Frame(frame_kubectl, bg="#111111")
    frame_configmap.grid(row=11, column=0, columnspan=2, pady=(0, 5), sticky="ew")
    frame_configmap.columnconfigure(0, weight=1)
    frame_configmap.columnconfigure(1, weight=1)
    
    # Botón LISTAR CONFIG MAP
    def listar_configmap():
        ns = simpledialog.askstring("Namespace", "Enter the namespace:")
        if ns:
            copiar_comando(f"kubectl.exe get configmaps -n {ns}")
    
    btn_listar_c = tk.Button(frame_configmap, text="LIST", command=listar_configmap,
                             width=15, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_listar_c.grid(row=0, column=0, padx=5, pady=5)
    btn_listar_c.bind("<Enter>", on_enter)
    btn_listar_c.bind("<Leave>", on_leave)
    
    # Botón DESCRIBIR CONFIG MAP
    def describir_configmap():
        ns = simpledialog.askstring("Namespace", "Enter the namespace:")
        name = simpledialog.askstring("ConfigMap", "Enter the configmap name:")
        if ns and name:
            copiar_comando(f"kubectl.exe describe configmap {name} -n {ns}")
    
    btn_describir_c = tk.Button(frame_configmap, text="DESCRIBE", command=describir_configmap,
                                width=15, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_describir_c.grid(row=0, column=1, padx=5, pady=5)
    btn_describir_c.bind("<Enter>", on_enter)
    btn_describir_c.bind("<Leave>", on_leave)

    




    label_cloudwatch = tk.Label(frame_kubectl, text="EKS LOGs INSIGHTS", bg="#111111", fg="white", font=("Arial", 12, "bold"))
    label_cloudwatch.grid(row=12, column=0, columnspan=2, pady=(20, 5), sticky="ew")
    
    btn_logs_grep = tk.Button(frame_kubectl, text="LOGs GREP", command=generar_query_cloudwatch, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_logs_grep.grid(row=13, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="ew")
    btn_logs_grep.bind("<Enter>", on_enter)
    btn_logs_grep.bind("<Leave>", on_leave)
    
    btn_conteo_errores = tk.Button(frame_kubectl, text="CONTEO ERRORES", command=generar_query_cloudwatch_conteo, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_conteo_errores.grid(row=14, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="ew")
    btn_conteo_errores.bind("<Enter>", on_enter)
    btn_conteo_errores.bind("<Leave>", on_leave)
    
    # Crear un frame contenedor centrado en el grid
    frame_cmds = tk.Frame(frame_kubectl, bg="#111111")
    frame_cmds.grid(row=15, column=0, columnspan=2, pady=(0, 5), sticky="ew")

    # Centrar el contenido dentro del frame
    frame_cmds.columnconfigure(0, weight=1)
    frame_cmds.columnconfigure(1, weight=1)

    # Botón CMD 3
    btn_cmd3 = tk.Button(frame_cmds, text="CMD 3", command=lambda: copiar_comando("echo CMD 3"),
                        bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_cmd3.grid(row=0, column=0, padx=5)
    btn_cmd3.bind("<Enter>", on_enter)
    btn_cmd3.bind("<Leave>", on_leave)

    # Botón CMD 4
    btn_cmd4 = tk.Button(frame_cmds, text="CMD 4", command=lambda: copiar_comando("echo CMD 4"),
                        bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_cmd4.grid(row=0, column=1, padx=5)
    btn_cmd4.bind("<Enter>", on_enter)
    btn_cmd4.bind("<Leave>", on_leave)


    
def copiar_script(texto):
    """Copia el texto dado al portapapeles y muestra un mensaje."""
    root.clipboard_clear()
    root.clipboard_append(texto)
    root.update()
    messagebox.showinfo("Comando Copiado", "El comando fué copiado.")

def mostrar_script():
    """
    Muestra la ventana de scripts. Si ya está abierta, la enfoca y la reposiciona.
    """
    x = root.winfo_x()
    y = root.winfo_y()
    ancho_principal = root.winfo_width()
    nueva_x = x + ancho_principal
    
    for ventana in ventanas_hijas:
        if ventana.winfo_exists() and ventana.title() == "MI BANCOLOMBIA":
            ventana.geometry(f"+{nueva_x}+{y}")
            ventana.lift()
            ventana.focus_force()
            return #

    ventana_script = tk.Toplevel(root)
    ventana_script.title("MI BANCOLOMBIA")
    ventanas_hijas.append(ventana_script)
    ventana_script.transient(root)
    ancho_nueva = 220
    alto_nueva = 290
    ventana_script.geometry(f"{ancho_nueva}x{alto_nueva}+{nueva_x}+{y}")
    ventana_script.configure(bg="#111111")
    frame_script = tk.Frame(ventana_script, bg="black")
    frame_script.pack(expand=True, padx=5, pady=10)
    button_texts = ["GOKU", "SCRIPT1", "SCRIPT2", "SCRIPT3", "SCRIPT4", "SCRIPT5"]
    for text in button_texts:
        btn = tk.Button(frame_script, text=text, command=lambda t="~/Documents/goku": copiar_script(t), #
                        bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"), relief="solid", bd=2)
        btn.pack(pady=5, fill="x")
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

# Configuración de la ventana principal
root = tk.Tk()
root.title("by PINKY")
root.geometry("230x590")
root.configure(bg="#111111")
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
style.configure("TButton", background="white", foreground="black", font=("Arial", 10, "bold"), relief="solid", bordercolor="black", borderwidth=2)

# Frame para el título y los botones de DOCUMENTACIÓN CYGNUS
frame_documentacion = tk.Frame(root, bg="#111111")
frame_documentacion.pack(pady=10)
label_titulo = tk.Label(frame_documentacion, text="DOCUMENTACIÓN", bg="#111111", fg="white", font=("Arial", 12, "bold"))
label_titulo.pack(pady=0)
frame_botones_doc = tk.Frame(frame_documentacion, bg="#111111")
frame_botones_doc.pack(pady=0)
btn_crq = tk.Button(frame_botones_doc, text="CRQ", command=iniciar_proceso_crq, height=1, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"), relief="solid", bd=2)
btn_crq.pack(side=tk.LEFT, padx=5)
btn_crq.bind("<Enter>", on_enter)
btn_crq.bind("<Leave>", on_leave)
btn_task = tk.Button(frame_botones_doc, text="TASK", command=iniciar_proceso_task, height=1, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"), relief="solid", bd=2)
btn_task.pack(side=tk.LEFT, padx=5)
btn_task.bind("<Enter>", on_enter)
btn_task.bind("<Leave>", on_leave)
btn_pods = tk.Button(frame_botones_doc, text="PODS", command=iniciar_proceso_pods, height=1, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"), relief="solid", bd=2)
btn_pods.pack(side=tk.LEFT, padx=5)
btn_pods.bind("<Enter>", on_enter)
btn_pods.bind("<Leave>", on_leave)

# Botón de Evento/Incidente en un frame separado para su propia fila
frame_evento = tk.Frame(root, bg="#111111")
frame_evento.pack(pady=0)

btn_evento = tk.Button(
    frame_evento,
    text="EVENTO / INCIDENTE",
    command=generar_evento_incidente,
    width=18,
    bg="#E9E9E9",
    fg="black",
    font=("Arial", 10, "bold"),
    relief="solid",
    bd=2
)

btn_evento.pack(pady=(0, 5))  # ← sin padx y sin fill="x"
btn_evento.bind("<Enter>", on_enter)
btn_evento.bind("<Leave>", on_leave)

# Frame para el título y los botones de CLUSTER
frame_cluster = tk.Frame(root, bg="#111111")
frame_cluster.pack(pady=5, fill="x")
frame_cluster.columnconfigure(0, weight=1)
frame_cluster.columnconfigure(1, weight=1)
label_cluster = tk.Label(frame_cluster, text="CLUSTER", bg="#111111", fg="white", font=("Arial", 12, "bold"))
label_cluster.grid(row=0, column=0, columnspan=2, pady=0, sticky="ew")
btn_listar_cluster = tk.Button(frame_cluster, text="LISTAR", command=listar_cluster, height=1, width=13, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"), relief="solid", bd=2)
btn_listar_cluster.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")
btn_listar_cluster.bind("<Enter>", on_enter)
btn_listar_cluster.bind("<Leave>", on_leave)
btn_cluster = tk.Button(frame_cluster, text="INGRESAR", command=ingresar_a_cluster, height=1, width=13, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"), relief="solid", bd=2)
btn_cluster.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="ew")
btn_cluster.bind("<Enter>", on_enter)
btn_cluster.bind("<Leave>", on_leave)

# Frame para el título y el botón de KUBECTL
frame_kubectl = tk.Frame(root, bg="#111111") #
frame_kubectl.pack(pady=5, fill="x", padx=20)  # ← nuevo
frame_kubectl.columnconfigure(0, weight=1)
label_kubectl = tk.Label(frame_kubectl, text="KUBECTL", bg="#111111", fg="white", font=("Arial", 12, "bold"))
label_kubectl.grid(row=0, column=0, pady=0, sticky="ew")

btn_kubectl = tk.Button(
    frame_kubectl,
    text="GENERADOR COMANDOS",
    command=generar_comando_kubectl,
    height=1,              # Aumenta la altura visual
    width=35,              # Controla el ancho en caracteres
    bg="#E9E9E9",
    fg="black",
    font=("Arial", 10, "bold"),  # Reduce ligeramente el tamaño de fuente
    relief="solid",
    bd=2
)

btn_kubectl.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")
btn_kubectl.bind("<Enter>", on_enter)
btn_kubectl.bind("<Leave>", on_leave)

btn_script = tk.Button(
    frame_kubectl,
    text="SCRIPTS",  # Mayúsculas para consistencia
    command=mostrar_script,
    height=1,
    width=20,
    bg="#E9E9E9",
    fg="black",
    font=("Arial", 10, "bold"),
    relief="solid",
    bd=2
)
btn_script.grid(row=2, column=0, padx=40, pady=(0, 5), sticky="ew")
btn_script.bind("<Enter>", on_enter)
btn_script.bind("<Leave>", on_leave)

# Frame para el título y los botones de CONTACTOS
# Frame para el título y los botones de CONTACTOS
frame_contactos = tk.Frame(root, bg="#111111")
frame_contactos.pack(pady=5, fill="x")
frame_contactos.columnconfigure(0, weight=1)
frame_contactos.columnconfigure(1, weight=1)
label_contactos = tk.Label(frame_contactos, text="CONTACTOS", bg="#111111", fg="white", font=("Arial", 12, "bold"))
label_contactos.grid(row=0, column=0, columnspan=2, pady=0, sticky="ew")



# Sub-frame centrado para los botones TEL y NUESTROS
subframe_botones_contactos = tk.Frame(frame_contactos, bg="#111111")
subframe_botones_contactos.grid(row=1, column=0, columnspan=2, pady=(0, 5))

btn_tel = tk.Button(subframe_botones_contactos, text="TEL", command=mostrar_telefonos,
                    width=12, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"),
                    relief="solid", bd=2)
btn_tel.pack(side=tk.LEFT, padx=5)
btn_tel.bind("<Enter>", on_enter)
btn_tel.bind("<Leave>", on_leave)



# Function to show the "NUESTROS" contacts window
def mostrar_nuestros():
    # Get position of main window
    x = root.winfo_x()
    y = root.winfo_y()
    ancho_principal = root.winfo_width()
    nueva_x = x + ancho_principal

    # Check if the window already exists
    for ventana in ventanas_hijas:
        if ventana.winfo_exists() and ventana.title() == "Contactos Nuestros":
            ventana.geometry(f"+{nueva_x}+{y}")
            ventana.lift()
            ventana.focus_force()
            return

    # Create new window
    ventana_nuestros = tk.Toplevel(root)
    ventana_nuestros.title("Contactos Nuestros")
    ventanas_hijas.append(ventana_nuestros)
    ventana_nuestros.transient(root)
    ancho_nueva = 510
    alto_nueva = 400
    ventana_nuestros.geometry(f"{ancho_nueva}x{alto_nueva}+{nueva_x}+{y}")
    ventana_nuestros.configure(bg="black")

    columnas = ("Nombre", "Correo", "Teléfono")
    tabla = ttk.Treeview(ventana_nuestros, columns=columnas, show="headings")
    tabla.pack(expand=True, fill="both", padx=10, pady=10)

    for col in columnas:
        tabla.column("Nombre", anchor="w", width=110)
        tabla.column("Correo", anchor="w", width=110)
        tabla.column("Teléfono", anchor="w", width=10)


    tabla.insert("", "end", values=(f"--- NUESTROS ---", "", ""))
    for contacto in contactos_nuestros:
        tabla.insert("", "end", values=contacto)
    tabla.insert("", "end", values=("", "", ""))

    estilo = ttk.Style()
    estilo.theme_use("default")
    estilo.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
    estilo.map("Treeview", background=[("selected", "gray")])

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

btn_nuestros = tk.Button(subframe_botones_contactos, text="NUESTROS", command=mostrar_nuestros,
                         width=12, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"),
                         relief="solid", bd=2)
btn_nuestros.pack(side=tk.LEFT, padx=5)
btn_nuestros.bind("<Enter>", on_enter)
btn_nuestros.bind("<Leave>", on_leave)




# Frame para el título y los botones de PRESENTACIÓN TURNOS
frame_turnos = tk.Frame(root, bg="#111111")
frame_turnos.pack(pady=5, fill="x")
label_turnos = tk.Label(frame_turnos, text="PRESENTACIÓN TURNOS", bg="#111111", fg="white", font=("Arial", 12, "bold"))
label_turnos.pack(pady=(0, 5))

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
    def confirmar_seleccion():
        seleccionados = [listbox.get(i) for i in listbox.curselection()]
        if len(seleccionados) < 1:
            messagebox.showwarning("Advertencia", "Selecciona al menos un integrante.")
            return

        if len(seleccionados) == 1:
            verbo = "continúo"
            nombres = ""  # No mostrar el nombre
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


    ventana_seleccion = tk.Toplevel(root)
    ventana_seleccion.title("Seleccionar integrantes")
    ventana_seleccion.geometry("300x400")
    ventana_seleccion.configure(bg="#111111")

    label = tk.Label(ventana_seleccion, text="Selecciona los integrantes:", bg="black", fg="white", font=("Arial", 10, "bold"))
    label.pack(pady=10)

    listbox = tk.Listbox(ventana_seleccion, selectmode=tk.MULTIPLE, bg="#E9E9E9", fg="black", font=("Arial", 10), height=10)
    listbox.pack(padx=10, pady=10, fill="both", expand=True)

    integrantes = [
        "Alvaro León Henao",
        "Claudia Yaneth Uribe Mora",
        "Edwin Fernando Rua",
        "Eduer Ferney Quintero",
        "Jonatan Fernando Rojas Marin",
        "Juan Pablo Rosero",
        "Mauricio Cardona Acosta"
    ]

    for nombre in integrantes:
        listbox.insert(tk.END, nombre)

    btn_confirmar = tk.Button(ventana_seleccion, text="Confirmar", command=confirmar_seleccion, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"))
    btn_confirmar.pack(pady=10)

# Botones de turnos
frame_botones_turnos = tk.Frame(frame_turnos, bg="#111111")
frame_botones_turnos.pack()
for turno in ["6-2", "2-10", "10-6"]:
    btn = tk.Button(frame_botones_turnos, text=turno, command=lambda t=turno: seleccionar_integrantes(t),
                    height=1, bg="#E9E9E9", fg="black", font=("Arial", 10, "bold"), relief="solid", bd=2, width=6)
    btn.pack(side=tk.LEFT, padx=5)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


frame_img = tk.Frame(root, bg="black")
frame_img.pack(pady=10)
def abrir_url(url):
    """Abre la URL dada en una nueva ventana del navegador."""
    try:
        webbrowser.open(url)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la URL:\n{e}")
def imagen_clicada(event):
    """
    Muestra la ventana de enlaces de Cygnus. Si ya está abierta, la enfoca y la reposiciona,
    agregando una barra de desplazamiento y los colores de los botones.
    """
    # Obtener la posición de la ventana principal
    x = root.winfo_x()
    y = root.winfo_y()
    ancho_principal = root.winfo_width()
    nueva_x = x + ancho_principal

    for ventana in ventanas_hijas:
        if ventana.winfo_exists() and ventana.title() == "Enlaces Cygnus":
            ventana.geometry(f"+{nueva_x}+{y}")
            ventana.lift()
            ventana.focus_force()
            return

    ventana_botones = tk.Toplevel(root)
    ventana_botones.title("Enlaces Cygnus")
    ventanas_hijas.append(ventana_botones)
    ventana_botones.transient(root)
    ventana_botones.geometry(f"228x590+{nueva_x}+{y}")
    ventana_botones.configure(bg="#111111")
    ventana_botones.resizable(False, False)

    # Crear el Canvas y la barra de desplazamiento
    contenedor_canvas = tk.Frame(ventana_botones, bg="black")
    contenedor_canvas.pack(side="left", fill="both", expand=True)

    canvas = tk.Canvas(contenedor_canvas, bg="black", highlightthickness=0)
    scrollbar = ttk.Scrollbar(contenedor_canvas, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Crear un Frame interior donde irán los botones
    frame_botones = tk.Frame(canvas, bg="black", padx=10, pady=10)
    canvas.create_window((0, 0), window=frame_botones, anchor="nw")

    def on_frame_configure(event):
        """Ajusta la región de desplazamiento del canvas cuando cambia el tamaño del frame."""
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Habilitar el desplazamiento con la rueda del mouse
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    frame_botones.bind("<Configure>", on_frame_configure)
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
        ("REPORTE HAPPY", "https://bancolombia.sharepoint.com.mcas.ms/sites/CO-VGH/SitePages/mis-beneficios-a-tiempo.aspx", "#CCB363"),
        ("CYGNUS HOME", "https://bancolombia.sharepoint.com/teams/Cygnus-AWS/SitePages/TrainingHome.aspx", "#CCB363"),
        ("CARPETA CYGNUS ONE DRIVE", "https://bancolombia.sharepoint.com/teams/PlataformasyDisponibilidaddeTI/Documentos%20compartidos/Forms/AllItems.aspx?id=%2Fteams%2FPlataformasyDisponibilidaddeTI%2FDocumentos%20compartidos%2FGeneral%2F02%2E%20Areas%2FIntegrada%C2%A0Operaci%C3%B3n%20TI%202%2FCYGNUS&viewid=57766697%2D4feb%2D4155%2Daa50%2D7e170cf7663f&csf=1&web=1&e=EkAc8b&FolderCTID=0x0120005E9D7AC01B2F224C9592BE475FCCCF12", "#CCB363"),
        ("CONECTADOS", "https://performancemanager8.successfactors.com/sf/start?_s.crb=aXY4tvGvZ%252bhWEJ65r%252bfyKs1XnEaUsD71QXK3e6RrN%252f8%253d", "#CCB363"),
        ("PORTAL CONTINUIDAD TI", "https://apps.powerapps.com/play/e/6bdfe354-f250-e0e7-941d-103fc5c5001d/a/913bb453-3222-4666-be40-dd026f570605?tenantId=b5e244bd-c492-495b-8b10-61bfd453e423", "#B85CCF"),
        ("PIPELINES", "https://bancolombia-is.onbmc.com/helix/index.html#/Autogestionados.Bancolombia/view/Autogestionados.Bancolombia:Servicios%20autogestionados", "#B85CCF"),
        ("GESTIONAR CAMBIOS TI", "https://bancolombia.sharepoint.com/sites/co-vsti/SitePages/sobre-nosotros_modelo-operativo_procesos_gestionar-cambios.aspx?xsdata=MDV8MDJ8fDdlNmJkODZkZDFiZDRiZDQ4YTgwMDhkZGVmZThjZTFmfGI1ZTI0NGJkYzQ5MjQ0NWI4YjEwNjFiZmQ0NTNlNDIzfDB8MHw2Mzg5MzA1MDUzMjYxMTU2Mjd8VW5rbm93bnxWR1ZoYlhOVFpXTjFjbWwwZVZObGNuWnBZMlY4ZXlKRFFTSTZJbFJsWVcxelgwRlVVRk5sY25acFkyVmZVMUJQVEU5R0lpd2lWaUk2SWpBdU1DNHdNREF3SWl3aVVDSTZJbGRwYmpNeUlpd2lRVTRpT2lKUGRHaGxjaUlzSWxkVUlqb3hNWDA9fDF8TDJOb1lYUnpMekU1T21GaU56bGlOV1ZoTFdVNVl6SXROR1l4TVMxaE16aGxMV000Tm1Oak9USTNZMk5sT1Y5bFlXVXlPVFppTWkwMFlqRmxMVFJoTVdRdFlUQmlZaTFoTVRZd01URmhPVGd3TmpaQWRXNXhMbWRpYkM1emNHRmpaWE12YldWemMyRm5aWE12TVRjMU56UTFNemN6TVRjME13PT18OTYyYWE2ZDdmNTZhNGE1YTNjMDcwOGRkZWZlOGNlMWZ8ZDU4NzVmNjI3OGUwNGU4Y2E5ZjUxNGM3NzE3ZTBhYWQ%3D&sdata=QlJkRWVIQVdLbGU3QWdVcEJENExja3FMQm1NQUZCK3BPaXpPOWFkZGJZdz0%3D&ovuser=b5e244bd-c492-495b-8b10-61bfd453e423%2Cefquinte%40bancolombia.com.co&OR=Teams-HL&CT=1757457468155&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiI0OS8yNTA4MTUwMDcxNyIsIkhhc0ZlZGVyYXRlZFVzZXIiOmZhbHNlfQ%3D%3D", "#B85CCF"),
        ("TABLERO HAs", "https://grupobancolombia.visualstudio.com/Vicepresidencia%20Servicios%20de%20Tecnología/_dashboards/dashboard/1f9264bd-fee1-48a1-bfd5-a8508c67acfb", "#C44141"),
        ("TABLERO CRQs", "https://bancolombia-ca1.onbmc.com/dashboards/d/b973b7b8-88f5-4201-a124-23f03094d644/tablero-cygnus?orgId=1271008613", "#C44141"),
        ("RESTRICCIÓN CAMBIOS", "https://bancolombia.sharepoint.com/:x:/r/sites/co-vsti/_layouts/15/Doc.aspx?sourcedoc=%7BDEC5F518-F360-4E63-99F6-8DA2FCA926DC%7D&file=Calendario%20Cambios%20Alto%20Impacto%20y%20Fechas%20Restricci%25u00f3n.xlsx&action=default&mobileredirect=true", "#D3DF68"),
        ("STAND BY", "https://bancolombia.sharepoint.com/sites/co-vsti/Lists/Programacin%20Stand%20By/IMes.aspx?viewid=ab3bc15f%2Dcce7%2D45c3%2D9eb4%2D319d54502d52&useFiltersInViewXml=1&OR=Teams%2DHL&CT=1706593136683&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiI0OS8yMzExMzAyODcyNCIsIkhhc0ZlZGVyYXRlZFVzZXIiOmZhbHNlfQ%3D%3D", "#D3DF68")
    ]
    
    for texto_boton, url, color in botones_coloreados:
        btn = tk.Button(frame_botones, text=texto_boton, command=lambda u=url: abrir_url(u),
                bg=color, fg="black", font=("Arial", 9, "bold"), relief="solid", bd=2)
        btn.pack(pady=1, fill="x")
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#E9E9E9"))
        btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))



# Modificando la ruta de la imagen
ruta_imagen = obtener_ruta_recurso("cygnussssss.png")
if os.path.exists(ruta_imagen):
    img = Image.open(ruta_imagen)
    img = img.resize((190, 150), Image.Resampling.LANCZOS)
    imagen_tk = ImageTk.PhotoImage(img)
    # Crea un widget Label con la imagen y lo empaqueta en el frame
    label_img = tk.Label(frame_img, image=imagen_tk, bd=0, highlightthickness=2, highlightbackground="gray")
    label_img.pack()
    # Guarda una referencia de la imagen para evitar que sea eliminada por el recolector de basura
    label_img.image = imagen_tk
    # Vincula el evento de clic a la imagen
    label_img.bind("<Button-1>", imagen_clicada)
    label_img.bind("<Enter>", on_enter_image)
    label_img.bind("<Leave>", on_leave_image)

# Inicia el bucle de eventos de Tkinter
root.mainloop() # Inicia el bucle principal de la aplicación.
