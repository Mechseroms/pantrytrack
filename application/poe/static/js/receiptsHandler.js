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

    document.getElementById('receiptStart').classList.add('uk-disabled')
    document.getElementById('receiptComplete').classList.remove('uk-disabled')
    document.getElementById('receiptClose').classList.remove('uk-disabled')

}

async function completeReceipt() {
    openedReceipt = false
    document.getElementById('barcode-input').classList.add('uk-disabled')
    document.getElementById('barcode-table').classList.add('uk-disabled')

    document.getElementById('receiptStart').classList.remove('uk-disabled')
    document.getElementById('receiptComplete').classList.add('uk-disabled')
    document.getElementById('receiptClose').classList.add('uk-disabled')

    await submitScanReceipt(scannedReceiptItems)
    let scanReceiptTableBody = document.getElementById("scanReceiptTableBody")
    scanReceiptTableBody.innerHTML = ""

    scannedReceiptItems = Array()
}

async function closeReceipt(){
    openedReceipt = false
    document.getElementById('barcode-input').classList.add('uk-disabled')
    document.getElementById('barcode-table').classList.add('uk-disabled')

    document.getElementById('receiptStart').classList.remove('uk-disabled')
    document.getElementById('receiptComplete').classList.add('uk-disabled')
    document.getElementById('receiptClose').classList.add('uk-disabled')

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
        if(scannedItem){
            let expires = scannedItem.food_info.expires
            if(scannedItem.food_info.expires){
                let today = new Date();
                today.setDate(today.getDate() + Number(scannedItem.food_info.default_expiration))
                expires = today.toISOString().split('T')[0];
            }
            scannedReceiptItems.push({item: {
                barcode: scannedItem.barcode,
                item_name: scannedItem.item_name,
                qty: scannedItem.item_info.uom_quantity,
                uom: scannedItem.item_info.uom.id,
                data: {cost: scannedItem.item_info.cost, expires: expires}
            }, type: 'sku'})
            document.getElementById('barcode-scan-receipt').value = ""
        } else {
            scannedReceiptItems.push({item: {
                barcode: `%${barcode}%`, 
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