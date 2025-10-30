import reflex as rx
from app.states.task_state import TaskState


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("bar-chart-horizontal", class_name="h-8 w-8 text-purple-600"),
                rx.el.h1(
                    "Virtual Advisor", class_name="font-bold text-xl text-gray-800"
                ),
                class_name="flex items-center gap-3 p-6 border-b border-gray-200",
            ),
            rx.el.div(
                rx.el.h2(
                    "Menu",
                    class_name="px-6 pt-6 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider",
                ),
                nav_item("List view", "list", "/", TaskState.router.page.path == "/"),
                nav_item(
                    "Calendar view",
                    "calendar-days",
                    "/calendar",
                    TaskState.router.page.path == "/calendar",
                ),
                class_name="flex flex-col gap-1",
            ),
            class_name="flex flex-col h-full",
        ),
        class_name="w-64 h-screen bg-white border-r border-gray-200 shrink-0",
    )


def nav_item(
    text: str, icon_name: str, href: str, is_active: rx.Var[bool]
) -> rx.Component:
    return rx.el.a(
        rx.icon(icon_name, class_name="h-5 w-5"),
        rx.el.span(text),
        href=href,
        class_name=rx.cond(
            is_active,
            "flex items-center gap-3 px-6 py-2.5 text-sm font-semibold text-purple-600 bg-purple-50 border-r-2 border-purple-600",
            "flex items-center gap-3 px-6 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors",
        ),
    )