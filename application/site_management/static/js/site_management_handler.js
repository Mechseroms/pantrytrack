async function changeSite(site){
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

document.addEventListener('DOMContentLoaded', async function() {
    let zones = await fetchZones()
    await updateZonesPagination()
    await replensihZonesTable(zones)

    let locations = await fetchLocations()
    await updateLocationsPagination()
    await replenishLocationsTable(locations)

    let vendors = await fetchVendors()
    await updateVendorsPagination()
    await replenishVendorsTable(vendors)

    let brands = await fetchBrands()
    await updateBrandsPagination()
    await replenishBrandsTable(brands)

    let prefixes = await fetchPrefixes()
    await updatePrefixesPagination()
    await replenishPrefixesTable(prefixes)

});

// ZONES TAB FUNCTIONS
let zones_current_page = 1
let zones_end_page = 10
let zones_limit = 25
async function fetchZones(){
    const url = new URL('/site-management/api/getZones', window.location.origin)
    url.searchParams.append('page', zones_current_page)
    url.searchParams.append('limit', zones_limit)
    const response = await fetch(url)
    data = await response.json()
    zones_end_page = data.end
    return data.zones
}

async function replensihZonesTable(zones){
    let zonesTableBody = document.getElementById('zonesTableBody')
    zonesTableBody.innerHTML = ""

    for(let i=0; i < zones.length; i++){
        let tableRow = document.createElement('tr')


        let idCell = document.createElement('td')
        idCell.innerHTML = `${zones[i].id}`
        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${zones[i].name}`
        let descriptionCell = document.createElement('td')
        descriptionCell.innerHTML = `${zones[i].description}`
        let opCell = document.createElement('td')
        opCell.innerHTML = ``

        let editOp = document.createElement('button')
        editOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        editOp.innerHTML = "edit"
        editOp.onclick = async function () {
            await openEditZoneModal(zones[i])
        }

        opCell.append(editOp)
        tableRow.append(idCell, nameCell, descriptionCell, opCell)
        zonesTableBody.append(tableRow)
    }
}

async function updateZonesPagination() {
    let paginationElement = document.getElementById("zonesPagination");
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(zones_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setZonePage(${zones_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(zones_current_page<=1){
        firstElement.innerHTML = `<a>1</a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setZonePage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(zones_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(zones_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick=setZonePage(${zones_current_page-1})>${zones_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(zones_current_page!=1 && zones_current_page != zones_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${zones_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(zones_current_page+2<zones_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick=setZonePage(${zones_current_page+1})>${zones_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(zones_current_page+2<=zones_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(zones_current_page>=zones_end_page){
        endElement.innerHTML = `<a>${zones_end_page}</a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setZonePage(${zones_end_page})">${zones_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(zones_current_page>=zones_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setZonePage(${zones_current_page+1})"><span uk-pagination-next></span></a>`;
    }
    paginationElement.append(nextElement)
}

async function setZonePage(pageNumber){
    zones_current_page = pageNumber;
    let zones = await fetchZones()
    await updateZonesPagination()
    await replensihZonesTable(zones)
}

async function openAddZoneModal() {
    document.getElementById('ZonesModalHeader').innerHTML = "Add Zone to system..."
    document.getElementById('ZonesModalSubmitButton').innerHTML = "Add"
    document.getElementById('ZoneName').value = ""
    document.getElementById('ZoneName').classList.remove('uk-disabled')
    document.getElementById('ZoneDescription').value = ""
    document.getElementById('ZonesModalSubmitButton').onclick = async function() {
        await postAddZone()
    }
    UIkit.modal(document.getElementById('ZonesModal')).show();
}

async function openEditZoneModal(zone) {
    document.getElementById('ZonesModalHeader').innerHTML = `Edit Zone: ${zone.name}...`
    document.getElementById('ZonesModalSubmitButton').innerHTML = "Save"
    document.getElementById('ZoneName').value = zone.name
    document.getElementById('ZoneName').classList.add('uk-disabled')
    document.getElementById('ZoneDescription').value = zone.description
    document.getElementById('ZonesModalSubmitButton').onclick = async function() {
        await postEditZone(zone.id)
    }
    UIkit.modal(document.getElementById('ZonesModal')).show();
}

async function postAddZone() {
    let zoneName = `${document.getElementById('ZoneName').value}`
    let description = `${document.getElementById('ZoneDescription').value}`

    const response = await fetch(`/site-management/api/postAddZone`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: zoneName,
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
    let zones = await fetchZones()
    await updateZonesPagination()
    await replensihZonesTable(zones)
    UIkit.modal(document.getElementById('ZonesModal')).hide();
}

async function postEditZone(zone_id) {
    let description = `${document.getElementById('ZoneDescription').value}`

    const response = await fetch(`/site-management/api/postEditZone`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            zone_id: zone_id,
            update: {'description': description}
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
    let zones = await fetchZones()
    await updateZonesPagination()
    await replensihZonesTable(zones)
    UIkit.modal(document.getElementById('ZonesModal')).hide();
}

// LOCATIONS TAB FUNCTIONS
let locations_current_page = 1
let locations_end_page = 10
let locations_limit = 25
async function fetchLocations(){
    const url = new URL('/site-management/api/getLocations', window.location.origin)
    url.searchParams.append('page', locations_current_page)
    url.searchParams.append('limit', locations_limit)
    const response = await fetch(url)
    data = await response.json()
    locations_end_page = data.end
    return data.locations
}

async function replenishLocationsTable(locations){
    let locationsTableBody = document.getElementById('locationsTableBody')
    locationsTableBody.innerHTML = ""

    for(let i=0; i < locations.length; i++){
        let tableRow = document.createElement('tr')


        let idCell = document.createElement('td')
        idCell.innerHTML = `${locations[i].id}`
        let uuidCell = document.createElement('td')
        uuidCell.innerHTML = `${locations[i].uuid}`
        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${locations[i].name}`
        let descriptionCell = document.createElement('td')
        descriptionCell.innerHTML = ``
        let opCell = document.createElement('td')
        opCell.innerHTML = ``

        tableRow.append(idCell, uuidCell,nameCell, descriptionCell, opCell)
        locationsTableBody.append(tableRow)
    }
}

async function updateLocationsPagination() {
    let paginationElement = document.getElementById("locationsPagination");
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(locations_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setLocationsPage(${locations_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(locations_current_page<=1){
        firstElement.innerHTML = `<a>1</a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setLocationsPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(locations_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(locations_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick=setLocationsPage(${locations_current_page-1})>${locations_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(locations_current_page!=1 && locations_current_page != locations_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${locations_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(locations_current_page+2<locations_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick=setLocationsPage(${locations_current_page+1})>${locations_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(locations_current_page+2<=locations_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(locations_current_page>=locations_end_page){
        endElement.innerHTML = `<a>${locations_end_page}</a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setLocationsPage(${locations_end_page})">${locations_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(locations_current_page>=locations_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setLocationsPage(${locations_current_page+1})"><span uk-pagination-next></span></a>`;
    }
    paginationElement.append(nextElement)
}

async function setLocationsPage(pageNumber){
    locations_current_page = pageNumber;
    let locations = await fetchLocations()
    await updateLocationsPagination()
    await replenishLocationsTable(locations)
}

async function openAddLocationModal() {
    document.getElementById('LocationsModalHeader').innerHTML = "Add Location to system..."
    document.getElementById('LocationsModalSubmitButton').innerHTML = "Add"
    document.getElementById('LocationUUID').value = ""
    document.getElementById('LocationName').value = ""
    document.getElementById('LocationName').classList.remove('uk-disabled')
    document.getElementById('LocationsModalSubmitButton').onclick = async function() {
        await postAddLocation()
    }
    UIkit.modal(document.getElementById('LocationsModal')).show();
}

async function postAddLocation() {
    let zone_id = parseInt(`${document.getElementById('LocationZoneId').value}`)
    let locationName = `${document.getElementById('LocationName').value}`
    let zone_name = document.getElementById(`locationzone_${zone_id}`).innerHTML
    let uuid = `${zone_name}@${locationName}`

    const response = await fetch(`/site_management/api/postAddLocation`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            uuid: uuid,
            name: locationName,
            zone_id: zone_id
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
    let locations = await fetchLocations()
    await updateLocationsPagination()
    await replenishLocationsTable(locations)
    UIkit.modal(document.getElementById('LocationsModal')).hide();
}

// VENDORS TAB FUNCTIONS
let vendors_current_page = 1
let vendors_end_page = 10
let vendors_limit = 25
async function fetchVendors(){
    const url = new URL('/site-management/api/getVendors', window.location.origin)
    url.searchParams.append('page', vendors_current_page)
    url.searchParams.append('limit', vendors_limit)
    const response = await fetch(url)
    data = await response.json()
    vendors_end_page = data.end
    return data.vendors
}

async function replenishVendorsTable(vendors){
    let vendorsTableBody = document.getElementById('vendorsTableBody')
    vendorsTableBody.innerHTML = ""

    for(let i=0; i < vendors.length; i++){
        let tableRow = document.createElement('tr')

        let idCell = document.createElement('td')
        idCell.innerHTML = `${vendors[i].id}`
        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${vendors[i].vendor_name}`
        let createdByCell = document.createElement('td')
        createdByCell.innerHTML = `${vendors[i].created_by}`
        let opCell = document.createElement('td')
        opCell.innerHTML = ``

        let editOp = document.createElement('button')
        editOp.innerHTML = "edit"
        editOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        editOp.onclick = async function () {
            await openEditVendorsModal(vendors[i])
        }

        opCell.append(editOp)
        tableRow.append(idCell,nameCell, createdByCell, opCell)
        vendorsTableBody.append(tableRow)
    }
}

async function updateVendorsPagination() {
    let paginationElement = document.getElementById("vendorsPagination");
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(vendors_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setVendorsPage(${vendors_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(vendors_current_page<=1){
        firstElement.innerHTML = `<a>1</a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setVendorsPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(vendors_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(vendors_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick=setVendorsPage(${vendors_current_page-1})>${vendors_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(vendors_current_page!=1 && vendors_current_page != vendors_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${vendors_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(vendors_current_page+2<vendors_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick=setVendorsPage(${vendors_current_page+1})>${vendors_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(vendors_current_page+2<=vendors_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(vendors_current_page>=vendors_end_page){
        endElement.innerHTML = `<a>${vendors_end_page}</a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setVendorsPage(${vendors_end_page})">${vendors_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(vendors_current_page>=vendors_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setVendorsPage(${vendors_current_page+1})"><span uk-pagination-next></span></a>`;
    }
    paginationElement.append(nextElement)
}

async function setVendorsPage(pageNumber){
    vendors_current_page = pageNumber;
    let vendors = await fetchVendors()
    await updateVendorsPagination()
    await replenishVendorsTable(vendors)
}

async function openAddVendorsModal() {
    document.getElementById('VendorsModalHeader').innerHTML = "Add Vendor to system..."
    document.getElementById('VendorsModalSubmitButton').innerHTML = "Add"
    document.getElementById('VendorName').value = ""
    document.getElementById('VendorPhoneNumber').value = ""
    document.getElementById('VendorAddress').value = ""
    document.getElementById('vendor_created').value = ""
    document.getElementById('vendor_created_by').value = ""
    document.getElementById('VendorsModalSubmitButton').onclick = async function() {
        await postAddVendor()
    }
    UIkit.modal(document.getElementById('VendorsModal')).show();
}

async function openEditVendorsModal(vendor) {
    document.getElementById('VendorsModalHeader').innerHTML = `Edit Vendor: ${vendor.vendor_name}`
    document.getElementById('VendorsModalSubmitButton').innerHTML = "Edit"
    document.getElementById('VendorName').value = vendor.vendor_name
    document.getElementById('VendorPhoneNumber').value = vendor.phone_number
    document.getElementById('VendorAddress').value = vendor.vendor_address
    document.getElementById('vendor_created').value = vendor.creation_date
    document.getElementById('vendor_created_by').value = vendor.created_by
    document.getElementById('VendorsModalSubmitButton').onclick = async function() {
        await postEditVendor(vendor.id)
    }
    UIkit.modal(document.getElementById('VendorsModal')).show();
}

async function postAddVendor() {
    let vendor_name = document.getElementById('VendorName').value
    let vendor_phone_number = document.getElementById('VendorPhoneNumber').value
    let vendor_address = document.getElementById('VendorAddress').value

    const response = await fetch(`/site-management/api/postAddVendor`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            vendor_name: vendor_name,
            vendor_phone_number: vendor_phone_number,
            vendor_address: vendor_address
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
    let vendors = await fetchVendors()
    await updateVendorsPagination()
    await replenishVendorsTable(vendors)
    UIkit.modal(document.getElementById('VendorsModal')).hide();
}

async function postEditVendor(vendor_id) {
    let vendor_name = document.getElementById('VendorName').value
    let vendor_phone_number = document.getElementById('VendorPhoneNumber').value
    let vendor_address = document.getElementById('VendorAddress').value

    const response = await fetch(`/site-management/api/postEditVendor`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            vendor_id: vendor_id,
            update: {'vendor_name': vendor_name, 'phone_number': vendor_phone_number, 'vendor_address': vendor_address}
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
    let vendors = await fetchVendors()
    await updateVendorsPagination()
    await replenishVendorsTable(vendors)
    UIkit.modal(document.getElementById('VendorsModal')).hide();
}

// BRANDS TAB FUNCTIONS
let brands_current_page = 1
let brands_end_page = 10
let brands_limit = 25
async function fetchBrands(){
    const url = new URL('/site-management/api/getBrands', window.location.origin)
    url.searchParams.append('page', brands_current_page)
    url.searchParams.append('limit', brands_limit)
    const response = await fetch(url)
    data = await response.json()
    brands_end_page = data.end
    return data.brands
}

async function replenishBrandsTable(brands){
    let brandsTableBody = document.getElementById('brandsTableBody')
    brandsTableBody.innerHTML = ""

    for(let i=0; i < brands.length; i++){
        let tableRow = document.createElement('tr')

        let idCell = document.createElement('td')
        idCell.innerHTML = `${brands[i].id}`
        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${brands[i].name}`
        let opCell = document.createElement('td')
        opCell.innerHTML = ``

        let editOp = document.createElement('button')
        editOp.innerHTML = "edit"
        editOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        editOp.onclick = async function() {
            await openEditBrandsModal(brands[i])
        }

        opCell.append(editOp)
        tableRow.append(idCell,nameCell, opCell)
        brandsTableBody.append(tableRow)
    }
}

async function updateBrandsPagination() {
    let paginationElement = document.getElementById("brandsPagination");
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(brands_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setBrandsPage(${brands_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(brands_current_page<=1){
        firstElement.innerHTML = `<a>1</a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setBrandsPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(brands_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(brands_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick=setBrandsPage(${brands_current_page-1})>${brands_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(brands_current_page!=1 && brands_current_page != brands_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${brands_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(brands_current_page+2<brands_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick=setBrandsPage(${brands_current_page+1})>${brands_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(brands_current_page+2<=brands_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(brands_current_page>=brands_end_page){
        endElement.innerHTML = `<a>${brands_end_page}</a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setBrandsPage(${brands_end_page})">${brands_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(brands_current_page>=brands_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setBrandsPage(${brands_current_page+1})"><span uk-pagination-next></span></a>`;
    }
    paginationElement.append(nextElement)
}

async function setBrandsPage(pageNumber){
    brands_current_page = pageNumber;
    let brands = await fetchBrands()
    await updateBrandsPagination()
    await replenishBrandsTable(brands)
}

async function openAddBrandsModal() {
    document.getElementById('BrandsModalHeader').innerHTML = "Add Vendor to system..."
    document.getElementById('BrandsModalSubmitButton').innerHTML = "Add"
    document.getElementById('BrandName').value = ""
    document.getElementById('BrandsModalSubmitButton').onclick = async function() {
        await postAddBrand()
    }
    UIkit.modal(document.getElementById('BrandsModal')).show();
}

async function openEditBrandsModal(brand) {
    document.getElementById('BrandsModalHeader').innerHTML = `Edit Brand: ${brand.name}`
    document.getElementById('BrandsModalSubmitButton').innerHTML = "Edit"
    document.getElementById('BrandName').value = brand.name
    
    document.getElementById('BrandsModalSubmitButton').onclick = async function() {
        await postEditBrand(brand.id)
    }
    UIkit.modal(document.getElementById('BrandsModal')).show();
}

async function postAddBrand() {
    let brand_name = document.getElementById('BrandName').value

    const response = await fetch(`/site-management/api/postAddBrand`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            brand_name: brand_name
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
    let brands = await fetchBrands()
    await updateBrandsPagination()
    await replenishBrandsTable(brands)
    UIkit.modal(document.getElementById('BrandsModal')).hide();
}

async function postEditBrand(brand_id) {
    let brand_name = document.getElementById('BrandName').value

    const response = await fetch(`/site-management/api/postEditBrand`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            brand_id: brand_id,
            update: {'name': brand_name}
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
    let brands = await fetchBrands()
    await updateBrandsPagination()
    await replenishBrandsTable(brands)
    UIkit.modal(document.getElementById('BrandsModal')).hide();
}

// PREFIXES TAB FUNCTIONS
let prefix_current_page = 1
let prefix_end_page = 10
let prefix_limit = 25
async function fetchPrefixes(){
    const url = new URL('/site-management/api/getPrefixes', window.location.origin)
    url.searchParams.append('page', prefix_current_page)
    url.searchParams.append('limit', prefix_limit)
    const response = await fetch(url)
    data = await response.json()
    prefix_end_page = data.end
    return data.prefixes
}

async function replenishPrefixesTable(prefixes){
    let prefixesTableBody = document.getElementById('prefixesTableBody')
    prefixesTableBody.innerHTML = ""

    for(let i=0; i < prefixes.length; i++){
        let tableRow = document.createElement('tr')

        let idCell = document.createElement('td')
        idCell.innerHTML = `${prefixes[i].id}`
        let uuidCell = document.createElement('td')
        uuidCell.innerHTML = `${prefixes[i].uuid}`
        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${prefixes[i].name}`
        let descriptionCell = document.createElement('td')
        descriptionCell.innerHTML = `${prefixes[i].description}`
        let opCell = document.createElement('td')
        opCell.innerHTML = ``

        let editOp = document.createElement('button')
        editOp.innerHTML = "edit"
        editOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        editOp.onclick = async function() {
            await openEditPrefixModal(prefixes[i])
        }

        opCell.append(editOp)

        tableRow.append(idCell,uuidCell, nameCell, descriptionCell, opCell)
        prefixesTableBody.append(tableRow)
    }
}

async function updatePrefixesPagination() {
    let paginationElement = document.getElementById("prefixesPagination");
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(prefix_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setPrefixesPage(${prefix_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(prefix_current_page<=1){
        firstElement.innerHTML = `<a>1</a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setPrefixesPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(prefix_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(prefix_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick=setPrefixesPage(${prefix_current_page-1})>${prefix_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(prefix_current_page!=1 && prefix_current_page != prefix_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${prefix_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(prefix_current_page+2<prefix_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick=setPrefixesPage(${prefix_current_page+1})>${prefix_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(prefix_current_page+2<=prefix_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(prefix_current_page>=prefix_end_page){
        endElement.innerHTML = `<a>${prefix_end_page}</a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setPrefixesPage(${prefix_end_page})">${prefix_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(prefix_current_page>=prefix_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setPrefixesPage(${prefix_current_page+1})"><span uk-pagination-next></span></a>`;
    }
    paginationElement.append(nextElement)
}

async function setPrefixesPage(pageNumber){
    prefix_current_page = pageNumber;
    let prefixes = await fetchPrefixes()
    await updatePrefixesPagination()
    await replenishPrefixesTable(prefixes)
}

async function openAddPrefixModal() {
    document.getElementById('PrefixModalHeader').innerHTML = "Add Prefix to system..."
    document.getElementById('PrefixModalSubmitButton').innerHTML = "Add"
    document.getElementById('PrefixUUID').value = ""
    document.getElementById('PrefixName').value = ""
    document.getElementById('PrefixDescription').value = ""
    document.getElementById('PrefixModalSubmitButton').onclick = async function() {
        await postAddPrefix()
    }
    UIkit.modal(document.getElementById('PrefixModal')).show();
}

async function openEditPrefixModal(prefix) {
    document.getElementById('PrefixModalHeader').innerHTML = `Edit Prefix: ${prefix.name}`
    document.getElementById('PrefixModalSubmitButton').innerHTML = "Edit"
    document.getElementById('PrefixUUID').value = prefix.uuid
    document.getElementById('PrefixName').value = prefix.name
    document.getElementById('PrefixDescription').value = prefix.description
    
    document.getElementById('PrefixModalSubmitButton').onclick = async function() {
        await postEditPrefix(prefix.id)
    }
    UIkit.modal(document.getElementById('PrefixModal')).show();
}

async function postAddPrefix() {
    let prefix_uuid = document.getElementById('PrefixUUID').value
    let prefix_name = document.getElementById('PrefixName').value
    let prefix_description = document.getElementById('PrefixDescription').value

    const response = await fetch(`/site-management/api/postAddPrefix`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prefix_uuid: prefix_uuid,
            prefix_name:prefix_name,
            prefix_description:prefix_description
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
    let prefixes = await fetchPrefixes()
    await updatePrefixesPagination()
    await replenishPrefixesTable(prefixes)
    UIkit.modal(document.getElementById('PrefixModal')).hide();
}

async function postEditPrefix(prefix_id) {
    let prefix_uuid = document.getElementById('PrefixUUID').value
    let prefix_name = document.getElementById('PrefixName').value
    let prefix_description = document.getElementById('PrefixDescription').value

    const response = await fetch(`/site-management/api/postEditPrefix`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prefix_id: prefix_id,
            update: {'name': prefix_name, 'uuid': prefix_uuid, 'description': prefix_description}
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
    let prefixes = await fetchPrefixes()
    await updatePrefixesPagination()
    await replenishPrefixesTable(prefixes)
    UIkit.modal(document.getElementById('PrefixModal')).hide();
}