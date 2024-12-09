let current_page = 1
let end_page;
let limit = 50
let search_text = ""
let zones;
let barcode = ""
let item_name = ""
let logistics_info_id = 0

async function setupZones() {
    let primary_zone = document.getElementById('zone')

    for (let i = 0; i < zones.length; i++){
        let option = document.createElement('option')
        option.value = zones[i]
        option.innerHTML = zones[i]
        primary_zone.appendChild(option)
    };
};

async function fetchZones() {
    const url = new URL('/getZones', window.location.origin);
    const response = await fetch(url);
    data =  await response.json();
    zones = data.zones;
};

async function fetchLocations(zone) {
    const url = new URL('/getLocations', window.location.origin);
    url.searchParams.append('zone', zone);
    const response = await fetch(url);
    data =  await response.json();
    return data.locations;
};

async function loadLocations() {
    let zone = document.getElementById('zone').value
    let locations = await fetchLocations(zone)
    await setupLocations(locations, 'location')
};

async function setupLocations(locations, el) {
    let loc_el = document.getElementById(el)
    console.log(locations)
    loc_el.innerHTML = ""

    let option = document.createElement('option')
        option.value = "undefined"
        option.innerHTML = "Select Location..."
        loc_el.appendChild(option)

    for (let i = 0; i < locations.length; i++){
        let option = document.createElement('option')
        option.value = locations[i]
        option.innerHTML = locations[i]
        loc_el.appendChild(option)
    };
};

async function fetchItems(){
    if (current_page === 1){
        document.getElementById('back').classList.add("disabled")
        document.getElementById('back').classList.remove("waves-effect")
    } else { 
        document.getElementById('back').classList.remove("disabled")
        document.getElementById('back').classList.add("waves-effect")
    };

    const url = new URL('/getItems', window.location.origin);
    url.searchParams.append('page', current_page);
    url.searchParams.append('limit', limit);            
    await fetch(url)
    .then(response => response.json())
    .then(data => {
        console.log(data)
        end_page = parseInt(data.end)
        if (current_page === end_page){
            document.getElementById('forward').classList.add("disabled")
            document.getElementById('forward').classList.remove("waves-effect")
        } else {
            document.getElementById('forward').classList.remove("disabled")
            document.getElementById('forward').classList.add("waves-effect")
        };
        
        // This is to populate the item table!
        var table = document.getElementById("item_table")
        while (table.rows.length > 0) {
            table.deleteRow(0);
        }
        const header = table.createTHead();
        const row = header.insertRow(0);

        var header_database_id = row.insertCell();
        header_database_id.classList.add('center')
        var header_barcode = row.insertCell();
        header_barcode.classList.add('center')
        var header_name = row.insertCell();
        header_name.classList.add('center')
        header_name.classList.add('hide-on-med-and-down')

        header_database_id.innerHTML = `<b>Database ID</b>`;
        header_barcode.innerHTML = `<b>Barcode</b>`;
        header_name.innerHTML = `<b>Product Name</b>`;

        let colorstate = 1;
        data.items.forEach(transaction => {
            console.log(transaction)
            var row = table.insertRow();
            
            var row_id = row.insertCell();
            row_id.classList.add('center')
            var row_barcode = row.insertCell();
            row_barcode.classList.add('center')
            var row_name = row.insertCell();
            row_name.classList.add('hide-on-med-and-down')
            row_name.classList.add('center')
            

            row_id.innerHTML = transaction[0];
            row_barcode.innerHTML = transaction[1];
            row_name.innerHTML = transaction[2];


            if ((colorstate % 2) == 0){
                row.classList.add('grey')
                row.classList.add('lighten-5')
            }
            row.classList.add("custom_row")
            row.addEventListener('click', function(){
                clickRow(transaction[0])
            })
            colorstate++
        });
    })
}

