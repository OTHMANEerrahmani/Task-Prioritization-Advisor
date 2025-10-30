import reflex as rx
from app.states.task_state import TaskState
import datetime


def main_panel() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "Task Dashboard", class_name="text-2xl font-bold text-gray-900"
                    ),
                    rx.el.p(
                        "Here's your task overview for today.",
                        class_name="text-gray-500",
                    ),
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-2"),
                    "Add New Task",
                    on_click=TaskState.toggle_task_form,
                    class_name="flex items-center bg-purple-600 text-white px-4 py-2 rounded-lg shadow-sm hover:bg-purple-700 transition-colors",
                ),
                class_name="flex justify-between items-center",
            ),
            stats_cards(),
            rx.el.div(
                task_list(),
                calendar_view(),
                class_name="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6",
            ),
            add_task_modal(),
            class_name="p-8 flex-1",
        ),
        class_name="flex-1 h-screen overflow-y-auto",
    )


def stats_cards() -> rx.Component:
    return rx.el.div(
        stat_card(
            "Total Tasks",
            TaskState.task_stats["total"],
            "align-justify",
            "bg-blue-100 text-blue-600",
        ),
        stat_card(
            "Active",
            TaskState.task_stats["active"],
            "loader",
            "bg-yellow-100 text-yellow-600",
        ),
        stat_card(
            "Urgent", TaskState.task_stats["urgent"], "siren", "bg-red-100 text-red-600"
        ),
        stat_card(
            "Completed",
            TaskState.task_stats["completed"],
            "check_check",
            "bg-green-100 text-green-600",
        ),
        class_name="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mt-6",
    )


def stat_card(
    title: str, value: rx.Var[int], icon: str, color_classes: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6"),
            class_name=f"p-3 rounded-lg {color_classes}",
        ),
        rx.el.div(
            rx.el.p(title, class_name="text-sm text-gray-500 font-medium"),
            rx.el.p(value.to_string(), class_name="text-2xl font-bold text-gray-900"),
        ),
        class_name="flex items-center gap-4 bg-white p-5 rounded-xl border border-gray-100 shadow-sm",
    )


def task_list() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2("Recommended Tasks", class_name="text-lg font-bold text-gray-800"),
            rx.el.p(
                "Top 5 tasks based on priority score.",
                class_name="text-sm text-gray-500",
            ),
        ),
        rx.el.div(
            rx.foreach(TaskState.recommended_tasks, task_item),
            class_name="flex flex-col gap-3 mt-4",
        ),
        class_name="lg:col-span-1 bg-white p-6 rounded-xl border border-gray-100 shadow-sm",
    )


def task_item(task: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.button(
                rx.icon(
                    rx.cond(task["completed"], "check-circle-2", "circle"),
                    class_name="h-5 w-5",
                ),
                on_click=TaskState.toggle_completed(task["id"]),
                class_name=rx.cond(
                    task["completed"],
                    "text-green-500",
                    "text-gray-300 hover:text-purple-500",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    task["nom"],
                    class_name=rx.cond(
                        task["completed"],
                        "text-gray-500 line-through",
                        "text-gray-800 font-medium",
                    ),
                ),
                rx.el.div(
                    badge(
                        rx.cond(task["urgente"], "Urgent", ""),
                        "bg-red-100 text-red-600",
                    ),
                    badge(
                        rx.cond(task["importante"], "Important", ""),
                        "bg-yellow-100 text-yellow-600",
                    ),
                    badge(
                        rx.cond(
                            task["deadline"],
                            "Due: "
                            + task["deadline"].to_string().split("-")[1]
                            + "-"
                            + task["deadline"].to_string().split("-")[2],
                            "",
                        ),
                        "bg-blue-100 text-blue-600",
                    ),
                    class_name="flex items-center gap-2 mt-1",
                ),
            ),
            class_name="flex items-start gap-3",
        ),
        rx.el.div(
            rx.el.p(task["score"].to_string(), class_name="font-bold text-lg"),
            rx.el.button(
                rx.icon("trash-2", class_name="h-4 w-4"),
                on_click=TaskState.delete_task(task["id"]),
                class_name="text-gray-400 hover:text-red-500 transition-colors",
            ),
            class_name="flex items-center gap-2 text-purple-600",
        ),
        class_name="flex justify-between items-center p-3 rounded-lg hover:bg-gray-50 transition-colors",
    )


def badge(text: rx.Var[str], color_classes: str) -> rx.Component:
    return rx.cond(
        text != "",
        rx.el.span(
            text,
            class_name=f"px-2 py-0.5 text-xs font-semibold rounded-full {color_classes}",
        ),
        rx.fragment(),
    )


