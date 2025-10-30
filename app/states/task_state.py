import reflex as rx
import datetime
from typing import TypedDict, Literal, Optional, Union
import logging


class Tache(TypedDict):
    id: int
    nom: str
    urgente: bool
    importante: bool
    deadline: str | None
    temps_estime: int
    score: int
    completed: bool


class CalendarTask(TypedDict):
    nom: str
    score: int


class CalendarDay(TypedDict):
    day: int
    is_today: bool
    tasks: list[CalendarTask]


class TaskState(rx.State):
    tasks: list[Tache] = []
    new_task_name: str = ""
    new_task_urgent: bool = False
    new_task_important: bool = False
    new_task_deadline: str = ""
    new_task_time: int = 30
    next_id: int = 1
    current_filter: str = "all"
    sort_by: str = "score"
    calendar_date: datetime.date = datetime.date.today()
    calendar_filter: str = "all"
    show_task_form: bool = False

    @rx.event
    def load_initial_data(self):
        self.load_test_scenario("scenario_1")

    def _calculate_score(self, task: Tache) -> int:
        score = 0
        if task["urgente"] and task["importante"]:
            score += 1000
        elif task["urgente"] and (not task["importante"]):
            score += 500
        elif not task["urgente"] and task["importante"]:
            score += 300
        if task["deadline"]:
            try:
                deadline_date = datetime.datetime.fromisoformat(task["deadline"]).date()
                days_to_deadline = (deadline_date - datetime.date.today()).days
                if days_to_deadline < 0:
                    score += 100 * abs(days_to_deadline)
                elif days_to_deadline <= 1:
                    score += 200
                elif days_to_deadline <= 3:
                    score += 100
                elif days_to_deadline <= 7:
                    score += 50
            except (ValueError, TypeError) as e:
                logging.exception(f"Error parsing deadline: {e}")
        if task["temps_estime"] <= 15:
            score += 40
        elif task["temps_estime"] <= 30:
            score += 20
        if task["deadline"]:
            score += 10
        score += 5
        if not task["urgente"] and (not task["importante"]):
            score -= 50
        if task["urgente"] and task["temps_estime"] > 120:
            score -= 20
        if task["importante"] and task["temps_estime"] < 30:
            score += 30
        return score

    @rx.event
    def add_task(self, form_data: dict):
        task_name = form_data.get("nom", "").strip()
        if not task_name:
            return rx.toast("Task name cannot be empty.", duration=3000)
        new_task: Tache = {
            "id": self.next_id,
            "nom": task_name,
            "urgente": bool(form_data.get("urgente")),
            "importante": bool(form_data.get("importante")),
            "deadline": form_data.get("deadline") or None,
            "temps_estime": int(form_data.get("temps_estime", 30)),
            "score": 0,
            "completed": False,
        }
        new_task["score"] = self._calculate_score(new_task)
        self.tasks.append(new_task)
        self.next_id += 1
        self.show_task_form = False
        return rx.toast("Task added successfully!", duration=3000)

    @rx.event
    def toggle_task_form(self):
        self.show_task_form = not self.show_task_form

    @rx.event
    def delete_task(self, task_id: int):
        self.tasks = [t for t in self.tasks if t["id"] != task_id]

    @rx.event
    def toggle_completed(self, task_id: int):
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                self.tasks[i]["completed"] = not self.tasks[i]["completed"]
                break

    @rx.var
    def filtered_tasks(self) -> list[Tache]:
        tasks = self.tasks
        if self.current_filter == "urgent":
            tasks = [t for t in tasks if t["urgente"]]
        elif self.current_filter == "important":
            tasks = [t for t in tasks if t["importante"]]
        elif self.current_filter == "completed":
            tasks = [t for t in tasks if t["completed"]]
        elif self.current_filter == "active":
            tasks = [t for t in tasks if not t["completed"]]
        return sorted(
            tasks, key=lambda t: t.get(self.sort_by, 0), reverse=self.sort_by == "score"
        )

    @rx.var
    def recommended_tasks(self) -> list[Tache]:
        return sorted(
            [task for task in self.tasks if not task["completed"]],
            key=lambda t: t["score"],
            reverse=True,
        )[:5]

    @rx.var
    def task_stats(self) -> dict[str, int]:
        total = len(self.tasks)
        completed = sum((1 for t in self.tasks if t["completed"]))
        urgent = sum((1 for t in self.tasks if t["urgente"] and (not t["completed"])))
        important = sum(
            (1 for t in self.tasks if t["importante"] and (not t["completed"]))
        )
        return {
            "total": total,
            "completed": completed,
            "urgent": urgent,
            "important": important,
            "active": total - completed,
        }

    @rx.event
    def prev_month(self):
        self.calendar_date = self.calendar_date.replace(day=1) - datetime.timedelta(
            days=1
        )

    @rx.event
    def next_month(self):
        self.calendar_date = (
            self.calendar_date.replace(day=28) + datetime.timedelta(days=4)
        ).replace(day=1)

    @rx.event
    def set_calendar_filter(self, filter_type: str):
        self.calendar_filter = filter_type

    @rx.var
    def calendar_grid(self) -> list[list[CalendarDay | None]]:
        today = datetime.date.today()
        year = self.calendar_date.year
        month = self.calendar_date.month
        first_day = datetime.date(year, month, 1)
        start_weekday = first_day.weekday()
        if start_weekday == 6:
            start_weekday = -1
        month_days = (
            (datetime.date(year, month % 12 + 1, 1) - datetime.timedelta(days=1)).day
            if month < 12
            else 31
        )
        days = [None] * (start_weekday + 1) + list(range(1, month_days + 1))
        days += [None] * (42 - len(days))
        grid = []
        for i in range(0, len(days), 7):
            week = []
            for day in days[i : i + 7]:
                if day is None:
                    week.append(None)
                    continue
                current_date = datetime.date(year, month, day)
                tasks_for_day = []
                for task in self.tasks:
                    if task["deadline"]:
                        try:
                            deadline_date = datetime.date.fromisoformat(
                                task["deadline"]
                            )
                            if deadline_date == current_date:
                                if (
                                    self.calendar_filter == "all"
                                    or (
                                        self.calendar_filter == "high"
                                        and task["score"] >= 500
                                    )
                                    or (
                                        self.calendar_filter == "medium"
                                        and 100 <= task["score"] < 500
                                    )
                                    or (
                                        self.calendar_filter == "low"
                                        and task["score"] < 100
                                    )
                                ):
                                    tasks_for_day.append(
                                        {"nom": task["nom"], "score": task["score"]}
                                    )
                        except ValueError as e:
                            logging.exception(
                                f"Error parsing deadline in calendar: {e}"
                            )
                            continue
                week.append(
                    {
                        "day": day,
                        "is_today": current_date == today,
                        "tasks": sorted(
                            tasks_for_day, key=lambda t: t["score"], reverse=True
                        ),
                    }
                )
            grid.append(week)
        return grid

    @rx.var
    def calendar_title(self) -> str:
        return self.calendar_date.strftime("%B %Y")

    def _formatted_deadline(self, deadline_str: str | None) -> str:
        if not deadline_str:
            return ""
        try:
            deadline_date = datetime.date.fromisoformat(deadline_str)
            return deadline_date.strftime("%b %d")
        except (ValueError, TypeError) as e:
            logging.exception(f"Error formatting deadline: {e}")
            return ""

    @rx.event
    def load_test_scenario(self, scenario: Literal["scenario_1", "scenario_2"]):
        self.tasks = []
        self.next_id = 1
        today = datetime.date.today()
        if scenario == "scenario_1":
            self.tasks = [
                {
                    "id": 1,
                    "nom": "Finaliser le rapport trimestriel",
                    "urgente": True,
                    "importante": True,
                    "deadline": (today + datetime.timedelta(days=2)).isoformat(),
                    "temps_estime": 120,
                    "score": 0,
                    "completed": False,
                },
                {
                    "id": 2,
                    "nom": "Préparer la présentation client",
                    "urgente": False,
                    "importante": True,
                    "deadline": (today + datetime.timedelta(days=5)).isoformat(),
                    "temps_estime": 90,
                    "score": 0,
                    "completed": False,
                },
                {
                    "id": 3,
                    "nom": "Répondre aux emails urgents",
                    "urgente": True,
                    "importante": False,
                    "deadline": today.isoformat(),
                    "temps_estime": 30,
                    "score": 0,
                    "completed": False,
                },
                {
                    "id": 4,
                    "nom": "Organiser la réunion d'équipe",
                    "urgente": False,
                    "importante": False,
                    "deadline": (today + datetime.timedelta(days=7)).isoformat(),
                    "temps_estime": 45,
                    "score": 0,
                    "completed": True,
                },
                {
                    "id": 5,
                    "nom": "Brainstorming nouveau projet",
                    "urgente": False,
                    "importante": True,
                    "deadline": None,
                    "temps_estime": 60,
                    "score": 0,
                    "completed": False,
                },
                {
                    "id": 6,
                    "nom": "Réservation billet d'avion",
                    "urgente": True,
                    "importante": False,
                    "deadline": (today + datetime.timedelta(days=1)).isoformat(),
                    "temps_estime": 15,
                    "score": 0,
                    "completed": False,
                },
            ]
        self.next_id = len(self.tasks) + 1
        for i in range(len(self.tasks)):
            self.tasks[i]["score"] = self._calculate_score(self.tasks[i])
        self.tasks.sort(key=lambda t: t["score"], reverse=True)
        if self.tasks:
            first_task_with_deadline = next(
                (t for t in self.tasks if t.get("deadline")), None
            )
            if first_task_with_deadline and first_task_with_deadline["deadline"]:
                try:
                    deadline_date = datetime.date.fromisoformat(
                        first_task_with_deadline["deadline"]
                    )
                    self.calendar_date = deadline_date.replace(day=1)
                except (ValueError, TypeError) as e:
                    logging.exception(f"Error setting calendar from scenario: {e}")
                    self.calendar_date = datetime.date.today()