# Makefile to create and populate a SQLite database from schema and data files

# Define variables
SCHEMA_FILE = mp1-schema.sql
DATA_FILE = initial_data.sql
DATABASE_FILE = database.db

# Define targets and their dependencies and commands
all: $(DATABASE_FILE)

$(DATABASE_FILE): $(SCHEMA_FILE) $(DATA_FILE)
	sqlite3 $(DATABASE_FILE) < $(SCHEMA_FILE)
	sqlite3 $(DATABASE_FILE) < $(DATA_FILE)

# Define clean target to remove the generated database file
clean:
	rm -f $(DATABASE_FILE)