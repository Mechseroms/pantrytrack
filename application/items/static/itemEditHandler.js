import { FoodInfo, InventoryItem, ItemInfo, LogisticsInfo } from './inventoryClasses.js';

var item;
var item_info;
var food_info;
var logistics_info;


document.addEventListener('DOMContentLoaded', async function() {
    //await setupFormDefaults()
    //await refreshForm()
    //await fetchItem()
    console.log(passed_item)
    item = new InventoryItem(passed_item);
    item_info = new ItemInfo(passed_item.item_info)
    food_info = new FoodInfo(passed_item.food_info)
    logistics_info = new LogisticsInfo(passed_item.logistics_info)
    console.log(item['item_category'])
    console.log(document.getElementById("item_subtype_input").value)

})


// Form controls
function updateItemType() {
    
}

function updateItemSubtype(){

}

// fetch functions
async function fetchItem() {
    const url = new URL('/items/api/getItem', window.location.origin);
    url.searchParams.append('item_uuid', item_uuid);
    const response = await fetch(url);
    let data =  await response.json();
    item = new InventoryItem(data.item);
    item_info = new ItemInfo(data.item.item_info)
    food_info = new FoodInfo(data.item.food_info)
    logistics_info = new LogisticsInfo(data.item.logistics_info)
};