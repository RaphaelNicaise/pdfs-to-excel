class ConsoleRedirect:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, mensaje):
        self.textbox.insert("end", mensaje)
        self.textbox.see("end")
        self.textbox.update_idletasks()

    def flush(self):
        pass