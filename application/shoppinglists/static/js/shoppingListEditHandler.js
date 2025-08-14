document.addEventListener('DOMContentLoaded', async function() {
    let shopping_list = await fetchShoppingList()
    await replenishForm(shopping_list)
    await replenishLineTable(shopping_list.sl_items)
})


async function replenishForm(shopping_list){
    document.getElementById('list_name').value = shopping_list.name
    document.getElementById('list_creation_date').value = shopping_list.creation_date
    document.getElementById('list_description').value = shopping_list.description
    document.getElementById('list_author').value = shopping_list.author
    document.getElementById('list_type').value = shopping_list.sub_type

    if(shopping_list.type == "calculated"){
        document.getElementById('addLineButton').classList.add("uk-disabled")
    } else {
        document.getElementById('addLineButton').classList.remove("uk-disabled")
    }

    if(shopping_list.type == "plain"){
        document.getElementById('lineCalc').classList.add("uk-disabled")
        document.getElementById('lineUOM').classList.add("uk-disabled")
        document.getElementById('lineName').classList.add("uk-disabled")
    } else {
        document.getElementById('lineCalc').classList.remove("uk-disabled")
        document.getElementById('lineUOM').classList.remove("uk-disabled")
        document.getElementById('lineName').classList.remove("uk-disabled")
    }

    

}

async function replenishLineTable(sl_items){
    let listItemsTableBody = document.getElementById('listItemsTableBody')
    listItemsTableBody.innerHTML = ""

    for(let i = 0; i < sl_items.length; i++){
        let tableRow = document.createElement('tr')

        let typeCell = document.createElement('td')
        typeCell.innerHTML = sl_items[i].item_type

        let uuidCell = document.createElement('td')
        uuidCell.innerHTML = sl_items[i].list_item_uuid

        let nameCell = document.createElement('td')
        nameCell.innerHTML = sl_items[i].item_name

        let opCell = document.createElement('td')

        let editOp = document.createElement('a')
        editOp.setAttribute('class', 'uk-button uk-button-default uk-button-small')
        editOp.innerHTML = `<span uk-icon="icon: pencil"></span>`
        editOp.style = 'margin-right: 5px;'
        editOp.onclick = async function () {
            await openLineEditModal(sl_items[i].list_item_uuid)
        }

        let deleteOp = document.createElement('a')
        deleteOp.setAttribute('class', 'uk-button uk-button-default uk-button-small')
        deleteOp.innerHTML = `<span uk-icon="icon: trash"></span>`
        deleteOp.onclick = async function () {
            await deleteLineItem(sl_items[i].list_item_uuid)
        }

        opCell.append(editOp, deleteOp)

        tableRow.append(typeCell, uuidCell, nameCell, opCell)
        listItemsTableBody.append(tableRow)
    }
}

async function fetchShoppingList() {
    const url = new URL('/shopping-lists/api/getList', window.location.origin);
    url.searchParams.append('list_uuid', list_uuid);
    const response = await fetch(url);
    data =  await response.json();
    return data.shopping_list; 
}

var pagination_current = 1;
var pagination_end = 1;
var search_string = ""

