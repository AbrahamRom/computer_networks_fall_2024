from customtkinter import *
from CTkTable import CTkTable
import client
import chose_options as cho

# -------------------------
# Configuración inicial de CTk
# -------------------------
window = CTk()  # Se crea la ventana principal de la aplicación

# Configuración de la ventana: tamaño, prohibición de redimensionar, padding y título
window.geometry("900x630")
window.resizable(False, False)
window.config(padx=20, pady=20)
window.title("HTTP client")

# -------------------------
# Variables globales y estados iniciales
# -------------------------
statusCode = StringVar()  # Variable de cadena para mostrar el código de estado en la GUI
responseHeaders = [["Key", "Value"]]  # Cabecera por defecto para la tabla de respuestas

statusCode.set("Status: none")  # Se inicializa el estado en "none"

# Diccionario para gestionar las opciones de encabezados disponibles (True = ya usado, False = disponible)
headersSelectorDict = {}
headersResSize = 0  # Contador del número de encabezados agregados a la tabla de solicitud

# Se inicializa el diccionario con los encabezados definidos en cho_options (ver [chose_options.py](e:/Proyectos/computer_networks_fall_2024/HTTP Protocol/chose_options.py))
for header in cho.generalHeaders + cho.requestHeaders + cho.entityHeaders:
    headersSelectorDict[header] = False


# -------------------------
# Handlers (manejadores de eventos)
# -------------------------
def addBtnHandler():
    global headersResSize
    # Si no se ha seleccionado un encabezado, se retorna sin hacer nada
    if headersKeySelector.get() == "":
        return

    # Se agrega una fila a la tabla de solicitud con el encabezado y su valor correspondiente
    headersReqTable.add_row(
        [headersKeySelector.get(), headerValues.get()], headersResSize + 1
    )

    # Se marca el encabezado como usado (True) en el diccionario
    headersSelectorDict[headersKeySelector.get()] = True

    # Se generan nuevas listas de encabezados disponibles y de los ya agregados para actualizar los menús
    values = [header for header in headersSelectorDict if headersSelectorDict[header] == False]
    delValues = [header for header in headersSelectorDict if headersSelectorDict[header] == True]
    # Actualiza el menú de selección de encabezados disponibles
    headersKeySelector.configure(values=values)
    headersKeySelector.set(values[0] if len(values) > 0 else "")
    # Actualiza el menú de eliminación de encabezados disponibles
    headersRemoverKeySelector.configure(values=delValues)
    headersRemoverKeySelector.set(delValues[0])

    headersResSize += 1  # Incrementa el contador de encabezados agregados


def removeBtnHandler():
    # Si no se ha seleccionado ningún encabezado a remover, se retorna sin acción
    if headersRemoverKeySelector.get() == "":
        return

    # Marca el encabezado como no utilizado (False)
    headersSelectorDict[headersRemoverKeySelector.get()] = False

    # Busca y elimina la fila correspondiente en la tabla de solicitud
    for i, header in enumerate(headersReqTable.values):
        if header[0] == headersRemoverKeySelector.get():
            headersReqTable.delete_row(i)
            break

    # Actualiza las listas de encabezados disponibles y los ya utilizados tras la eliminación
    values = [header for header in headersSelectorDict if headersSelectorDict[header] == False]
    delValues = [header for header in headersSelectorDict if headersSelectorDict[header] == True]
    headersKeySelector.configure(values=values)
    headersKeySelector.set(values[0])
    headersRemoverKeySelector.configure(values=delValues)
    headersRemoverKeySelector.set(delValues[0] if len(delValues) > 0 else "")



def sendBtnHandler():
    global responseHeaders

    # Se extraen los encabezados ingresados en la tabla. Se omite la fila de cabecera
    headers = [(row[0], row[1]) for row in headersReqTable.values[1:]]
    # Se realiza el request utilizando los valores de la interfaz:
    # - método desde el menú desplegable
    # - URL desde el campo de texto
    # - encabezados y cuerpo desde el textbox correspondiente
    status, response_headers, body = client.request(
        methodMenu.get(), URL.get(), headers, bodyReqFrame.get(0.0, "end")
    )
    # Se formatea la respuesta para incluir como cabecera la fila por defecto
    responseHeaders = [["Key", "Value"]] + response_headers

    print(f"[body] {body}")  # Imprime el cuerpo de la respuesta en la consola para depuración

    statusCode.set("Status: " + status)  # Actualiza la etiqueta del estado con el código de respuesta

    # Se limpia y se actualiza la tabla de respuesta con los nuevos encabezados
    headersResTable.delete_rows([i for i in range(0, headersResTable.rows)])
    for header in responseHeaders:
        headersResTable.add_row(header, headersResTable.rows)

    # Se actualiza el área de texto del cuerpo de la respuesta
    bodyResFrame.delete(0.0, "end")
    bodyResFrame.insert(0.0, body)



