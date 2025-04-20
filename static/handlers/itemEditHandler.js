var darkmode = false
function toggleDarkMode(){
    if (!darkmode){
        document.body.classList.add('dark-mode-body')
        document.body.classList.add('uk-light')
        document.getElementById('navbar').classList.add('uk-light')
        document.getElementById('navbar').style = "background-color: #121212;"
        document.getElementById('weblinkModal').classList.add('dark-mode-element')
        document.getElementById('weblinkModalFooter').classList.add('dark-mode-element')
        document.getElementById('brandsModalinner').classList.add('dark-mode-element')
        document.getElementById('locationsModalInner').classList.add('dark-mode-element')
        document.getElementById('zonesModalInner').classList.add('dark-mode-element')
        document.getElementById('modeToggle').innerHTML = "light_mode"

        darkmode = true
    } else {
        document.body.classList.remove('dark-mode-body')
        document.body.classList.remove('uk-light')
        document.getElementById('navbar').classList.remove('uk-light')
        document.getElementById('navbar').style = ""
        document.getElementById('weblinkModal').classList.remove('dark-mode-element')
        document.getElementById('weblinkModalFooter').classList.remove('dark-mode-element')
        document.getElementById('brandsModalinner').classList.remove('dark-mode-element')
        document.getElementById('locationsModalInner').classList.remove('dark-mode-element')
        document.getElementById('zonesModalInner').classList.remove('dark-mode-element')
        document.getElementById('modeToggle').innerHTML = "dark_mode"

        darkmode=false
    }
}

var item;
var linked_items;
var tags = new Set();
var weblinks;
var groups;
var shopping_lists;
var food_groups = new Set();
var ingrediants = new Set();
var primary_zone;
var primary_zone_id;
var primary_location;
var auto_zone;
var auto_zone_id;
var auto_location;
var brand;
var locations;

var current_page = 1;
var limit = 2;
var end_page = 1;
var search_string = '';

var updated = {};

// form defaults, make this editable.
var item_types = [['Single', 'single'], ['Linked List', 'list'], ['Linked Item', 'link']];
var item_subtypes = [['Food', 'FOOD'], ['Food PLU', 'FOOD_PLU'], ['Other', 'OTHER'], ['Medicinal', 'MEDICINE'], ['Hygenic', 'HYGENIC']];

document.addEventListener('DOMContentLoaded', async function() {
    await setupFormDefaults()
    await fetchItem()
    console.log(item)
    document.getElementById('title').innerHTML = item.item_name;
    await setBasicInfo()
    await updateWebLinksTable()
    await updateReferenceTable()
    await updateLocationsTable()
    await updateLinkedItemsTable()
    await updateConversionsTableBody()
    await updatePrefixTableBody()
    await updateTags()
})

async function setupFormDefaults() {
    let itemTypeSelect = document.getElementById('itemTypeSelect')
    for(let i=0; i<item_types.length; i++){
        let elem = document.createElement('option')
        elem.innerHTML = `${item_types[i][0]}`
        elem.value = `${item_types[i][1]}`
        itemTypeSelect.append(elem)
    }

    let itemSubTypeSelect = document.getElementById('itemSubTypeSelect')
    for(let i=0; i<item_subtypes.length; i++){
        let elem = document.createElement('option')
        elem.innerHTML = `${item_subtypes[i][0]}`
        elem.value = `${item_subtypes[i][1]}`
        itemSubTypeSelect.append(elem)
    }
}

async function updateConversionsTableBody(){
    let conversionsTableBody = document.getElementById('conversionsTableBody')
    conversionsTableBody.innerHTML = "";
    
    for(let i=0; i < item.item_info.conversions.length; i++){
        let tableRow = document.createElement('tr')

        let parentUOM = document.createElement('td')
        parentUOM.innerHTML = `1 ${item.item_info.uom.fullname} to ${item.item_info.conversions[i].conv_factor} ${item.item_info.conversions[i].fullname}`
        parentUOM.setAttribute('class', 'uk-text-center')
        let opCell = document.createElement('td')
        
        let deleteButton = document.createElement('button')
        deleteButton.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        deleteButton.innerHTML = 'delete'
        deleteButton.onclick = async function(){
            await deleteConversion(item.item_info.conversions[i].conv_id)
        }

        let editButton = document.createElement('button')
        editButton.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        editButton.innerHTML = 'edit'
        editButton.onclick = async function(){
            await openEditConversionsModal(item.item_info.conversions[i])
        }


        opCell.append(deleteButton, editButton)

        tableRow.append(parentUOM, opCell)
        conversionsTableBody.append(tableRow)
    }
}

async function updatePrefixTableBody(){
    let prefixesTableBody = document.getElementById('prefixesTableBody')
    prefixesTableBody.innerHTML = "";
    
    for(let i=0; i < item.item_info.prefixes.length; i++){
        let tableRow = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${item.item_info.prefixes[i].name}`
        nameCell.setAttribute('class', 'uk-text-center')
        
        let opCell = document.createElement('td')
        
        let deleteButton = document.createElement('button')
        deleteButton.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        deleteButton.innerHTML = 'delete'
        deleteButton.onclick = async function(){
            await deletePrefix(item.item_info.prefixes[i].id)
        }
        opCell.append(deleteButton)

        tableRow.append(nameCell, opCell)
        prefixesTableBody.append(tableRow)
    }
}

async function updatePrefixModalTableBody(prefixes) {
    let prefixesModalTableBody = document.getElementById('prefixesModalTableBody')
    prefixesModalTableBody.innerHTML = "";

    for(let i=0; i < prefixes.length; i++){
        let tableRow = document.createElement('tr')
        tableRow.classList.add("selectableRow")

        let idCell = document.createElement('td')
        idCell.innerHTML = `${prefixes[i].id}`

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${prefixes[i].name}`


        tableRow.append(idCell, nameCell)
        tableRow.onclick = async function(){
            await postPrefix(prefixes[i].id)
        }
        prefixesModalTableBody.append(tableRow) 
    }

}