async function updateItemsModalTable(items) {
    let itemsTableBody = document.getElementById('itemsTableBody');
    itemsTableBody.innerHTML = "";
    
    for(let i=0; i < items.length; i++){
        let tableRow = document.createElement('tr')


        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${items[i].item_name}`

        let opCell = document.createElement('td')

        let selectButton = document.createElement('button')
        selectButton.innerHTML = "Select"
        selectButton.setAttribute('class', 'uk-button uk-button-primary uk-button-small')

        selectButton.onclick = async function(){

            let newItem = {
                list_uuid: list_uuid,
                item_type: 'sku',
                item_name: items[i].item_name,
                uom: items[i].item_info.uom,
                qty: items[i].item_info.uom_quantity,
                item_uuid:  items[i].item_uuid,
                links: {'main': items[i].links['main']}
            }

            await submitItemToList(newItem)
            let shopping_list = await fetchShoppingList()
            await replenishForm(shopping_list)
            await replenishLineTable(shopping_list.sl_items)
            let itemsModal = document.getElementById('itemsModal')
            UIkit.modal(itemsModal).hide();

        }

        opCell.append(selectButton)
        tableRow.append(nameCell, opCell)
        itemsTableBody.append(tableRow)
    }
}

async function openSKUModal() {
    let itemsModal = document.getElementById('itemsModal')
    let items = await fetchItems()
    pagination_current = 1;
    search_string = '';
    document.getElementById('searchItemsInput').value = '';
    await updateItemsModalTable(items)
    await updateItemsPaginationElement()
    UIkit.modal(itemsModal).show();
}

async function openLineEditModal(list_item_uuid) {
    let sl_item = await fetchSLItem(list_item_uuid)
    document.getElementById('lineName').value = sl_item.item_name
    document.getElementById('lineQty').value = sl_item.qty
    document.getElementById('lineUOM').value = sl_item.uom.id
    
    if(!sl_item.links.hasOwnProperty('main')){
        sl_item.links.main = ''
    }

    document.getElementById('lineLink').value = sl_item.links.main

    document.getElementById('saveLineButton').onclick = async function () {
        links = sl_item.links
        links.main = document.getElementById('lineLink').value
        update = {
            item_name: document.getElementById('lineName').value,
            qty: document.getElementById('lineQty').value,
            uom: document.getElementById('lineUOM').value,
            links: links
        }
        await saveLineItem(sl_item.list_item_uuid, update)
        UIkit.modal(document.getElementById('lineEditModal')).hide();    
    }
    UIkit.modal(document.getElementById('lineEditModal')).show();

}

async function searchItemTable(event) {
    if(event.key==='Enter'){
        search_string = event.srcElement.value
        let items = await fetchItems()
        await updateItemsModalTable(items)
        await updateItemsPaginationElement()
    }
}

async function setItemsPage(pageNumber){
    pagination_current = pageNumber;
    let items = await fetchItems()
    await updateItemsModalTable(items)
    await updateItemsPaginationElement()
}

async function updateItemsPaginationElement() {
    let paginationElement = document.getElementById('itemsPage');
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(pagination_current<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setItemsPage(${pagination_current-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(pagination_current<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setItemsPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(pagination_current-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(pagination_current-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="setItemsPage(${pagination_current-1})">${pagination_current-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(pagination_current!=1 && pagination_current != pagination_end){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${pagination_current}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(pagination_current+2<pagination_end+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="setItemsPage(${pagination_current+1})">${pagination_current+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(pagination_current+2<=pagination_end){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(pagination_current>=pagination_end){
        endElement.innerHTML = `<a><strong>${pagination_end}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setItemsPage(${pagination_end})">${pagination_end}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(pagination_current>=pagination_end){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setItemsPage(${pagination_current+1})"><span uk-pagination-next></span></a>`;
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}

let items_limit = 25;
async function fetchItems() {
    const url = new URL('/shopping-lists/api/getItems', window.location.origin);
    url.searchParams.append('page', pagination_current);
    url.searchParams.append('limit', items_limit);
    url.searchParams.append('search_string', search_string);
    const response = await fetch(url);
    data =  await response.json();
    pagination_end = data.end
    return data.items; 
}

async function fetchSLItem(list_item_uuid) {
    console.log(list_item_uuid)
    const url = new URL('/shopping-lists/api/getListItem', window.location.origin);
    url.searchParams.append('list_item_uuid', list_item_uuid);
    const response = await fetch(url);
    data =  await response.json();
    return data.list_item; 
}

async function addCustomItem() {
    let customModal = document.getElementById('customModal')
    UIkit.modal(customModal).hide();


    let newItem = {
        list_uuid: list_uuid,
        item_type: 'custom',
        item_name: document.getElementById('customName').value,
        uom: document.getElementById('customUOM').value,
        qty: parseFloat(document.getElementById('customQty').value),
        item_uuid:  null,
        links: {'main': document.getElementById('customLink').value}
    }

    await submitItemToList(newItem)

    let shopping_list = await fetchShoppingList()
    await replenishForm(shopping_list)
    await replenishLineTable(shopping_list.sl_items)
}

async function submitItemToList(newItem) {
    const response = await fetch(`/shopping-lists/api/postListItem`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            data: newItem
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
}

async function deleteLineItem(sli_id) {
    const response = await fetch(`/shopping-lists/api/deleteListItem`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sli_id: sli_id
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

    let shopping_list = await fetchShoppingList()
    await replenishForm(shopping_list)
    await replenishLineTable(shopping_list.sl_items)
}

async function saveLineItem(list_item_uuid, update) {
    const response = await fetch(`/shopping-lists/api/saveListItem`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            list_item_uuid: list_item_uuid,
            update: update
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

    let shopping_list = await fetchShoppingList()
    await replenishForm(shopping_list)
    await replenishLineTable(shopping_list.sl_items)
}


// Recipes Modal and Functions
var recipes_pagination_current = 1;
var recipes_pagination_end = 1;
var recipes_search_string = ""
let recipes_limit = 25;


async function updateRecipesModalTable(recipes) {
    let receipesTableBody = document.getElementById('receipesTableBody');
    receipesTableBody.innerHTML = "";
    
    for(let i=0; i < recipes.length; i++){
        let tableRow = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${recipes[i].name}`

        let opCell = document.createElement('td')

        let selectButton = document.createElement('button')
        selectButton.innerHTML = "Select"
        selectButton.setAttribute('class', 'uk-button uk-button-primary uk-button-small')

        selectButton.onclick = async function(){
            await addRecipeLine(recipes[i].recipe_uuid)
        }   

        opCell.append(selectButton)
        tableRow.append(nameCell, opCell)
        receipesTableBody.append(tableRow)
    }
}

