document.addEventListener('DOMContentLoaded', async function() {
    let shopping_list = await fetchShoppingList()
    await replenishForm(shopping_list)

    list_items = shopping_list.sl_items
    if(shopping_list.sub_type == "calculated"){
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
    console.log(sl_items)

    let grouped = sl_items.reduce((accumen, item) => {
        if (!accumen[item.item_type]) {
            accumen[item.item_type] = [];
        }
        accumen[item.item_type].push(item);
        return accumen;
        }, {});
    
    console.log(grouped)
    for(let key in grouped){
        console.log(key)
        let items = grouped[key]
        let headerRow = document.createElement('tr')
        let headerCell = document.createElement('td')
        headerCell.colSpan = 3;
        headerCell.textContent = key.toUpperCase();
        headerCell.className = 'type-header';
        headerCell.style = `font-weight: bold;background: #eee; text-align: left;`
        headerRow.appendChild(headerCell);
        listItemsTableBody.appendChild(headerRow);

        for(let i = 0; i < items.length; i++){
            console.log(items)
            let tableRow = document.createElement('tr')
            let item = items[i]
            let checkboxCell = document.createElement('td')
            checkboxCell.innerHTML = `<label><input class="uk-checkbox" type="checkbox" ${item.list_item_state ? 'checked' : ''}></label>`
            checkboxCell.onclick = async function (event) {
                console.log(item)
                await updateListItemState(item.list_item_uuid, event.target.checked)
            }

            namefield = items[i].item_name
            if(items[i].links.hasOwnProperty('main')){
                namefield = `<a href=${item.links.main} target='_blank'>${item.item_name}</a>`
            }

            let nameCell = document.createElement('td')
            nameCell.innerHTML = namefield

            let qtyuomCell = document.createElement('td')
            qtyuomCell.innerHTML = `${item.qty} ${item.uom.fullname}`

            checkboxCell.checked = item.list_item_state
            tableRow.append(checkboxCell, nameCell, qtyuomCell)
            listItemsTableBody.append(tableRow)
        }

    }
}

async function fetchShoppingList() {
    const url = new URL('/shopping-lists/api/getList', window.location.origin);
    url.searchParams.append('list_uuid', list_uuid);
    const response = await fetch(url);
    data =  await response.json();
    return data.shopping_list; 
}

async function fetchSLItem(sli_id) {
    const url = new URL('/shopping-lists/api/getListItem', window.location.origin);
    url.searchParams.append('sli_id', sli_id);
    const response = await fetch(url);
    data =  await response.json();
    return data.list_item; 
}

async function fetchItemsFullCalculated() {
    const url = new URL('/shopping-lists/api/getSKUItemsFull', window.location.origin);
    const response = await fetch(url);
    data =  await response.json();
    return data.list_items; 
}

async function updateListItemState(list_item_uuid, state){
    console.log(list_item_uuid, state)
    const response = await fetch(`/shopping-lists/api/setListItemState`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            list_item_uuid: list_item_uuid,
            list_item_state: state
        }),
    });
}