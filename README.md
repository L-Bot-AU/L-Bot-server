# L-Bot-server

when running the server:
- run (in any order):
  - "run_database_tasks.py"
  - run "run_website_client_interface.py"
  - run "run_website.py"
- if someone made a change to the database structure and/or you're getting an error about SQLAlchemy not being able to insert something, in constants.py, set DO_RESTARTDB to True, rerun everything and then set it back to False