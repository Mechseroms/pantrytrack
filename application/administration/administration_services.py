# 3RD PARTY IMPORTS
import psycopg2
import datetime

# APPLICATION IMPORTS
import config
from application import postsqldb, database_payloads
from application.administration import administration_database, administration_models
from dataclasses import dataclass, field

from application.database_postgres import (
    CostLayersModel,
    BrandsModel,
    FoodInfoModel,
    ItemInfoModel,
    ZonesModel,
    LocationsModel,
    LogisticsInfoModel,
    TransactionsModel,
    ItemsModel,
    ItemLocationsModel,
    ConversionsModel,
    SKUPrefixModel,
    BarcodesModel,
    VendorsModel,
    ReceiptsModel,
    ReceiptItemsModel,
    RecipesModel,
    RecipeItemsModel,
    ShoppingListsModel,
    ShoppingListItemsModel,
    PlansModel,
    PlanEventsModel,
    SitesModel,
    UsersModel,
    RolesModel,
    UnitsModel
)

from application.database_postgres import BaseModel

@dataclass
class SiteManager:
    site_name: str
    admin_user: tuple
    default_zone: int
    default_location: int
    description: str
    create_order: list = field(init=False)
    drop_order: list = field(init=False)

    def create_tables(self, conn):
        UsersModel.UsersModel.create_table(self.site_name, conn=conn)
        SitesModel.SitesModel.create_table(self.site_name, conn=conn)
        RolesModel.RolesModel.create_table(self.site_name, conn=conn)
        UnitsModel.UnitsModel.create_table(self.site_name, conn=conn)

        # Needed for Items and Logistics
        BrandsModel.BrandsModel.create_table(self.site_name, conn=conn)
        ZonesModel.ZonesModel.create_table(self.site_name, conn=conn)
        LocationsModel.LocationsModel.create_table(self.site_name, conn=conn)
        ItemsModel.ItemsModel.create_table(self.site_name, conn=conn)
        FoodInfoModel.FoodInfoModel.create_table(self.site_name, conn=conn)
        ItemInfoModel.ItemInfoModel.create_table(self.site_name, conn=conn)
        LogisticsInfoModel.LogisticsInfoModel.create_table(self.site_name, conn=conn)
        ItemLocationsModel.ItemLocationsModel.create_table(self.site_name, conn=conn)
        CostLayersModel.CostLayersModel.create_table(self.site_name, conn=conn)
        ConversionsModel.ConversionsModel.create_table(self.site_name, conn=conn)
        TransactionsModel.TransactionsModel.create_table(self.site_name, conn=conn)
        SKUPrefixModel.SKUPrefixModel.create_table(self.site_name, conn=conn)
        BarcodesModel.BarcodesModel.create_table(self.site_name, conn=conn)


        # Vendors is used losely in Planner and in receipts.
        VendorsModel.VendorsModel.create_table(self.site_name, conn=conn)
        ReceiptsModel.ReceiptsModel.create_table(self.site_name, conn=conn)
        ReceiptItemsModel.ReceiptItemsModel.create_table(self.site_name, conn=conn)

        # This is the Recipe Module
        RecipesModel.RecipesModel.create_table(self.site_name, conn=conn)
        RecipeItemsModel.RecipeItemsModel.create_table(self.site_name, conn=conn)

        # this is the Shopping List Module
        ShoppingListsModel.ShoppingListsModel.create_table(self.site_name, conn=conn)
        ShoppingListItemsModel.ShoppingListItemsModel.create_table(self.site_name, conn=conn)

        # Planner Module
        PlansModel.PlansModel.create_table(self.site_name, conn=conn)
        PlanEventsModel.PlanEventsModel.create_table(self.site_name, conn=conn)

    def drop_tables(self, conn):
        # Needed for Items and Logistics
        BrandsModel.BrandsModel.drop_table(self.site_name,conn=conn)
        CostLayersModel.CostLayersModel.drop_table(self.site_name, conn=conn)
        FoodInfoModel.FoodInfoModel.drop_table(self.site_name, conn=conn)
        ItemInfoModel.ItemInfoModel.drop_table(self.site_name, conn=conn)
        ZonesModel.ZonesModel.drop_table(self.site_name, conn=conn)
        LocationsModel.LocationsModel.drop_table(self.site_name, conn=conn)
        LogisticsInfoModel.LogisticsInfoModel.drop_table(self.site_name, conn=conn)
        TransactionsModel.TransactionsModel.drop_table(self.site_name, conn=conn)
        ItemsModel.ItemsModel.drop_table(self.site_name, conn=conn)
        ItemLocationsModel.ItemLocationsModel.drop_table(self.site_name, conn=conn)
        ConversionsModel.ConversionsModel.drop_table(self.site_name, conn=conn)
        SKUPrefixModel.SKUPrefixModel.drop_table(self.site_name, conn=conn)
        BarcodesModel.BarcodesModel.drop_table(self.site_name, conn=conn)


        # Vendors is used losely in Planner and in receipts.
        VendorsModel.VendorsModel.drop_table(self.site_name, conn=conn)
        ReceiptsModel.ReceiptsModel.drop_table(self.site_name, conn=conn)
        ReceiptItemsModel.ReceiptItemsModel.drop_table(self.site_name, conn=conn)

        # This is the Recipe Module
        RecipesModel.RecipesModel.drop_table(self.site_name, conn=conn)
        RecipeItemsModel.RecipeItemsModel.drop_table(self.site_name, conn=conn)

        # this is the Shopping List Module
        ShoppingListsModel.ShoppingListsModel.drop_table(self.site_name, conn=conn)
        ShoppingListItemsModel.ShoppingListItemsModel.drop_table(self.site_name, conn=conn)

        # Planner Module
        PlansModel.PlansModel.drop_table(self.site_name, conn=conn)
        PlanEventsModel.PlanEventsModel.drop_table(self.site_name, conn=conn)

