from datetime import datetime
from pprint import pprint
from rich import print, pretty
import re
import hashlib
from rich.console import Console
from libs.log import log
from office.views import (
    UserViewSet,
    ProjectViewSet,
    UserProjectViewSet,
    TaskViewSet,
    CommentViewSet
)
from rich.console import Console
from rich.table import Table
from office.models import ProjectModel, TaskModel, Date, CommentModel


def show_users(user_id: str):
    view = UserViewSet()
    pprint(view.list())


def email_validation(email: str, view: UserViewSet) -> bool:
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(pattern, email):
        if email_exist(email, view):
            console.print("[bold red]there is a user with this Email address![/bold red]")
            return False
        else:
            return True
    console.print("[bold red]Invalid Email address![/bold red]")
    return False


def username_exist(username: str, view: UserViewSet) -> bool:
    all_users = list(map(lambda item: item["username"], view.list()["objects"]))
    for temp_username in all_users:
        if temp_username == username:
            return True
    return False


def email_exist(email: str, view: UserViewSet) -> bool:
    all_users = list(map(lambda item: item["email"], view.list()["objects"]))
    for temp_username in all_users:
        if temp_username == email:
            return True
    return False


def password_validation(username: str, password: str, view: UserViewSet) -> bool:
    correct_password = list(filter(
        lambda item: item["username"] == username, view.list()["objects"]
    ))[0].get("password")
    encrypted_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if correct_password == encrypted_password:
        return True
    return False


def check_activation(username: str, view: UserViewSet) -> bool:
    return list(filter(lambda item: item["username"] == username, view.list()["objects"]))[0].get("is_active")


def sign_up(user_id: str):
    view = UserViewSet()
    user_info = dict()
    username = console.input("[bold cyan]Enter your username : [/bold cyan]")
    if username == "return":
        return
    while username_exist(username, view):
        username = console.input("[bold red]There is a user with that username."
                                 "[/bold red]\n[bold yellow]please enter another username : [/bold yellow]")
        if username == "return":
            return
    user_info["username"] = username
    email = console.input("[bold cyan]Enter your Email address :[/bold cyan]")
    if email == "return":
        return
    while not email_validation(email, view):
        email = console.input("[bold yellow]Please try again : [/bold yellow]")
        if email == "return":
            return
    user_info["email"] = email
    user_info["password"] = console.input("[bold cyan]Enter your password : [/bold cyan]")
    # print(user_info)
    view.create(user_info)
    # show_menu("main",)


def log_in(user_id: str):
    view = UserViewSet()
    username = console.input("[bold cyan]Enter your username : [/bold cyan]")
    if username == "return":
        return
    while not username_exist(username, view):
        username = console.input("[bold red]There is a no user with that username.[/bold red]\n"
                                 "[bold yellow]Please try again : [/bold yellow]")
        if username == "return":
            return
    password = console.input("[bold cyan]Enter your password :[/bold cyan]")
    if password == "return":
        return
    while not password_validation(username, password, view):
        password = console.input("[bold red]Invalid password ![/bold red]\n"
                                 "[bold yellow]Please try again : [/bold yellow]")
        if password == "return":
            return
    if not check_activation(username, view):
        print("[bold red]Your account is not active.[/bold red]")
    else:
        print(f"[bold green]{username} logged in successfully.[/bold green]")
        # print(log.info("ailreza"))
        show_menu("logged", list(filter(lambda item: item["username"] == username, view.list()["objects"]))[0].get("id"))


def users_activity(user_id: str):
    view = UserViewSet()
    users = list(map(lambda item: item["username"], view.list()["objects"]))
    user_activity = dict()
    for user in users:
        user_activity[user] = list(filter(lambda item: item["username"] == user, view.list()["objects"]))[0].get("is_active")
    print(user_activity)
    user_input = console.input("Enter username to change activity: ")


