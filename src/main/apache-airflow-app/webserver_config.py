from flask_appbuilder.const import AUTH_DB

# Use Airflow's default database-backed authentication
AUTH_TYPE = AUTH_DB

# Roles
AUTH_ROLE_ADMIN = "Admin"
AUTH_ROLE_PUBLIC = "Viewer"
