# Employee-Project-Assignment-Django-Project

In this project, the task is:
My consultancy firm have various projects from different companies and they have to be assigned to the Employees of my firm.
Each project has verious modules which can be assigned to employees by Team leader.

There are 3 type of designations: Admin (not a superuser created in django), Team Leader and Employee (low-level).

Admin can register new employee in my firm and give out uniqueemail id and password to the Team Leaders and EMployees so that 
they can sign in and see their respective projects. Admin can CRUD companies, projects, employee and modules.

Team leader can assignee modules to employees and see the projects details and update/delete modules.

Employee can only see modules and projects details of only those of which he is part of.

1. Create a superuser right after migrating to check the working of the apps.
2. add 
    AUTHENTICATION_BACKENDS = ['jira.backends.EmailBackend']
    DATE_INPUT_FORMATS = ['%d-%m-%Y']
    DATETIME_INPUT_FORMATS = ['%d-%m-%Y %H:%M']
    AUTH_USER_MODEL = 'jira.MyUser' 
    LOGIN_URL = 'login'
    LOGIN_REDIRECT_URL = 'company_list_view'
    
I have not setup proper html yet with links to  right now navigation thorugh url is advised
you cna change     LOGIN_REDIRECT_URL = 'company_list_view' to whatever suits you as i am working on permissions on this project 
and i will complete it soon and update it.


Delete all migrations and pyc files before running the first migration

Create a superuser and use 'register' view to create users for the app.
