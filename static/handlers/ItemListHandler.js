var current_page = 1;
var limit = 50;
var searchText = "";
var sort_order = "";
var view = "";
var items;
var end_page = 10
var settingsState = false;

var item_subtypes = [['Food', 'FOOD'], ['Food PLU', 'FOOD_PLU'], ['Other', 'OTHER'], ['Medicinal', 'MEDICINE'], ['Hygenic', 'HYGENIC']];

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

if(session.user.flags.darkmode){
    toggleDarkMode()
}

var detailedList = false
async function setViewMode() {
    detailedList = !detailedList;
    let toggle = document.getElementById('view_mode_toggle')
    if(detailedList){
        toggle.innerHTML = `Table <span uk-icon="icon: table"></span>`
    } else {
        toggle.innerHTML = `Cards <span uk-icon="icon: thumbnails"></span>`
    }
    await reloadCards()
}

document.addEventListener('DOMContentLoaded', async function() {
    await getItems()
    await setupFormDefaults()
    await reloadCards()
});

async function setupFormDefaults() {
    let subtype_select = document.getElementById('subtype_select')
    for(let i=0; i<item_subtypes.length; i++){
        let elem = document.createElement('option')
        elem.innerHTML = `${item_subtypes[i][0]}`
        elem.value = `${item_subtypes[i][1]}`
        subtype_select.append(elem)
    }
}

async function searchItems(event){
    event.preventDefault();
    searchInput = document.getElementById('searchInput')
    searchText = searchInput.value;
    current_page = 1;
    await getItems()
    await reloadCards()
}

function toggleSettings(){
    if (settingsState==false) {
        document.getElementById('settings').hidden = false
        settingsState = true;
    } else if (settingsState==true){
        document.getElementById('settings').hidden = true;
        settingsState = false;
    }
}

async function reloadCards() {
    if(detailedList){
        await updateListElements()
    } else {
        await updateTableElements()
    }
    await updatePaginationElement()
}

async function updatePaginationElement() {
        let paginationElement = document.getElementById("paginationElement");
        paginationElement.innerHTML = "";
        // previous
        let previousElement = document.createElement('li')
        if(current_page<=1){
            previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
            previousElement.classList.add('uk-disabled');
        }else {
            previousElement.innerHTML = `<a onclick="setPage(${current_page-1})"><span uk-pagination-previous></span></a>`;
        }
        paginationElement.append(previousElement)
        
        //first
        let firstElement = document.createElement('li')
        if(current_page<=1){
            firstElement.innerHTML = `<a>1</a>`;
            firstElement.classList.add('uk-disabled');
        }else {
            firstElement.innerHTML = `<a onclick="setPage(1)">1</a>`;
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
            lastElement.innerHTML = `<a onclick=setPage(${current_page-1})>${current_page-1}</a>`
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
            nextElement.innerHTML = `<a onclick=setPage(${current_page+1})>${current_page+1}</a>`
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
            endElement.innerHTML = `<a>${end_page}</a>`;
            endElement.classList.add('uk-disabled');
        }else {
            endElement.innerHTML = `<a onclick="setPage(${end_page})">${end_page}</a>`;
        }
        paginationElement.append(endElement)
        //next button
        let nextElement = document.createElement('li')
        if(current_page>=end_page){
            nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
            nextElement.classList.add('uk-disabled');
        }else {
            nextElement.innerHTML = `<a onclick="setPage(${current_page+1})"><span uk-pagination-next></span></a>`;
        }
        paginationElement.append(nextElement)
}

async function setPage(pageNumber){
    current_page = pageNumber;
    await getItems()
    await reloadCards()
}

async function updateTableElements(){
    let items_list = document.getElementById("items_list");
    items_list.innerHTML = "";

    let main_table = document.createElement('table')
    main_table.setAttribute('class', 'uk-table uk-table-striped')

    let table_head = document.createElement('thead')

    let head_row = document.createElement('tr')
    let nameCell = document.createElement('th')
    nameCell.innerHTML="Name"
    let descriptionCell = document.createElement('th')
    descriptionCell.innerHTML = 'Description'
    descriptionCell.setAttribute('class', 'uk-visible@m')
    let qtyUOMCell = document.createElement('th')
    qtyUOMCell.innerHTML = 'QTY/UOM'
    
    let opsCell = document.createElement('th')
    opsCell.innerHTML = 'Operations'

    head_row.append(nameCell, descriptionCell, opsCell)
    table_head.append(head_row)
    main_table.append(table_head)


    let table_body = document.createElement('tbody')

    for (let i = 0; i < items.length; i++){
        let table_row = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = items[i].item_name
        nameCell.setAttribute('class', 'uk-width-1-4')
        let descriptionCell = document.createElement('td')
        descriptionCell.innerHTML = items[i].description
        descriptionCell.setAttribute('class', 'uk-text-truncate uk-table-expand uk-visible@m')

        let qtyUOMCell = document.createElement('td')
        qtyUOMCell.innerHTML = `${parseFloat(items[i].total_qoh)} ${items[i].uom.fullname}`

        let opsCell = document.createElement('td')
        opsCell.setAttribute('class', 'uk-width-1-4')

        let buttonGroup = document.createElement('div')
        buttonGroup.setAttribute('class', 'uk-button-group')

        let viewOp = document.createElement('a')
        viewOp.innerHTML = `edit <span uk-icon="icon: pencil"></span>`
        viewOp.setAttribute('class', 'uk-button uk-button-default uk-button-small')
        viewOp.href = `/item/${items[i].id}`

        let historyOp = document.createElement('a')
        historyOp.innerHTML = `history <span uk-icon="icon: history"></span>`
        historyOp.setAttribute('class', 'uk-button uk-button-default uk-button-small')
        historyOp.href = `/transactions/${items[i].id}`

        buttonGroup.append(viewOp, historyOp)
        opsCell.append(buttonGroup)

        table_row.append(nameCell, descriptionCell, qtyUOMCell, opsCell)
        table_body.append(table_row)
    }
    
    main_table.append(table_body)
    items_list.append(main_table)
}

