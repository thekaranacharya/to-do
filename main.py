# All imports
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# create engine
engine = create_engine('sqlite:///todo.db?check_same_thread=False')

# describe table
Base = declarative_base()

class Tasks(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=datetime.today().date())

    def __repr__(self):
        return f'{self.id}. {self.task}'


# create table 'task' in db 'todo.db'
# [C]
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# ---------------- helper methods to be called from main -----------------------

# method to get today's tasks (1)
# [R]
def read_today(session):
    today = datetime.today()
    today_tasks = session.query(Tasks).filter(Tasks.deadline == today.date()).all()
    print(f'Today {today.day} {today.strftime("%b")}:')
    if not today_tasks:
        print('Nothing to do!')
    else:
        print()
        for index, task in enumerate(today_tasks):
            print(f'{index + 1}. {task.task}')
        print()

# method to get upcoming week's tasks (2)
# [R]
def get_upcoming_week(session):
    today = datetime.today()

    # Create next_week list to store 7 datetime objects from today onwards
    next_week = [today + timedelta(days=i) for i in range(7)]
    print()

    # for every row in the list, print the date and the task(s) for that date
    for row in next_week:
        today_tasks = session.query(Tasks).filter(Tasks.deadline == row.date()).all()
        print(f'{row.strftime("%A")} {row.strftime("%-d")} {row.strftime("%b")}:')
        if not today_tasks:
            print('Nothing to do!')
            print()
        else:
            # print task(s) for this date
            for index, task in enumerate(today_tasks):
                print(f'{index + 1}. {task.task}')
                print()

# method to read all tasks (3)
# [R]
def read_all(session):
    all = session.query(Tasks).order_by(Tasks.deadline).all()
    return all

# method to get missed tasks (4)
# [R]
def get_missed_tasks(session):
    missed = session.query(Tasks)\
        .filter(Tasks.deadline < datetime.today().date())\
        .order_by(Tasks.deadline).all()
    print()
    print('Missed tasks:')
    if not missed:  # if empty
        print('Nothing is missed!')
    else:
        for index, row in enumerate(missed):
            print('{number}. {task_name}. {date} {month_abbr}'
                  .format(number=index + 1,
                          task_name=row.task,
                          date=row.deadline.strftime("%-d"),
                          month_abbr=row.deadline.strftime("%b")
                          )
                  )
    print()

# method to add new task (5)
# [U]
def add_task(session, task_name, deadline):
    # Convert datetime string (input from user) to a datetime object todo_deadline
    todo_deadline = datetime.strptime(deadline, '%Y-%m-%d')

    # Create new Tasks object new_task
    new_task = Tasks(task=task_name, deadline=todo_deadline.date())

    # use the session variable to add the new task
    session.add(new_task)

    print('The task has been added!')
    print()

# method to delete task (6)
# [D]
def delete_task(session, task_id):
    session.query(Tasks).filter(Tasks.id == task_id).delete()
    print('The task has been deleted!')

#---- main program execution starts here------------------

while(True):
    print("1) Today's tasks")
    print("2) Week's tasks")
    print("3) All tasks")
    print("4) Missed tasks")
    print("5) Add task")
    print("6) Delete task")
    print("0) Exit")

    choice = int(input())
    if choice != 0:
        # Create session (will be created for every iteration of the loop before it's also committed at the end)
        session = Session()

        if choice == 1:
            # get today's tasks
            read_today(session)
        elif choice == 2:
            # get the week's tasks
            get_upcoming_week(session)
        elif choice == 3:
            # get all tasks
            all_tasks = read_all(session)
            if not all_tasks:
                print('Nothing to do!')
            else:
                print()
                # print every task
                for index, row in enumerate(all_tasks):
                    print('{number}. {task_name}. {date} {month_abbr}'
                          .format(number=index + 1,
                                  task_name=row.task,
                                  date=row.deadline.strftime("%-d"),
                                  month_abbr=row.deadline.strftime("%b")
                                  )
                          )
        elif choice == 4:
            # get missed tasks
            get_missed_tasks(session)
        elif choice == 5:
            # add new task
            print()
            print('Enter task')
            task_name = input()
            print('Enter deadline')
            deadline = input()
            add_task(session, task_name, deadline)
        elif choice == 6:
            # calling the read_all function [R]
            all_tasks = read_all(session)
            if not all_tasks:
                print('Nothing to delete!')
            else:
                print()
                tasks_dict = {}
                print('Choose the number of the task you want to delete:')
                for index, row in enumerate(all_tasks) :
                    # tasks_dict : key=task number , value=task.id (from the table)
                    tasks_dict[str(index + 1)] = row.id
                    # print every task
                    print('{number}. {task_name}. {date} {month_abbr}'
                          .format(number=index + 1,
                                  task_name=row.task,
                                  date=row.deadline.strftime("%-d"),
                                  month_abbr=row.deadline.strftime("%b")
                                  )
                          )
                # Input task number to delete from the user
                task_number = input()
                # Pass the corresponding value of the key=task_number to delete_tasks
                delete_task(session, tasks_dict[task_number])

        # Commit the session
        session.commit()
    else:
        print('Bye!')
        break