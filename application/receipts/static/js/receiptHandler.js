var pagination_current = 1;
var pagination_end = 10

document.addEventListener('DOMContentLoaded', async function() {
    await refreshReceipt()
})

async function refreshReceipt() {
    let receipt = await getReceipt(receipt_id)
    await replenishFields(receipt)
    await replenishLinesTable(receipt.receipt_items)
    await replenishFilesCards(receipt.files)
}

async function replenishFields(receipt) {
    if (receipt){
        document.getElementById('title').innerHTML = receipt.receipt_id
        // document.getElementById('crumbID').innerHTML = receipt.receipt_id
        document.getElementById('receipt_id').innerHTML = receipt.receipt_id
        document.getElementById('database_id').value = receipt.id
        document.getElementById('date_submitted').value = receipt.date_submitted
        document.getElementById('submitted_by').value = receipt.submitted_by
        document.getElementById('receipt_status').value = receipt.receipt_status
        document.getElementById('vendor_id').value = receipt.vendor.id
        document.getElementById('vendor_name').value = receipt.vendor.vendor_name
        document.getElementById('vendor_address').value = receipt.vendor.vendor_address
        document.getElementById('vendor_phone').value = receipt.vendor.phone_number
        if(receipt.receipt_status=="Resolved"){
            document.getElementById('resolveReceiptButton').hidden = true
            document.getElementById('lineAddButton').hidden = true
            document.getElementById('fileUploadButton').hidden = true
            document.getElementById('fileUploadForm').hidden = true
            document.getElementById('vendorSelectDiv').hidden = true
            document.getElementById('vendorSelectButton').hidden = true
        }
    }
}

async function replenishLinesTable(receipt_items) {
    let linesTableBody = document.getElementById("linesTableBody")
    linesTableBody.innerHTML = ""

    let deniedTableBody = document.getElementById("deniedTableBody")
    deniedTableBody.innerHTML = ""

    let resolvedTableBody = document.getElementById("resolvedTableBody")
    resolvedTableBody.innerHTML = ""

    for(let i = 0; i < receipt_items.length; i++){
        let tableRow = document.createElement('tr')


        let statusCell = document.createElement('td')
        statusCell.innerHTML = receipt_items[i].status
        let barcodeCell = document.createElement('td')
        barcodeCell.innerHTML = receipt_items[i].barcode
        let typeCell = document.createElement('td')

        let label_color = 'grey'
        if(receipt_items[i].type == 'sku'){
            label_color = 'green'
        }
        if(receipt_items[i].type == 'new sku'){
            label_color = 'orange'
        }
        if(receipt_items[i].type == 'api'){
            label_color = 'purple'
        }
        if(receipt_items[i].type == 'PLU SKU'){
            label_color = 'blue'
        }

        typeCell.innerHTML = `<span style="background-color: ${label_color};" class="uk-label">${receipt_items[i].type}</span>`
        let nameCell = document.createElement('td')
        nameCell.innerHTML = receipt_items[i].name
        
        let operationsCell = document.createElement('td')


        let linkOp = document.createElement('a')
        linkOp.style = "margin-right: 5px;"
        linkOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        linkOp.setAttribute('uk-icon', 'icon: link')
        linkOp.onclick = async function () {
            await openItemBarcodeSelectModal(receipt_items[i].id)
        }

        let editOp = document.createElement('a')
        editOp.style = "margin-right: 5px;"
        editOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        editOp.setAttribute('uk-icon', 'icon: pencil')
        editOp.onclick = async function () {
            await openLineEditModal(receipt_items[i])
        }

        let resolveOp = document.createElement('a')
        resolveOp.style = "margin-right: 5px;"
        resolveOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        resolveOp.setAttribute('uk-icon', 'icon: check')
        resolveOp.onclick = async function(){
            await resolveLine(receipt_items[i].id)
        }

        let denyOp = document.createElement('a')
        denyOp.style = "margin-right: 5px;"
        denyOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        denyOp.setAttribute('uk-icon', 'icon: close-circle')
        denyOp.onclick = async function() {
            await denyLine(receipt_items[i].id)
        }

        let deleteOp = document.createElement('a')
        deleteOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        deleteOp.setAttribute('uk-icon', 'icon: trash')
        deleteOp.onclick = async function(){
            await deleteLine(receipt_items[i].id)
        }


        if (receipt_items[i].type === "new sku"){
            operationsCell.append(linkOp)
        }

        operationsCell.append(editOp, resolveOp, denyOp, deleteOp)

        operationsCell.classList.add("uk-flex")
        operationsCell.classList.add("uk-flex-right")

        if(receipt_items[i].status === "Denied" || receipt_items[i].status === "Resolved"){
            tableRow.classList.add('uk-disabled')
        }

        tableRow.append(statusCell, barcodeCell,typeCell, nameCell, operationsCell)

        if(receipt_items[i].status === "Denied"){
            deniedTableBody.append(tableRow)
        } else if(receipt_items[i].status === "Resolved") {
            resolvedTableBody.append(tableRow)
        } else {
            linesTableBody.append(tableRow)
        }
    }
}

