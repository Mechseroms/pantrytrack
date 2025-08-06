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

var scannedItems = Array();
const queueLimit = 49; // 49 should be default

async function addToQueue(event) {
    if (event.key == "Enter"){
        let data = await getItemBarcode(document.getElementById('barcode-scan').value)
        let scannedItem = data.item
        console.log(scannedItem)
        if(data.error){
            UIkit.notification({
            message: data.message,
            status: "danger",
            pos: 'top-right',
            timeout: 5000
            });
        }
        if(scannedItems.length > queueLimit){
            scannedItems.shift()
        }
        if(!Array.isArray(scannedItem) && !data.error){
            let status = await submitScanTransaction(scannedItem)
            scannedItems.push({'item': scannedItem, 'type': `${document.getElementById('scan_trans_type').value}`, 'error': status})
            document.getElementById('barcode-scan').value = ""
        }
    }
    await replenishScanTable()
}

async function getItemBarcode(barcode) {
    console.log(`selected item: ${barcode}`)
    const url = new URL('/poe/getItem/barcode', window.location.origin);
    url.searchParams.append('barcode', barcode);
    const response = await fetch(url);
    data =  await response.json();
    return data;
}

async function submitScanTransaction(scannedItem) {
            /// I need to find the location that matches the items auto issue location id

        let trans_type = document.getElementById('scan_trans_type').value
        let scan_transaction_item_location_id = 0
        let comparator = 0
        
        if (trans_type === "Adjust In"){
            comparator = scannedItem.primary_location_id
        } else if (trans_type === "Adjust Out"){
            comparator = scannedItem.auto_issue_location_id
        }

        for (let i = 0; i < scannedItem.item_locations.length; i++){
            if (scannedItem.item_locations[i].location_id === comparator){
                scan_transaction_item_location_id = scannedItem.item_locations[i].location_id
            }
        }
        const response = await fetch(`/poe/postTransaction`, {
            method: 'POST',
            headers: {
                    'Content-Type': 'application/json',
                },
            body: JSON.stringify({
                item_id: scannedItem.item_id,
                logistics_info_id: scannedItem.logistics_info_id,
                barcode: scannedItem.barcode,
                item_name: scannedItem.item_name,
                transaction_type: document.getElementById('scan_trans_type').value,
                quantity: scannedItem.uom_quantity,
                description: "",
                cost: parseFloat(scannedItem.cost),
                vendor: 0,
                expires: null,
                location_id: scan_transaction_item_location_id
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

async function replenishScanTable() {
    let scanTableBody = document.getElementById("scanTableBody")
    scanTableBody.innerHTML = ""

    let reversedScannedItems = scannedItems.slice().reverse()

    for(let i = 0; i < reversedScannedItems.length; i++){
        let tableRow = document.createElement('tr')

        let icon = `<span uk-icon="check"></span>`
        if(reversedScannedItems[i].error){
            icon = `<span uk-icon="warning"></span>`
        }

        let statusCell = document.createElement('td')
        statusCell.innerHTML = icon
        let barcodeCell = document.createElement('td')
        barcodeCell.innerHTML = reversedScannedItems[i].item.barcode
        let nameCell = document.createElement('td')
        nameCell.innerHTML = reversedScannedItems[i].item.item_name
        let typeCell = document.createElement('td')
        typeCell.innerHTML = reversedScannedItems[i].type
        let locationCell = document.createElement('td')
        if (reversedScannedItems[i].type === "Adjust In"){
            locationCell.innerHTML = reversedScannedItems[i].item.primary_location_uuid
        } else {
            locationCell.innerHTML = reversedScannedItems[i].item.auto_issue_location_uuid
        }

        tableRow.append(statusCell, barcodeCell, nameCell, typeCell, locationCell)
        scanTableBody.append(tableRow)
    }
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