let current_page = 1
let end_page;
let limit = 50
let search_text = ""
let zones;

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

async function clickRow(database_id){
    let item = await fetchItem(database_id);
    await populateFields(item)

};

async function populateFields(item){
    document.getElementById("database_id").value = item[0];
    document.getElementById("barcode").value = item[1];
    document.getElementById("name").value = item[2];
    document.getElementById("QOH").value = item[19];

    let location = item[16].split('@')
    await setLocation(location[0], location[1])
}

async function setLocation(zone, location){
    document.getElementById('zone').value = zone
    await loadLocations()
    document.getElementById('location').value = location
};

async function fetchItem(database_id){
    const url = new URL('/getItem', window.location.origin);
    url.searchParams.append('id', database_id);
    const response = await fetch(url);
    data =  await response.json();
    return data.item;
}

document.getElementById('forward').addEventListener('click', async function(){
    current_page++
    await fetchItems()
})

document.getElementById('back').addEventListener('click', async function(){
    current_page--
    await fetchItems()
})