def project_environment(project_id: str):
    pview = ProjectViewSet()
    upview = UserProjectViewSet()
    view = UserViewSet()
    console.print("Title : ", list(filter(lambda item: item["id"] == project_id, pview.list()["objects"]))[0].get("title"))
    leader_id = list(filter(lambda item: item["id"] == project_id, pview.list()["objects"]))[0].get("leader_id")
    console.print("Leader : ", list(filter(lambda item: item["id"] == leader_id, view.list()["objects"]))[0].get("username"))
    users = list(filter(lambda item: item["project_id"] == project_id, upview.list()["objects"]))
    console.print("Users : ")
    for user in users:
        if user.get("user_id") != leader_id:
            console.print(list(filter(lambda item: item["id"] == user.get("user_id"), view.list()["objects"]))[0].get("username"))


def manage_task():
    pass


def delete_user(user_id: str, project_id: str):
    upview = UserProjectViewSet()
    view = UserViewSet()
    pview = ProjectViewSet()
    while True:
        users = upview.filter(project_id=project_id)
        table = Table(title="Users")
        table.add_column("Users", justify="full", style="cyan", no_wrap=True)
        for user in users:
            # console.print(view.filter(id=user.get("user_id"))[0].get("username"))
            table.add_row(view.filter(id=user.get("user_id"))[0].get("username"))
        console.print(table)
        member = console.input("Enter username to delete :")
        if member == "return":
            return
        is_ok = False
        for user in users:
            target_user_id = user.get("user_id")
            if member == view.filter(id=target_user_id)[0].get("username"):
                is_ok = True
                if target_user_id != pview.filter(id=project_id)[0].get("leader_id"):
                    upview.delete(user_id=target_user_id, project_id=project_id)
                else:
                    console.print("leader can`t be removed, you can delete project from menu.")
        if not is_ok:
            console.print("There is no user with this username in project.")


def delete_project(user_id: str, project_id: str):
    view = ProjectViewSet()
    view.delete(id=project_id)


def show_history():
    pass


def show_task(user_id: str, project_id: str, task_id: str):
    uview = UserViewSet()
    tview = TaskViewSet()
    task = tview.filter(id=task_id)[0]
    users_in_task = TaskModel.from_data(TaskModel.Meta.adapter.get(task_id)).get_members()
    table = Table()
    table.add_column("Field", justify="full", style="magenta")
    table.add_column("Value", justify="full", style="magenta")
    table.add_row("title", task.get("title"))
    table.add_row("Description", task.get("description"))
    table.add_row("Started at", task.get("started_at"))
    table.add_row("Finishes at", task.get("ended_at"))
    table.add_row("Assignees", "")
    for user in users_in_task:
        table.add_row( "", uview.filter(id=user)[0].get("username"))
    table.add_row("priority", TaskModel.Priority(task.get("priority")).name)
    table.add_row("status", TaskModel.Status(task.get("status")).name)
    console.print(table)


