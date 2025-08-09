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

async function getItemBarcode(barcode) {
    console.log(`selected item: ${barcode}`)
    const url = new URL('/poe/getItem/barcode', window.location.origin);
    url.searchParams.append('barcode', barcode);
    const response = await fetch(url);
    data =  await response.json();
    return data;
}

async function submitScanReceipt(items) {
    const response = await fetch(`/poe/postReceipt`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            items: items
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

    return data.error
}

var openedReceipt = false
async function startReceipt() {
    openedReceipt = true
    document.getElementById('barcode-input').classList.remove('uk-disabled')
    document.getElementById('barcode-table').classList.remove('uk-disabled')

    document.getElementById('receiptStart').setAttribute('class', 'uk-button uk-button-default uk-disabled')
    document.getElementById('receiptComplete').setAttribute('class', 'uk-button uk-button-primary')
    document.getElementById('receiptClose').setAttribute('class', 'uk-button uk-button-danger')

}

async function completeReceipt() {
    openedReceipt = false
    document.getElementById('barcode-input').classList.add('uk-disabled')
    document.getElementById('barcode-table').classList.add('uk-disabled')

    document.getElementById('receiptStart').setAttribute('class', 'uk-button uk-button-primary')
    document.getElementById('receiptComplete').setAttribute('class', 'uk-button uk-button-default uk-disabled')
    document.getElementById('receiptClose').setAttribute('class', 'uk-button uk-button-default uk-disabled')

    await submitScanReceipt(scannedReceiptItems)
    let scanReceiptTableBody = document.getElementById("scanReceiptTableBody")
    scanReceiptTableBody.innerHTML = ""

    scannedReceiptItems = Array()
}

async function closeReceipt(){
    openedReceipt = false
    document.getElementById('barcode-input').classList.add('uk-disabled')
    document.getElementById('barcode-table').classList.add('uk-disabled')

    document.getElementById('receiptStart').setAttribute('class', 'uk-button uk-button-primary')
    document.getElementById('receiptComplete').setAttribute('class', 'uk-button uk-button-default uk-disabled')
    document.getElementById('receiptClose').setAttribute('class', 'uk-button uk-button-default uk-disabled')

    let scanReceiptTableBody = document.getElementById("scanReceiptTableBody")
    scanReceiptTableBody.innerHTML = ""

    scannedReceiptItems = Array()
}

var scannedReceiptItems = Array();
async function addToReceipt(event) {
    if (event.key == "Enter"){
        let barcode = document.getElementById('barcode-scan-receipt').value
        let data = await getItemBarcode(barcode)
        let scannedItem = data.item
        console.log(scannedItem)
        if(scannedItem){
            let expires = scannedItem.expires
            if(scannedItem.expires){
                let today = new Date();
                today.setDate(today.getDate() + Number(scannedItem.default_expiration))
                expires = today.toISOString().split('T')[0];
            }
            scannedReceiptItems.push({item: {
                barcode: scannedItem.barcode,
                item_uuid: scannedItem.item_uuid,
                item_name: scannedItem.item_name,
                qty: scannedItem.uom_quantity,
                uom: scannedItem.uom,
                data: {cost: scannedItem.cost, expires: expires}
            }, type: 'sku'})
            document.getElementById('barcode-scan-receipt').value = ""
        } else {
            scannedReceiptItems.push({item: {
                barcode: `%${barcode}%`,
                item_uuid: null,
                item_name: "unknown",
                qty: 1,
                uom: 1,
                data: {'cost': 0.00, 'expires': false}
            }, type: 'new sku'})
            document.getElementById('barcode-scan-receipt').value = ""
        }
    }
    await replenishScannedReceiptTable(scannedReceiptItems)
}

async function replenishScannedReceiptTable(items) {
    let scanReceiptTableBody = document.getElementById("scanReceiptTableBody")
    scanReceiptTableBody.innerHTML = ""

    for(let i = 0; i < items.length; i++){
        let tableRow = document.createElement('tr')

        let typeCell = document.createElement('td')
        typeCell.innerHTML = items[i].type
        let barcodeCell = document.createElement('td')
        barcodeCell.innerHTML = items[i].item.barcode
        let nameCell = document.createElement('td')
        nameCell.innerHTML = items[i].item.item_name
        
        let operationsCell = document.createElement('td')

        let editOp = document.createElement('a')
        editOp.style = "margin-right: 5px;"
        editOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        editOp.setAttribute('uk-icon', 'icon: pencil')
        editOp.onclick = async function () {
            await openLineEditModal(i, items[i])
        }

        let deleteOp = document.createElement('a')
        deleteOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        deleteOp.setAttribute('uk-icon', 'icon: trash')
        deleteOp.onclick = async function() {
            scannedReceiptItems.splice(i, 1)
            await replenishScannedReceiptTable(scannedReceiptItems)
        }

        operationsCell.append(editOp, deleteOp)

        operationsCell.classList.add("uk-flex")
        operationsCell.classList.add("uk-flex-right")

        tableRow.append(typeCell, barcodeCell, nameCell, operationsCell)
        scanReceiptTableBody.append(tableRow)
    }
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

// PLU Modal Controls
async function openPLUModal() {
    let items = await getPLUItems()
    await generatePLUCards(items)
    UIkit.modal(document.getElementById("PLUDASHModal")).show();
}

plu_current_page = 1
plu_limit = 50 
async function getPLUItems() {
    const url = new URL('/poe/api/paginatePLUItems', window.location.origin);
    url.searchParams.append('page', plu_current_page);
    url.searchParams.append('limit', plu_limit);
    const response = await fetch(url);
    data =  await response.json();
    return data.items;
}

async function generatePLUCards(plu_items) {
    let PLUCardsBody = document.getElementById('PLUCardsBody')
    PLUCardsBody.innerHTML = ""

    for (let i = 0; i < plu_items.length; i++){
        let container_div = document.createElement('div')

        let card_div = document.createElement('div')
        card_div.setAttribute('class','uk-card uk-card-default uk-card-small uk-card-hover uk-text-center')

        // need to check for key, use placeholder
        let image_div = document.createElement('div')
        image_div.setAttribute('class', 'uk-card-media-top uk-flex uk-flex-center uk-padding-small')

        let item_image = document.createElement('img')
        //item_image.src = "https://cdn-icons-png.flaticon.com/128/2756/2756716.png"
        item_image.width = "60"

        image_div.append(item_image)

        let card_body_div = document.createElement('div')
        card_body_div.setAttribute('class', 'uk-card-body uk-padding-small')

        let item_header = document.createElement('h5')
        item_header.setAttribute('class', 'uk-card-title')
        item_header.style = "margin-bottom: 4px;"
        item_header.innerHTML = plu_items[i].item_name

        let id_text = document.createElement('div')
        id_text.style = "font-size: 0.8em; margin-bottom: 7px;"
        id_text.innerHTML = `ID: ${plu_items[i].item_uuid}`

        let add_button = document.createElement('button')
        add_button.setAttribute('class', 'uk-button uk-button-primary uk-button-small')
        add_button.onclick = async function(){await addPLUToReceipt(plu_items[i])}
        add_button.innerHTML = "Add"


        card_body_div.append(item_header, id_text, add_button)

        card_div.append(image_div, card_body_div)
        
        container_div.append(card_div)
        
        PLUCardsBody.append(container_div)


    }

}

async function addPLUToReceipt(item) {
    scannedReceiptItems.push({item: {
                barcode: null,
                item_uuid: item.item_uuid ,
                item_name: item.item_name,
                qty: 1,
                uom: 1,
                data: {'cost': 0.00, 'expires': false}
            }, type: 'PLU SKU'})
    await replenishScannedReceiptTable(scannedReceiptItems)
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