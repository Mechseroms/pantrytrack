# 3RD PARTY IMPORTS
import psycopg2
import datetime

# APPLICATION IMPORTS
import config
from application import postsqldb, database_payloads
from application.administration import administration_database

def dropSiteTables(conn, site_manager):
    try:
        for table in site_manager.drop_order:
            administration_database.dropTable(site_manager.site_name, table, conn=conn)
            with open("logs/process.log", "a+") as file:
                file.write(f"{datetime.datetime.now()} --- INFO --- {table} DROPPED!\n")
    except Exception as error:
        raise error

def deleteSite(site, user, conn=None):
    """Uses a Site Manager to delete a site from the system.

    Args:
        site_manager (MyDataclasses.SiteManager): 

    Raises:
        Exception: 
    """
    self_conn = False
    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True
    
    try:
        admin_user = (user['username'], user['password'], user['email'], user['row_type'])
        site_manager = database_payloads.SiteManager(
            site['site_name'],
            admin_user,
            site['default_zone'],
            site['default_primary_location'],
            site['site_description']
        )

        roles = administration_database.selectRolesTupleBySite((site['id'],), conn=conn)
        administration_database.deleteRolesTuple([role['id'] for role in roles], conn=conn)
        
        dropSiteTables(conn, site_manager)

        for role in roles:
            administration_database.updateUsersRoles({'role_id': role['id']}, conn=conn)
        
        administration_database.updateUsersSites({'site_id': site['id']}, conn=conn)
        
        site = administration_database.deleteSitesTuple((site['id'], ), conn=conn)
        
        if self_conn:
            conn.commit()
            conn.close()

    except Exception as error:
        with open("logs/process.log", "a+") as file:
            file.write(f"{datetime.datetime.now()} --- ERROR --- {error}\n")
        conn.rollback()
        conn.close()

def addAdminUser(conn, site_manager, convert=True):
    admin_user = ()
    try:
        sql = f"INSERT INTO logins (username, password, email, row_type) VALUES (%s, %s, %s, %s) ON CONFLICT (username) DO UPDATE SET username = excluded.username RETURNING *;"
        with conn.cursor() as cur:
            cur.execute(sql, site_manager.admin_user)
            rows = cur.fetchone()
            if rows and convert:
                admin_user = postsqldb.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                admin_user = rows   
        with open("logs/process.log", "a+") as file:
            file.write(f"{datetime.datetime.now()} --- INFO --- Admin User Created!\n")
    except Exception as error:
        raise error
    return admin_user

def setupSiteTables(conn, site_manager):
    try:
        for table in site_manager.create_order:
            administration_database.createTable(site_manager.site_name, table, conn=conn)
            with open("logs/process.log", "a+") as file:
                file.write(f"{datetime.datetime.now()} --- INFO --- {table} Created!\n")
    except Exception as error:
        raise error

def addSite(payload, conn=None):
    """uses a Site Manager to add a site to the system

    Args:
        site_manager (MyDataclasses.SiteManager):
    """
    self_conn = False
    site_manager = database_payloads.SiteManager(
            payload['site_name'],
            payload['admin_user'],
            payload['default_zone'],
            payload['default_primary_location'],
            payload['site_description']
        )

    try:

        if not conn:
            database_config = config.config()
            conn = psycopg2.connect(**database_config)
            conn.autocommit = False
            self_conn = True

        setupSiteTables(conn, site_manager)
        
        admin_user = addAdminUser(conn, site_manager)
        
        site = database_payloads.SitePayload(
            site_name=site_manager.site_name,
            site_description=site_manager.description,
            site_owner_id=admin_user['id']
        )

        site = administration_database.insertSitesTuple(site.payload(), conn=conn)

        role = database_payloads.RolePayload("Admin", f"Admin for {site['site_name']}", site['id'])
        role = administration_database.insertRolesTuple(role.payload(), conn=conn)

        admin_user = administration_database.updateAddLoginSitesRoles((site["id"], role["id"], admin_user["id"]), conn=conn)
        
        default_zone = database_payloads.ZonesPayload(site_manager.default_zone)
        default_zone = administration_database.insertZonesTuple(site["site_name"], default_zone.payload(), conn=conn)
        uuid = f"{site_manager.default_zone}@{site_manager.default_location}"

        default_location = database_payloads.LocationsPayload(uuid, site_manager.default_location, default_zone['id'])
        default_location = administration_database.insertLocationsTuple(site['site_name'], default_location.payload(), conn=conn)
        
        payload = {
            'id': site['id'],
            'update': {
                'default_zone': default_zone['id'], 
                'default_auto_issue_location': default_location['id'],
                'default_primary_location': default_location['id']
            }
        }

        administration_database.updateSitesTuple(payload, conn=conn)
        
        
        blank_vendor = database_payloads.VendorsPayload("None", admin_user['id'])
        blank_brand = database_payloads.BrandsPayload("None")
        
        blank_vendor = administration_database.insertVendorsTuple(site['site_name'], blank_vendor.payload(), conn=conn)
        blank_brand = administration_database.insertBrandsTuple(site['site_name'], blank_brand.payload(), conn=conn)
        
        
        if self_conn:
            conn.commit()
            conn.close()

    except Exception as error:
        with open("logs/process.log", "a+") as file:
            file.write(f"{datetime.datetime.now()} --- ERROR --- {error}\n")
        conn.rollback()
        raise error