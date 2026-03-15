import sqlite3
import yaml
from datetime import datetime
from ascii_colors import ASCIIColors
class ModelsDB:
    def __init__(self, db_name='models.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS models (
                                id INTEGER PRIMARY KEY,
                                category TEXT,
                                icon TEXT,
                                datasets TEXT,
                                last_commit_time TEXT,
                                license TEXT,
                                model_creator TEXT,
                                model_creator_link TEXT,
                                name TEXT UNIQUE,
                                provider TEXT,
                                ctx_size INTEGER,
                                rank REAL,
                                type TEXT
                            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS variants (
                                id INTEGER PRIMARY KEY,
                                model_id INTEGER,
                                name TEXT,
                                size INTEGER,
                                FOREIGN KEY(model_id) REFERENCES models(id)
                            )''')
        self.conn.commit()


    def add_entry(self, entry):
        # Check if a model with the same name already exists
        self.cursor.execute("SELECT id FROM models WHERE name=?", (entry.get('name'),))
        model_id = self.cursor.fetchone()

        if model_id is None:
            datasets = entry.get('datasets', [])
            license = entry.get('license')
            # If the model does not exist, insert a new one
            data = (entry.get('category'), entry.get('icon'), ','.join(datasets) if type(datasets)==list else datasets, entry.get('last_commit_time'),
                    ','.join(license) if type(license)==list else license,                     
                    entry.get('model_creator'), entry.get('model_creator_link'), entry.get('name'),
                    entry.get('provider'), entry.get('ctx_size', 4096), entry.get('rank'), entry.get('type'))
            self.cursor.execute('''INSERT INTO models VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
            model_id = self.cursor.lastrowid
            # Insert the variants
            for variant in entry.get('variants', []):
                variant_name = variant.get('name')
                variant_size = variant.get('size')
                variant_data = (model_id, variant_name, variant_size)
                self.cursor.execute('''INSERT INTO variants VALUES (NULL, ?, ?, ?)''', variant_data)
        else:
            ASCIIColors.warning(f"A duplicate of the model {entry.get('name')} has been detected")


        self.conn.commit()


    def import_from_yaml(self, file_path):
        with open(file_path) as file:
            data = yaml.safe_load(file)

        for entry in data:
            self.add_entry(entry)


    def query(self, n=None, model_types=None, variant_name=None, keyword=None):
        query = "SELECT models.*, variants.name as variant_name, variants.size as variant_size FROM models LEFT JOIN variants ON models.id = variants.model_id WHERE 1=1"
        params = []
        if model_types:
            query += " AND models.type IN (" + ", ".join("?" for _ in model_types) + ")"
            params.extend(model_types)
        if variant_name:
            query += " AND variants.name=?"
            params.append(variant_name)
        if keyword:
            query += " AND models.name LIKE ?"
            params.append('%' + keyword + '%')
        if n:
            query += " ORDER BY models.last_commit_time DESC LIMIT ?"
            params.append(n)
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()

        # Group the results by model id and convert the row to a dictionary
        model_results = {}
        for row in results:
            model_id = row[0]
            if model_id not in model_results:
                model_results[model_id] = {
                    "id": row[0],
                    "category": row[1],
                    "icon": row[2],
                    "datasets": row[3].split(',') if row[3] is not None else None,
                    "last_commit_time": row[4],
                    "license": row[5],
                    "model_creator": row[6],
                    "model_creator_link": row[7],
                    "name": row[8],
                    "provider": row[9],
                    "ctx_size": row[10],
                    "rank": row[11],
                    "type": row[12],
                    "variants": []
                }
            model_results[model_id]["variants"].append({"name": row[13], "size": row[14]})

        return list(model_results.values())




    def remove_entry(self, model_name):
        self.cursor.execute("DELETE FROM variants WHERE model_id IN (SELECT id FROM models WHERE name=?)", (model_name,))
        self.cursor.execute("DELETE FROM models WHERE name=?", (model_name,))
        self.conn.commit()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Build a database from a YAML file.')
    parser.add_argument('--yaml_path', type=str, help='Path to the YAML file')
    parser.add_argument('--db_path', type=str, help='Path to the database file')

    args = parser.parse_args()

    # Create a database instance
    db = ModelsDB(db_name=args.db_path)

    # Import entries from a YAML file
    db.import_from_yaml(args.yaml_path)

    # Query the database
    print(db.query(n=3, model_types=['gguf']))

if __name__=="__main__":
    main()
