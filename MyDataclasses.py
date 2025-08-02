from dataclasses import dataclass, field
import json, datetime
from database import lst2pgarr

@dataclass
class LogisticsInfoPayload:
    barcode: str
    primary_location: int
    primary_zone: int
    auto_issue_location: int
    auto_issue_zone: int
    
    def payload(self):
        return (self.barcode, 
                self.primary_location, 
                self.primary_zone,
                self.auto_issue_location,
                self.auto_issue_zone)

@dataclass
class ItemInfoPayload:
    barcode: str
    packaging: str = ""
    uom_quantity: float = 1.0
    uom: int = 1
    cost: float = 0.0
    safety_stock: float = 0.0
    lead_time_days: float = 0.0
    ai_pick: bool = False
    prefixes: list = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.barcode, str):
            raise TypeError(f"barcode must be of type str; not {type(self.barcode)}")
        
    def payload(self):
        return (
            self.barcode,
            self.packaging,
            self.uom_quantity,
            self.uom,
            self.cost,
            self.safety_stock,
            self.lead_time_days,
            self.ai_pick,
            lst2pgarr(self.prefixes)
        )
    
@dataclass
class FoodInfoPayload:
    food_groups: list = field(default_factory=list)
    ingrediants: list = field(default_factory=list)
    nutrients: dict = field(default_factory=dict)
    expires: bool = False
    default_expiration: float = 0.0

    def payload(self):
        return (
            lst2pgarr(self.food_groups),
            lst2pgarr(self.ingrediants),
            json.dumps(self.nutrients),
            self.expires,
            self.default_expiration
        )

    
@dataclass
class ItemsPayload:
    barcode: str
    item_name: str
    item_info_id: int
    logistics_info_id: int
    food_info_id: int
    brand: int = 0
    description: str = ""
    tags: list = field(default_factory=list)
    links: dict = field(default_factory=dict)
    row_type: str = ""
    item_type: str = ""
    search_string: str =""


    def payload(self):
        return (
            self.barcode,
            self.item_name,
            self.brand,
            self.description,
            lst2pgarr(self.tags),
            json.dumps(self.links),
            self.item_info_id,
            self.logistics_info_id,
            self.food_info_id,
            self.row_type,
            self.item_type,
            self.search_string
        )

  # done  
@dataclass
class TransactionPayload:
    timestamp: datetime.datetime
    logistics_info_id: int
    barcode: str
    name: str
    transaction_type: str
    quantity: float
    description: str
    user_id: int
    data: dict = field(default_factory=dict)

    def payload(self):
        return (
            self.timestamp,
            self.logistics_info_id,
            self.barcode,
            self.name,
            self.transaction_type,
            self.quantity,
            self.description,
            self.user_id,
            json.dumps(self.data)
        )
    
@dataclass
class CostLayerPayload:
    aquisition_date: datetime.datetime
    quantity: float
    cost: float
    currency_type: str
    vendor: int = 0
    expires: datetime.datetime = None

    def payload(self):
        return (
            self.aquisition_date,
            self.quantity,
            self.cost,
            self.currency_type,
            self.expires,
            self.vendor
        )
    
@dataclass
class ItemLinkPayload:
    barcode: str
    link: int
    data: dict = field(default_factory=dict)
    conv_factor: float = 1

    def __post_init__(self):
        if not isinstance(self.barcode, str):
            raise TypeError(f"barcode must be of type str; not {type(self.barocde)}")
        if not isinstance(self.link, int):
            raise TypeError(f"link must be of type str; not {type(self.link)}")

    def payload(self):
        return (
            self.barcode,
            self.link,
            json.dumps(self.data),
            self.conv_factor
        )

@dataclass
class GroupPayload:
    name: str
    description: str
    group_type: str = "plain"

    def payload(self):
        return (
            self.name,
            self.description,
            self.group_type
        )

@dataclass
class GroupItemPayload:
    uuid: str
    gr_id: int
    item_type: str
    item_name:str
    uom: str
    qty: float = 0.0
    item_id: int = None
    links: dict = field(default_factory=dict)

    def payload(self):
        return (
            self.uuid,
            self.gr_id,
            self.item_type,
            self.item_name,
            self.uom,
            self.qty,
            self.item_id,
            json.dumps(self.links)
        )

@dataclass
class RecipeItemPayload:
    uuid: str
    rp_id: int
    item_type: str
    item_name:str
    uom: str
    qty: float = 0.0
    item_id: int = None
    links: dict = field(default_factory=dict)

    def payload(self):
        return (
            self.uuid,
            self.rp_id,
            self.item_type,
            self.item_name,
            self.uom,
            self.qty,
            self.item_id,
            json.dumps(self.links)
        )

