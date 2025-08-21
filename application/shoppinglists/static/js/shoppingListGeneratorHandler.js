function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

document.addEventListener('DOMContentLoaded', async function() {
    await generateCustomItemsTable()
    await generateUncalculatedItemsTable()
    await generateCalculatedItemsTable()
});

var items_limit = 25
var item_current_page = 1
var item_end_page = 1
var item_search_string = ""

async function fetchItems(){
    const url = new URL('/shopping-lists/api/getItems', window.location.origin);
    url.searchParams.append('page', item_current_page);
    url.searchParams.append('limit', items_limit);
    url.searchParams.append('search_string', item_search_string);
    const response = await fetch(url);
    data =  await response.json();
    item_end_page = data.end
    return data.items; 
}

async function fetchCalculatedItems(){
    const url = new URL('/shopping-lists/api/getCalculatedItems', window.location.origin);
    url.searchParams.append('page', item_current_page);
    url.searchParams.append('limit', items_limit);
    url.searchParams.append('search_string', item_search_string);
    const response = await fetch(url);
    data =  await response.json();
    item_end_page = data.end
    return data.items; 
}

var recipes_limit = 25
var recipes_current_page = 1
var recipes_end_page = 1
var recipes_search_string = ""

async function fetchRecipes(){
    const url = new URL('/shopping-lists/api/getRecipesModal', window.location.origin);
    url.searchParams.append('page', recipes_current_page);
    url.searchParams.append('limit', recipes_limit);
    url.searchParams.append('search_string', recipes_search_string);
    const response = await fetch(url);
    data =  await response.json();
    recipes_end_page = data.end
    return data.recipes; 
}

var lists_limit = 25
var lists_current_page = 1
var lists_end_page = 1
var lists_search_string = ""

async function fetchLists(){
    const url = new URL('/shopping-lists/api/getListsModal', window.location.origin);
    url.searchParams.append('page', lists_current_page);
    url.searchParams.append('limit', lists_limit);
    url.searchParams.append('search_string', lists_search_string);
    const response = await fetch(url);
    data =  await response.json();
    lists_end_page = data.end
    return data.lists; 
}


// Custom Item Card Functions
var custom_items_card_active = false;
var custom_items = {};
async function addCustomItemsCard(){
    if(!custom_items_card_active){ 
        document.getElementById('customItemsCard').hidden = false
        custom_items_card_active = true;

    }
}

async function removeCustomItemsCard(){
    document.getElementById('customItemsCard').hidden = true
    custom_items_card_active = false;
    custom_items = {}
}

var customZoneState = true
async function changeCustomZoneState() {
    customZoneState = !customZoneState
    document.getElementById('customCardZone').hidden = !customZoneState
}

async function openCustomItemsModal(){
    document.getElementById('customName').value = ""
    document.getElementById('customQty').value = ""
    document.getElementById('customUnit').value = 1
    document.getElementById('customLink').value = ""
    document.getElementById('customItemModalButton').innerHTML = "Add"
    document.getElementById('customItemModalButton').onclick = async function () {await addCustomItem()}
    UIkit.modal(document.getElementById('CustomItemModal')).show()
}

async function addCustomItem() {
    let uuid = uuidv4();
    let customUnit = document.getElementById('customUnit')
    let selected_fullname = customUnit.options[customUnit.selectedIndex]
    custom_items[uuid] = {
        item_type: 'custom',
        item_name: document.getElementById('customName').value,
        uom: parseInt(document.getElementById('customUnit').value),
        qty: parseFloat(document.getElementById('customQty').value),
        link: document.getElementById('customLink').value,
        fullname: selected_fullname.dataset.fullname
    }
    UIkit.modal(document.getElementById('CustomItemModal')).hide()
    console.log(custom_items)
    await generateCustomItemsTable()
}

