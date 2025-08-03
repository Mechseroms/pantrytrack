var mode = false
async function toggleDarkMode() {
    let darkMode = document.getElementById("dark-mode");    
    darkMode.disabled = !darkMode.disabled;
    mode = !mode;
    if(mode){
        document.getElementById('modeToggle').innerHTML = "light_mode"
        document.getElementById('main_html').classList.add('uk-light')
    } else {
        document.getElementById('modeToggle').innerHTML = "dark_mode"
        document.getElementById('main_html').classList.remove('uk-light')

    }
}

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
    document.getElementById('list_type').value = shopping_list.type

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
        uuidCell.innerHTML = sl_items[i].uuid

        let nameCell = document.createElement('td')
        nameCell.innerHTML = sl_items[i].item_name

        let opCell = document.createElement('td')

        let editOp = document.createElement('a')
        editOp.setAttribute('class', 'uk-button uk-button-default uk-button-small')
        editOp.innerHTML = `<span uk-icon="icon: pencil"></span>`
        editOp.style = 'margin-right: 5px;'
        editOp.onclick = async function () {
            await openLineEditModal(sl_items[i].id)
        }

        let deleteOp = document.createElement('a')
        deleteOp.setAttribute('class', 'uk-button uk-button-default uk-button-small')
        deleteOp.innerHTML = `<span uk-icon="icon: trash"></span>`
        deleteOp.onclick = async function () {
            await deleteLineItem(sl_items[i].id)
        }

        opCell.append(editOp, deleteOp)

        tableRow.append(typeCell, uuidCell, nameCell, opCell)
        listItemsTableBody.append(tableRow)
    }
}

async function fetchShoppingList() {
    const url = new URL('/shopping-lists/api/getList', window.location.origin);
    url.searchParams.append('id', sl_id);
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

        let idCell = document.createElement('td')
        idCell.innerHTML = `${items[i].id}`

        let barcodeCell = document.createElement('td')
        barcodeCell.innerHTML = `${items[i].barcode}`

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${items[i].item_name}`

        tableRow.id = items[i].id
        tableRow.onclick = async function(){

            let newItem = {
                uuid: items[i].barcode,
                sl_id: sl_id,
                item_type: 'sku',
                item_name: items[i].item_name,
                uom: items[i].item_info.uom,
                qty: items[i].item_info.uom_quantity,
                item_id:  items[i].id,
                links: {'main': items[i].links['main']}
            }

            await submitItemToList(newItem)
            let shopping_list = await fetchShoppingList()
            await replenishForm(shopping_list)
            await replenishLineTable(shopping_list.sl_items)
            let itemsModal = document.getElementById('itemsModal')
            UIkit.modal(itemsModal).hide();

        }
        tableRow.append(idCell, barcodeCell, nameCell)
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

async function openLineEditModal(sli_id) {
    let sl_item = await fetchSLItem(sli_id)
    console.log(sl_item)
    document.getElementById('lineName').value = sl_item.item_name
    document.getElementById('lineQty').value = sl_item.qty
    document.getElementById('lineUOM').value = sl_item.uom.id
    console.log(sl_item.links)
    
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
        await saveLineItem(sl_item.id, update)
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

async function fetchSLItem(sli_id) {
    const url = new URL('/shopping-lists/api/getListItem', window.location.origin);
    url.searchParams.append('sli_id', sli_id);
    const response = await fetch(url);
    data =  await response.json();
    return data.list_item; 
}

async function addCustomItem() {
    let customModal = document.getElementById('customModal')
    UIkit.modal(customModal).hide();

    uuid = `${sl_id}${Math.random().toString(36).substring(2, 8)}`

    let newItem = {
        uuid: uuid,
        sl_id: sl_id,
        item_type: 'custom',
        item_name: document.getElementById('customName').value,
        uom: document.getElementById('customUOM').value,
        qty: parseFloat(document.getElementById('customQty').value),
        item_id:  null,
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

async function saveLineItem(sli_id, update) {
    const response = await fetch(`/shopping-lists/api/saveListItem`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sli_id: sli_id,
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