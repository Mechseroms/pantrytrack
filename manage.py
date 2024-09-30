import sys, os, shutil
import main

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


def create():
    site_name = input("Site Name: ")
    site_owner = input("Site Owner: ")
    email = input("Contact Email: ")
    
    default_zone_name = input("Set Default Zone Name (default): ").strip()
    if default_zone_name == "":
        default_zone_name = "default"

    print(f"\n")

    print(f"Now you will set the default location that you wish for things to be received into (primary location) and used from (auto-issue).")
    default_location_name = input("Set Default Location (all): ").strip()
    if default_location_name == "":
        default_location_name = "all"

    if not os.path.exists(f"sites/{site_name}"):
        print(f"Creating {site_name} site...")
        os.mkdir(f"sites/{site_name}")
        
        print(f"Creating sql tables files...")
        shutil.copytree(f"sites/default/sql", f"sites/{site_name}/sql")
        rename_create_sql(site_name)
        rename_drop_sql(site_name)

        with open(f"sites/{site_name}/site.ini", "w+") as config:
            config.write(f"[site]\n")
            config.write(f"site_name={site_name}\n")
            config.write(f"site_owner={site_owner}\n")
            config.write(f"email={email}\n")
            config.write(f"\n")

            config.write(f"[defaults]\n")
            config.write(f"default_zone={default_zone_name}\n")
            config.write(f"default_primary_location={default_location_name}\n")
            config.write(f"default_auto_issue_location={default_location_name}\n")


        print(f"Site {site_name} config created!")
        print(f"Site {site_name} created!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        func_name = sys.argv[1]

        if func_name == "create_site":
            create()

        if func_name == "propagate":
            main.create_site(sys.argv[2])
        
        if func_name == "delete":
            main.delete_site(sys.argv[2])
            shutil.rmtree(f"sites/{sys.argv[2]}")

        if func_name == "add_item":
            barcode = input("barcode: ")
            name = input("name: ")
            qty = float(input("qty: "))
            main.add_food_item(sys.argv[2], barcode, name, qty, payload=main.payload_food_item)

        if func_name == "transact":
            barcode = input("barcode: ")
            qty = float(input("qty: "))
            location = input("TO: ")

            main.add_transaction(sys.argv[2], barcode, qty, 1, description="manual", location=location)