# -------------------------
# Configuración de la sección de solicitud
# -------------------------
# Menú desplegable para seleccionar el método HTTP (valores definidos en [chose_options.py](e:/Proyectos/computer_networks_fall_2024/HTTP Protocol/chose_options.py))
methodMenu = CTkComboBox(window, values=cho.methods)
# Entrada para la URL de la solicitud
URL = CTkEntry(window, placeholder_text="URL", width=630, font=("", 11))
# Botón para enviar la solicitud, vinculado a sendBtnHandler
sendBtn = CTkButton(window, width=100, font=("", 11), text="Send", command=sendBtnHandler)

# Se crea un Tabview para agrupar los datos de la solicitud (encabezados y cuerpo)
requestDataFields = CTkTabview(window, width=870, height=200, anchor="nw")
headersReqTab = requestDataFields.add("Headers")
bodyReqTab = requestDataFields.add("Body")

# Se establecen frames dentro de cada Tab para contener los widgets
headersReqFrame = CTkScrollableFrame(headersReqTab, width=830, height=190)
bodyReqFrame = CTkTextbox(bodyReqTab, width=850, height=210)

# Tabla para mostrar los encabezados de la solicitud (inicialmente con la cabecera ["Key", "Value"])
headersReqTable = CTkTable(headersReqFrame, column=2, values=[["Key", "Value"]], width=410)

# Menú para seleccionar un encabezado a añadir (se muestran aquellos que aún no fueron agregados)
headersKeySelector = CTkOptionMenu(
    headersReqFrame,
    values=[header for header in headersSelectorDict if headersSelectorDict[header] == False],
)
# Campo de texto para ingresar el valor del encabezado seleccionado
headerValues = CTkEntry(headersReqFrame, width=550)
# Botón que invoca la función para agregar el encabezado
addHeaderBtn = CTkButton(headersReqFrame, text="ADD", command=addBtnHandler)

# Menú para seleccionar un encabezado a remover (se muestran aquellos que ya han sido agregados)
headersRemoverKeySelector = CTkOptionMenu(
    headersReqFrame,
    values=[header for header in headersSelectorDict if headersSelectorDict[header] == True],
)
# Botón que invoca la función para remover el encabezado
removeHeaderBtn = CTkButton(headersReqFrame, text="Remove", command=removeBtnHandler)
# Se inicializa el menú de remover encabezados en blanco
headersRemoverKeySelector.set("")

# Se ubican los widgets de la sección de solicitud en la ventana
methodMenu.grid(row=0, column=0)
URL.grid(row=0, column=1)
sendBtn.grid(row=0, column=2)
requestDataFields.grid(row=1, column=0, columnspan=3)

# Se empaquetan los frames dentro de los tabs
headersReqFrame.pack(fill="both", expand=True)
bodyReqFrame.pack(fill="both", expand=True)
# Se ubica la tabla de encabezados en el frame correspondiente
headersReqTable.grid(row=0, column=0, columnspan=3, pady=(0, 10))
# Ubicación de los widgets para agregar y remover encabezados
headersKeySelector.grid(row=1, column=0)
headerValues.grid(row=1, column=1)
addHeaderBtn.grid(row=1, column=2)
headersRemoverKeySelector.grid(row=2, column=0, pady=10)
removeHeaderBtn.grid(row=2, column=2, pady=10)

# -------------------------
# Configuración de la sección de respuesta
# -------------------------
# Etiqueta "Response" y etiqueta para el estado de la respuesta
responseLabel = CTkLabel(window, text="Response", anchor="w")
statusCodeLabel = CTkLabel(window, textvariable=statusCode)

# Tabview para agrupar la información de la respuesta (encabezados, cuerpo y cookies)
responseDataFields = CTkTabview(window, width=870, height=200, anchor="nw")
headersResTab = responseDataFields.add("Headers")
bodyResTab = responseDataFields.add("Body")
cookiesResTab = responseDataFields.add("Cookies")

# Se crean frames para cada sección de respuesta
headersResFrame = CTkScrollableFrame(headersResTab, width=830, height=200)
bodyResFrame = CTkTextbox(bodyResTab, width=850, height=210)
cookiesResFrame = CTkScrollableFrame(cookiesResTab, width=830, height=200)

# Tabla para mostrar los encabezados de la respuesta, iniciando con la fila de cabecera
headersResTable = CTkTable(headersResFrame, column=2, values=responseHeaders)
# Tabla para mostrar las cookies de la respuesta, con columnas específicas
cookiesResTable = CTkTable(
    cookiesResFrame,
    column=7,
    values=[["Name", "Value", "Domain", "Path", "Expires", "HttpOnly", "Secure"]],
)

# Ubicación de las etiquetas y del tabview de respuesta en la ventana
responseLabel.grid(row=2, column=0)
statusCodeLabel.grid(row=2, column=1, columnspan=2)
responseDataFields.grid(row=3, column=0, columnspan=3)

# Empaquetado de los frames y tablas de la respuesta
headersResFrame.pack(fill="both", expand=True)
bodyResFrame.pack(fill="both", expand=True)
cookiesResFrame.pack(fill="both", expand=True)
headersResTable.pack(fill="both", expand=True)
cookiesResTable.pack(fill="both", expand=True)

# -------------------------
# Inicio de la aplicación
# -------------------------
window.mainloop()  # Inicia el loop principal de la interfaz gráfica