async function updateReferenceTable(){
    let referenceTableBody = document.getElementById('referenceTableBody')
    referenceTableBody.innerHTML = "";
    for(let i=0; i < groups.length; i++){
        let tableRow = document.createElement('tr')

        let typeCell = document.createElement('td')
        typeCell.innerHTML = `group`
        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${groups[i].name}`
        nameCell.classList.add('uk-text-truncate')
        nameCell.classList.add('uk-table-expand')
        nameCell.classList.add('uk-width-3-4')

        tableRow.append(typeCell)
        tableRow.append(nameCell)
        referenceTableBody.append(tableRow)
    }
    for(let i=0; i < shopping_lists.length; i++){
        let tableRow = document.createElement('tr')

        let typeCell = document.createElement('td')
        typeCell.classList.add('uk-width-1-4')
        typeCell.innerHTML = `shopping list`
        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${shopping_lists[i].name}`
        nameCell.classList.add('uk-text-truncate')
        nameCell.classList.add('uk-table-expand')
        nameCell.classList.add('uk-width-3-4')

        tableRow.append(typeCell)
        tableRow.append(nameCell)
        referenceTableBody.append(tableRow)
    }
}

async function addWebLink(){
    if (!updated.hasOwnProperty('item')){
        updated['item'] = {}
    }
    let key = document.getElementById('weblinkName').value
    let value = document.getElementById('weblinkLink').value
    document.getElementById('weblinkName').value = ""
    document.getElementById('weblinkLink').value = ""
    weblinks[key] = value
    await updateWebLinksTable()
    updated['item']['links'] = weblinks
    UIkit.modal(document.getElementById('addWeblinkModal')).hide();
}