def update_task(user_id: str, project_id: str, task_id: str):
    user_view = UserViewSet()
    tview = TaskViewSet()
    user_project_view = UserProjectViewSet()
    task = tview.filter(id=task_id)[0]
    changed_task: TaskModel = TaskModel.from_data(TaskModel.Meta.adapter.get(task_id))
    users_in_task = TaskModel.from_data(TaskModel.Meta.adapter.get(task_id)).get_members()
    users_in_task_id = changed_task.get_members()
    while True:
        table = Table()
        table.add_column("Number", justify="full", style="magenta")
        table.add_column("Field", justify="full", style="magenta")
        table.add_column("Base", justify="full", style="magenta")
        table.add_column("Changed", justify="full", style="magenta")
        table.add_row("1", "title", task.get("title"), changed_task.title)
        table.add_row("2", "Description", task.get("description"), changed_task.description)
        table.add_row("3", "Started at", task.get("started_at"), str(changed_task.started_at))
        table.add_row("4", "Finishes at", task.get("ended_at"), str(changed_task.ended_at))
        table.add_row("5", "Assignees", "")
        for i in range(max(len(users_in_task), len(users_in_task_id))):
            if len(users_in_task) >= i+1 > len(users_in_task_id):
                table.add_row("", "", user_view.filter(id=users_in_task[i])[0].get("username"), "")
            elif len(users_in_task_id) >= i+1 > len(users_in_task):
                table.add_row("", "", "", user_view.filter(id=users_in_task_id[i])[0].get("username"))
            else:
                table.add_row("", "", user_view.filter(id=users_in_task[i])[0].get("username"),
                              user_view.filter(id=users_in_task_id[i])[0].get("username"))
        table.add_row("6", "priority", TaskModel.Priority(task.get("priority")).name,
                      TaskModel.Priority(changed_task.priority).name)
        table.add_row("7", "status", TaskModel.Status(task.get("status")).name,
                      TaskModel.Status(changed_task.status).name)
        console.print(table)

        member_number = console.input("Enter Field number to change : ")
        if member_number == "return":
            return
        if member_number == "save":

            break
        if int(member_number) == 1:
            changed_task.title = console.input("Enter new title : ")
        if int(member_number) == 2:
            changed_task.description = console.input("Enter new description : ")
        if int(member_number) == 3:
            while True:
                _input = console.input("Enter start date and time: ")
                if validate_date(_input):
                    input_time = Date.from_string(_input)
                    if input_time.started_at.time.timestamp() > changed_task.ended_at.time.timestamp():
                        console.print("Invalid time")
                    else:
                        changed_task.started_at = input_time
                        break
                else:
                    console.print("Invalid format")
        if int(member_number) == 4:
            _input = console.input("Enter end date and time: ")
            if validate_date(_input):
                input_time = Date.from_string(_input)
                if changed_task.started_at.time.timestamp() > input_time.time.timestamp():
                    console.print("Invalid time")
                else:
                    changed_task.ended_at = input_time
                    break
            else:
                console.print("Invalid format")
        if int(member_number) == 6:
            for i in range(1, 5):
                console.print(f"{i} - {TaskModel.Priority(i).name}")
            while True:
                _input = console.input("Enter priority number: ")
                if 1 <= int(_input) <= 4:
                    changed_task.priority = int(_input)
                    break
                else:
                    console.print("Invalid input")

        if int(member_number) == 7:
            for i in range(1, 6):
                console.print(f"{i} - {TaskModel.Status(i).name}")
            while True:
                _input = console.input("Enter status number: ")
                if 1 <= int(_input) <= 5:
                    changed_task.status = int(_input)
                    break
                else:
                    console.print("Invalid input")

        if int(member_number) == 0:
            return

        if int(member_number) == 5:
            users_in_project = user_project_view.filter(project_id=project_id)
            while True:
                table = Table(title="Users")
                table.add_column("Users", justify="full", style="cyan", no_wrap=True)
                table.add_column("Users who are not in task", justify="full", style="red", no_wrap=True)
                table.add_column("Users who are in task", justify="full", style="green", no_wrap=True)
                for user in users_in_project:
                    is_in_task = False
                    for id in users_in_task_id:
                        if id == user.get("user_id"):
                            is_in_task = True
                    if not is_in_task:
                        table.add_row(user_view.filter(id=user.get("user_id"))[0].get("username"), user_view.filter(id=user.get("user_id"))[0].get("username"), "")
                    else:
                        table.add_row(user_view.filter(id=user.get("user_id"))[0].get("username"), "", user_view.filter(id=user.get("user_id"))[0].get("username"))
                console.print(table)

                member_username = console.input(f"Enter the username of member: ")
                if member_username == "return":
                    break
                if members := user_view.filter(username=member_username):
                    member_id = members[0].get("id")
                    for user in users_in_project:
                        if user.get("user_id") == member_id:
                            is_in_task = False
                            for id in users_in_task_id:
                                if member_id == id:
                                    is_in_task = True
                            if not is_in_task:
                                changed_task.add_member(member_id=member_id)
                                users_in_task_id.append(member_id)
                            else:
                                changed_task.remove_member(member_id=member_id)
                                users_in_task_id.remove(member_id)
                else:
                    console.print("There is no user with this username")





