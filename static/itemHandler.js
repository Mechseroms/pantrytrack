async function fetchItem() {
    const url = new URL('/getItem', window.location.origin);
    url.searchParams.append('id', item_id);
    const response = await fetch(url);
    data =  await response.json();
    item = data.item;
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

async function setupZones() {
    let primary_zone = document.getElementById('primary_zone')

    for (let i = 0; i < zones.length; i++){
        let option = document.createElement('option')
        option.value = zones[i]
        option.innerHTML = zones[i]
        primary_zone.appendChild(option)
    };

    let issue_zone = document.getElementById('issue_zone')
    for (let i = 0; i < zones.length; i++){
        let option = document.createElement('option')
        option.value = zones[i]
        option.innerHTML = zones[i]
        issue_zone.appendChild(option)
    };

};

async function loadPrimaryLocations() {
    let primary_zone = document.getElementById('primary_zone').value
    primary_locations = await fetchLocations(primary_zone)
    await setupLocations(primary_locations, 'primary_location')
};

async function loadIssueLocations() {
    let issue_zone = document.getElementById('issue_zone').value
    issue_locations = await fetchLocations(issue_zone)
    await setupLocations(issue_locations, 'issue_location')
};

async function addLink(){
    event.preventDefault()
    let key = document.getElementById('link_name').value;
    let link = document.getElementById('link').value;
    links[key] = link;
    console.log(links)
    links_changed = true;
    await propagateLinks()
};

function updatePrimaryLocation(){
    let primary_zone = document.getElementById('primary_zone').value
    let primary_location = document.getElementById('primary_location').value

    if (primary_location == "undefined"){
        document.getElementById('primary_location').style = "border-color: red;"
    } else {
        document.getElementById('primary_location').style = ""
        logistics_info['primary_location'] = `${primary_zone}@${primary_location}`
    };
    console.log(logistics_info)
};

function updateIssueLocation(){
    let issue_zone = document.getElementById('issue_zone').value
    let issue_location = document.getElementById('issue_location').value

    if (issue_location == "undefined"){
        document.getElementById('issue_location').style = "border-color: red;"
    } else {
        document.getElementById('issue_location').style = ""
        logistics_info['auto_issue_location'] = `${issue_zone}@${issue_location}`
    };
};

function updateEntryType(){
    updated['row_type'] = document.getElementById('entry_type').value;
    console.log(updated)
};

function updateItemType(){
    updated['item_type'] = document.getElementById('item_type').value;
    console.log(updated)
};

function updatePackaging(){
    let packaging = document.getElementById('packaging').value;
    item_info['packaging'] = packaging;
    console.log(item_info)
};

function updateUOM(){
    let uom = document.getElementById('uom').value;
    item_info['uom'] = uom;
    console.log(item_info)
};

function updateCost(){
    let cost = document.getElementById('cost').value;
    item_info['cost'] = parseFloat(cost);
    console.log(item_info)
};

function updateSafetyStock(){
    let safety_stock = document.getElementById('safety_stock').value;
    item_info['safety_stock'] = parseFloat(safety_stock);
    console.log(item_info)
};

function updateLeadTimeDays(){
    let lead_time_days = document.getElementById('lead_time_days').value;
    item_info['lead_time_days'] = parseFloat(lead_time_days);
    console.log(item_info)
};

function updateAiPickable(){
    let ai_pick = document.getElementById('ai_pickable');
    item_info['ai_pick'] = ai_pick.checked;
    console.log(item_info)
};

function updateExpires(){
    let expires = document.getElementById('expires');
    food_info['expires'] = expires.checked;
    console.log(food_info)
};

function updateNutrients(){
    nutrients = {
        serving: document.getElementById('serving').value,
        serving_unit: document.getElementById('serving_unit').value,
        calories: document.getElementById('calories').value,
        calories_unit: document.getElementById('calories_unit').value,
        proteins: document.getElementById('proteins').value,
        proteins_unit: document.getElementById('proteins_unit').value,
        fats: document.getElementById('fats').value,
        fats_unit: document.getElementById('fats_unit').value,
        carbohydrates: document.getElementById('carbohydrates').value,
        carbohydrates_unit: document.getElementById('carbohydrates_unit').value,
        sugars: document.getElementById('sugars').value,
        sugars_unit: document.getElementById('sugars_unit').value,
        sodium: document.getElementById('sodium').value,
        sodium_unit: document.getElementById('sodium_unit').value,
        fibers: document.getElementById('fibers').value,
        fibers_unit: document.getElementById('fibers_unit').value
    };
    console.log(nutrients)
    nutrients_changed = true;
    

}

async function saveItem() {

    // Only add the key, values if something has changed
    if (food_groups_changed){
        food_info['food_groups'] = food_groups;
    };
    if (tags_changed){
        updated['tags'] = tags;
    };
    if (ingrediants_changed){
        food_info['ingrediants'] = ingrediants;
    };
    if (nutrients_changed){
        food_info['nutrients'] = nutrients;
    };
    if (links_changed){
        updated['links'] = links;
    };

    console.log(`going into fetch ${logistics_info}`)

    await fetch(`/updateItem`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: item_id,
            logistics_info_id: item[8],
            food_info_id: item[9],
            item_info_id: item[7],
            updated: updated,
            item_info: item_info,
            logistics_info: logistics_info,
            food_info: food_info,
        }),
    });
    M.toast({html: "Item has been saved successfully!", classes: "rounded green lighten-4 black-text"});
};
