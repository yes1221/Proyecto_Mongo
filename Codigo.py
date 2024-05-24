import random
import string
import tkinter as tk
from tkinter import messagebox, simpledialog
from pymongo import MongoClient

# Conectar a la base de datos MongoDB
client = MongoClient('mongodb://192.168.29.1/')
db = client.hospital

# Comprobar y crear las colecciones si no existen
def crear_colecciones():
    if 'pacientes' not in db.list_collection_names():
        db.create_collection('pacientes')
    if 'doctores' not in db.list_collection_names():
        db.create_collection('doctores')
    if 'citas' not in db.list_collection_names():
        db.create_collection('citas')

# Función para generar un código personal aleatorio para pacientes nuevos
def generar_codigo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Función para verificar si el paciente existe y devolver su ID
def verificar_paciente(codigo):
    paciente = db.pacientes.find_one({"codigo": codigo})
    if paciente:
        return paciente['_id']
    else:
        return None

# Función para agregar un nuevo paciente
def agregar_paciente(nombre, edad):
    codigo = generar_codigo()
    db.pacientes.insert_one({"codigo": codigo, "nombre": nombre, "edad": edad})
    messagebox.showinfo("Éxito", "Paciente agregado con éxito. Su código personal es: " + codigo)
    return codigo  # Devolver el código generado

# Función para obtener los doctores disponibles
def obtener_doctores():
    doctores = db.doctores.find()
    return [(doctor['nombre'], doctor['especialidad']) for doctor in doctores]

# Función para agregar una cita para un paciente existente
def agregar_cita(codigo, fecha, hora, doctor):
    paciente_id = verificar_paciente(codigo)
    if paciente_id:
        db.citas.insert_one({"paciente_id": paciente_id, "fecha": fecha, "hora": hora, "doctor": doctor})
        messagebox.showinfo("Éxito", "Cita agregada con éxito para el paciente con código: " + codigo)
    else:
        messagebox.showerror("Error", "El paciente con el código proporcionado no existe.")

# Función para ver todas las citas de un paciente
def ver_citas(codigo):
    paciente_id = verificar_paciente(codigo)
    if paciente_id:
        citas = db.citas.find({"paciente_id": paciente_id})
        citas_list = list(citas)
        if citas_list:
            messagebox.showinfo("Citas del paciente", "\n".join([f"Fecha: {cita['fecha']}, Hora: {cita['hora']}, Doctor: {cita['doctor']}" for cita in citas_list]))
        else:
            messagebox.showinfo("Citas del paciente", "El paciente no tiene citas registradas.")
    else:
        messagebox.showerror("Error", "El paciente con el código proporcionado no existe.")

# Función para cancelar una cita de un paciente
def cancelar_cita(codigo, fecha, hora):
    paciente_id = verificar_paciente(codigo)
    if paciente_id:
        db.citas.delete_one({"paciente_id": paciente_id, "fecha": fecha, "hora": hora})
        messagebox.showinfo("Éxito", "Cita cancelada con éxito para el paciente con código: " + codigo)
        # Actualizar la vista de citas después de la cancelación
        ver_citas(codigo)
    else:
        messagebox.showerror("Error", "El paciente con el código proporcionado no existe.")

# Función para agregar los doctores predefinidos en la base de datos
def agregar_doctores_predefinidos():
    doctores = [
        {"nombre": "Dr. Juan Pérez", "especialidad": "General"},
        {"nombre": "Dra. María García", "especialidad": "Dermatólogo"},
        {"nombre": "Dr. Carlos López", "especialidad": "Otra especialidad"}
    ]
    db.doctores.insert_many(doctores)
    messagebox.showinfo("Éxito", "Doctores predefinidos agregados con éxito.")

# Agregar los doctores predefinidos al iniciar la aplicación
def inicializar_doctores():
    if db.doctores.count_documents({}) == 0:  # Solo agregar si no hay doctores en la colección
        agregar_doctores_predefinidos()

# Función para limpiar los datos introducidos
def limpiar_datos(codigo_entry, fecha_entry, hora_entry):
    codigo_entry.delete(0, tk.END)
    fecha_entry.delete(0, tk.END)
    hora_entry.delete(0, tk.END)

# Función principal de la aplicación
def main():
    root = tk.Tk()
    root.title("Hospital")

    # Verificar si el paciente es nuevo o no
    respuesta = messagebox.askquestion("Bienvenido", "¿Es su primera vez en el hospital?")
    if respuesta == 'yes':
        # Solicitar nombre y edad al paciente
        nombre = simpledialog.askstring("Nombre", "Por favor, ingrese su nombre:")
        edad = simpledialog.askinteger("Edad", "Por favor, ingrese su edad:")
        codigo = agregar_paciente(nombre, edad)
    else:
        codigo = simpledialog.askstring("Código", "Por favor, ingrese su código personal:")

    # Si el paciente no proporciona un código personal, finalizar la aplicación
    if not codigo:
        return

    # Obtener los doctores disponibles
    doctores = obtener_doctores()
    nombres_doctores = [doctor[0] + " - " + doctor[1] for doctor in doctores]

    # Crear etiquetas y campos de entrada para la interfaz gráfica
    tk.Label(root, text="Código del paciente:").grid(row=0, column=0)
    codigo_entry = tk.Entry(root)
    codigo_entry.grid(row=0, column=1)
    codigo_entry.insert(0, codigo)

    tk.Label(root, text="Fecha de la cita (YYYY-MM-DD):").grid(row=1, column=0)
    fecha_entry = tk.Entry(root)
    fecha_entry.grid(row=1, column=1)

    tk.Label(root, text="Hora de la cita (HH:MM):").grid(row=2, column=0)
    hora_entry = tk.Entry(root)
    hora_entry.grid(row=2, column=1)

    tk.Label(root, text="Doctor:").grid(row=3, column=0)
    doctor_var = tk.StringVar(root)
    doctor_var.set(nombres_doctores[0])  # Por defecto, selecciona el primer doctor de la lista
    doctor_option_menu = tk.OptionMenu(root, doctor_var, *nombres_doctores)
    doctor_option_menu.grid(row=3, column=1)

    # Función para manejar el botón de agregar cita
    def agregar_cita_handler():
        agregar_cita(codigo_entry.get(), fecha_entry.get(), hora_entry.get(), doctor_var.get().split(" - ")[0])
        limpiar_datos(codigo_entry, fecha_entry, hora_entry)

    agregar_button = tk.Button(root, text="Agregar cita", command=agregar_cita_handler)
    agregar_button.grid(row=4, column=0)

    # Botón para ver citas
    ver_button = tk.Button(root, text="Ver citas", command=lambda: ver_citas(codigo_entry.get()))
    ver_button.grid(row=4, column=1)

    # Botón para cancelar cita
    cancelar_button = tk.Button(root, text="Cancelar cita", command=lambda: cancelar_cita(codigo_entry.get(), fecha_entry.get(), hora_entry.get()))
    cancelar_button.grid(row=4, column=2)

    # Botón para salir
    salir_button = tk.Button(root, text="Salir", command=root.destroy)
    salir_button.grid(row=5, column=0)

    root.mainloop()

    # Limpiar todos los registros de la base de datos al salir
    db.pacientes.delete_many({})
    db.doctores.delete_many({})
    db.citas.delete_many({})

# Crear colecciones si no existen
crear_colecciones()

# Agregar doctores predefinidos si no existen
inicializar_doctores()

# Ejecutar la aplicación
main()