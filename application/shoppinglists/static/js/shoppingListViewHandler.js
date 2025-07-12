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

    list_items = shopping_list.sl_items
    if(shopping_list.type == "calculated"){
        list_items = await fetchItemsFullCalculated()
    }

    await replenishLineTable(list_items)
})


async function replenishForm(shopping_list){
    document.getElementById('listName').innerHTML = shopping_list.name
    document.getElementById('listCreationDate').innerHTML = shopping_list.creation_date
    document.getElementById('listDescription').innerHTML = shopping_list.description
    
}

async function replenishLineTable(sl_items){
    let listItemsTableBody = document.getElementById('listItemsTableBody')
    listItemsTableBody.innerHTML = ""

    for(let i = 0; i < sl_items.length; i++){
        let tableRow = document.createElement('tr')

        let checkboxCell = document.createElement('td')
        checkboxCell.innerHTML = `<label><input class="uk-checkbox" type="checkbox"></label>`
        
        namefield = sl_items[i].item_name
        if(sl_items[i].links.hasOwnProperty('main')){
            namefield = `<a href=${sl_items[i].links.main} target='_blank'>${sl_items[i].item_name}</a>`
        }

        let nameCell = document.createElement('td')
        nameCell.innerHTML = namefield

        let qtyuomCell = document.createElement('td')
        qtyuomCell.innerHTML = `${sl_items[i].qty} ${sl_items[i].uom.fullname}`

        tableRow.append(checkboxCell, nameCell, qtyuomCell)
        listItemsTableBody.append(tableRow)
    }
}

async function fetchShoppingList() {
    const url = new URL('/shopping-lists/getList', window.location.origin);
    url.searchParams.append('id', sl_id);
    const response = await fetch(url);
    data =  await response.json();
    return data.shopping_list; 
}

async function fetchSLItem(sli_id) {
    const url = new URL('/shopping-lists/getListItem', window.location.origin);
    url.searchParams.append('sli_id', sli_id);
    const response = await fetch(url);
    data =  await response.json();
    return data.list_item; 
}

async function fetchItemsFullCalculated() {
    const url = new URL('/shopping-lists/getSKUItemsFull', window.location.origin);
    const response = await fetch(url);
    data =  await response.json();
    return data.list_items; 
}