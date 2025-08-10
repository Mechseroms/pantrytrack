// Beginning of site specific code!
var recipe = [];
document.addEventListener('DOMContentLoaded', async function() {
    recipe = await getRecipe()
    console.log(recipe)
    await replenishRecipe()
});

async function replenishRecipe() {
    document.getElementById('title').innerHTML = `${recipe.name}`
    // document.getElementById('breadcrumb').innerHTML = `${recipe.name}`
    document.getElementById('recipeTitle').innerHTML = `${recipe.name}`
    document.getElementById('recipeAuthor').innerHTML = `${recipe.author}`
    document.getElementById('recipeDescription').innerHTML = `${recipe.description}`
    document.getElementById('recipeImage').src = `${recipe.picture_path}`

    if(recipe.picture_path){
        document.getElementById('imgDiv').classList.remove('uk-hidden')
        document.getElementById('titleDiv').classList.add('uk-width-3-4@m')
    }

    await replenishIngrediantsTable()
    await replenishInstructions()
    await replenishTransactionsTable()
    
    await getImage()
    
}

async function replenishIngrediantsTable() {
    let ingrediantsTableBody = document.getElementById('ingrediantsTableBody')
    ingrediantsTableBody.innerHTML = ""


    for(let i=0; i<recipe.recipe_items.length; i++){
        let qty_needed = recipe.recipe_items[i].qty
        let quantity_on_hand = recipe.recipe_items[i].quantity_on_hand
        let item_type = recipe.recipe_items[i].item_type

        let tableRow = document.createElement('tr')

        let markerCell = document.createElement('td')
        if (qty_needed <= quantity_on_hand && item_type === "sku"){
            markerCell.innerHTML = `<span class="uk-label uk-label-success">On Hand</span>`
        } else if (qty_needed > quantity_on_hand && item_type === "sku") {
            markerCell.innerHTML = `<span class="uk-label uk-label-danger">Missing</span>`
        } else {
            markerCell.innerHTML = ""
        }

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${recipe.recipe_items[i].item_name}`

        let qtyUOMCell = document.createElement('td')
        qtyUOMCell.innerHTML = `${recipe.recipe_items[i].qty} ${recipe.recipe_items[i].uom.fullname}`

        tableRow.append(markerCell, nameCell, qtyUOMCell)
        ingrediantsTableBody.append(tableRow)
    }

}

async function replenishTransactionsTable() {
    let receiptRecipeTableBody = document.getElementById('receiptRecipeTableBody')
    receiptRecipeTableBody.innerHTML = ""

    for(let i=0; i < recipe.recipe_items.length; i++){
        if (recipe.recipe_items[i].item_type === "sku"){
            let tableRow = document.createElement('tr')

            let nameCell = document.createElement('td')
            nameCell.innerHTML = `${recipe.recipe_items[i].item_name}`

            let qtyUOMCell = document.createElement('td')
            qtyUOMCell.innerHTML = `${recipe.recipe_items[i].qty}`

            tableRow.append(nameCell, qtyUOMCell)
            receiptRecipeTableBody.append(tableRow)
        }
    }

}

async function replenishInstructions() {
    let tileList = document.getElementById('tileList')
    tileList.innerHTML = ""

    for(let i=0; i<recipe.instructions.length; i++){
        let tile = document.createElement('div')
        let innerTile = document.createElement('div')
        innerTile.setAttribute('class', 'uk-tile uk-tile-default uk-padding-small')

        let instruction = document.createElement('p')
        instruction.innerHTML = `<strong>Step ${i+1}:</strong> ${recipe.instructions[i]}`


        innerTile.append(instruction)
        tile.append(innerTile)
        tileList.append(tile)
    }
}

async function getRecipe() {
    const url = new URL('/recipes/getRecipe', window.location.origin)
    url.searchParams.append('id', recipe_id);
    const response = await fetch(url)
    data = await response.json()
    return data.recipe
}

async function getImage(){
    console.log('fetching image!')
    await fetch(`/recipes/getImage/${recipe.id}`)
    .then(response => response.blob())
    .then(imageBlob => {
        const imageURL = URL.createObjectURL(imageBlob);
        document.getElementById('recipeImage').src = imageURL;
    });
}

async function receiptRecipe(){
    let recipe_id = recipe.id
    const response = await fetch(`/recipes/api/receiptRecipe`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
            },
        body: JSON.stringify({
            recipe_id: recipe_id
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
}