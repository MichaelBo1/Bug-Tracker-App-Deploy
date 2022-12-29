# Bug-Tracker-App
A simple bug tracker application (WIP) built as a Django Web app. In its basic functionality it has 4 different kinds of user roles: 
- Administrator (full access and ability to change user's roles)
- Project Manager (manage users related to a certain project
- Developer (can be assigned to work on tickets)
- Submitter (able to submit new tickets to the system)
Any ticket created is linked to a project to highlight bugs/potential changes etc.
## Access
The application is [hosted here](https://www.mb-bt.com). You are able to either login with a demo account, but cannot make any changes, or setup an account with a verified email (you will be a submitter by default).

The application could be run locally, but would require configuration of environmental variables, including for a Postgresql server and AWS bucket, which can be found in `settings.py`


## What I've Learned
- Implemented the fundamental concepts of relational databases, user authentication, and managing different user roles in an application.
- Creating permissions to control view access and user functionality.
- Writing unit tests to cover all aspects of my code.
- Configuring AWS to host media files and a Linux server for the application using Nginx and Gunicorn.
## Built With

* [Django](https://www.djangoproject.com/) - The web framework used

## License

This project is licensed under the GNU GPL License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
This project was inspired by the following:
- [CoderFoundry](https://www.youtube.com/watch?v=vG824vBdYY8&t=271s)
