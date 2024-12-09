let receipt;
let receipt_items;
document.addEventListener('DOMContentLoaded', async function() {
    await updateReceipt();

    var elems = document.querySelectorAll('.modal');
    var instances = M.Modal.init(elems, {
        // specify options here
    });
    var elems = document.getElementById('vendor_address');
    var instances = M.CharacterCounter.init(elems);
    var elems = document.querySelectorAll('.tooltipped');
    var instances = M.Tooltip.init(elems, {
      // specify options here
    });
});

async function updateReceipt(){
    await fetchReceipt();
    await propagateInfo();
    await propagateItems();
};

async function fetchReceiptItem(index){
    const url = new URL('/getReceiptItem', window.location.origin);
    url.searchParams.append('index', index);
    const response = await fetch(url);
    data =  await response.json();
    console.log(data)
    receipt_item = data.receipt_item;
    return receipt_item
}

async function fetchReceipt(){
    const url = new URL('/getReceipt', window.location.origin);
    url.searchParams.append('id', receipt_id);
    const response = await fetch(url);
    data =  await response.json();
    receipt = data.receipt;
    receipt_items = data.receipt_items
};

async function propagateInfo(){
    document.getElementById('receipt_id').innerHTML = receipt[1]
    document.getElementById('database_id').innerHTML = `Database ID: ${receipt[0]}`
    document.getElementById('status').innerHTML = receipt[2]
    document.getElementById('created').innerHTML = receipt[3]
    document.getElementById('vendor_name').value = receipt[8]
    document.getElementById('vendor_number').value = receipt[12]
    document.getElementById('vendor_address').value = receipt[9]
    M.Forms.textareaAutoResize(document.getElementById('vendor_address'));
};

async function propagateItems(){
    const table = document.getElementById('item_table')
    while (table.rows.length > 1) {
        table.deleteRow(1);
    };
    let reference_state = 1
    receipt_items.sort((a, b) => a[0] - b[0])
    for (let i = 0; i < receipt_items.length; i++){
        var row = table.insertRow();
        if (receipt_items[i][7] == "Resolved" || receipt_items[i][7] == "Voided"){
            row.classList.add("disabled-row")
        }
        
        var row_type = row.insertCell();
        var row_barcode = row.insertCell();
        var row_name = row.insertCell();
        var row_qty = row.insertCell();
        var row_cost = row.insertCell();
        var row_status = row.insertCell();

        row_type.innerHTML = receipt_items[i][1]
        row_barcode.innerHTML = receipt_items[i][3]
        row_name.innerHTML = receipt_items[i][4]
        row_qty.innerHTML = receipt_items[i][5]
        row_cost.innerHTML = receipt_items[i][6][28]
        row_status.innerHTML = receipt_items[i][7]

        if ((reference_state % 2) == 0){
            row.classList.add('green')
            row.classList.add('lighten-5')
        }
        row.classList.add("custom_row")
        row.addEventListener('click', function(){
            modify_item(receipt_items[i][0])
        })
        reference_state++
    };

}

async function modify_item(index){
    console.log(index)
    item = await fetchReceiptItem(index)
    console.log(item)
    const modal = document.getElementById("modify_item")
    var instance = M.Modal.getInstance(modal);
    document.getElementById('item_barcode').value = item[3]
    document.getElementById('item_database_id').value = item[0]
    document.getElementById('item_type').value = item[1]
    document.getElementById('item_name').value = item[4]
    document.getElementById('item_qty').value = item[5]
    document.getElementById('item_cost').value = item[6][28]
    instance.open()
}

async function saveItem(){
    let index = document.getElementById('item_database_id').value
    console.log(index)
    const url = new URL('/saveReceiptItem', window.location.origin);
    await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            index: index,
            cost: parseFloat(document.getElementById('item_cost').value),
            qty: parseFloat(document.getElementById('item_qty').value),
            barcode: document.getElementById('item_barcode').value
        })
    })
    await updateReceipt();
    const modal = document.getElementById("modify_item")
    var instance = M.Modal.getInstance(modal);
    instance.close()
}


async function deleteItem(){
    let index = document.getElementById('item_database_id').value
    const url = new URL('/deleteReceiptItem', window.location.origin);
    await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            index: index 
        })
    })
    await updateReceipt();
    const modal = document.getElementById("modify_item")
    var instance = M.Modal.getInstance(modal);
    instance.close()
}

async function voidItem(){
    let index = document.getElementById('item_database_id').value
    const url = new URL('/voidReceiptItem', window.location.origin);
    await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            index: index 
        })
    })
    await updateReceipt();
    const modal = document.getElementById("modify_item")
    var instance = M.Modal.getInstance(modal);
    instance.close()
}


async function resolveItem(){
    let index = document.getElementById('item_database_id').value
    console.log(index)
    await saveItem()
    const url = new URL('/resolveReceiptItem', window.location.origin);
    await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            index: index 
        })
    })
    await updateReceipt();
    const modal = document.getElementById("modify_item")
    var instance = M.Modal.getInstance(modal);
    instance.close()
}

async function fetchVendors(){
    const url = new URL('/getVendors', window.location.origin);
    const response = await fetch(url);
    data =  await response.json();
    var vendors = data.vendors;
    return vendors
}

async function selectVendor(index){
    const url = new URL('/saveReceipt', window.location.origin);
    await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            vendor_index: index,
            receipt_index: receipt[0]
        })
    })
    await updateReceipt();
    const modal = document.getElementById("vendors")
    var instance = M.Modal.getInstance(modal);
    instance.close()
}

async function populateVendors() {
    const modal = document.getElementById("vendors")
    var instance = M.Modal.getInstance(modal);
    vendors = await fetchVendors()
    console.log(vendors)
    instance.open()

    var table = document.getElementById("vendors_table")
    while (table.rows.length > 0) {
        table.deleteRow(0);
    }
    const header = table.createTHead();
    const row = header.insertRow(0);

    var header_database_id = row.insertCell();
    header_database_id.classList.add('center')
    var header_name = row.insertCell();
    header_name.classList.add('center')
    var header_address = row.insertCell();
    header_address.classList.add('center')
    var header_number = row.insertCell();
    header_number.classList.add('center')



    header_database_id.innerHTML = `ID`;
    header_name.innerHTML = `Name`;
    header_address.innerHTML = `Address`;
    header_number.innerHTML = `Phone Number`;

    let colorstate = 1;
    for (let i = 0; i < vendors.length; i++){
        
        var vendor_row = table.insertRow();
            
        var row_id = vendor_row.insertCell();
        row_id.classList.add('center');
        var row_name = vendor_row.insertCell();
        row_name.classList.add('center');
        var row_address = vendor_row.insertCell();
        row_address.classList.add('center');
        var row_number = vendor_row.insertCell();
        row_number.classList.add('center');
                
        row_id.innerHTML = vendors[i][0];
        row_name.innerHTML = vendors[i][1];
        row_address.innerHTML = vendors[i][2];
        row_number.innerHTML = vendors[i][5];



        if ((colorstate % 2) == 0){
            vendor_row.classList.add('green')
            vendor_row.classList.add('lighten-5')
        }
        vendor_row.classList.add("custom_row")
        vendor_row.addEventListener('click', function(){
            selectVendor(vendors[i][0])
        })
        colorstate++
    }
}