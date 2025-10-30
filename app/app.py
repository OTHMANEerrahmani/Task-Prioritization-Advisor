import reflex as rx
from app.states.task_state import TaskState
from app.components.sidebar import sidebar
from app.components.main_panel import main_panel, calendar_view


def index() -> rx.Component:
    return rx.el.div(
        sidebar(),
        main_panel(),
        class_name="flex bg-gray-50 font-['Poppins'] min-h-screen",
    )


def calendar_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.div(calendar_view(), class_name="p-8 flex-1"),
            class_name="flex-1 h-screen overflow-y-auto",
        ),
        class_name="flex bg-gray-50 font-['Poppins'] min-h-screen",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, on_load=TaskState.load_initial_data)
app.add_page(calendar_page, route="/calendar", on_load=TaskState.load_initial_data)