def show_task_options(user_id: str, project_id: str, task_id: str):
    pview = ProjectViewSet()
    tview = TaskViewSet()
    show_task(user_id, project_id, task_id)
    options = {
        "Update task": update_task,
        "Add comment": add_comment,
        "Show comments": show_comments,
        "Show history": show_history,
    }
    users_in_task = TaskModel.from_data(TaskModel.Meta.adapter.get(task_id)).get_members()
    options_list = list(options.keys())
    if not user_id in users_in_task:
        options_list.pop(0)

    table = Table(title="Options")
    table.add_column("Number", justify="full", style="cyan", no_wrap=True)
    table.add_column("Option", justify="full", style="magenta")
    for index in range(len(options_list)):
        table.add_row(str(index + 1), options_list[index])
    console.print(table)
    user_input = int(input("Enter your Option: ")) - 1
    if user_input == -1:
        return
    func = options[options_list[user_input]]
    func(user_id, project_id, task_id)
    show_task_options(user_id, project_id, task_id)


def show_project_options(user_id: str, project_id: str):
    pview = ProjectViewSet()
    options = {
        "Show tasks": show_tasks,
        "Add task": add_task,
        "Delete users": delete_user,
        "Delete project": delete_project,
    }
    options_list = list(options.keys())
    if not user_id == pview.filter(id=project_id)[0].get("leader_id"):
        options_list.pop(1)
        options_list.pop(1)
        options_list.pop(1)

    table = Table(title="Options")
    table.add_column("Number", justify="full", style="cyan", no_wrap=True)
    table.add_column("Option", justify="full", style="magenta")
    for index in range(len(options_list)):
        table.add_row(str(index + 1), options_list[index])
        # print(f"{index + 1}. {options_list[index]}")
    console.print(table)
    user_input = int(input("Enter your Option: ")) - 1
    if user_input == -1:
        return
    func = options[options_list[user_input]]
    func(user_id, project_id)
    if user_input == 3:
        return
    show_project_options(user_id, project_id)


def show_projects(user_id: str):
    view = UserProjectViewSet()
    pview = ProjectViewSet()
    user_projects_id = list()
    console.print("You are leader of these projects :")
    for project in list(filter(lambda item: item["leader_id"] == user_id, pview.list()["objects"])):
        user_projects_id.append(project.get("id"))
        console.print(f"{len(user_projects_id)}. {project.get("title")}")
    print("\nYou are normal user in these projects :")
    projects = list(filter(lambda item: item["user_id"] == user_id, view.list()["objects"]))
    for project in projects:
        is_ok = True
        for lproject in list(filter(lambda item: item["leader_id"] == user_id, pview.list()["objects"])):
            if project.get("project_id") == lproject.get("id"):
                is_ok = False
        if is_ok:
            user_projects_id.append(project.get("project_id"))
            console.print(f"{len(user_projects_id)}. {list(filter(lambda item: item["id"] == project.get("project_id"), pview.list()["objects"]))[0].get("title")}")
    user_number = int(console.input("Enter number of project to open:"))
    if user_number == 0:
        return
    project_environment(user_projects_id[user_number-1])
    show_project_options(user_id, user_projects_id[user_number-1])


def can_add(project_id: str, user_id: str, count: int) -> bool:
    view = UserViewSet()
    pview = UserProjectViewSet()
    if username_exist(list(filter(lambda item: item["id"] == user_id, view.list()["objects"]))[0].get("username"), view):
        users_in_project = list(filter(lambda item: item["project_id"] == project_id, pview.list()["objects"]))
        for i in range(count):
            if users_in_project[i].get("user_id") == user_id:
                console.print()
                return False
        return True
    return False


def title_exist(title: str,) -> bool:
    pview = ProjectViewSet()
    if len(list(filter(lambda item: item["title"] == title, pview.list()["objects"]))) == 0:
        return True
    return False


def add_project(user_id: str):
    view = UserViewSet()
    title = console.input("[bold cyan]Enter your title: [/bold cyan]")
    if title == "return":
        return
    while not title_exist(title):
        if title == "return":
            return
        title = console.input("[bold red]There is a project with this title.[/bold red]\n"
                              "[bold yellow]Please try again : [/bold yellow]")
    project = ProjectModel(title=title, leader_id=user_id)
    project.save()
    project.add_member(member_id=user_id)
    members_count = int(console.input("Enter your count of members: "))
    index = 1
    while index < members_count + 1:
        member_username = console.input(f"{index} - Enter the username of member: ")
        if member_username == "return":
            return
        if not username_exist(member_username, view):
            console.print("There is no user with this username.")
            continue
        member_id = list(filter(lambda item: item["username"] == member_username, view.list()["objects"]))[0].get("id")
        if can_add(project.id, list(filter(lambda item: item["username"] == member_username, view.list()["objects"]))[0].get("id"), index):
            project.add_member(member_id=member_id)
            index = index + 1
        else:
            console.print("You cant add this user.")