async function updateWebLinksTable(){
    let weblinksTableBody = document.getElementById('weblinksTableBody')
    weblinksTableBody.innerHTML = "";

    for(let key in weblinks){
        let tableRow = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${key}`
        let linkCell = document.createElement('td')
        linkCell.classList.add('uk-table-expand')
        linkCell.classList.add('uk-text-truncate')
        linkCell.innerHTML = `<a class="uk-link-muted" target="_blank" href="${weblinks[key]}">${weblinks[key]}</a>`
        let buttonCell = document.createElement('td')
        buttonCell.classList.add('uk-width-1-4')

        let deleteButton = document.createElement('button')
        deleteButton.setAttribute('class', 'uk-flex uk-flex-middle uk-flex-center uk-button uk-button-small uk-align-right delete_button')
        deleteButton.onclick = function (){
            deleteLink(key)
        }
        deleteButton.innerHTML = `<span uk-icon="icon: trash"></span>`

        buttonCell.append(deleteButton)

        tableRow.append(nameCell)
        tableRow.append(linkCell)
        tableRow.append(buttonCell)
        weblinksTableBody.append(tableRow)
    }
}

async function updateTags() {
    let chipZoneTags = document.getElementById('tagsRow')
    chipZoneTags.innerHTML = "";
    tags.forEach(tagText => {
        let tag = document.createElement('div')
        tag.setAttribute("uk-tooltip", "title: Double click to Remove; pos: bottom")
        tag.setAttribute("class", "chip uk-border-pill uk-label uk-margin-xsmall-right")
        tag.setAttribute("id", `tag_${tagText}`)
        tag.innerHTML = tagText
        tag.ondblclick = function(){
            removeTag(tagText, tag.id)
        }
        chipZoneTags.append(tag)
    });
    let foodGroupsTags = document.getElementById('foodGroupsTagsRow')
    foodGroupsTags.innerHTML = "";
    food_groups.forEach(tagText => {
        let tag = document.createElement('div')
        tag.setAttribute("uk-tooltip", "title: Double click to Remove; pos: bottom")
        tag.setAttribute("class", "chip uk-border-pill uk-label uk-margin-xsmall-right")
        tag.setAttribute("id", `tag_${tagText}`)
        tag.innerHTML = tagText
        tag.ondblclick = function(){
            removeFoodGroup(tagText, tag.id)
        }
        foodGroupsTags.append(tag)
    });
    let ingrediantsRow = document.getElementById('ingrediantsRow')
    ingrediantsRow.innerHTML = "";
    ingrediants.forEach(tagText => {
        let tag = document.createElement('div')
        tag.setAttribute("uk-tooltip", "title: Double click to Remove; pos: bottom")
        tag.setAttribute("class", "chip uk-border-pill uk-label uk-margin-xsmall-right")
        tag.setAttribute("id", `ingr_${tagText}`)
        tag.innerHTML = tagText
        tag.ondblclick = function(){
            removeIngrediant(tagText, tag.id)
        }
        ingrediantsRow.append(tag)
    });
}

async function updateLocationsTable() {
    let locationsTableBody = document.getElementById('locationsTableBody')
    locationsTableBody.innerHTML = "";
    for(let i=0; i < locations.length; i++){
        console.log(locations[i])
        let tableRow = document.createElement('tr')

        let locationCell = document.createElement('td')
        locationCell.innerHTML = `${locations[i].uuid}`
        let QOHCell = document.createElement('td')
        QOHCell.innerHTML = `${locations[i].quantity_on_hand}`

        tableRow.append(locationCell)
        tableRow.append(QOHCell)
        locationsTableBody.append(tableRow)
    }
}

async function setBasicInfo() {
    document.getElementById('itemName').value = item.item_name
    document.getElementById('itemBarcode').innerHTML = item.barcode
    document.getElementById('itemBrand').value = brand;
    document.getElementById('itemDescription').value = item.description
    document.getElementById('itemTypeSelect').value = item.row_type
    if(item.row_type === "list"){
        document.getElementById("linkedListLink").classList.remove("uk-disabled")
    } else if (item.row_type === "link"){
        document.getElementById('itemTypeSelect').classList.add("uk-disabled")
    } else {
        document.getElementById("linkedListLink").classList.add("uk-disabled")
        document.getElementById('itemTypeSelect').classList.remove("uk-disabled")
    }
    document.getElementById('itemSubTypeSelect').value = item.item_type
    document.getElementById('aiPickableCheckbox').checked = item.item_info.ai_pick
    document.getElementById('expiresCheckbox').checked = item.food_info.expires
    document.getElementById('expirePeriod').value = item.food_info.default_expiration
    document.getElementById('safetyStock').value = item.item_info.safety_stock
    document.getElementById('leadTimeInDays').value = item.item_info.lead_time_days
    document.getElementById('skuCost').value = item.item_info.cost.toLocaleString('en-US', {style: 'currency', currency: 'USD'})
    document.getElementById('uom_quantity').value = item.item_info.uom_quantity
    document.getElementById('uom').value = item.item_info.uom.id
    document.getElementById('packaging').value = item.item_info.packaging
    document.getElementById('primaryZone').value = primary_zone
    document.getElementById('primaryLocation').value = primary_location
    document.getElementById('autoZone').value = auto_zone
    document.getElementById('autoLocation').value = auto_location

    document.getElementById('main_qty_uom').value = `${item.item_info.uom_quantity} ${item.item_info.uom}`
    document.getElementById('main_barcode').value = item.barcode
    document.getElementById('search_string_main').value = item.search_string

}

function addTag(event){
    if (!updated.hasOwnProperty('item')){
        updated['item'] = {}
    }
    let tagInput = document.getElementById('tagInput');
    tagText = tagInput.value;
    if((event.code=="Enter" || event.type=="click") && !tags.has(tagText)){
        console.log(tagText)
        tags.add(tagText)
        updated['item']['tags'] = Array.from(tags)
        let chipZoneTags = document.getElementById('tagsRow')

        let tag = document.createElement('div')
        tag.setAttribute("uk-tooltip", "title: Double click to Remove; pos: bottom")
        tag.setAttribute("class", "chip uk-border-pill uk-label uk-margin-xsmall-right")
        tag.setAttribute("id", `tag_${tagText}`)
        tag.innerHTML = tagText
        tag.ondblclick = function(){
            removeTag(tagText, tag.id)
        }
        chipZoneTags.append(tag)
        tagInput.classList.remove('uk-form-danger')
    } else if((event.code=="Enter" || event.type=="click") && tags.has(tagText)){
        tagInput.classList.add('uk-form-danger')
        UIkit.notification({
            message: 'Duplicate Tags are not Allowed!',
            status: 'danger',
            pos: 'top-right',
            timeout: 2000
        });
        
    } else {
        tagInput.classList.remove('uk-form-danger') 
    }
}

function addFoodGroup(event){
    if (!updated.hasOwnProperty('food_info')){
        updated['food_info'] = {}
    }
    let foodGroupsInput = document.getElementById('foodGroupsInput');
    tagText = foodGroupsInput.value;
    if((event.code=="Enter" || event.type=="click") && !food_groups.has(tagText)){
        food_groups.add(tagText)
        updated['food_info']['food_groups'] = Array.from(food_groups)
        let chipZoneTags = document.getElementById('foodGroupsTagsRow')
        let tag = document.createElement('div')
        tag.setAttribute("uk-tooltip", "title: Double click to Remove; pos: bottom")
        tag.setAttribute("class", "chip uk-border-pill uk-label uk-margin-xsmall-right")
        tag.setAttribute("id", `food_group_${tagText}`)
        tag.innerHTML = tagText
        tag.ondblclick = function(){
            removeFoodGroup(tagText, tag.id)
        }
        chipZoneTags.append(tag)
        foodGroupsInput.classList.remove('uk-form-danger')
    } else if((event.code=="Enter" || event.type=="click") && food_groups.has(tagText)){
        foodGroupsInput.classList.add('uk-form-danger')
        UIkit.notification({
            message: 'Duplicate Food Groups are not Allowed!',
            status: 'danger',
            pos: 'top-right',
            timeout: 2000
        });
        
    } else {
        foodGroupsInput.classList.remove('uk-form-danger') 
    }
}

function addIngrediant(event){
    if (!updated.hasOwnProperty('food_info')){
        updated['food_info'] = {}
    }
    let ingrediantsInput = document.getElementById('ingrediantsInput');
    tagText = ingrediantsInput.value;
    if((event.code=="Enter" || event.type=="click") && !ingrediants.has(tagText)){
        ingrediants.add(tagText)
        updated['food_info']['ingrediants'] = Array.from(ingrediants)
        let chipZoneTags = document.getElementById('ingrediantsRow')

        let tag = document.createElement('div')
        tag.setAttribute("uk-tooltip", "title: Double click to Remove; pos: bottom")
        tag.setAttribute("class", "chip uk-border-pill uk-label uk-margin-xsmall-right")
        tag.setAttribute("id", `ingr_${tagText}`)
        tag.innerHTML = tagText
        tag.ondblclick = function(){
            removeIngrediant(tagText, tag.id)
        }
        chipZoneTags.append(tag)
        ingrediantsInput.classList.remove('uk-form-danger')
    } else if((event.code=="Enter" || event.type=="click") && ingrediants.has(tagText)){
        ingrediantsInput.classList.add('uk-form-danger')
        UIkit.notification({
            message: 'Duplicate ingrediants are not Allowed!',
            status: 'danger',
            pos: 'top-right',
            timeout: 2000
        });
        
    } else {
        ingrediantsInput.classList.remove('uk-form-danger') 
    }
}

function removeTag(tagText, elementID) {
    if (!updated.hasOwnProperty('item')){
        updated['item'] = {}
    }
    let childElement = document.getElementById(elementID)
    let tempTags = Array.from(tags);
    tempTags = tempTags.filter(item => item !== tagText);
    updated['item']['tags'] = tempTags;
    tags = new Set(tempTags);
    childElement.parentNode.removeChild(childElement)
}

function removeFoodGroup(tagText, elementID) {
    if (!updated.hasOwnProperty('food_info')){
        updated['food_info'] = {}
    }
    let childElement = document.getElementById(elementID)
    let tempTags = Array.from(food_groups);
    tempTags = tempTags.filter(item => item !== tagText);
    updated['food_info']['food_groups'] = tempTags;
    food_groups = new Set(tempTags);
    childElement.parentNode.removeChild(childElement)
}

function removeIngrediant(tagText, elementID) {
    if (!updated.hasOwnProperty('food_info')){
        updated['food_info'] = {}
    }
    console.log(tagText)
    console.log(elementID)
    let childElement = document.getElementById(elementID)
    let tempTags = Array.from(ingrediants);
    tempTags = tempTags.filter(item => item !== tagText);
    updated['food_info']['ingrediants'] = tempTags
    ingrediants = new Set(tempTags);
    childElement.parentNode.removeChild(childElement)
}

function deleteLink(linkKey){
    console.log(linkKey)
}

async function updateLocationsSelectTable(logis) {
    let fetchedLocations;
    let selectlocationsTableBody = document.getElementById('selectlocationsTableBody')
    selectlocationsTableBody.innerHTML = ""
    
    if (logis=='primary_location'){
        data = await fetchLocations('primary_location');
        fetchedLocations = data.locations;
        end_page = data.endpage;
    } else if (logis=='auto_issue_location'){
        data = await fetchLocations('auto_issue_location');
        fetchedLocations = data.locations;
        end_page = data.endpage;
    }
    
    console.log(fetchedLocations)
    for(let i = 0; i < fetchedLocations.length; i++){
        
        let tableRow = document.createElement('tr')
        tableRow.classList.add("selectableRow")

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${fetchedLocations[i].name}`

        tableRow.id = fetchedLocations[i].id

        tableRow.append(nameCell)
        tableRow.onclick = function(){
            closeZoneLocationBrandModal(fetchedLocations[i].name, fetchedLocations[i].id, logis)
        }
        selectlocationsTableBody.append(tableRow) 
    }
}