async function replenishFilesCards(files) {
    let fileCards = document.getElementById('fileCards')
    fileCards.innerHTML = ""

    for(let key in files){
        let parent_div = document.createElement('div')

        let card_div = document.createElement('div')
        card_div.setAttribute('class', 'uk-card uk-card-default uk-card-small')

        let baseStaticUrl = `/receipts/api/getPreview/`;
        let imgSrc = `${baseStaticUrl}${files[key].preview_image}`;

        let media_div = document.createElement('div')
        media_div.setAttribute('class', 'uk-card-media-top')
        media_div.innerHTML = `<img data-src="${imgSrc}" width="600" height="400" alt="" uk-img />`;
        let body_div = document.createElement('div')
        body_div.setAttribute('class', 'uk-card-body')

        let file_size = (files[key].file_size / (1024 * 1024)).toFixed(2)

        body_div.innerHTML = `
                <h3 class="uk-card-title">${key}</h3>
                <p>Size: ${file_size} MB</p>
                <p>uploaded_by: ${files[key].uploaded_by}</p>
                <p>Type: ${files[key].file_type}</p>
                <button onclick="viewFile('${key}')" class="uk-button uk-primary">view</button>
            `

        card_div.append(media_div, body_div)
        parent_div.append(card_div)
        fileCards.append(parent_div)

    }
}

async function viewFile(source) {
    let iframeModalBody = document.getElementById('iframeModalBody')
    iframeModalBody.innerHTML = ""

    document.getElementById('filenameiframemodal').innerHTML = source

    let iframe = document.createElement('iframe')
    iframe.src = `/receipts/api/getFile/${source}`
    iframe.width = "100%"
    iframe.style.height = "100%"

    iframeModalBody.append(iframe)

    UIkit.modal(document.getElementById("iframeModal")).show();

}

async function openLineEditModal(line_data) {
    console.log(line_data)
    document.getElementById('lineName').value = line_data.name
    document.getElementById('lineQty').value = line_data.qty
    document.getElementById('lineUOM').value = line_data.uom.id
    document.getElementById('lineCost').value = line_data.data.cost
    document.getElementById('lineExpires').value = line_data.data.expires
    if(line_data.type === 'sku'){
        document.getElementById('lineUOM').classList.add('uk-disabled')
    } else {
        document.getElementById('lineUOM').classList.remove('uk-disabled')
    }
    
    if(line_data.type === 'PLU SKU'){
        document.getElementById('lineUOM').classList.add('uk-disabled')
    } else {
        document.getElementById('lineUOM').classList.remove('uk-disabled')
    }
    


    if(!line_data.data.expires){
        document.getElementById('lineExpires').classList.add('uk-disabled')
    } else {
        document.getElementById('lineExpires').classList.remove('uk-disabled')
    }
    document.getElementById('saveLineButton').onclick = async function() {
        await saveLine(line_data.id)
    }
    UIkit.modal(document.getElementById("lineEditModal")).show();
}

async function addSKULine(item_id) {
    console.log(item_id)
    const response = await fetch(`/receipts/api/addSKULine`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            item_id: item_id, 
            receipt_id: receipt_id
        }),
    });
    await refreshReceipt()
    UIkit.modal(document.getElementById("itemsModal")).hide();

}

async function resolveLine(line_id) {
    const response = await fetch(`/receipts/api/resolveLine`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            line_id: line_id
        }),
    });
    await refreshReceipt()
}

async function resolveReceipt() {
    const response = await fetch(`/receipts/api/resolveReceipt`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            receipt_id: receipt_id
        }),
    });
    await refreshReceipt()
}

async function uploadFile() {
    const fileInput = document.querySelector('input[type="file"]');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    await fetch(`/receipts/api/uploadfile/${receipt_id}`, {
    method: 'POST',
    body: formData
    })
    .then(response => response.json())
    .then(data => console.log('File uploaded!', data))
    .catch(error => console.error('Error:', error));
    await refreshReceipt()
}