def validate_date(date: str) -> bool:
    pattern = r'\d{4}-\d?\d-\d?\d (?:2[0-3]|[01]?[0-9]):[0-5]?[0-9]:[0-5]?[0-9]'
    if re.fullmatch(pattern, date):
        now = Date(time=datetime.now())
        input_time = Date.from_string(date)
        if now.time.timestamp() > input_time.time.timestamp():
            return False
        return True
    return False


def add_task(user_id: str, project_id: str):
    user_view = UserViewSet()
    project_view = ProjectViewSet()
    user_project_view = UserProjectViewSet()
    title = console.input("Enter task title: ")
    description = console.input("Enter your description: ")
    started_at: Date
    while True:
        if _input := console.input("Enter start date and time: "):
            if validate_date(_input):
                started_at = Date.from_string(_input)
                break
            else:
                console.print("Invalid format")
        else:
            started_at = Date(time=datetime.now())
            break

    ended_at: Date
    while True:
        if _input := console.input("Enter end date and time: "):
            if validate_date(_input):
                input_time = Date.from_string(_input)
                if started_at.time.timestamp() > input_time.time.timestamp():
                    console.print("Invalid time")
                else:
                    ended_at = Date.from_string(_input)
                    break
            else:
                console.print("Invalid format")
        else:
            now = started_at.time
            ended_at = Date(time=now.replace(day=now.day+1))
            break

    for i in range(1, 5):
        console.print(f"{i} - {TaskModel.Priority(i).name}")
    priority: int
    while True:
        if _input := console.input("Enter priority number: "):
            if 1 <= int(_input) <= 4:
                priority = int(_input)
                break
            else:
                console.print("Invalid input")
        else:
            priority = 1
            break

    for i in range(1, 6):
        console.print(f"{i} - {TaskModel.Status(i).name}")
    status: int
    while True:
        if _input := console.input("Enter status number: "):
            if 1 <= int(_input) <= 5:
                status = int(_input)
                break
            else:
                console.print("Invalid input")
        else:
            status = 1
            break

    task = TaskModel(title=title, project_id=project_id, description=description,
                     started_at=started_at, ended_at=ended_at,
                     priority=priority, status=status)
    task.save()

    users_in_task_id = list()
    users_in_project = user_project_view.filter(project_id=project_id)
    while True:

        table = Table(title="Users")
        table.add_column("Users", justify="full", style="cyan", no_wrap=True)
        table.add_column("Users who are not in task", justify="full", style="red", no_wrap=True)
        table.add_column("Users who are in task", justify="full", style="green", no_wrap=True)
        for user in users_in_project:
            is_in_task = False
            for id in users_in_task_id:
                if id == user.get("user_id"):
                    is_in_task = True
            if not is_in_task:
                table.add_row(user_view.filter(id=user.get("user_id"))[0].get("username"), user_view.filter(id=user.get("user_id"))[0].get("username"), "")
            else:
                table.add_row(user_view.filter(id=user.get("user_id"))[0].get("username"), "", user_view.filter(id=user.get("user_id"))[0].get("username"))
        console.print(table)

        member_username = console.input(f"Enter the username of member: ")
        if member_username == "return":
            return
        if members := user_view.filter(username=member_username):
            member_id = members[0].get("id")
            for user in users_in_project:
                if user.get("user_id") == member_id:
                    is_in_task = False
                    for id in users_in_task_id:
                        if member_id == id:
                            is_in_task = True
                    if not is_in_task:
                        task.add_member(member_id=member_id)
                        users_in_task_id.append(member_id)
                    else:
                        task.remove_member(member_id=member_id)
                        users_in_task_id.remove(member_id)
        else:
            console.print("There is no user with this username")