async function editCustomItem(customItemUUID) {
    let data = custom_items[customItemUUID]
    document.getElementById('customName').value = data['item_name']
    document.getElementById('customQty').value = data['qty']
    document.getElementById('customUnit').value = data['uom']
    document.getElementById('customLink').value = data['link']
    document.getElementById('customItemModalButton').innerHTML = "Save"
    document.getElementById('customItemModalButton').onclick = async function () {
        custom_items[customItemUUID] = {
            item_type: 'custom',
            item_name: document.getElementById('customName').value,
            uom: document.getElementById('customUnit').value,
            qty: parseFloat(document.getElementById('customQty').value),
            link: document.getElementById('customLink').value,
            fullname: data.fullname
        }
        await generateCustomItemsTable()
        UIkit.modal(document.getElementById('CustomItemModal')).hide()

    }
    UIkit.modal(document.getElementById('CustomItemModal')).show()
}

async function deleteCustomItem(customItemUUID) {
    delete custom_items[customItemUUID]
    await generateCustomItemsTable()
}

async function generateCustomItemsTable() {
    let customItemsTableBody = document.getElementById('customItemsTableBody')
    customItemsTableBody.innerHTML = ""

    for(const key in custom_items){
        if(custom_items.hasOwnProperty(key)){
            let tableRow = document.createElement('tr')


            let nameCell = document.createElement('td')
            nameCell.innerHTML = `${custom_items[key].item_name}`

            let qty_uomCell = document.createElement('td')
            qty_uomCell.innerHTML = `${custom_items[key].qty} ${custom_items[key].fullname}`

            let opCell = document.createElement('td')

            let editButton = document.createElement('button')
            editButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
            editButton.innerHTML = "Edit"
            editButton.setAttribute('uk-tooltip', 'Edit item information for this row.')

            editButton.onclick = async function() {await editCustomItem(key)}

            let removeButton = document.createElement('button')
            removeButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
            removeButton.setAttribute('uk-tooltip', 'Removes item from the saved custom items list.')
            removeButton.innerHTML = "Remove"
            removeButton.onclick = async function() {await deleteCustomItem(key)}


            opCell.append(editButton, removeButton)

            tableRow.append(nameCell, qty_uomCell, opCell)
            customItemsTableBody.append(tableRow)

        }
    }

}

// Uncalculated System Items Card
var uncalculated_items_card_active = false;
var uncalculated_items = {};
async function addUncalculatedItemsCard(){
    if(!uncalculated_items_card_active){ 
        document.getElementById('uncalcedItemsCard').hidden = false
        uncalculated_items_card_active = true;
    }
}

async function removeUncalcedItemsCard(){
    document.getElementById('uncalcedItemsCard').hidden = true
    uncalculated_items_card_active = false;
    uncalculated_items = {}
}

var uncalculatedZoneState = true
async function changeUncalculatedZoneState() {
    uncalculatedZoneState = !uncalculatedZoneState
    document.getElementById('uncalculatedCardZone').hidden = !uncalculatedZoneState
}

async function openUncalculatedItemsModal(){
    item_current_page = 1
    item_search_string = ""
    item_end_page = 1 
    let items = await fetchItems()
    console.log(items)
    await generateUncalculatedItemsModalTable(items)
    await updateUncalculatedItemsModalPagination()
    UIkit.modal(document.getElementById('uncalculatedItemModal')).show()
}

async function addUncalculatedItem(item_data, qtySRCid) {
    console.log(qtySRCid)
    let qty = parseFloat(document.getElementById(qtySRCid).value)

    let link = ""
    if(item_data.links.hasOwnProperty('main')){
        link = item_data.links.main
    }

    uncalculated_items[item_data.item_uuid] = {
        item_type: 'uncalculated sku',
        item_name: item_data.item_name,
        uom: item_data.unit_id,
        qty: qty,
        link: link,
        fullname: item_data.fullname
    }
    UIkit.modal(document.getElementById('uncalculatedItemModal')).hide()
    console.log(uncalculated_items)

    await generateUncalculatedItemsTable()
}