async function updateListElements(){
    let items_list = document.getElementById("items_list");
    items_list.innerHTML = "";

    let main_list = document.createElement('div')
    main_list.setAttribute('class', 'uk-child-width-1-3@m')
    main_list.setAttribute('uk-grid', 'masonry: pack')

    let placceholderDIV = document.createElement('div')
    for (let i = 0; i < items.length; i++){
        let outerShell = document.createElement('div')
        
        let listItem = document.createElement('div');
        listItem.classList.add('uk-card')
        listItem.classList.add('uk-card-default')
        listItem.classList.add('uk-card-small')
        listItem.classList.add('uk-card-hover')
        listItem.style = "border-radius: 10px;"

        let header = document.createElement('div')
        header.classList.add('uk-card-header')
        header.style = "border-radius: 0px, 10px, 0px, 10px;"

        header.innerHTML = `<h3>${items[i].item_name}</h3><div style="color: black;background-color: lightgrey; border-radius:10px;" class="uk-label uk-text-default">Quantity on Hand: ${parseFloat(items[i].total_qoh)} ${items[i].uom.fullname}</div>`
        
        let content = document.createElement('div')
        content.classList.add('uk-card-body')
        content.innerHTML = `<p>${items[i].description}</p>`

        let footer = document.createElement('div')
        footer.classList.add('uk-card-footer')
        footer.innerHTML = `<a style="margin-right: 5px; border-radius: 10px;" class="uk-button uk-button-default uk-button-small" uk-icon="icon: pencil" href="/item/${items[i].id}">edit</a>
        <a style="border-radius: 10px;" class="uk-button uk-button-default uk-button-small" uk-icon="icon: history" href="/transactions/${items[i].id}">History</a>`
        
        listItem.append(header)
        if(!items[i].description == ""){
            listItem.append(content)
        }
        listItem.append(footer)

        outerShell.append(listItem)

        placceholderDIV.append(outerShell)

    }
    main_list.innerHTML = placceholderDIV.innerHTML
    items_list.append(main_list)
}

async function getItems(){
    const url = new URL('/item/getItemsWithQOH', window.location.origin);
    url.searchParams.append('page', current_page);
    url.searchParams.append('limit', limit);
    url.searchParams.append('search_text', searchText);
    url.searchParams.append('sort_order', sort_order);
    url.searchParams.append('view', view);

    await fetch(url)
    .then(response => response.json())
    .then(data => {
        items = data.items;
        end_page = data.end;
    })
};

async function openAddItemModal() {
    UIkit.modal(document.getElementById('addItemModal')).show();
}

async function openAddPrefixModal() {
    UIkit.modal(document.getElementById('addPrefixModal')).show();
}

async function addSKUPrefix() {
    let uuid = `%${document.getElementById('addUUID').value}%`
    let name = `${document.getElementById('addPrefixName').value}`
    let description = `${document.getElementById('addPrefixDescription').value}`

    const response = await fetch(`/items/addSKUPrefix`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            uuid: uuid,
            name: name,
            description: description,
        }),
    });
    data =  await response.json();
    transaction_status = "success"
    if (data.error){
        transaction_status = "danger"
    }

    UIkit.notification({
        message: data.message,
        status: transaction_status,
        pos: 'top-right',
        timeout: 5000
    });
    UIkit.modal(document.getElementById('addPrefixModal')).hide();

}

async function addBlankItem() {
    let barcode = `%${document.getElementById('addBarcode').value}%`
    let name = `${document.getElementById('addName').value}`
    let subtype = `${document.getElementById('subtype_select').value}`

    const response = await fetch(`/items/addBlankItem`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            barcode: barcode,
            name: name,
            subtype: subtype,
        }),
    });
    data =  await response.json();
    transaction_status = "success"
    if (data.error){
        transaction_status = "danger"
    }

    UIkit.notification({
        message: data.message,
        status: transaction_status,
        pos: 'top-right',
        timeout: 5000
    });
    UIkit.modal(document.getElementById('addItemModal')).hide();

}

async function changeSite(site){
    console.log(site)
    const response = await fetch(`/changeSite`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            site: site,
        }),
    });
    data =  await response.json();
    transaction_status = "success"
    if (data.error){
        transaction_status = "danger"
    }

    UIkit.notification({
        message: data.message,
        status: transaction_status,
        pos: 'top-right',
        timeout: 5000
    });
    location.reload(true)
}