async function populateLocations(locations) {
    console.log(locations)
    var table = document.getElementById("location_table")
    while (table.rows.length > 0) {
        table.deleteRow(0);
    }
    const header = table.createTHead();
    const row = header.insertRow(0);

    var header_database_id = row.insertCell();
    header_database_id.classList.add('center')
    var header_barcode = row.insertCell();
    header_barcode.classList.add('center')
    var header_name = row.insertCell();
    header_name.classList.add('center')

    header_database_id.innerHTML = `Zone`;
    header_barcode.innerHTML = `Location`;
    header_name.innerHTML = `QOH`;

    let colorstate = 1;
    for (let key in locations){
        console.log(key);
        
        var location_row = table.insertRow();
            
        var row_zone = location_row.insertCell();
        row_zone.classList.add('center');
        var row_location = location_row.insertCell();
        row_location.classList.add('center');
        var row_qoh = location_row.insertCell();
        row_qoh.classList.add('center');
        
        let r_location = key.split("@");

        row_zone.innerHTML = r_location[0];
        row_location.innerHTML = r_location[1];
        row_qoh.innerHTML = locations[key];


        if ((colorstate % 2) == 0){
            location_row.classList.add('grey')
            location_row.classList.add('lighten-5')
        }
        location_row.classList.add("custom_row")
        location_row.addEventListener('click', function(){
            clickRowLocation(r_location)
        })
        colorstate++
    }
}

async function clickRow(database_id){
    let item = await fetchItem(database_id);
    await populateFields(item)
    await populateLocations(item[18])
    let modal = document.getElementById("item_modal")
    var instance = M.Modal.getInstance(modal)
    instance.close()
};

async function clickRowLocation(location){
    console.log(location)
    let modal = document.getElementById("locations")
    var instance = M.Modal.getInstance(modal)
    await setLocation(location[0], location[1])
    instance.close()
};

async function populateFields(item){
    barcode = item[1]
    item_name = item[2]
    logistics_info_id = item[8]
    document.getElementById("database_id").value = item[0];
    document.getElementById("database_id").style = "";
    document.getElementById("barcode").value = item[1];
    document.getElementById("barcode").style = "";
    document.getElementById("name").value = item[2];
    document.getElementById("QOH").value = item[19];
    document.getElementById("UOM").value = item[27];
    document.getElementById("transaction_cost").value = item[28];

    let location = item[16].split('@')
    await setLocation(location[0], location[1])
}

async function setLocation(zone, location){
    document.getElementById('zone').value = zone
    document.getElementById('zone').style = ""
    await loadLocations()
    document.getElementById('location').value = location
    document.getElementById('location').style = ""
};

async function fetchItem(database_id){
    const url = new URL('/getItem', window.location.origin);
    url.searchParams.append('id', database_id);
    const response = await fetch(url);
    data =  await response.json();
    return data.item;
}

function validateSubmit(){
    var checked = true;
    let database_id = document.getElementById('database_id')
    let barcode = document.getElementById("barcode")
    let zone = document.getElementById('zone')
    let loc = document.getElementById('location')
    let trans_type = document.getElementById("trans_type")
    let qty = document.getElementById('transaction_quantity')

    if (database_id.value == ""){
        database_id.style = "border-color: red;"
        checked = false;
    } else {
        database_id.style = ""
    }
    if (barcode.value == ""){
        barcode.style = "border-color: red;"
        checked = false;
    } else {
        barcode.style = ""
    }
    if (trans_type.value == ""){
        trans_type.style = "border-color: red;"
        checked = false;
    } else {
        trans_type.style = ""
    }
    if (parseFloat(qty.value) == 0.0 || Number.isNaN(parseFloat(qty.value))){
        qty.style = "border-color: red;"
        checked = false;
    }
    if (zone.value == ""){
        zone.style = "border-color: red;"
        checked = false;
    }
    if (loc.value == ""){
        loc.style = "border-color: red;"
        checked = false;
    } else {
        loc.style = ""
    }

    return checked;
}

function addTransaction() {
    let zone = document.getElementById('zone').value
    let loc = document.getElementById('location').value
    let location = `${zone}@${loc}`
    let barcode = document.getElementById("barcode").value
    let trans_type = document.getElementById("trans_type").value
    let trans_cost = parseFloat(document.getElementById("transaction_cost").value)
    let qty = parseFloat(document.getElementById('transaction_quantity').value)

    var result = validateSubmit();

    console.log(result)
    if (result === true){
        fetch(`/transact`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                logistics_info_id: logistics_info_id,
                barcode: barcode,
                name: item_name,
                location: location,
                qty: qty,
                trans_type: trans_type,
                trans_cost: trans_cost
            }),
        });
        M.toast({text: 'Transaction Complete!'})
        document.getElementById('transaction_quantity').value = "";
    } else {
        M.toast({text: 'Please ensure your receipt is filled out.'})
    }

}

document.getElementById('forward').addEventListener('click', async function(){
    current_page++
    await fetchItems()
})

document.getElementById('back').addEventListener('click', async function(){
    current_page--
    await fetchItems()
})