from itertools import chain
from basecampy3.endpoints import Comments
from datetime import datetime
from dateutil import parser
from api import APIWrapper
from api_iterator import BasecampAPIIterator
from recording_events import RecordingEvents

wrapper = APIWrapper()
wrapper.authenticate()
api = wrapper.api
recordingevents = RecordingEvents(api)

me = api.people.get()
my_id = me.id
print(f'My id {me.id}')

today = datetime.today()

for project in api.projects.list():
    print(f'Project "{project.name}"')
    todoset = api.todosets.get(project)
    for todolist in BasecampAPIIterator(api.todolists.list(project, todoset)):
        print(f'  List: {todolist.name}')
        completed_todos = BasecampAPIIterator(api.todos.list(todolist, project, completed=True))
        incomplete_todos = BasecampAPIIterator(api.todos.list(todolist, project, completed=False))
        all_todos = chain(completed_todos, incomplete_todos)
        for todo in all_todos:
            events = recordingevents.list(todo, project)
            for event in BasecampAPIIterator(events):
                action = event.action
                creator = event.creator

                creator_id = creator["id"]
                if creator_id != my_id:
                    continue

                created_at = parser.parse(event.created_at)
                if created_at.date() != today.date():
                    continue

                if action == "completed":
                    print(f'YOU completed TODAY todo: {todo.id} - {todo.title}')
                else:
                    print(f'YOU "{action}" TODAY todo: {todo.id} - {todo.title}')
                # print(f'event action: {event.action}, creator id: {creator_id}, my identity {my_id}')

            comments = Comments(api, todo).list()
            for comment in BasecampAPIIterator(comments):
                creator = comment.creator
                creator_id = creator["id"]
                if creator_id != my_id:
                    continue
                # print(f'comment: {comment}')
                created_at = parser.parse(comment.created_at)
                updated_at = parser.parse(comment.updated_at)

                if created_at.date() == today.date() or updated_at.date() == today.date():
                    print(f'YOU COMMENTED on todo: {todo.id} - {todo.title}')