async function saveLine(line_id){
    let name = document.getElementById('lineName').value
    let qty = document.getElementById('lineQty').value
    let uom = document.getElementById('lineUOM').value
    let cost = document.getElementById('lineCost').value
    let expires = document.getElementById('lineExpires').value
    console.log(expires)

    if(expires === ''){
        expires = false
    }

    UIkit.modal(document.getElementById("lineEditModal")).hide();

    let payload = {
        name: name,
        qty: qty,
        uom: uom,
        data: {
            cost: cost,
            expires: expires
        }
    }

    const response = await fetch(`/receipts/api/saveLine`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            line_id: line_id,
            payload: payload
        }),
    });
    await refreshReceipt()


}

async function deleteLine(id) {
    const response = await fetch(`/receipts/api/deleteLine`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            line_id: id
        }),
    });
    await refreshReceipt()
}

async function denyLine(id) {
    console.log(id)
    const response = await fetch(`/receipts/api/denyLine`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            line_id: id
        }),
    });
    await refreshReceipt()
}

async function getReceipt(id) {
    const url = new URL('/receipts/api/getReceipt', window.location.origin);
    url.searchParams.append('id', id);
    const response = await fetch(url);
    data =  await response.json();
    let receipt = data.receipt;
    return receipt;
}

// Custom Line Modal Functions
async function openAddCustomLineModal() {
    console.log("custom")
    document.getElementById('CustomlineName').value = ""
    document.getElementById('CustomlineQty').value = 0
    document.getElementById('CustomlineUOM').value = 1
    document.getElementById('CustomlineCost').value = 0.00
    document.getElementById('saveCustomLineButton').innerHTML = "Add"
    document.getElementById('saveCustomLineButton').onclick = async function() {
        await addCustomLine()        
    }

    UIkit.modal(document.getElementById("CustomLineModal")).show();  
}

async function addCustomLine(){
    let LineName = document.getElementById('CustomlineName').value
    let LineQty = document.getElementById('CustomlineQty').value
    let LineUOM = document.getElementById('CustomlineUOM').value
    let LineCost = document.getElementById('CustomlineCost').value
    console.log(LineName)
    UIkit.modal(document.getElementById("CustomLineModal")).hide();

    const response = await fetch(`/receipts/api/addCustomLine`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            line_name: LineName,
            line_qty: LineQty,
            line_UOM: LineUOM,
            line_cost: LineCost,
            receipt_id: receipt_id
        }),
    });
    await refreshReceipt()
}


// SKU Modal functions
let items_limit = 50;
var ItemsModal_search_string = ""
async function getItems() {
    console.log("getting items")
    const url = new URL('/receipts/api/getItems', window.location.origin);
    url.searchParams.append('page', pagination_current);
    url.searchParams.append('limit', items_limit);
    url.searchParams.append('search_string', ItemsModal_search_string);
    const response = await fetch(url);
    data =  await response.json();
    pagination_end = data.end
    let items = data.items;
    return items;
}

async function setPage(page) {
    pagination_current = page
    let items = await getItems()
    await replenishItemsTable(items)
    await updateItemsPaginationElement()
}

async function ItemsModalSearch(event) {
    if (event.key === "Enter"){
        ItemsModal_search_string = document.getElementById('ItemsModalSearchInput').value
        let items = await getItems()
        await replenishItemsTable(items)
        await updateItemsPaginationElement()
    }
}

