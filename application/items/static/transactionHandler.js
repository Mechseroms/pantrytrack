var pagination_current = 1;
var search_string = '';
var defaqult_limit = 2;
var pagination_end = 1;
var item;

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

async function replenishItemsTable(items) {
    let itemsTableBody = document.getElementById("itemsTableBody")
    itemsTableBody.innerHTML = ""

    for(let i = 0; i < items.length; i++){
        let tableRow = document.createElement('tr')


        let idCell = document.createElement('td')
        idCell.innerHTML = items[i].id
        let barcodeCell = document.createElement('td')
        barcodeCell.innerHTML = items[i].barcode
        let nameCell = document.createElement('td')
        nameCell.innerHTML = items[i].item_name

        tableRow.append(idCell)
        tableRow.append(barcodeCell)
        tableRow.append(nameCell)

        tableRow.onclick = function(){
            selectItem(items[i].id)
        }

        itemsTableBody.append(tableRow)
    }
}

async function populateForm() {
    if (item){
        console.log(item)
        document.getElementById('database_id').value = item.id
        document.getElementById('barcode').value = item.barcode
        document.getElementById('name').value = item.item_name
        document.getElementById('transaction_cost').value = parseFloat(item.item_info.cost)
        
        await selectLocation(
            item.logistics_info.primary_zone.id, 
            item.logistics_info.primary_location.id,
            item.logistics_info.primary_zone.name,
            item.logistics_info.primary_location.name
        )


        let quantity_on_hand = 0
        let locations = await getItemLocations()
        for(let i = 0; i < locations.length; i++){
            quantity_on_hand = quantity_on_hand + locations[i].quantity_on_hand
        }
        document.getElementById('QOH').value = quantity_on_hand
        document.getElementById('UOM').value = item.item_info.uom.fullname

        await replenishItemLocationsTable(locations)

    }
}

async function selectItem(id) {
    UIkit.modal(document.getElementById("itemsModal")).hide();
    item = await getItem(id)
    await populateForm()
}

var transaction_zone_id = 0
var transaction_item_location_id = 0
async function selectLocation(zone_id, location_id, zone_name, location_name) {
    document.getElementById('zone').value = zone_name
    document.getElementById('location').value = location_name
    transaction_zone_id = zone_id
    transaction_item_location_id = location_id
}

async function openItemsModal(elementID){
    UIkit.modal(document.getElementById("itemsModal")).show();
    pagination_current = 1
    search_string = ''
    let items = await getItems()
    await replenishItemsTable(items)
    await updatePaginationElement(elementID)
    setFormButtonsEnabled(true)
}

async function setFormButtonsEnabled(state) {
    let item_location_button = document.getElementById("itemLocations")

    if(state){
        item_location_button.classList.remove("uk-disabled")
    } else {
        item_location_button.classList.add("uk-disabled")
    }
}

async function setTransactionTypeAdjustments() {
    let trans_type = document.getElementById('trans_type').value

    if(trans_type=="Adjust Out"){
        document.getElementById('transaction_cost').classList.add('uk-disabled')
    }
    if(trans_type=="Adjust In"){
        document.getElementById('transaction_cost').classList.remove('uk-disabled')
    }

}

async function replenishItemLocationsTable(locations) {
    let itemLocationTableBody = document.getElementById('itemLocationTableBody')
    itemLocationTableBody.innerHTML = ""
    for(let i = 0; i < locations.length; i++){
        let tableRow = document.createElement('tr')

        let loca = locations[i].uuid.split('@')

        let zoneCell = document.createElement('td')
        zoneCell.innerHTML = loca[0]

        let locationCell = document.createElement('td')
        locationCell.innerHTML = loca[1]

        let qohCell = document.createElement('td')
        qohCell.innerHTML = parseFloat(locations[i].quantity_on_hand)

        tableRow.append(zoneCell, locationCell, qohCell)
        tableRow.onclick = async function(){
            await selectLocation(
                locations[i].zone_id,
                locations[i].id,
                loca[0],
                loca[1]
            )
        }
        itemLocationTableBody.append(tableRow)
    }
}

let locations_limit = 10;
async function getItemLocations() {
    console.log("getting Locations")
    const url = new URL('/items/getItemLocations', window.location.origin);
    url.searchParams.append('page', pagination_current);
    url.searchParams.append('limit', locations_limit);
    url.searchParams.append('id', item.id);
    const response = await fetch(url);
    data =  await response.json();
    pagination_end = data.end
    let locations = data.locations;
    console.log(locations)
    return locations;
}


let items_limit = 50;
async function getItems() {
    console.log("getting items")
    const url = new URL('/items/getModalItems', window.location.origin);
    url.searchParams.append('page', pagination_current);
    url.searchParams.append('limit', items_limit);
    url.searchParams.append('search_string', search_string)
    const response = await fetch(url);
    data =  await response.json();
    pagination_end = data.end
    let items = data.items;
    return items;
}

async function getItem(id) {
    console.log(`selected item: ${id}`)
    const url = new URL('/items/getItem', window.location.origin);
    url.searchParams.append('id', id);
    const response = await fetch(url);
    data =  await response.json();
    item = data.item;
    return item;
}

