class LogisticsInfo {
    constructor(data){
        this.item_auto_issue_location = data.item_default_expiration;
        this.item_auto_issue_zone = data.item_expires;
        this.item_primary_location = data.item_food_groups;
        this.item_primary_zone = data.item_ingredients;
        this.item_uuid = data.item_uuid;
    }
    
    update(data) {
        Object.keys(data).forEach((key) => {
            if(Object.prototype.hasOwnProperty.call(this, key)){
                this[key] = data[key]
            }
        })
    }
}


class FoodInfo {
    constructor(data){
        this.item_default_expiration = data.item_default_expiration;
        this.item_expires = data.item_expires;
        this.item_food_groups = data.item_food_groups;
        this.item_ingredients = data.item_ingredients;
        this.item_nutrients = data.item_nutrients;
        this.item_uuid = data.item_uuid;
    }
    
    update(data) {
        Object.keys(data).forEach((key) => {
            if(Object.prototype.hasOwnProperty.call(this, key)){
                this[key] = data[key]
            }
        })
    }
}

class ItemInfo {
    constructor(data){
        this.item_uuid = data.item_uuid;
        this.item_uom = data.item_uom;
        this.item_packaging = data.item_packaging;
        this.item_uom_quantity = data.item_uom_quantity;
        this.item_cost = data.item_cost;
        this.item_safety_stock = data.item_safety_stock;
        this.item_lead_time_days = data.item_lead_time_days;
        this.item_ai_pick = data.item_ai_pick;
        this.item_prefixes = data.item_prefixes;
        this.conversions = data.conversions;
        this.prefixes = data.prefixes;
    }
    
    update(data) {
        Object.keys(data).forEach((key) => {
            if(Object.prototype.hasOwnProperty.call(this, key)){
                this[key] = data[key]
            }
        })
    }
}


class InventoryItem {
    constructor(data){
        this.item_uuid = data.item_uuid; // string
        this.item_created_at = data.item_created_at; // date
        this.item_updated_at = data.item_updated_at; // date
        this.item_name = data.item_name; // string
        this.item_description = data.item_description; // string
        this.item_tags = data.item_tags; // array
        this.item_links = data.item_links; // dict
        this.item_brand_uuid = data.item_brand_uuid; // uuid
        this.item_category = data.item_category; // string
        this.item_search_string = data.item_search_string; // string
        this.item_inactive = data.item_inactive; // bool
        this.item_locations = data.item_locations; // array
        this.item_barcodes = data.item_barcodes; // array
    }

    update(data) {
        Object.keys(data).forEach((key) => {
            if(Object.prototype.hasOwnProperty.call(this, key)){
                this[key] = data[key]
            }
        })
    }

    toString() {
        return JSON.stringify(this, null, 2);
    }
}

export { InventoryItem, ItemInfo, FoodInfo, LogisticsInfo };