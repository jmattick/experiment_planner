# Django Experiment Planner

Web app to optimally schedule long protocols 

### In Progress

Initialize project:
````
django-admin startproject experiment_planner
````

Create protocols app:
````
python manage.py startapp protocols
````

Create views:
- protocol landing page
- detailed protocol page

Create Models:
- Protocol
- Step

Migrate database:
```
python manage.py makemigrations protocols
python manage.py migrate
```

Setup admin site:
- Create superuser
```
python manage.py createsuperuser
```

Add custom ProtocolLinkedList datastructure:
- LinkedList of Step subclasses:
    - Step-dependent Step
    - Repeating Step-dependent Step
    - Time-dependent Step
- build_DAG function to build directed acyclic graph of all possible experiments