async function validateTransaction() {
    let database_id = document.getElementById("database_id")
    let transaction_type = document.getElementById("trans_type")
    let transaction_zone = document.getElementById("zone")
    let transaction_location = document.getElementById("location")
    let transaction_quantity = document.getElementById("transaction_quantity")
    let transaction_cost = document.getElementById("transaction_cost")


    let error_count = 0
    if(database_id.value === ""){
        error_count = error_count + 1
        database_id.classList.add("uk-form-danger")
    } else {
        database_id.classList.remove("uk-form-danger")
    }
    if(transaction_type.value === "0"){
        error_count = error_count + 1
        transaction_type.classList.add("uk-form-danger")
    } else {
        transaction_type.classList.remove("uk-form-danger")
    }

    if (transaction_zone.value === ""){
        error_count = error_count + 1
        transaction_zone.classList.add("uk-form-danger")
    } else {
        transaction_zone.classList.remove("uk-form-danger")
    }

    if (transaction_location.value === ""){
        error_count = error_count + 1
        transaction_location.classList.add("uk-form-danger")
    } else {
        transaction_location.classList.remove("uk-form-danger")
    }

    let transaction_quantity_int = parseFloat(transaction_quantity.value)
    if (transaction_quantity_int === 0.00 || transaction_quantity_int < 0.00){
        error_count = error_count + 1
        transaction_quantity.classList.add("uk-form-danger")
    } else {
        transaction_quantity.classList.remove("uk-form-danger")
    }

    let transaction_cost_int = parseFloat(transaction_cost.value)
    if (transaction_cost_int == 0.00 && transaction_type.value == "Adjust In"){
        error_count = error_count + 1
        transaction_cost.classList.add("uk-form-danger")
    } else {
        transaction_cost.classList.remove("uk-form-danger")
    }

    if(error_count > 0){
        return false
    }

    return true
}

async function submitTransaction() {
    let validated = await validateTransaction()
    if (validated){
        let cost = parseFloat(document.getElementById('transaction_cost').value.replace(/[^0-9.-]+/g, ""));
        const response = await fetch(`/items/postTransaction`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: item.id,
                logistics_info_id: item.logistics_info_id,
                barcode: item.barcode,
                item_name: item.item_name,
                transaction_type: document.getElementById('trans_type').value,
                quantity: parseFloat(document.getElementById('transaction_quantity').value),
                description: document.getElementById('transaction_description').value,
                cost: cost,
                vendor: 0,
                expires: null,
                location_id: transaction_item_location_id
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

        item = await getItem(item.id)
        await populateForm()
        document.getElementById('transaction_quantity').value = '0.00'

    } else {
        UIkit.notification({
            message: 'Please verify your transaction receipt.',
            status: 'warning',
            pos: 'top-right',
            timeout: 5000
    })
}
}

async function searchTable(event, logis, elementID) {
    if(event.key==='Enter' && logis==='items'){
        search_string = event.srcElement.value
        let items = await getItems()
        await replenishItemsTable(items)
    }
    await updatePaginationElement(elementID)
}

async function setPage(pageNumber, elementID){
    pagination_current = pageNumber;
    
    if(elementID=="itemsPage"){
        let items = await getItems()
        await replenishItemsTable(items)
    }
    await updatePaginationElement(elementID)
}

async function updatePaginationElement(elementID) {
    let paginationElement = document.getElementById(elementID);
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(pagination_current<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setPage(${pagination_current-1}, '${elementID}')"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(pagination_current<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setPage(1, '${elementID}')">1</a>`;
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
        lastElement.innerHTML = `<a onclick="setPage(${pagination_current-1}, '${elementID}')">${pagination_current-1}</a>`
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
        nextElement.innerHTML = `<a onclick="setPage(${pagination_current+1}, '${elementID}')">${pagination_current+1}</a>`
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
        endElement.innerHTML = `<a onclick="setPage(${pagination_end}, '${elementID}')">${pagination_end}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(pagination_current>=pagination_end){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setPage(${pagination_current+1}, '${elementID}')"><span uk-pagination-next></span></a>`;
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}

async function getItemBarcode(barcode) {
    console.log(`selected item: ${barcode}`)
    const url = new URL('/items/getItem/barcode', window.location.origin);
    url.searchParams.append('barcode', barcode);
    const response = await fetch(url);
    data =  await response.json();
    return data;
}


async function openLineEditModal(ind, line_data) {
    console.log(line_data)
    document.getElementById('lineName').value = line_data.item.item_name
    document.getElementById('lineQty').value = line_data.item.qty
    document.getElementById('lineUOM').value = line_data.item.uom
    document.getElementById('lineCost').value = line_data.item.data.cost
    document.getElementById('lineExpires').value = line_data.item.data.expires
    if(line_data.type === 'sku'){
        document.getElementById('lineUOM').classList.add('uk-disabled')
    } else {
        document.getElementById('lineUOM').classList.remove('uk-disabled')
    }
    
    if(!line_data.item.data.expires){
        document.getElementById('lineExpires').classList.add('uk-disabled')
    } else {
        document.getElementById('lineExpires').classList.remove('uk-disabled')
    }
    
    document.getElementById('saveLineButton').onclick = async function() {
        line_data.item.item_name =  document.getElementById('lineName').value
        line_data.item.qty =  document.getElementById('lineQty').value
        line_data.item.uom =  document.getElementById('lineUOM').value
        line_data.item.data.cost =  document.getElementById('lineCost').value
        if(line_data.item.data.expires){
            line_data.item.data.expires =  document.getElementById('lineExpires').value
        }

        scannedReceiptItems[ind] = line_data
        UIkit.modal(document.getElementById("lineEditModal")).hide();
        await replenishScannedReceiptTable(scannedReceiptItems)
    }

    UIkit.modal(document.getElementById("lineEditModal")).show();
}

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