async function updateItemsPaginationElement() {
    let paginationElement = document.getElementById("itemsPage");
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(pagination_current<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setPage(${pagination_current-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(pagination_current<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setPage(1)">1</a>`;
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
        lastElement.innerHTML = `<a onclick="setPage(${pagination_current-1})">${pagination_current-1}</a>`
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
        nextElement.innerHTML = `<a onclick="setPage(${pagination_current+1})">${pagination_current+1}</a>`
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
        endElement.innerHTML = `<a onclick="setPage(${pagination_end})">${pagination_end}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(pagination_current>=pagination_end){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setPage(${pagination_current+1})"><span uk-pagination-next></span></a>`;
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}

async function openSKUModal() {
    pagination_current = 1
    ItemsModal_search_string = ""
    document.getElementById('ItemsModalSearchInput').value = ""
    let items = await getItems()
    await replenishItemsTable(items)
    await updateItemsPaginationElement()
    UIkit.dropdown(document.getElementById("addLineDropDown")).hide(false);
    UIkit.modal(document.getElementById("itemsModal")).show();
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
        
        tableRow.onclick = async function() {
            await addSKULine(items[i].id)
        }

        tableRow.append(idCell, barcodeCell, nameCell)
        itemsTableBody.append(tableRow)
    }
}

// Select Vendor functions
let vendor_limit = 25
let vendor_current_page = 1
let vendor_end_page = 10
async function getVendors() {
    const url = new URL('/receipts/api/getVendors', window.location.origin);
    url.searchParams.append('page', vendor_current_page);
    url.searchParams.append('limit', vendor_limit);
    const response = await fetch(url);
    data =  await response.json();
    vendor_end_page = data.end
    return data.vendors;
}

async function postVendorUpdate(vendor_id) {
    const response = await fetch(`/receipts/api/postVendorUpdate`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            receipt_id: receipt_id,
            vendor_id: vendor_id
        }),
    });
    data = await response.json()
    message_type = "primary"
    if(data.error){
        message_type = "danger"
    }
    UIkit.notification({
        message: data.message,
        status: message_type,
        pos: 'top-right',
        timeout: 5000
    });
    await refreshReceipt()
    UIkit.modal(document.getElementById("vendorsModal")).hide();

}

async function openVendorsSelectModal() {
    let vendors = await getVendors();
    await replenishVendorsTableBody(vendors);
    await updateVendorsPaginationElement()
    UIkit.modal(document.getElementById("vendorsModal")).show();
}

async function replenishVendorsTableBody(vendors) {
    let vendorsTableBody = document.getElementById('vendorsTableBody')
    vendorsTableBody.innerHTML = ""

    for(let i=0; i < vendors.length; i++){
        let tableRow = document.createElement('tr')

        let idCell = document.createElement('td')
        idCell.innerHTML = vendors[i].id

        let nameCell = document.createElement('td')
        nameCell.innerHTML = vendors[i].vendor_name

        let phoneCell = document.createElement('td')
        phoneCell.innerHTML = vendors[i].phone_number

        let addressCell = document.createElement('td')
        addressCell.innerHTML = vendors[i].vendor_address

        tableRow.onclick = async function() {
            await postVendorUpdate(vendors[i].id)
        }

        tableRow.append(idCell,nameCell,phoneCell, addressCell)
        vendorsTableBody.append(tableRow)
    }

}

async function setVendorPage(pageNumber) {
    vendor_current_page = pageNumber;
    let vendors = await getVendors()
    await updateVendorsPaginationElement()
    await replenishVendorsTableBody(vendors)
}