@dataclass
class RecipePayload:
    name: str
    author: int
    description: str
    creation_date: datetime.datetime = field(init=False)
    instructions: list = field(default_factory=list)
    picture_path: str = ""

    def __post_init__(self):
        self.creation_date = datetime.datetime.now()

    def payload(self):
        return (
            self.name,
            self.author,
            self.description,
            self.creation_date,
            lst2pgarr(self.instructions),
            self.picture_path
        )

@dataclass
class ReceiptItemPayload:
    type: str
    receipt_id: int
    barcode: str
    name: str
    qty: float = 1.0
    uom: str = "each"
    data: dict = field(default_factory=dict)
    status: str = "Unresolved"

    def payload(self):
        return (
            self.type,
            self.receipt_id,
            self.barcode,
            self.name,
            self.qty,
            self.uom,
            json.dumps(self.data),
            self.status
        )
    
@dataclass
class ReceiptPayload:
    receipt_id: str
    receipt_status: str = "Unresolved"
    date_submitted: datetime.datetime = field(init=False)
    submitted_by: int = 0
    vendor_id: int = 1
    files: dict = field(default_factory=dict)

    def __post_init__(self):
        self.date_submitted = datetime.datetime.now()

    def payload(self):
        return (
            self.receipt_id,
            self.receipt_status,
            self.date_submitted,
            self.submitted_by,
            self.vendor_id,
            json.dumps(self.files)
        )
    
@dataclass
class ShoppingListItemPayload:
    uuid: str
    sl_id: int
    item_type: str
    item_name: str
    uom: str
    qty: float
    item_id: int = None
    links: dict = field(default_factory=dict)

    def payload(self):
        return (
            self.uuid,
            self.sl_id,
            self.item_type,
            self.item_name,
            self.uom,
            self.qty,
            self.item_id,
            json.dumps(self.links)
        )
    
@dataclass
class ShoppingListPayload:
    name: str
    description: str
    author: int
    type: str = "plain"
    creation_date: datetime.datetime = field(init=False)

    def __post_init__(self):
        self.creation_date = datetime.datetime.now()

    def payload(self):
        return (
            self.name,
            self.description,
            self.author,
            self.creation_date,
            self.type
        )


# DONE
@dataclass
class SitePayload:
    site_name: str
    site_description: str
    site_owner_id: int
    default_zone: str = None
    default_auto_issue_location: str = None
    default_primary_location: str = None
    creation_date: datetime.datetime = field(init=False)
    flags: dict = field(default_factory=dict)

    def __post_init__(self):
        self.creation_date = datetime.datetime.now()
    
    def payload(self):
        return (
            self.site_name,
            self.site_description,
            self.creation_date,
            self.site_owner_id,
            json.dumps(self.flags),
            self.default_zone,
            self.default_auto_issue_location,
            self.default_primary_location
        )
    
    def get_dictionary(self):
        return self.__dict__


#DONE
@dataclass
class RolePayload:
    role_name:str
    role_description:str
    site_id: int
    flags: dict = field(default_factory=dict)

    def payload(self):
        return (
            self.role_name,
            self.role_description,
            self.site_id,
            json.dumps(self.flags)
        )

@dataclass
class SiteManager:
    site_name: str
    admin_user: tuple
    default_zone: int
    default_location: int
    description: str
    create_order: list = field(init=False)
    drop_order: list = field(init=False)

    def __post_init__(self):
        self.create_order = [
        "logins",
        "sites",
        "roles",
        "units",
        "cost_layers",
        "linked_items",
        "brands",
        "food_info",
        "item_info",
        "zones",
        "locations",
        "logistics_info",
        "transactions",
        "item",
        "vendors",
        "groups",
        "group_items",
        "receipts",
        "receipt_items",
        "recipes",
        "recipe_items",
        "shopping_lists",
        "shopping_list_items",
        "item_locations",
        "conversions",
        "sku_prefix"
    ]
        self.drop_order = [
        "item_info",
        "items",
        "cost_layers",
        "linked_items",
        "transactions",
        "brands",
        "food_info",
        "logistics_info",
        "zones",
        "locations",
        "vendors",
        "group_items",
        "groups",
        "receipt_items",
        "receipts",
        "recipe_items",
        "recipes",
        "shopping_list_items",
        "shopping_lists",
        "item_locations",
        "conversions",
        "sku_prefix"
    ]