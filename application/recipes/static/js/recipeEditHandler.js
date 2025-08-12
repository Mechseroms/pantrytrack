// Beginning of site specific code!
var recipe = [];
document.addEventListener('DOMContentLoaded', async function() {
    recipe = await getRecipe()
    console.log(recipe)
    await replenishRecipe()
});


async function replenishRecipe() {
    document.getElementById('title').innerHTML = `${recipe.name}`
    //document.getElementById('breadcrumb').innerHTML = `${recipe.name}`

    document.getElementById('recipeName').value = `${recipe.name}`
    document.getElementById('recipeCreationDate').value = `${recipe.creation_date}`
    document.getElementById('recipeAuthor').value = `${recipe.author}`
    document.getElementById('recipeDescription').value = `${recipe.description}`

    await replenishInstructions()
    await replenishIngrediants()
    await getImage()
}

async function replenishInstructions() {
    let instructions_list = document.getElementById('instructions_list')
    instructions_list.innerHTML = ''

    for(let i = 0; i < recipe.instructions.length; i++){
        let liElem = document.createElement('li')
        liElem.setAttribute('class', 'instruction-card')
        liElem.innerHTML = `${i+1}. ${recipe.instructions[i]}<button onclick="deleteInstruction(${i})" class="instruction-button">x</button>`
        instructions_list.append(liElem)
    }
}