async function openLocationsModal(logis, elementID){
    let LocationsModal = document.getElementById("LocationsModal")
    current_page = 1;
    search_string = '';
    await updateLocationsSelectTable(logis)
    await updatePaginationElement(logis, elementID)
    UIkit.modal(LocationsModal).show();
}

async function updateZonesTable(logis) {
    let zonesTableBody = document.getElementById('zonesTableBody')
    zonesTableBody.innerHTML = ""
    data = await fetchZones()
    zones = data.zones
    end_page = data.endpage
    for(let i = 0; i < zones.length; i++){
        let tableRow = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${zones[i].name}`

        tableRow.id = zones[i].id

        tableRow.append(nameCell)
        tableRow.onclick = function(){
            closeZoneLocationBrandModal(zones[i].name, zones[i].id, logis)
        }
        zonesTableBody.append(tableRow)
    }
}

async function updateLinkedItemsTable() {
    let linkedItemsTableBody = document.getElementById('linkedItemsTableBody')
    linkedItemsTableBody.innerHTML = ""
    
    let linked_items = item.linked_items
    for(let i = 0; i < linked_items.length; i++){
        
        let tableRow = document.createElement('tr')

        let barcodeCell = document.createElement('td')
        barcodeCell.innerHTML = linked_items[i].barcode
        let nameCell = document.createElement('td')
        nameCell.innerHTML = linked_items[i].data.item_name
        let opCell = document.createElement('td')

        let editOp = document.createElement('a')
        editOp.setAttribute('class', 'uk-button uk-button-default')
        editOp.setAttribute('uk-icon', 'icon: pencil')
        editOp.setAttribute('href', `/item/${item['id']}/itemLink/${linked_items[i].id}`)

        opCell.append(editOp)

        tableRow.append(barcodeCell, nameCell, opCell)
        linkedItemsTableBody.append(tableRow) 
    }
}


async function openZonesModal(logis, elementID){
    let zonesModal = document.getElementById("zonesModal")
    current_page = 1;
    search_string = '';
    await updateZonesTable(logis)
    await updatePaginationElement(logis, elementID)
    UIkit.modal(zonesModal).show();
}

function closeZoneLocationBrandModal(selectName, selectID, key){
    if (!updated.hasOwnProperty('logistics_info')){
        updated['logistics_info'] = {}
    }
    if (!updated.hasOwnProperty('item')){
        updated['item'] = {}
    }

    if(key=='primary_zone'){
        primary_zone = selectName;
        primary_zone_id = selectID;
        document.getElementById('primaryZone').value = selectName;
        updated['logistics_info']['primary_zone'] = selectID
        document.getElementById('primaryLocation').classList.add('uk-form-danger')
        document.getElementById('primaryLocation').value = "";
        UIkit.modal(document.getElementById('zonesModal')).hide();
    }
    if(key=='auto_issue_zone'){
        auto_zone = selectName;
        auto_zone_id = selectID;
        document.getElementById('autoZone').value = selectName;
        updated['logistics_info']['auto_issue_zone'] = selectID;
        document.getElementById('autoLocation').classList.add('uk-form-danger')
        document.getElementById('autoLocation').value = "";
        UIkit.modal(document.getElementById('zonesModal')).hide();
    }
    if(key=='primary_location'){
        primary_location = selectName;
        document.getElementById('primaryLocation').value = selectName;
        updated['logistics_info']['primary_location'] = selectID;
        document.getElementById('primaryLocation').classList.remove('uk-form-danger')
        UIkit.modal(document.getElementById('LocationsModal')).hide();
    }
    if(key=='auto_issue_location'){
        auto_location = selectName;
        document.getElementById('autoLocation').value = selectName;
        updated['logistics_info']['auto_issue_location'] = selectID;
        document.getElementById('autoLocation').classList.remove('uk-form-danger')
        UIkit.modal(document.getElementById('LocationsModal')).hide();
    }
    if(key=='brand'){
        brand = selectName;
        document.getElementById('itemBrand').value = selectName;
        updated['item']['brand'] = selectID;
        UIkit.modal(document.getElementById('brandsModal')).hide();
    }
    if(key=='items'){
        barcode = selectName[0];
        document.getElementById('linked_item').value = barcode;
        document.getElementById('conversion_factor_uom').value = selectName[1];
        document.getElementById('linked_item_id').value = selectID;
        document.getElementById('linkAdd').onclick = async function () {
            await addLinkedItem(item_id, selectID)
        }
        UIkit.modal(document.getElementById('itemsModal')).hide();
    }
}

async function updateBrandsModalTable(logis) {
    let brandsTableBody = document.getElementById('brandsTableBody');
    brandsTableBody.innerHTML = "";
    data = await fetchBrands();
    end_page = data.endpage;
    let fetchedBrands = data.brands;

    for(let i=0; i < fetchedBrands.length; i++){
        let tableRow = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${fetchedBrands[i].name}`

        tableRow.id = fetchedBrands[i].id
        tableRow.onclick = function(){
            closeZoneLocationBrandModal(fetchedBrands[i].name, fetchedBrands[i].id, logis)
        }
        tableRow.append(nameCell)
        brandsTableBody.append(tableRow)
    }
}

