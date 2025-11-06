import flet as ft
from controller import Controlador

class Loginvista:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Login"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.window.width = 411
        self.page.window.height = 831
        self.page.window.resizable = False
        self.page.clean()
        self.controlador = Controlador(page)
        self.build()

    def build(self):
        logo = ft.Image(src="condominio.png", width=150)
        usuario = ft.TextField(label="usuario")
        password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)

        def entrar(e):
            self.controlador.handle_login(usuario.value, password.value)

        def ir_a_registro(e):
            from registro import Registrovista
            self.page.clean()
            Registrovista(self.page)
        def porrol(e):
            from registro import Registrovista
            self.page.clean()
            Registrovista(self.page)


        self.page.add(
            ft.Column([
                logo,
                ft.Text("Iniciar Sesión", size=22, weight="bold"),
                usuario,
                password,
                ft.ElevatedButton("Entrar", on_click=entrar),
                ft.TextButton("Ir a Registro", on_click=ir_a_registro),
            ],
            alignment="center",
            horizontal_alignment="center",
            spacing=15
            )
        )

        