async function replenishIngrediants() {
    let ingrediantsTableBody = document.getElementById('ingrediantsTableBody')
    ingrediantsTableBody.innerHTML = ""

    for(let i=0; i< recipe.recipe_items.length; i++){
        let tableRow = document.createElement('tr')

        let typeCell = document.createElement('td')
        typeCell.innerHTML = `${recipe.recipe_items[i].item_type}`

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${recipe.recipe_items[i].item_name}`

        let qtyCell = document.createElement('td')
        qtyCell.innerHTML = `${recipe.recipe_items[i].qty}`

        let uomCell = document.createElement('td')
        uomCell.innerHTML = `${recipe.recipe_items[i].uom.fullname}`

        tableRow.append(typeCell, nameCell, qtyCell, uomCell)

        tableRow.onclick = async function(){
            await openLineItemModal(recipe.recipe_items[i])
        }

        ingrediantsTableBody.append(tableRow)
    }

}

async function openLineItemModal(item){
    document.getElementById('lineHeader').innerHTML = `Edit ${item.uuid}...`
    document.getElementById('lineType').value = `${item.item_type}`
    document.getElementById('lineName').value = `${item.item_name}`
    document.getElementById('lineQty').value = `${item.qty}`
    document.getElementById('lineWeblink').value = `${item.links.main}`

    document.getElementById('lineUOM').innerHTML = ""

    if(item.item_type=="sku"){
        document.getElementById('lineName').classList.add('uk-disabled')
        document.getElementById('lineWeblink').classList.add('uk-disabled')
        let main_uom = document.createElement('option')
        main_uom.value = item.item_uom.id
        main_uom.innerHTML = item.item_uom.fullname

        document.getElementById('lineUOM').append(main_uom)

        for(let i=0; i<item.conversions.length; i++){
            let secondary_uom = document.createElement('option')
            secondary_uom.value = item.conversions[i].unit.id
            secondary_uom.innerHTML = item.conversions[i].unit.fullname

            document.getElementById('lineUOM').append(secondary_uom)
        }

    } else {
        document.getElementById('lineName').classList.remove('uk-disabled')
        document.getElementById('lineWeblink').classList.remove('uk-disabled')

        for(let i = 0; i < units.length; i++){
            let secondary_uom = document.createElement('option')
            secondary_uom.value = units[i].id
            secondary_uom.innerHTML = units[i].fullname
            document.getElementById('lineUOM').append(secondary_uom)
        }

    }
    document.getElementById('lineUOM').value = `${item.uom.id}`

    document.getElementById('deleteLineItemButton').onclick = async function() {
        await deleteLineItem(item.id)
    }

    document.getElementById('saveLineItemButton').onclick = async function() {
        await saveLineItem(item)
    }

    UIkit.modal(document.getElementById('editLineItem')).show();
}

async function deleteLineItem(index){
    const response = await fetch(`/recipes/deleteRecipeItem`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            id: index
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
    recipe = data.recipe
    await replenishRecipe()
    UIkit.modal(document.getElementById('editLineItem')).hide();
}

async function saveLineItem(item){
    item.links.main = document.getElementById('lineWeblink').value
    let line_update = {
        item_name: document.getElementById('lineName').value,
        qty: document.getElementById('lineQty').value,
        uom: document.getElementById('lineUOM').value,
        links: item.links
    }
    const response = await fetch(`/recipes/api/saveRecipeItem`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            id: item.id,
            update: line_update
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
    recipe = data.recipe
    await replenishRecipe()
    UIkit.modal(document.getElementById('editLineItem')).hide();
}

async function getRecipe() {
    const url = new URL('/recipes/getRecipe', window.location.origin)
    url.searchParams.append('id', recipe_id);
    const response = await fetch(url)
    data = await response.json()
    return data.recipe
}

async function getImage(){
    await fetch(`/recipes/getImage/${recipe.id}`)
    .then(response => response.blob())
    .then(imageBlob => {
        const imageURL = URL.createObjectURL(imageBlob);
        document.getElementById('recipeImage').src = imageURL;
    });
}

async function addCustomItem() {
    payload = {
        rp_id: recipe.id,
        item_type: document.getElementById('customType').value,
        item_name: document.getElementById('customName').value,
        qty: document.getElementById('customQty').value,
        uom: document.getElementById('customUOM').value,
        links: {main: document.getElementById('customWeblink').value}
    }
    const response = await fetch(`/recipes/postCustomItem`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify(payload),
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
    recipe = data.recipe
    await replenishRecipe()
    document.getElementById('customName').value = ""
    document.getElementById('customQty').value = ""
    document.getElementById('customUOM').value = ""
    document.getElementById('customWeblink').value = ""
    UIkit.modal(document.getElementById('addCustomItem')).hide();
}

async function addSKUItem(item_id) {
    const response = await fetch(`/recipes/postSKUItem`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            recipe_id: recipe.id,
            item_id: item_id
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
    recipe = data.recipe
    await replenishRecipe()
    UIkit.modal(document.getElementById('itemsModal')).hide();
}

async function addNewSKUItem() {
    let newSKUName = document.getElementById('newSKUName').value
    let newSKUSubtype = document.getElementById('newSKUSubtype').value
    let newSKUQty = parseFloat(document.getElementById('newSKUQty').value)
    let newSKUUOM = parseInt(document.getElementById('newSKUUOM').value)
    let newWeblink = document.getElementById('newWeblink').value
    let newSKUCost = parseFloat(document.getElementById('newSKUCost').value)


    const response = await fetch(`/recipes/api/postNewSKUItem`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            recipe_id: recipe.id,
            name: newSKUName,
            subtype: newSKUSubtype,
            qty: newSKUQty,
            uom_id: newSKUUOM,
            main_link: newWeblink,
            cost: newSKUCost
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
    recipe = data.recipe
    await replenishRecipe()
    UIkit.modal(document.getElementById('addNewSKUItem')).hide();
}


let updated = {}
async function postUpdate() {
    let description = document.getElementById('recipeDescription').value
    updated.description = description    
        
    const response = await fetch(`/recipes/postUpdate`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            recipe_id: recipe_id,
            update: updated
        }),
    });
    data = await response.json()
    message_type = "primary"
    if(data.error){
        message_type = "danger"
    } else {
        updated = {}
    }
    UIkit.notification({
        message: data.message,
        status: message_type,
        pos: 'top-right',
        timeout: 5000
    });
};

async function updateImage() {
    const fileInput = document.querySelector('input[type="file"]');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    await fetch(`/recipes/postImage/${recipe.id}`, {
    method: 'POST',
    body: formData
    })
    .then(response => response.json())
    .then(data => console.log('File uploaded!', data))
    .catch(error => console.error('Error:', error));
}

async function updateName() {
    updated.name = document.getElementById('recipeName').value
}

async function updateDescription() {
    updated.description = document.getElementById('recipeDescription').value
}

async function addInstruction() {
    let instruction = document.getElementById('addInstruction').value
    if(!document.getElementById('addInstruction').value==""){
        let instructions = recipe.instructions.slice()
        document.getElementById('addInstruction').value = ""
        instructions.push(instruction)
        recipe.instructions = instructions
        updated.instructions = instructions
        await replenishInstructions()
    }
}

async function deleteInstruction(index){
    recipe.instructions.splice(index, 1)
    let instructions = recipe.instructions.slice()
    recipe.instructions = instructions
    updated.instructions = instructions
    await replenishInstructions()
}


async function openNewSKUModal() {
    let itemsModal = document.getElementById('addNewSKUItem')
    document.getElementById('newSKUName').value = ""
    document.getElementById('newSKUSubtype').value = "FOOD"
    document.getElementById('newSKUQty').value = 1
    document.getElementById('newSKUUOM').value = "1"
    document.getElementById('newWeblink').value = ""
    document.getElementById('newSKUCost').value = 0.00
    UIkit.modal(itemsModal).show();
}

let pagination_current = 1;
let pagination_end = 10;
let search_string = "";
let items_limit = 25;
async function openSKUModal() {
    let itemsModal = document.getElementById('itemsModal')
    pagination_current = 1;
    search_string = '';
    document.getElementById('searchItemsInput').value = '';
    let items = await fetchItems()
    await updateItemsModalTable(items)
    await updateItemsPaginationElement()
    UIkit.modal(itemsModal).show();
}

async function searchItemTable(event) {
    if(event.key==='Enter'){
        search_string = event.srcElement.value
        let items = await fetchItems()
        await updateItemsModalTable(items)
        await updateItemsPaginationElement()
    }
}

async function setItemsPage(pageNumber){
    pagination_current = pageNumber;
    let items = await fetchItems()
    await updateItemsModalTable(items)
    await updateItemsPaginationElement()
}

async function updateItemsPaginationElement() {
    let paginationElement = document.getElementById('itemsPage');
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(pagination_current<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setItemsPage(${pagination_current-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(pagination_current<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setItemsPage(1)">1</a>`;
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
        lastElement.innerHTML = `<a onclick="setItemsPage(${pagination_current-1})">${pagination_current-1}</a>`
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
        nextElement.innerHTML = `<a onclick="setItemsPage(${pagination_current+1})">${pagination_current+1}</a>`
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
        endElement.innerHTML = `<a onclick="setItemsPage(${pagination_end})">${pagination_end}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(pagination_current>=pagination_end){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setItemsPage(${pagination_current+1})"><span uk-pagination-next></span></a>`;
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}

async function fetchItems() {
    const url = new URL('/recipes/getItems', window.location.origin);
    url.searchParams.append('page', pagination_current);
    url.searchParams.append('limit', items_limit);
    url.searchParams.append('search_string', search_string);
    const response = await fetch(url);
    data =  await response.json();
    pagination_end = data.end
    return data.items; 
}

async function updateItemsModalTable(items) {
    let itemsTableBody = document.getElementById('itemsTableBody');
    itemsTableBody.innerHTML = "";
    
    for(let i=0; i < items.length; i++){
        let tableRow = document.createElement('tr')

        let idCell = document.createElement('td')
        idCell.innerHTML = `${items[i].id}`

        let barcodeCell = document.createElement('td')
        barcodeCell.innerHTML = `${items[i].barcode}`

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${items[i].item_name}`

        tableRow.id = items[i].id
        tableRow.onclick = async function(){
            await addSKUItem(items[i].id)
        }
        tableRow.append(idCell, barcodeCell, nameCell)
        itemsTableBody.append(tableRow)
    }
}