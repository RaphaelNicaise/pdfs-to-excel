class ConsoleRedirect:
    """
    Clase para redirigir la salida estandar a un widget de texto de Tkinter.
    """
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, mensaje):
        self.textbox.insert("end", mensaje)
        self.textbox.see("end")
        self.textbox.update_idletasks()

    def flush(self):
        pass