def show_tasks(user_id: str, project_id: str):
    view = TaskViewSet()
    tasks = view.filter(project_id=project_id)
    backlog_tasks = list()
    todo_tasks = list()
    doing_tasks = list()
    done_tasks = list()
    archived_tasks = list()
    for task in tasks:
        if task.get("status") == 1:
            backlog_tasks.append(task.get("title"))
        if task.get("status") == 2:
            todo_tasks.append(task.get("title"))
        if task.get("status") == 3:
            doing_tasks.append(task.get("title"))
        if task.get("status") == 4:
            done_tasks.append(task.get("title"))
        if task.get("status") == 5:
            archived_tasks.append(task.get("title"))
    max_row = max(len(backlog_tasks),len(todo_tasks),len(doing_tasks),len(done_tasks),len(archived_tasks))

    table = Table(title="Tasks")
    table.add_column("BACKLOG", justify="full", style="cyan", no_wrap=True)
    table.add_column("TODO", justify="full", style="red", no_wrap=True)
    table.add_column("DOING", justify="full", style="red", no_wrap=True)
    table.add_column("DONE", justify="full", style="red", no_wrap=True)
    table.add_column("ARCHIVED", justify="full", style="red", no_wrap=True)

    for i in range(max_row):
        temp_backlog_tasks: str
        temp_todo_tasks: str
        temp_doing_tasks: str
        temp_done_tasks: str
        temp_archived_tasks: str
        if i >= len(backlog_tasks):
            temp_backlog_tasks = ""
        else:
            temp_backlog_tasks = backlog_tasks[i]

        if i >= len(todo_tasks):
            temp_todo_tasks = ""
        else:
            temp_todo_tasks = todo_tasks[i]

        if i >= len(doing_tasks):
            temp_doing_tasks = ""
        else:
            temp_doing_tasks = doing_tasks[i]

        if i >= len(done_tasks):
            temp_done_tasks = ""
        else:
            temp_done_tasks = done_tasks[i]

        if i >= len(archived_tasks):
            temp_archived_tasks = ""
        else:
            temp_archived_tasks = archived_tasks[i]
        table.add_row(temp_backlog_tasks, temp_todo_tasks, temp_doing_tasks, temp_done_tasks, temp_archived_tasks)

    while True:
        console.print(table)
        member_input = console.input("Enter Task title :")
        if member_input == "return":
            return
        for task in tasks:
            if task.get("title") == member_input:
                show_task_options(user_id, project_id, task.get("id"))


def add_comment(user_id: str, project_id: str, task_id: str):
    text = console.input("Enter your text: ")
    comment = CommentModel(task_id=task_id, text=text, user_id=user_id)
    comment.save()


def show_comments(user_id: str, project_id: str, task_id: str):
    view = CommentViewSet()
    print(view.list())


def show_menu(_type: str, user_id: str):
    view = UserViewSet()
    options = {
        "Show users": show_users,
        "Sign Up": sign_up,
        "Log in": log_in,
        "Change users activity": users_activity,
        "Show projects": show_projects,
        "Add project": add_project
    }
    options_list = list(options.keys())
    if _type == "main":
        options_list.pop(0)
        options_list.pop(2)
        options_list.pop(2)
        options_list.pop(2)
    elif not list(filter(lambda item: item["id"] == user_id, view.list()["objects"]))[0].get("is_admin"):
        for i in range(4):
            options_list.pop(0)
    else:
        for i in range(3):
            options_list.pop(0)

    table = Table(title="Options")
    table.add_column("Number", justify="full", style="cyan", no_wrap=True)
    table.add_column("Option", justify="full", style="magenta")

    for index in range(len(options_list)):
        table.add_row(str(index + 1), options_list[index])
    console.print(table)
    user_input = int(input("Enter your Option: ")) - 1
    if user_input == -1:
        return
    func = options[options_list[user_input]]
    func(user_id)
    show_menu(_type, user_id)


def main():
    show_menu("main", 0)


if __name__ == "__main__":
    pretty.install()
    console = Console()
    main()