async function editUncalculatedItem(itemUUID) {
    let data = uncalculated_items[itemUUID]
    document.getElementById('uncalculatedItemName').value = data['item_name']
    document.getElementById('uncalculatedItemQty').value = data['qty']
    document.getElementById('uncalculatedItemUnit').value = data['uom']
    document.getElementById('uncalculatedItemLink').value = data['link']
    document.getElementById('uncalculatedItemModalEditButton').innerHTML = "Save"
    document.getElementById('uncalculatedItemModalEditButton').onclick = async function () {
        uncalculated_items[itemUUID] = {
            item_type: data.item_type,
            item_name: data.item_name,
            uom: data.uom,
            qty: parseFloat(document.getElementById('uncalculatedItemQty').value),
            link: document.getElementById('uncalculatedItemLink').value,
            fullname: data.fullname
        }
        await generateUncalculatedItemsTable()
        UIkit.modal(document.getElementById('uncalculatedItemModalEdit')).hide()

    }
    UIkit.modal(document.getElementById('uncalculatedItemModalEdit')).show()

}

async function deleteUncalculatedItem(itemUUID) {
    delete uncalculated_items[itemUUID]
    await generateUncalculatedItemsTable()
}

async function searchItemTable(event) {
    console.log(event)
    if(event.key==='Enter'){
        item_search_string = event.srcElement.value
        let items = await fetchItems()
        await generateUncalculatedItemsModalTable(items)
        await updateUncalculatedItemsModalPagination()
    }
}

async function setItemsPage(pageNumber){
    item_current_page = pageNumber;
    let items = await fetchItems()
    await generateUncalculatedItemsModalTable(items)
    await updateUncalculatedItemsModalPagination()
}