async function updateItemsModalTable(logis) {
    let itemsTableBody = document.getElementById('itemsTableBody');
    itemsTableBody.innerHTML = "";
    data = await fetchItems();
    end_page = data.end;
    let fetchedItems = data.items;


    for(let i=0; i < fetchedItems.length; i++){
        let tableRow = document.createElement('tr')

        let idCell = document.createElement('td')
        idCell.innerHTML = `${fetchedItems[i].id}`

        let barcodeCell = document.createElement('td')
        barcodeCell.innerHTML = `${fetchedItems[i].barcode}`

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${fetchedItems[i].item_name}`

        tableRow.id = fetchedItems[i].id
        tableRow.onclick = async function(){
            closeZoneLocationBrandModal([fetchedItems[i].barcode, fetchedItems[i].item_info.uom], fetchedItems[i].id, logis)
        }
        tableRow.append(idCell, barcodeCell, nameCell)
        itemsTableBody.append(tableRow)
        console.log(tableRow.onclick)
    }
}

async function openBrandsModal(logis, elementID) {
    let brandsModal = document.getElementById('brandsModal')
    current_page = 1;
    search_string = '';
    await updateBrandsModalTable(logis)
    await updatePaginationElement(logis, elementID)
    UIkit.modal(brandsModal).show();

}

async function openItemsModal(logis, elementID) {
    let itemsModal = document.getElementById('itemsModal')
    current_page = 1;
    search_string = '';
    document.getElementById('searchItemsInput').value = '';
    await updateItemsModalTable(logis)
    await updatePaginationElement(logis, elementID)
    UIkit.modal(itemsModal).show();
}

async function openAddConversionsModal() {
    let conversionsModal = document.getElementById('conversionsModal')
    document.getElementById('parent_uom').value = `${item.item_info.uom.fullname}`
    document.getElementById('conversionSubmitButton').innerHTML = "Add"
    document.getElementById('conversionSubmitButton').onclick = async function() {
        await postConversion()
    }
    UIkit.modal(conversionsModal).show()
}

async function openEditConversionsModal(conversion) {
    let conversionsModal = document.getElementById('conversionsModal')
    document.getElementById('parent_uom').value = `${item.item_info.uom.fullname}`
    document.getElementById('conversion_factor_modal').value = `${conversion.conv_factor}`
    document.getElementById('conversion_uom').value = `${conversion.id}`
    document.getElementById('conversionSubmitButton').innerHTML = "Save"
    document.getElementById('conversionSubmitButton').onclick = async function() {
        let update = {'conv_factor': document.getElementById('conversion_factor_modal').value}
        await postConversionUpdate(conversion.conv_id, update)
    }
    UIkit.modal(conversionsModal).show()
}


async function postConversion() {
    const response = await fetch(`/item/addConversion`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            parent_id: parseInt(item.id),
            uom_id: parseInt(document.getElementById('conversion_uom').value),
            conv_factor: parseFloat(document.getElementById('conversion_factor_modal').value)
        }),
    });
    data =  await response.json();
    response_status = 'primary'
    if (data.error){
        response_status = 'danger'
    }

    UIkit.notification({
        message: data.message,
        status: response_status,
        pos: 'top-right',
        timeout: 5000
    });
    await fetchItem()
    await setBasicInfo()
    await updateConversionsTableBody()

    UIkit.modal(conversionsModal).hide()
}

async function postConversionUpdate(id, update) {
    const response = await fetch(`/item/updateConversion`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            conversion_id: id,
            update: update
        }),
    });
    data =  await response.json();
    response_status = 'primary'
    if (data.error){
        response_status = 'danger'
    }

    UIkit.notification({
        message: data.message,
        status: response_status,
        pos: 'top-right',
        timeout: 5000
    });
    await fetchItem()
    await setBasicInfo()
    await updateConversionsTableBody()

    UIkit.modal(conversionsModal).hide()
}

async function deleteConversion(conversion_id) {
    const response = await fetch(`/item/deleteConversion`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            conversion_id: conversion_id
        }),
    });
    data =  await response.json();
    response_status = 'primary'
    if (data.error){
        response_status = 'danger'
    }

    UIkit.notification({
        message: data.message,
        status: response_status,
        pos: 'top-right',
        timeout: 5000
    });

    await fetchItem()
    await setBasicInfo()
    await updateConversionsTableBody()

    UIkit.modal(conversionsModal).hide()

}

async function openAddPrefixesModal() {
    let prefixesModal = document.getElementById('prefixesModal')
    current_page = 1;
    let data = await fetchPrefixes()
    let prefixes = data.prefixes
    end_page = data.end;
    await updatePrefixModalTableBody(prefixes)
    await updatePrefixPaginationElement()
    UIkit.modal(prefixesModal).show()
}

async function postPrefix(id) {
    const response = await fetch(`/item/addPrefix`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            parent_id: parseInt(item.item_info_id),
            prefix_id: parseInt(id)
        }),
    });
    data =  await response.json();
    response_status = 'primary'
    if (data.error){
        response_status = 'danger'
    }

    UIkit.notification({
        message: data.message,
        status: response_status,
        pos: 'top-right',
        timeout: 5000
    });
    await fetchItem()
    await setBasicInfo()
    await updatePrefixTableBody()
    UIkit.modal(document.getElementById('prefixesModal')).hide()
}

async function deletePrefix(prefix_id) {
    const response = await fetch(`/item/deletePrefix`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_info_id: item.item_info_id,
            prefix_id: prefix_id
        }),
    });
    data =  await response.json();
    response_status = 'primary'
    if (data.error){
        response_status = 'danger'
    }

    UIkit.notification({
        message: data.message,
        status: response_status,
        pos: 'top-right',
        timeout: 5000
    });

    await fetchItem()
    await setBasicInfo()
    await updatePrefixTableBody()

    UIkit.modal(document.getElementById('prefixesModal')).hide()

}

let prefix_limit = 2;
async function fetchPrefixes() {
    const url = new URL('/item/getPrefixes', window.location.origin);
    url.searchParams.append('page', current_page);
    url.searchParams.append('limit', prefix_limit);
    const response = await fetch(url);
    data =  await response.json();
    return data; 
}

let brands_limit = 25;
async function fetchBrands() {
    const url = new URL('/item/getBrands', window.location.origin);
    url.searchParams.append('page', current_page);
    url.searchParams.append('limit', brands_limit);
    const response = await fetch(url);
    data =  await response.json();
    return data; 
}

let items_limit = 25;
async function fetchItems() {
    const url = new URL('/item/getModalItems', window.location.origin);
    url.searchParams.append('page', current_page);
    url.searchParams.append('limit', items_limit);
    url.searchParams.append('search_string', search_string);
    const response = await fetch(url);
    data =  await response.json();
    return data; 
}

let zones_limit = 20;
async function fetchZones(){
    const url = new URL('/item/getZonesBySku', window.location.origin);
    url.searchParams.append('page', current_page);
    url.searchParams.append('limit', zones_limit);
    url.searchParams.append('item_id', item.id);
    const response = await fetch(url);
    data =  await response.json();
    return data;
}

let locations_limit = 10;
async function fetchLocations(logis) {
    const url = new URL('/item/getLocationsBySkuZone', window.location.origin);
    url.searchParams.append('page', current_page);
    url.searchParams.append('limit', locations_limit);
    url.searchParams.append('part_id', item.id);
    if(logis=="primary_location"){
        url.searchParams.append('zone_id', primary_zone_id);
    } else if (logis=="auto_issue_location"){
        url.searchParams.append('zone_id', auto_zone_id);
    }
    const response = await fetch(url);
    data =  await response.json();
    return data;
}

async function fetchItem() {
    const url = new URL('/item/getItem', window.location.origin);
    url.searchParams.append('id', item_id);
    const response = await fetch(url);
    data =  await response.json();
    item = data.item;
    tags = new Set(item.tags);
    weblinks = item.links;
    groups = item.item_groups;
    shopping_lists = item.item_shopping_lists;
    food_groups = new Set(item.food_info.food_groups);
    ingrediants = new Set(item.food_info.ingrediants);

    primary_zone = item.logistics_info.primary_zone.name
    primary_zone_id = item.logistics_info.primary_zone.id
    primary_location = item.logistics_info.primary_location.name

    auto_zone = item.logistics_info.auto_issue_zone.name
    auto_zone_id = item.logistics_info.auto_issue_zone.id
    auto_location = item.logistics_info.auto_issue_location.name
    locations = item.item_locations

    brand = item.brand.name
};

async function searchTable(event, logis, elementID) {
    if(event.key==='Enter' && logis==='items'){
        search_string = event.srcElement.value
        await updateItemsModalTable(logis)
    }
    await updatePaginationElement(logis, elementID)
}

async function setPage(pageNumber, logis, elementID){
    current_page = pageNumber;
    
    if(elementID=="zonesPage"){
        await updateZonesTable(logis)
    } else if(elementID=="locationsPage"){
        await updateLocationsSelectTable(logis)
    }else if (elementID=="brandsPage"){
        await updateBrandsModalTable(logis)
    } else if (elementID=="itemsPage"){
        await updateItemsModalTable(logis)
    }
    await updatePaginationElement(logis, elementID)
    console.log(current_page)
}

async function updatePaginationElement(logis, elementID) {
    let paginationElement = document.getElementById(elementID);
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setPage(${current_page-1}, '${logis}', '${elementID}')"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(current_page<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setPage(1, '${logis}', '${elementID}')">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="setPage(${current_page-1}, '${logis}', '${elementID}')">${current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(current_page!=1 && current_page != end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(current_page+2<end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="setPage(${current_page+1}, '${logis}', '${elementID}')">${current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(current_page+2<=end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(current_page>=end_page){
        endElement.innerHTML = `<a><strong>${end_page}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setPage(${end_page}, '${logis}', '${elementID}')">${end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(current_page>=end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setPage(${current_page+1}, '${logis}', '${elementID}')"><span uk-pagination-next></span></a>`;
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}

async function addLinkedItem(parent_id, child_id) {
    let conversion_factor = parseFloat(document.getElementById('conversion_factor').value)
    
    if(Number.isInteger(conversion_factor)){
        document.getElementById('conversion_factor').classList.remove('uk-form-danger')
        const response = await fetch(`/item/addLinkedItem`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                parent_id: parseInt(parent_id),
                child_id: parseInt(child_id),
                conv_factor: conversion_factor
            }),
        });
        data =  await response.json();
        response_status = 'primary'
        if (data.error){
            response_status = 'danger'
        }

        UIkit.notification({
            message: data.message,
            status: response_status,
            pos: 'top-right',
            timeout: 5000
        });

        document.getElementById('linked_item').value = ""
        document.getElementById('conversion_factor').value = ""
        document.getElementById('linked_item_id').value = ""
        document.getElementById('linkAdd').onclick = null

        await fetchItem()
        await setBasicInfo()
        await updateLinkedItemsTable()

    } else {
        document.getElementById('conversion_factor').classList.add('uk-form-danger')
    }
}

async function saveUpdated() {
    const response = await fetch(`/item/updateItem`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: parseInt(item_id),
            data: updated
        }),
    });

    data =  await response.json();
    response_status = 'success'
    if (data.error){
        response_status = 'danger'
    }

    UIkit.notification({
        message: data.message,
        status: response_status,
        pos: 'top-right',
        timeout: 5000
    });

    updated = {}
    await fetchItem()
    await setBasicInfo()
};

async function refreshSearchString() {
    const response = await fetch(`/item/refreshSearchString`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: parseInt(item.id)
        }),
    });

    data =  await response.json();
    response_status = 'success'
    if (data.error){
        response_status = 'danger'
    }

    UIkit.notification({
        message: data.message,
        status: response_status,
        pos: 'top-right',
        timeout: 5000
    });

    await fetchItem()
    await setBasicInfo()
};


async function descriptionChanged() {
    if (!updated.hasOwnProperty('item')){
        updated['item'] = {}
    }

    updated['item']['description'] = document.getElementById('itemDescription').value
}

async function nameChanged() {
    if (!updated.hasOwnProperty('item')){
        updated['item'] = {}
    }

    updated['item']['item_name'] = document.getElementById('itemName').value
}

async function selectChanged(logis) {
    if (!updated.hasOwnProperty('item')){
        updated['item'] = {}
    }
    if(logis=='row_type'){
        updated['item'][logis] = document.getElementById('itemTypeSelect').value
    }
    if(logis == 'item_type'){
        updated['item'][logis] = document.getElementById('itemSubTypeSelect').value
    }
}

async function itemInfoChanged(logis) {
    if (!updated.hasOwnProperty('item_info')){
        updated['item_info'] = {}
    }
    if (logis == 'safety_stock'){
        let value = document.getElementById('safetyStock').value
        updated['item_info']['safety_stock'] = parseFloat(value)
    }
    if (logis == 'lead_time_days'){
        let value = document.getElementById('leadTimeInDays').value
        updated['item_info']['lead_time_days'] = parseFloat(value)
    }
    if (logis == 'cost'){
        let value = document.getElementById('skuCost').value
        value = parseFloat(value.replace(/[^0-9.-]+/g,""));
        updated['item_info']['cost'] = value
    }
    if (logis == 'uom_quantity'){
        let value = document.getElementById('uom_quantity').value
        updated['item_info']['uom_quantity'] = value
    }
    if (logis == 'uom'){
        let value = document.getElementById('uom').value
        updated['item_info']['uom'] = value
    }
    if (logis == 'packaging'){
        let value = document.getElementById('packaging').value
        updated['item_info']['packaging'] = value
    }
    if (logis == 'ai_pick'){
        let value = document.getElementById('aiPickableCheckbox').checked
        console.log(value)
        updated['item_info']['ai_pick'] = value
    }
}

async function foodInfoChanged(logis) {
    if (!updated.hasOwnProperty('food_info')){
        updated['food_info'] = {}
    }
    if (logis === "expires"){
        let value = document.getElementById('expiresCheckbox').checked
        updated['food_info']['expires'] = value
    }
    if (logis === "default_expiration"){
        let value = document.getElementById('expirePeriod').value
        updated['food_info']['default_expiration'] = value
    }
}

async function setPrefixPage(pageNumber){
    current_page = pageNumber; 
    let data = await fetchPrefixes()
    end_page = data.end;
    await updatePrefixModalTableBody(data.prefixes)
    await updatePrefixPaginationElement()
}

async function updatePrefixPaginationElement() {
    let paginationElement = document.getElementById('prefixesModalPage');
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setPrefixPage(${current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(current_page<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setPrefixPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="setPrefixPage(${current_page-1})">${current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(current_page!=1 && current_page != end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(current_page+2<end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="setPrefixPage(${current_page+1})">${current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(current_page+2<=end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(current_page>=end_page){
        endElement.innerHTML = `<a><strong>${end_page}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setPrefixPage(${end_page})">${end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(current_page>=end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setPrefixPage(${current_page+1})"><span uk-pagination-next></span></a>`;
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}

// Possible Locations functions
var new_locations_current_page = 1
var new_locations_end_page = 1
var new_locations_limit = 25
async function fetch_new_locations() {
    const url = new URL('/item/getPossibleLocations', window.location.origin);
    url.searchParams.append('page', new_locations_current_page);
    url.searchParams.append('limit', new_locations_limit);
    const response = await fetch(url);
    data =  await response.json();
    new_locations_end_page = data.end;
    return data.locations
};

async function postNewItemLocation(location_id) {
    const response = await fetch(`/item/postNewItemLocation`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: parseInt(item_id),
            location_id: parseInt(location_id)
        }),
    });

    data =  await response.json();
    response_status = 'success'
    if (data.error){
        response_status = 'danger'
    }

    UIkit.notification({
        message: data.message,
        status: response_status,
        pos: 'top-right',
        timeout: 5000
    });
    await fetchItem()
    await updateLocationsTable()
}

async function replenishPossibleLocationsTableBody(locations){
    let NewLocationsModalTableBody = document.getElementById('NewLocationsModalTableBody')
    NewLocationsModalTableBody.innerHTML = ""

    for(let i =0; i <locations.length; i++){
        let tableRow = document.createElement('tr')

        let zoneCell = document.createElement('td')
        zoneCell.innerHTML = locations[i].zone.name

        let locationCell = document.createElement('td')
        locationCell.innerHTML = locations[i].name
        
        tableRow.onclick = async function() {
            await postNewItemLocation(locations[i].id)
        }

        tableRow.append(zoneCell, locationCell)
        NewLocationsModalTableBody.append(tableRow)
    }
}

async function openPossibleLocationsModal() {
    let locations = await fetch_new_locations()
    await replenishPossibleLocationsTableBody(locations)
    await updateNewLocationsPaginationElement()
    UIkit.modal(document.getElementById('NewLocationsModal')).show()
}


async function setNewLocationPage(pageNumber){
    new_locations_current_page = pageNumber; 
    let locations = await fetch_new_locations()
    await updatePrefixModalTableBody(locations)
    await updateNewLocationsPaginationElement()
}

async function updateNewLocationsPaginationElement() {
    let paginationElement = document.getElementById('NewLocationsModalPage');
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(new_locations_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setNewLocationPage(${new_locations_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(new_locations_current_page<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setNewLocationPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(new_locations_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(new_locations_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="setNewLocationPage(${new_locations_current_page-1})">${new_locations_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(new_locations_current_page!=1 && new_locations_current_page != new_locations_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${new_locations_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(new_locations_current_page+2<new_locations_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="setNewLocationPage(${new_locations_current_page+1})">${new_locations_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(new_locations_current_page+2<=new_locations_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(new_locations_current_page>=new_locations_end_page){
        endElement.innerHTML = `<a><strong>${new_locations_end_page}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setNewLocationPage(${new_locations_end_page})">${new_locations_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(new_locations_current_page>=new_locations_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setNewLocationPage(${new_locations_current_page+1})"><span uk-pagination-next></span></a>`;
    }
    paginationElement.append(nextElement)
}