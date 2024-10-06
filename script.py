import pywhatkit
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import re

class WhatsAppSender:
    def __init__(self, master):
        self.master = master
        master.title("Envío de Mensajes por WhatsApp")
        master.geometry("600x800")
        master.configure(bg="#f0f0f0")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6, relief="flat", background="#4CAF50", foreground="white")
        style.map("TButton", background=[("active", "#45a049")])
        

        self.create_widgets()

    def create_widgets(self):
        # Marco para la entrada del mensaje
        message_frame = tk.Frame(self.master, bg="#f0f0f0")
        message_frame.pack(pady=(20, 10))

        # Entrada del mensaje
        tk.Label(message_frame, text="Plantilla de Mensaje:", bg="#f0f0f0", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.message_entry = scrolledtext.ScrolledText(message_frame, height=5, width=60, font=("Helvetica", 10))
        self.message_entry.pack()

        # Marco para la lista de estudiantes
        student_frame = tk.Frame(self.master, bg="#f0f0f0")
        student_frame.pack(pady=(10, 10))

        # Entrada de la lista de estudiantes
        tk.Label(student_frame, text="Lista de Estudiantes (Nombre, Número):", bg="#f0f0f0", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.student_entry = scrolledtext.ScrolledText(student_frame, height=10, width=60, font=("Helvetica", 10))
        self.student_entry.pack()

        # Marco para los botones
        buttons_frame = tk.Frame(self.master, bg="#f0f0f0")
        buttons_frame.pack(pady=10)

        # Botón para procesar datos
        self.process_btn = ttk.Button(buttons_frame, text="Procesar Datos", command=self.process_data)
        self.process_btn.pack(side="left", padx=5)

        # Botón para enviar mensajes
        self.send_btn = ttk.Button(buttons_frame, text="Enviar Mensajes", command=self.start_sending, state='disabled')
        self.send_btn.pack(side="left", padx=5)

        # Área de texto para mostrar la lista procesada
        tk.Label(self.master, text="Lista Procesada:", bg="#f0f0f0", font=("Helvetica", 10, "bold")).pack(pady=(10, 5))
        self.output_text = scrolledtext.ScrolledText(self.master, height=10, width=60, font=("Helvetica", 10), state='disabled')
        self.output_text.pack(pady=10)

        # Barra de progreso
        self.progress = ttk.Progressbar(self.master, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Etiqueta de estado
        self.status_label = tk.Label(self.master, text="", bg="#f0f0f0", font=("Helvetica", 10))
        self.status_label.pack(pady=5)

    def process_data(self):
        self.message_template = self.message_entry.get("1.0", tk.END).strip()
        student_data = self.student_entry.get("1.0", tk.END).strip()

        if not self.message_template or not student_data:
            messagebox.showerror("Error", "Por favor, ingrese tanto la plantilla de mensaje como los datos de estudiantes.")
            return

        self.students = self.parse_student_data(student_data)
        if not self.students:
            messagebox.showerror("Error", "Formato de datos de estudiantes inválido.")
            return

        self.update_output()
        self.send_btn.config(state='normal')
        messagebox.showinfo("Éxito", "Datos procesados correctamente. Puede proceder a enviar los mensajes.")

    def parse_student_data(self, data):
        students = []
        for line in data.strip().split('\n'):
            # Separar por comas, tabulaciones o dos o más espacios
            parts = re.split(r'\s*,\s*|\s{2,}|\t+', line.strip())
            if len(parts) >= 2:
                name = parts[0].strip()
                number = parts[1].strip().replace('-', '').replace(' ', '')
                if not number.startswith('+'):
                    number = '+52' + number
                students.append({'name': name, 'number': number})
            else:
                print(f"Error al procesar la línea: {line}")
        return students

    def update_output(self):
        self.output_text.config(state='normal')
        self.output_text.delete("1.0", tk.END)
        for student in self.students:
            self.output_text.insert(tk.END, f"{student['name']} - {student['number']}\n")
        self.output_text.config(state='disabled')

    def start_sending(self):
        self.send_btn.config(state='disabled')
        self.process_btn.config(state='disabled')
        threading.Thread(target=self.send_messages, daemon=True).start()

    def send_messages(self):
        total = len(self.students)
        for i, student in enumerate(self.students, 1):
            try:
                message = self.message_template.replace("{nombre}", student['name'])
                # Actualizar el estado
                self.update_status(f"Enviando a {student['name']} ({i}/{total})")
                pywhatkit.sendwhatmsg_instantly(student['number'], message, wait_time=20)
                print(f"Mensaje enviado a {student['name']} al número {student['number']}")
                time.sleep(15)  # Ajustar el tiempo entre mensajes según sea necesario
            except Exception as e:
                self.update_status(f"Error al enviar a {student['name']}: {str(e)}")
                print(f"Error al enviar a {student['name']}: {str(e)}")
            self.progress['value'] = (i / total) * 100
            time.sleep(5)  # Ajustar el tiempo entre mensajes según sea necesario

        self.master.after(0, self.sending_completed)

    def update_status(self, message):
        self.master.after(0, lambda: self.status_label.config(text=message))

    def sending_completed(self):
        messagebox.showinfo("Completo", "Todos los mensajes han sido enviados.")
        self.send_btn.config(state='normal')
        self.process_btn.config(state='normal')
        self.progress['value'] = 0
        self.status_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppSender(root)
    root.mainloop()
