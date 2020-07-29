from Project import app
# From __init__.py of Project we import app.
# __init__.py contains all the initialisations like app, database and mail service along with login manager

if __name__ == "__main__":
    app.run(debug=True)