def add_task_modal() -> rx.Component:
    return rx.cond(
        TaskState.show_task_form,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2("Add New Task", class_name="text-lg font-bold"),
                    rx.el.button(
                        rx.icon("x"),
                        on_click=TaskState.toggle_task_form,
                        class_name="text-gray-500 hover:text-gray-800",
                    ),
                    class_name="flex justify-between items-center pb-4 border-b",
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label("Task Name", class_name="text-sm font-medium"),
                        rx.el.input(
                            placeholder="e.g., Finalize report",
                            name="nom",
                            class_name="w-full mt-1 p-2 border rounded-md",
                        ),
                        class_name="mt-4",
                    ),
                    rx.el.div(
                        rx.el.label("Deadline", class_name="text-sm font-medium"),
                        rx.el.input(
                            type="date",
                            name="deadline",
                            class_name="w-full mt-1 p-2 border rounded-md",
                        ),
                        class_name="mt-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Estimated Time (minutes)", class_name="text-sm font-medium"
                        ),
                        rx.el.input(
                            type="number",
                            name="temps_estime",
                            default_value=TaskState.new_task_time,
                            class_name="w-full mt-1 p-2 border rounded-md",
                        ),
                        class_name="mt-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.input(
                                type="checkbox", name="urgente", class_name="h-4 w-4"
                            ),
                            rx.el.label("Urgent", class_name="ml-2 text-sm"),
                            class_name="flex items-center",
                        ),
                        rx.el.div(
                            rx.el.input(
                                type="checkbox", name="importante", class_name="h-4 w-4"
                            ),
                            rx.el.label("Important", class_name="ml-2 text-sm"),
                            class_name="flex items-center",
                        ),
                        class_name="flex gap-6 mt-4",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=TaskState.toggle_task_form,
                            class_name="px-4 py-2 bg-gray-200 rounded-lg",
                        ),
                        rx.el.button(
                            "Add Task",
                            type="submit",
                            class_name="px-4 py-2 bg-purple-600 text-white rounded-lg",
                        ),
                        class_name="flex justify-end gap-3 pt-4 mt-4 border-t",
                    ),
                    on_submit=TaskState.add_task,
                ),
                class_name="bg-white p-6 rounded-xl shadow-2xl w-full max-w-md",
            ),
            class_name="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50",
        ),
    )


def calendar_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    TaskState.calendar_title,
                    class_name="text-lg font-bold text-gray-800",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("chevron-left"),
                        on_click=TaskState.prev_month,
                        class_name="p-1 hover:bg-gray-100 rounded-md",
                    ),
                    rx.el.button(
                        rx.icon("chevron-right"),
                        on_click=TaskState.next_month,
                        class_name="p-1 hover:bg-gray-100 rounded-md",
                    ),
                    class_name="flex items-center gap-2",
                ),
            ),
            rx.el.div(
                calendar_filter_button("All", "all"),
                calendar_filter_button("High", "high"),
                calendar_filter_button("Medium", "medium"),
                calendar_filter_button("Low", "low"),
                class_name="flex items-center gap-2 mt-4",
            ),
            class_name="flex justify-between items-center",
        ),
        rx.el.div(
            rx.el.div(
                rx.foreach(
                    ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                    lambda day: rx.el.div(
                        day,
                        class_name="text-center text-xs font-semibold text-gray-500",
                    ),
                ),
                class_name="grid grid-cols-7 gap-px mt-4",
            ),
            rx.el.div(
                rx.foreach(TaskState.calendar_grid, calendar_week),
                class_name="grid grid-cols-1",
            ),
        ),
        class_name="lg:col-span-2 bg-white p-6 rounded-xl border border-gray-100 shadow-sm",
    )


def calendar_filter_button(text: str, filter_type: str) -> rx.Component:
    is_active = TaskState.calendar_filter == filter_type
    return rx.el.button(
        text,
        on_click=TaskState.set_calendar_filter(filter_type),
        class_name=rx.cond(
            is_active,
            "px-3 py-1 text-sm rounded-md bg-purple-100 text-purple-700 font-semibold",
            "px-3 py-1 text-sm rounded-md bg-gray-100 text-gray-600 hover:bg-gray-200",
        ),
    )


def calendar_week(week_data: rx.Var[list]) -> rx.Component:
    return rx.el.div(
        rx.foreach(week_data, calendar_day), class_name="grid grid-cols-7 gap-px"
    )


def calendar_day(day_data: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.cond(
            day_data,
            rx.el.div(
                rx.el.p(
                    day_data["day"].to_string(),
                    class_name=rx.cond(
                        day_data["is_today"],
                        "flex items-center justify-center h-6 w-6 rounded-full bg-purple-600 text-white text-xs font-bold",
                        "text-xs font-medium",
                    ),
                ),
                rx.el.div(
                    rx.foreach(day_data["tasks"], calendar_task_dot),
                    class_name="flex items-center justify-center gap-1 mt-1",
                ),
                class_name="flex flex-col items-center justify-start h-24 p-1 border-t border-gray-100",
            ),
            rx.el.div(class_name="h-24"),
        )
    )


def calendar_task_dot(task: dict) -> rx.Component:
    task_var = rx.Var.create(task, dict)
    return rx.el.div(
        rx.el.div(task_var["nom"], class_name="sr-only"),
        class_name=rx.cond(
            task_var["score"] >= 500,
            "h-1.5 w-1.5 rounded-full bg-red-500",
            rx.cond(
                task_var["score"] >= 100,
                "h-1.5 w-1.5 rounded-full bg-yellow-500",
                "h-1.5 w-1.5 rounded-full bg-green-500",
            ),
        ),
        custom_attrs={"title": task_var["nom"]},
    )