async function openRecipesModal() {
    let recipesModal = document.getElementById('recipesModal')
    let recipes = await fetchRecipes()
    recipes_pagination_current = 1;
    recipes_search_string = '';
    document.getElementById('searchRecipesInput').value = '';
    await updateRecipesModalTable(recipes)
    await updateRecipesPaginationElement()
    UIkit.modal(recipesModal).show();
}

async function searchRecipesTable(event) {
    if(event.key==='Enter'){
        recipes_search_string = event.srcElement.value
        let recipes = await fetchRecipes()
        await updateRecipesModalTable(recipes)
        await updateRecipesPaginationElement()
    }
}

async function setRecipesPage(pageNumber){
    recipes_pagination_current = pageNumber;
    let recipes = await fetchRecipes()
    await updateRecipesModalTable(recipes)
    await updateRecipesPaginationElement()
}

async function updateRecipesPaginationElement() {
    let paginationElement = document.getElementById('recipesPage');
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(recipes_pagination_current<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setRecipesPage(${recipes_pagination_current-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(recipes_pagination_current<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setRecipesPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(recipes_pagination_current-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(recipes_pagination_current-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="setRecipesPage(${recipes_pagination_current-1})">${recipes_pagination_current-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(recipes_pagination_current!=1 && recipes_pagination_current != recipes_pagination_end){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${recipes_pagination_current}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(recipes_pagination_current+2<recipes_pagination_end+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="setRecipesPage(${recipes_pagination_current+1})">${recipes_pagination_current+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(recipes_pagination_current+2<=recipes_pagination_end){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(recipes_pagination_current>=recipes_pagination_end){
        endElement.innerHTML = `<a><strong>${recipes_pagination_end}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setRecipesPage(${recipes_pagination_end})">${recipes_pagination_end}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(recipes_pagination_current>=recipes_pagination_end){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setRecipesPage(${recipes_pagination_current+1})"><span uk-pagination-next></span></a>`;
    }
    paginationElement.append(nextElement)
}

async function fetchRecipes() {
    const url = new URL('/shopping-lists/api/getRecipesModal', window.location.origin);
    url.searchParams.append('page', recipes_pagination_current);
    url.searchParams.append('limit', recipes_limit);
    url.searchParams.append('search_string', recipes_search_string);
    const response = await fetch(url);
    data =  await response.json();
    recipes_pagination_end = data.end
    return data.recipes; 
}

async function addRecipeLine(recipe_uuid){
    const response = await fetch(`/shopping-lists/api/postRecipeLine`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            recipe_uuid: recipe_uuid,
            list_uuid: list_uuid
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

}