async function updateUncalculatedItemsModalPagination() {
    let paginationElement = document.getElementById('itemsPage');
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(item_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setItemsPage(${item_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(item_current_page<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setItemsPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(item_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(item_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="setItemsPage(${item_current_page-1})">${item_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(item_current_page!=1 && item_current_page != item_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${item_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(item_current_page+2<item_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="setItemsPage(${item_current_page+1})">${item_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(item_current_page+2<=item_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(item_current_page>=item_end_page){
        endElement.innerHTML = `<a><strong>${item_end_page}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setItemsPage(${item_end_page})">${item_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(item_current_page>=item_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setItemsPage(${item_current_page+1})"><span uk-pagination-next></span></a>`;
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}

async function generateUncalculatedItemsModalTable(items) {
    // used to fill out items modal... bad name bad
    let uncalculatedItemsModalTableBody = document.getElementById('uncalculatedItemsModalTableBody')
    uncalculatedItemsModalTableBody.innerHTML = ""

    for(let i = 0; i < items.length; i++){
        
        let tableRow = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${items[i].item_name}`

        let qtyCell = document.createElement('td')
        let qty_input_id = `${items[i].item_uuid}_qty`
        qtyCell.innerHTML = `<input id="${qty_input_id}" class="uk-input" type="number" value=1 aria-label="Quantity">`

        let uomCell = document.createElement('td')
        uomCell.innerHTML = `${items[i].fullname}`

        let opCell = document.createElement('td')

        let selectButton = document.createElement('button')
        selectButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
        selectButton.innerHTML = "Select"
        selectButton.setAttribute('uk-tooltip', 'Selects item to add to list, must have Qty set or assumes 1.')

        selectButton.onclick = async function() {
            await addUncalculatedItem(items[i], qty_input_id)
        }

        opCell.append(selectButton)

        tableRow.append(nameCell, qtyCell, uomCell, opCell)
        uncalculatedItemsModalTableBody.append(tableRow)
    }

}

async function generateUncalculatedItemsTable() {
    let uncalculatedItemsTableBody = document.getElementById('uncalculatedItemsTableBody')
    uncalculatedItemsTableBody.innerHTML = ""

    for(const key in uncalculated_items){
        if(uncalculated_items.hasOwnProperty(key)){
            let tableRow = document.createElement('tr')


            let nameCell = document.createElement('td')
            nameCell.innerHTML = `${uncalculated_items[key].item_name}`

            let qty_uomCell = document.createElement('td')
            qty_uomCell.innerHTML = `${uncalculated_items[key].qty} ${uncalculated_items[key].fullname}`

            let opCell = document.createElement('td')

            let editButton = document.createElement('button')
            editButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
            editButton.innerHTML = "Edit"
            editButton.setAttribute('uk-tooltip', 'Edit item information for this row.')

            editButton.onclick = async function() {await editUncalculatedItem(key)}

            let removeButton = document.createElement('button')
            removeButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
            removeButton.setAttribute('uk-tooltip', 'Removes item from the saved custom items list.')
            removeButton.innerHTML = "Remove"
            removeButton.onclick = async function() {await deleteUncalculatedItem(key)}


            opCell.append(editButton, removeButton)

            tableRow.append(nameCell, qty_uomCell, opCell)
            uncalculatedItemsTableBody.append(tableRow)

        }
    }

}

// Calculated System Item Functions
var calculated_items_card_active = false;
var calculated_items = {};
async function addCalculatedItemsCard(){
    if(!calculated_items_card_active && !full_sku_card_active){ 
        document.getElementById('calculatedItemsCard').hidden = false
        calculated_items_card_active = true;
    } else if (!calculated_items_card_active && full_sku_card_active){
        let prompt_text = `This will remove the Full Calculation Operator as both these 
        operators can not exist together. You will lose all configured items, are you sure you wish to proceed?`
        UIkit.modal.confirm(prompt_text).then(async function() {
            await removeFullSKUCard()
            document.getElementById('calculatedItemsCard').hidden = false
            calculated_items_card_active = true;
        }, async function() {
            document.getElementById('calculatedItemsCard').hidden = false
            calculated_items_card_active = true;
        });
    }
}

async function removeCalculatedItemsCard(){
    document.getElementById('calculatedItemsCard').hidden = true
    calculated_items_card_active = false;
    calculated_items = {}
}

var calculatedZoneState = true
async function changeCalculatedZoneState() {
    calculatedZoneState = !calculatedZoneState
    document.getElementById('calculatedCardZone').hidden = !calculatedZoneState
}

async function openCalculatedItemsModal(){
    item_current_page = 1
    item_search_string = ""
    item_end_page = 1 
    let items = await fetchCalculatedItems()
    await generateCalculatedItemsModalTable(items)
    await updateCalculatedItemsModalPagination()
    UIkit.modal(document.getElementById('calculatedItemModal')).show()
}

async function addCalculatedItem(item_data) {
    let link = ""
    if(item_data.links.hasOwnProperty('main')){
        link = item_data.links.main
    }

    calculated_items[item_data.item_uuid] = {
        item_type: 'calculated sku',
        item_name: item_data.item_name,
        uom: item_data.unit_id,
        qty: 0,
        link: link,
        fullname: item_data.fullname
    }
    UIkit.modal(document.getElementById('calculatedItemModal')).hide()
    console.log(calculated_items)

    await generateCalculatedItemsTable()
}

async function deleteCalculatedItem(itemUUID) {
    delete calculated_items[itemUUID]
    await generateCalculatedItemsTable()
}

async function searchCalculatedItemTable(event) {
    console.log(event)
    if(event.key==='Enter'){
        item_search_string = event.srcElement.value
        let items = await fetchItems()
        await generateCalculatedItemsModalTable(items)
        await updateCalculatedItemsModalPagination()
    }
}

async function setCalculatedItemsPage(pageNumber){
    item_current_page = pageNumber;
    let items = await fetchItems()
    await generateCalculatedItemsModalTable(items)
    await updateCalculatedItemsModalPagination()
}

async function updateCalculatedItemsModalPagination() {
    let paginationElement = document.getElementById('itemsCalculatedPage');
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(item_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setCalculatedItemsPage(${item_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(item_current_page<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setCalculatedItemsPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(item_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(item_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="setCalculatedItemsPage(${item_current_page-1})">${item_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(item_current_page!=1 && item_current_page != item_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${item_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(item_current_page+2<item_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="setCalculatedItemsPage(${item_current_page+1})">${item_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(item_current_page+2<=item_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(item_current_page>=item_end_page){
        endElement.innerHTML = `<a><strong>${item_end_page}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setCalculatedItemsPage(${item_end_page})">${item_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(item_current_page>=item_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setCalculatedItemsPage(${item_current_page+1})"><span uk-pagination-next></span></a>`;
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}

async function generateCalculatedItemsModalTable(items) {
    let calculatedItemsModalTableBody = document.getElementById('calculatedItemsModalTableBody')
    calculatedItemsModalTableBody.innerHTML = ""

    for(let i = 0; i < items.length; i++){
        
        let tableRow = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${items[i].item_name}`

        let opCell = document.createElement('td')

        let selectButton = document.createElement('button')
        selectButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
        selectButton.innerHTML = "Select"
        selectButton.setAttribute('uk-tooltip', 'Selects item to add to list, must have Qty set or assumes 1.')

        selectButton.onclick = async function() {
            await addCalculatedItem(items[i])
        }

        opCell.append(selectButton)

        tableRow.append(nameCell, opCell)
        calculatedItemsModalTableBody.append(tableRow)
    }

}

async function generateCalculatedItemsTable() {
    let calculatedItemsTableBody = document.getElementById('calculatedItemsTableBody')
    calculatedItemsTableBody.innerHTML = ""

    for(const key in calculated_items){
        if(calculated_items.hasOwnProperty(key)){
            let tableRow = document.createElement('tr')


            let nameCell = document.createElement('td')
            nameCell.innerHTML = `${calculated_items[key].item_name}`

            let opCell = document.createElement('td')

            let removeButton = document.createElement('button')
            removeButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
            removeButton.setAttribute('uk-tooltip', 'Removes item from the saved calculated systems items list.')
            removeButton.innerHTML = "Remove"
            removeButton.onclick = async function() {await deleteCalculatedItem(key)}

            opCell.append(removeButton)

            tableRow.append(nameCell, opCell)
            calculatedItemsTableBody.append(tableRow)

        }
    }

}

// Recipes Operator functions
var recipes_items_card_active = false;
var recipes = {};
async function addRecipesCard(){
    if(!recipes_items_card_active){ 
        document.getElementById('recipesCard').hidden = false
        recipes_items_card_active = true;
    }
}

async function removeRecipesItemsCard(){
    document.getElementById('recipesCard').hidden = true
    recipes_items_card_active = false;
    recipes = {}
}

var recipesZoneState = true
async function changeRecipesZoneState() {
    recipesZoneState = !recipesZoneState
    document.getElementById('recipesCardZone').hidden = !recipesZoneState
}

async function openRecipesModal(){
    let recipes = await fetchRecipes()
    await generateRecipesModalTable(recipes)
    await updateRecipesModalPagination()
    UIkit.modal(document.getElementById('recipesModal')).show()
}

async function addRecipe(recipe_data) {
    recipes[recipe_data.recipe_uuid] = recipe_data
    UIkit.modal(document.getElementById('recipesModal')).hide()
    console.log(recipes)
    await generateRecipesTable()
}

async function deleteRecipe(recipeUUID) {
    delete recipes[recipeUUID]
    await generateRecipesTable()
}

async function searchRecipesTable(event) {
    console.log(event)
    if(event.key==='Enter'){
        recipes_search_string = event.srcElement.value
        let recipes = await fetchRecipes()
        await generateRecipesModalTable(recipes)
        await updateRecipesModalPagination()
    }
}

async function setRecipesPage(pageNumber){
    recipes_current_page = pageNumber;
    let recipes = await fetchRecipes()
    await generateRecipesModalTable(recipes)
    await updateRecipesModalPagination()
}

async function updateRecipesModalPagination() {
    let paginationElement = document.getElementById('recipesPage');
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(recipes_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setRecipesPage(${recipes_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(recipes_current_page<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setRecipesPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(recipes_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(recipes_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="setRecipesPage(${recipes_current_page-1})">${recipes_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(recipes_current_page!=1 && recipes_current_page != recipes_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${recipes_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(recipes_current_page+2<recipes_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="setRecipesPage(${recipes_current_page+1})">${recipes_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(recipes_current_page+2<=recipes_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(recipes_current_page>=recipes_end_page){
        endElement.innerHTML = `<a><strong>${recipes_end_page}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setRecipesPage(${recipes_end_page})">${recipes_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(recipes_current_page>=recipes_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setRecipesPage(${recipes_current_page+1})"><span uk-pagination-next></span></a>`;
    }
    paginationElement.append(nextElement)
}

async function generateRecipesModalTable(recipes) {
    let recipesModalTableBody = document.getElementById('recipesModalTableBody')
    recipesModalTableBody.innerHTML = ""

    for(let i = 0; i < recipes.length; i++){
        
        let tableRow = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${recipes[i].name}`

        let opCell = document.createElement('td')

        let selectButton = document.createElement('button')
        selectButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
        selectButton.innerHTML = "Select"
        selectButton.setAttribute('uk-tooltip', 'Selects Recipe to add to list.')

        selectButton.onclick = async function() {
            await addRecipe(recipes[i])
        }

        opCell.append(selectButton)

        tableRow.append(nameCell, opCell)
        recipesModalTableBody.append(tableRow)
    }

}

async function generateRecipesTable() {
    let recipesTableBody = document.getElementById('recipesTableBody')
    recipesTableBody.innerHTML = ""

    for(const key in recipes){
        if(recipes.hasOwnProperty(key)){
            let tableRow = document.createElement('tr')


            let nameCell = document.createElement('td')
            nameCell.innerHTML = `${recipes[key].name}`

            let opCell = document.createElement('td')

            let removeButton = document.createElement('button')
            removeButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
            removeButton.setAttribute('uk-tooltip', 'Removes Recipe from the saved receipes')
            removeButton.innerHTML = "Remove"
            removeButton.onclick = async function() {await deleteRecipe(recipes[key].recipe_uuid)}

            opCell.append(removeButton)

            tableRow.append(nameCell, opCell)
            recipesTableBody.append(tableRow)

        }
    }

}

// Full SKU Calcuation Functions
var full_sku_card_active = false;
var full_sku_enabled = false;
async function addFullSKUCard(){
    if(!full_sku_card_active){ 
        document.getElementById('fullSKUCard').hidden = false
        full_sku_card_active = true;
        full_sku_enabled = false;
        document.getElementById('fullSKUCheckbox').checked = false
    }
}

async function removeFullSKUCard(){
    document.getElementById('fullSKUCard').hidden = true
    full_sku_card_active = false;
    full_sku_enabled = false;
    document.getElementById('fullSKUCheckbox').checked = false
}


async function fullSKUEnabledChange(event){
    if(calculated_items_card_active){
        let prompt_text = `This will remove the calculated system item operator as both these 
        operators can not exist together. You will lose all configured itesm, are you sure you wish to proceed?`
        UIkit.modal.confirm(prompt_text).then(async function() {
            await removeCalculatedItemsCard()
            full_sku_enabled = true;
            event.target.checked = full_sku_enabled;
            console.log(calculated_items)
        }, async function() {
            full_sku_enabled = false;
            event.target.checked = full_sku_enabled;
        });
    } else {
        full_sku_enabled = event.target.checked
    }  
}

// Shopping Lists functions
var lists_card_active = false;
var shopping_lists = {};
async function addListsCard(){
    if(!lists_card_active){ 
        document.getElementById('listsCard').hidden = false
        lists_card_active = true;
    }
}

async function removeListsItemsCard(){
    document.getElementById('listsCard').hidden = true
    lists_card_active = false;
    shopping_lists = {}
}

var ListsZoneState = true
async function changeListsZoneState() {
    ListsZoneState = !ListsZoneState
    document.getElementById('listsCardZone').hidden = !ListsZoneState
}

async function openListsModal(){
    let lists = await fetchLists()
    await generateListsModalTable(lists)
    await updateListsModalPagination()
    UIkit.modal(document.getElementById('listsModal')).show()
}

async function addList(list_data) {
    shopping_lists[list_data.list_uuid] = list_data
    UIkit.modal(document.getElementById('listsModal')).hide()
    console.log(shopping_lists)
    await generateListsTable()
}

async function deleteList(listUUID) {
    delete shopping_lists[listUUID]
    await generateListsTable()
}

async function searchListsTable(event) {
    console.log(event)
    if(event.key==='Enter'){
        lists_search_string = event.srcElement.value
        let lists = await fetchLists()
        await generateListsModalTable(lists)
        await updateListsModalPagination()
    }
}

async function setListsPage(pageNumber){
    lists_current_page = pageNumber;
    let lists = await fetchLists()
    await generateListsModalTable(lists)
    await updateListsModalPagination()
}

async function updateListsModalPagination() {
    let paginationElement = document.getElementById('listsPage');
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(lists_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setListsPage(${lists_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(lists_current_page<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setListsPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(lists_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(lists_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="setListsPage(${lists_current_page-1})">${lists_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(lists_current_page!=1 && lists_current_page != lists_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${lists_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(lists_current_page+2<lists_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="setListsPage(${lists_current_page+1})">${lists_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(lists_current_page+2<=lists_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(lists_current_page>=lists_end_page){
        endElement.innerHTML = `<a><strong>${lists_end_page}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setListsPage(${lists_end_page})">${lists_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(lists_current_page>=lists_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setListsPage(${lists_current_page+1})"><span uk-pagination-next></span></a>`;
    }
    paginationElement.append(nextElement)
}

async function generateListsModalTable(lists) {
    let listsModalTableBody = document.getElementById('listsModalTableBody')
    listsModalTableBody.innerHTML = ""

    for(let i = 0; i < lists.length; i++){
        
        let tableRow = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${lists[i].name}`

        let opCell = document.createElement('td')

        let selectButton = document.createElement('button')
        selectButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
        selectButton.innerHTML = "Select"
        selectButton.setAttribute('uk-tooltip', 'Selects Shopping List to add to list.')

        selectButton.onclick = async function() {
            await addList(lists[i])
        }

        opCell.append(selectButton)

        tableRow.append(nameCell, opCell)
        listsModalTableBody.append(tableRow)
    }

}

async function generateListsTable() {
    let listsTableBody = document.getElementById('listsTableBody')
    listsTableBody.innerHTML = ""

    for(const key in shopping_lists){
        if(shopping_lists.hasOwnProperty(key)){
            let tableRow = document.createElement('tr')


            let nameCell = document.createElement('td')
            nameCell.innerHTML = `${shopping_lists[key].name}`

            let opCell = document.createElement('td')

            let removeButton = document.createElement('button')
            removeButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
            removeButton.setAttribute('uk-tooltip', 'Removes Shopping List from the saved shopping lists')
            removeButton.innerHTML = "Remove"
            removeButton.onclick = async function() {await deleteList(shopping_lists[key].list_uuid)}

            opCell.append(removeButton)

            tableRow.append(nameCell, opCell)
            listsTableBody.append(tableRow)

        }
    }

}

// Site Planner Functions
var site_planners = {}
var site_planner_card_active = false;
async function addPlannerCard(){
    if(!site_planner_card_active){ 
        document.getElementById('plannerCard').hidden = false
        site_planner_card_active = true;
    }
}

async function removePlannerCard(){
    document.getElementById('plannerCard').hidden = true
    site_planner_card_active = false;
    site_planners = []
}

var PlannerZoneState = true
async function changePlannerZoneState() {
    PlannerZoneState = !PlannerZoneState
    document.getElementById('plannerZone').hidden = !PlannerZoneState
}

async function openPlannerModal(){
    document.getElementById('planUUID').setAttribute('class', 'uk-input uk-disabled')
    document.getElementById('planUUID').value = 'site'
    document.getElementById('planStartDate').value = ''
    document.getElementById('planEndDate').value = ''
    document.getElementById('plannerModalButton').innerHTML = "Save"
    document.getElementById('plannerModalButton').onclick = async function () { await addPlanner()}
    UIkit.modal(document.getElementById('plannerModal')).show()
}

async function addPlanner() {
    var planner_select = document.getElementById('planUUID')
    planner_uuid = planner_select.value
    plan_name = planner_select.options[planner_select.selectedIndex].text
    startDate = document.getElementById('planStartDate').value
    endDate = document.getElementById('planEndDate').value
    site_planners[planner_uuid] = {
        start_date: startDate,
        end_date: endDate,
        plan_uuid: planner_uuid,
        plan_name: plan_name
    }
    UIkit.modal(document.getElementById('plannerModal')).hide()
    console.log(site_planners)
    await generatePlannerTable()
}

async function editPlanner(planUUID) {
    let data = site_planners[planUUID]
    document.getElementById('planUUID').setAttribute('class', 'uk-input uk-disabled')
    document.getElementById('planUUID').value = data['plan_uuid']
    document.getElementById('planStartDate').value = data['start_date']
    document.getElementById('planEndDate').value = data['end_date']
    document.getElementById('plannerModalButton').innerHTML = "Save"
    document.getElementById('plannerModalButton').onclick = async function () {
            var planner_select = document.getElementById('planUUID')
            planner_uuid = planner_select.value
            plan_name = planner_select.options[planner_select.selectedIndex].text
            startDate = document.getElementById('planStartDate').value
            endDate = document.getElementById('planEndDate').value
            site_planners[planner_uuid] = {
                start_date: startDate,
                end_date: endDate,
                plan_uuid: planner_uuid,
                plan_name: plan_name
            }
        
            await generatePlannerTable()
            UIkit.modal(document.getElementById('plannerModal')).hide()
        }
    
    UIkit.modal(document.getElementById('plannerModal')).show()
}


async function deletePlan(plannerUUID) {
    delete site_planners[plannerUUID]
    await generatePlannerTable()
}

async function generatePlannerTable() {
    let plannerTableBody = document.getElementById('plannerTableBody')
    plannerTableBody.innerHTML = ""

    for(const key in site_planners){
        if(site_planners.hasOwnProperty(key)){
            let tableRow = document.createElement('tr')


            let nameCell = document.createElement('td')
            nameCell.innerHTML = `${site_planners[key].plan_name}`

            let startCell = document.createElement('td')
            startCell.innerHTML = `${site_planners[key].start_date}`

            let endCell = document.createElement('td')
            endCell.innerHTML = `${site_planners[key].end_date}`

            let opCell = document.createElement('td')

            let editButton = document.createElement('button')
            editButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
            editButton.setAttribute('uk-tooltip', 'Edits this rows plan dates.')
            editButton.innerHTML = "Edit"
            editButton.onclick = async function() {await editPlanner(site_planners[key].plan_uuid)}


            let removeButton = document.createElement('button')
            removeButton.setAttribute('class', 'uk-button uk-button-default uk-button-small')
            removeButton.setAttribute('uk-tooltip', 'Removes Shopping List from the saved shopping lists')
            removeButton.innerHTML = "Remove"
            removeButton.onclick = async function() {await deletePlan(site_planners[key].plan_uuid)}

            opCell.append(editButton, removeButton)

            tableRow.append(nameCell, startCell, endCell, opCell)
            plannerTableBody.append(tableRow)

        }
    }

}

// Generate Functions
async function postGenerateList() {
    let data = {
        list_type: String(document.getElementById('generated_list_type').value),
        list_name: String(document.getElementById('generated_list_name').value),
        list_description: String(document.getElementById('generated_list_description').value),
        custom_items: Object.values(custom_items),
        uncalculated_items: Object.values(uncalculated_items),
        calculated_items: Object.keys(calculated_items),
        recipes: Object.keys(recipes),
        full_system_calculated: full_sku_enabled,
        shopping_lists: Object.keys(shopping_lists),
        site_plans: Object.values(site_planners)
    }

    const response = await fetch(`/shopping-lists/api/postGeneratedList`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    location.href = "/shopping-lists"
}