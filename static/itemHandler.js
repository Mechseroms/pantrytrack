async function addLink(){
    event.preventDefault()
    let key = document.getElementById('link_name').value;
    let link = document.getElementById('link').value;
    links[key] = link;
    console.log(links)
    await propagateLinks()
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