def deleteSite(payload, conn=None):
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
    
    
    site_manager = SiteManager(
        payload['site_name'],
        payload['admin_user'],
        payload['default_zone'],
        payload['default_primary_location'],
        payload['site_description']
    )

    roles = administration_models.ExtendedRolesModel.select_by_site_uuid({'site_uuid': payload['site_uuid']}, conn=conn)
    roles = RolesModel.RolesModel.delete_tuples([role['role_uuid'] for role in roles], conn=conn)
        
    site_manager.drop_tables(conn=conn)

    for role in roles:
        administration_models.ExtendedUsersModel.update_roles({'role_uuid': role['role_uuid']}, conn=conn)
    

    administration_models.ExtendedUsersModel.update_sites({'site_uuid': payload['site_uuid']}, conn=conn)
    
    SitesModel.SitesModel.delete_tuples((payload['site_uuid'],), conn=conn)
    
    if self_conn:
        conn.commit()
        conn.close()

def addSite(payload, conn=None):
    """uses a Site Manager to add a site to the system

    Args:
        site_manager (MyDataclasses.SiteManager):
    """
    self_conn = False
    site_manager = SiteManager(
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

        sql = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
        with conn.cursor() as cur:
            cur.execute(sql)

        site_manager.create_tables(conn=conn)
        
        
        admin_user = administration_models.ExtendedUsersModel.add_admin_user(site_manager.admin_user, conn=conn)
        
        site = SitesModel.SitesModel.Payload(
            site_name=site_manager.site_name,
            site_description=site_manager.description,
            site_created_by=admin_user['user_uuid']
        )

        # have to build site table
        site = SitesModel.SitesModel.insert_tuple(site.site_name, site.payload_dictionary(), conn=conn)

        # have to build roles table
        role = RolesModel.RolesModel.Payload(
            role_name="Admin",
            role_description=f"Admin for {site['site_name']}",
            role_site_uuid=site['site_uuid']
        )
        role = RolesModel.RolesModel.insert_tuple(site['site_name'], role.payload_dictionary(), conn=conn)

        # have to build logins table
        payload = {
            'user_uuid': admin_user['user_uuid'], 
            'site_uuid': site['site_uuid'],
            'role_uuid': role['role_uuid']
            }
        admin_user = administration_models.ExtendedUsersModel.update_user_site_roles(payload, conn=conn)

        default_zone = ZonesModel.ZonesModel.Payload(zone_name=site_manager.default_zone)
        default_zone = ZonesModel.ZonesModel.insert_tuple(site["site_name"], default_zone.payload_dictionary(), conn=conn)
        uuid = f"{site_manager.default_zone}@{site_manager.default_location}"

        default_location = LocationsModel.LocationsModel.Payload(
            location_shortname=uuid,
            location_name=site_manager.default_location, 
            zone_uuid=default_zone['zone_uuid']
        )

        default_location = LocationsModel.LocationsModel.insert_tuple(site['site_name'], default_location.payload_dictionary(), conn=conn)
        
        payload = {
            'key': site['site_uuid'],
            'update': {
                'site_default_zone_uuid': default_zone['zone_uuid'], 
                'site_default_auto_issue_location_uuid': default_location['location_uuid'],
                'site_default_primary_location_uuid': default_location['location_uuid']
            }
        }

        SitesModel.SitesModel.update_tuple(payload, conn=conn)
        
        
        blank_vendor = VendorsModel.VendorsModel.Payload("None", admin_user['user_uuid'])
        blank_brand = BrandsModel.BrandsModel.Payload("None")
        
        VendorsModel.VendorsModel.insert_tuple(site['site_name'], blank_vendor.payload_dictionary(), conn=conn)
        BrandsModel.BrandsModel.insert_tuple(site['site_name'], blank_brand.payload_dictionary(), conn=conn)
        
        if self_conn:
            conn.commit()
            conn.close()

    except Exception as error:
        with open("logs/process.log", "a+") as file:
            file.write(f"{datetime.datetime.now()} --- ERROR --- {error}\n")
        conn.rollback()
        raise error