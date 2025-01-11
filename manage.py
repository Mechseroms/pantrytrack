import sys, os, shutil
import main
import config as cfg

""" 
Manage.py is where the databases and configuration is set up. Its a CLI for quick serving the databases necessary for
MyPantry App.
"""

def rename_unique_sql(site_name):
    files = os.walk(f"sites/{site_name}/sql/unique")

    sql_files = []
    for file in files:
        sql_files = file[2]
        
    for file_name in sql_files:
        words = None
        with open(f"sites/{site_name}/sql/unique/{file_name}", "r") as file:
            words = file.read()
            words = words.replace("%sitename%", site_name)
        
        with open(f"sites/{site_name}/sql/unique/{file_name}", "w") as file:
            file.write(words)

def rename_drop_sql(site_name):
    files = os.walk(f"sites/{site_name}/sql/drop")

    sql_files = []
    for file in files:
        sql_files = file[2]
        
    for file_name in sql_files:
        words = None
        with open(f"sites/{site_name}/sql/drop/{file_name}", "r") as file:
            words = file.read()
            words = words.replace("%sitename%", site_name)
        
        with open(f"sites/{site_name}/sql/drop/{file_name}", "w") as file:
            file.write(words)

def rename_create_sql(site_name):
    files = os.walk(f"sites/{site_name}/sql/create")

    sql_files = []
    for file in files:
        sql_files = file[2]
        
    for file_name in sql_files:
        words = None
        with open(f"sites/{site_name}/sql/create/{file_name}", "r") as file:
            words = file.read()
            words = words.replace("%sitename%", site_name)
        
        with open(f"sites/{site_name}/sql/create/{file_name}", "w") as file:
            file.write(words)

def create(site_name, owner_name, default_zone_name, default_location_name, email=""):

    if not os.path.exists(f"sites/{site_name}"):
        print(f"Creating {site_name} site...")
        os.mkdir(f"sites/{site_name}")
        
        print(f"Creating sql tables files...")
        shutil.copytree(f"sites/default/sql", f"sites/{site_name}/sql")
        rename_create_sql(site_name)
        rename_drop_sql(site_name)
        rename_unique_sql(site_name)

        with open(f"sites/{site_name}/site.ini", "w+") as config:
            config.write(f"[site]\n")
            config.write(f"site_name={site_name}\n")
            config.write(f"site_owner={owner_name}\n")
            config.write(f"email={email}\n")
            config.write(f"\n")

            config.write(f"[defaults]\n")
            config.write(f"default_zone={default_zone_name}\n")
            config.write(f"default_primary_location={default_location_name}\n")
            config.write(f"default_auto_issue_location={default_location_name}\n")

        cfg.write_new_site(site_name)

        print(f"Site {site_name} config created!")
        print(f"Site {site_name} created!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        func_name = sys.argv[1]
        argument = sys.argv[2]

        if func_name == "create" and argument == "site":
            create()

        if func_name == "propagate" and argument == "site":
            main.create_site(sys.argv[3])
        
        if func_name == "delete" and argument == "site":
            print(func_name, argument)
            main.delete_site(sys.argv[3])
            shutil.rmtree(f"sites/{sys.argv[3]}")
            cfg.delete_site(sys.argv[3])


        if func_name == "item":
            if argument == "add":
                barcode = input("barcode: ")
                name = input("name: ")
                qty = float(input("qty: "))
                main.add_food_item(sys.argv[3], barcode, name, qty, payload=main.payload_food_item)

            if argument == "update_primary":
                barcode = input("barcode: ")
                location = input(f"New Zone/Location (default@all): ")
                main.update_item_primary(sys.argv[3], barcode, location)

            if argument == "transact":
                barcode = input("barcode: ")
                qty = float(input("qty: "))
                location = str(input("TO: ")).strip()

                if location == "":
                    location = None

                main.add_transaction(sys.argv[3], barcode, qty, 1, description="manual", location=location)
            
            if argument == "transfer":
                barcode = input("barcode: ")
                qty = float(input("qty: "))
                from_location = str(input("From: ")).strip()
                to_location = str(input("To: ")).strip()


        if func_name == "location":
            if argument == "add":
                location_name = str(input(f"New Location Name: ")).replace(" ", "_")
                zone_id = int(input(f"Zone ID: "))
                main.add_location(sys.argv[3], location_name, zone_id)

        if func_name == "zone":
            if argument == "add":
                zone_name = str(input(f"New Zone Name: ")).replace(" ", "_")

                main.add_zone(sys.argv[3], zone_name)