async function updateVendorsPaginationElement() {
    let paginationElement = document.getElementById("vendorsPage");
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(vendor_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setVendorPage(${vendor_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(vendor_current_page<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setVendorPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(vendor_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(vendor_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="setVendorPage(${vendor_current_page-1})">${vendor_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(vendor_current_page!=1 && vendor_current_page != vendor_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${vendor_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(vendor_current_page+2<vendor_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="setVendorPage(${vendor_current_page+1})">${vendor_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(vendor_current_page+2<=vendor_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(vendor_current_page>=vendor_end_page){
        endElement.innerHTML = `<a><strong>${vendor_end_page}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setVendorPage(${vendor_end_page})">${vendor_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(vendor_current_page>=vendor_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setVendorPage(${vendor_current_page+1})"><span uk-pagination-next></span></a>`;
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}

// Select Barcode Link Functions
var ItemBarcodeSelectModal_limit = 50
var ItemBarcodeSelectModal_page = 1
var ItemBarcodeSelectModal_page_end = 1
var selectedReceiptItemID = 0
var ItemBarcodeSelectModal_search_text = ""

async function openItemBarcodeSelectModal(receipt_item_id) {
    selectedReceiptItemID = receipt_item_id
    ItemBarcodeSelectModal_search_text = ""
    document.getElementById('ItemBarcodeSelectSearchInput').value = ""
    ItemBarcodeSelectModal_page = 1
    ItemBarcodeSelectModal_page_end = 1
    await setupItemsBarcodeSelect()
    UIkit.modal(document.getElementById("ItemBarcodeSelectModal")).show();
}

async function setupItemsBarcodeSelect() {
    let items = await getItemsForModal()
    await generateItemsBarcodeSelectTable(items)
    await updateItemsBarcodeSelectPagination()
}

async function generateItemsBarcodeSelectTable(items) {
    let ItemBarcodeSelectTable = document.getElementById('ItemBarcodeSelectTable')
    ItemBarcodeSelectTable.innerHTML = ""

    for(let i = 0; i < items.length; i++){
        let tableRow = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = items[i].item_name

        let inCell = document.createElement('td')
        inCell.innerHTML = `<input id="${items[i].item_uuid}_in" class="uk-input" type="number" value="1" aria-label="Input">`

        let outCell = document.createElement('td')
        outCell.innerHTML = `<input id="${items[i].item_uuid}_out" class="uk-input" type="number" value="1" aria-label="Input">`
        
        let descriptorCell = document.createElement('td')
        descriptorCell.innerHTML = `<input id="${items[i].item_uuid}_descriptor" class="uk-input" type="text" value="${items[i].item_name}" aria-label="Input">`
        

        let opCell = document.createElement('td')

        let selectButton = document.createElement('button')
        selectButton.setAttribute('class', 'uk-button uk-button-small uk-button-primary')
        selectButton.innerHTML = "Select"
        selectButton.onclick = async function() {
            let payload = {
                item_uuid: items[i].item_uuid,
                in_exchange: parseFloat(document.getElementById(`${items[i].item_uuid}_in`).value),
                out_exchange: parseFloat(document.getElementById(`${items[i].item_uuid}_out`).value),
                descriptor: document.getElementById(`${items[i].item_uuid}_descriptor`).value
            }
            await updateReceiptItemBarcode(payload)
        }

        opCell.append(selectButton)

        tableRow.append(nameCell, inCell, outCell, descriptorCell, opCell)

        ItemBarcodeSelectTable.append(tableRow)
    }
}

async function getItemsForModal() {
    const url = new URL('/receipts/api/getItems', window.location.origin);
    url.searchParams.append('page', ItemBarcodeSelectModal_page);
    url.searchParams.append('limit', ItemBarcodeSelectModal_limit);
    url.searchParams.append('search_string', ItemBarcodeSelectModal_search_text);
    const response = await fetch(url);
    data =  await response.json();
    ItemBarcodeSelectModal_page_end = data.end
    let items = data.items;
    return items;
}

async function updateItemsBarcodeSelectPagination() {
    let paginationElement = document.getElementById("ItemBarcodeSelectModalPage");
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(pagination_current<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="ItemBarcodeSelectModalPage(${ItemBarcodeSelectModal_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(pagination_current<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="ItemBarcodeSelectModalPage(1)">1</a>`;
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
    if(ItemBarcodeSelectModal_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="ItemBarcodeSelectModalPage(${ItemBarcodeSelectModal_page-1})">${ItemBarcodeSelectModal_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(ItemBarcodeSelectModal_page!=1 && ItemBarcodeSelectModal_page != ItemBarcodeSelectModal_page_end){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${ItemBarcodeSelectModal_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(ItemBarcodeSelectModal_page+2<ItemBarcodeSelectModal_page_end+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="ItemBarcodeSelectModalPage(${ItemBarcodeSelectModal_page+1})">${ItemBarcodeSelectModal_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(ItemBarcodeSelectModal_page+2<=ItemBarcodeSelectModal_page_end){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(pagination_current>=ItemBarcodeSelectModal_page_end){
        endElement.innerHTML = `<a><strong>${ItemBarcodeSelectModal_page_end}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="ItemBarcodeSelectModalPage(${ItemBarcodeSelectModal_page_end})">${ItemBarcodeSelectModal_page_end}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(pagination_current>=ItemBarcodeSelectModal_page_end){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="ItemBarcodeSelectModalPage(${ItemBarcodeSelectModal_page+1})"><span uk-pagination-next></span></a>`;
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}

async function ItemBarcodeSelectModalPage(pageNumber){
    ItemBarcodeSelectModal_page = pageNumber;
    await setupItemsBarcodeSelect()
}

async function ItemBarcodeSelectModalSearch(event) {
    if (event.key === "Enter"){
        ItemBarcodeSelectModal_search_text = document.getElementById('ItemBarcodeSelectSearchInput').value
        await setupItemsBarcodeSelect()
    }
}

async function updateReceiptItemBarcode(payload) {

    UIkit.modal(document.getElementById("ItemBarcodeSelectModal")).hide();

    const response = await fetch(`/receipts/api/saveBarcodeLink`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            receipt_item_id: selectedReceiptItemID,
            payload: payload
        }),
    });
    await refreshReceipt()


}