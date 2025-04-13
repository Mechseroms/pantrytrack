var pagination_current = 1;
var pagination_end = 3;



document.addEventListener('DOMContentLoaded', async function() {
    let lists = await getShoppingLists()
    await replenishShoppingListCards(lists)
    await updatePaginationElement()
});


async function replenishShoppingListCards(lists) {
    let shopping_list_lists = document.getElementById('shopping_list_lists')
    shopping_list_lists.innerHTML = ""

    for(let i=0; i < lists.length; i++){
        console.log(lists[i])
        let main_div = document.createElement('div')
        main_div.setAttribute('class', 'uk-card uk-card-default uk-card-small uk-margin')

        let badge_div = document.createElement('div')
        badge_div.setAttribute('class', 'uk-card-badge uk-label')
        badge_div.innerHTML = `${lists[i].sl_items.length} Lines`

        let badge_div_dos = document.createElement('div')
        badge_div_dos.setAttribute('class', 'uk-card-badge uk-label')
        badge_div_dos.innerHTML = lists[i].type
        badge_div_dos.style = "margin-top: 30px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width:150px; text-align: right;"

        let card_header_div = document.createElement('div')
        card_header_div.setAttribute('class', 'uk-card-header')
        card_header_div.style = "border: none;"

        let header_grid_div = document.createElement('div')
        header_grid_div.setAttribute('class', 'uk-flex-middle uk-grid uk-grid-small')

        let title_div = document.createElement('div')
        title_div.setAttribute('class', '')
        title_div.innerHTML = `
            <h3 class="my-card uk-card-title uk-margin-remove-bottom">${lists[i].name}</h3>
            <p class="uk-text-meta uk-margin-remove-top"><time datetime="${lists[i].creation_date}">${lists[i].creation_date}</time></p>
            `

        header_grid_div.append(title_div)
        card_header_div.append(badge_div, badge_div_dos, header_grid_div)

        let body_div = document.createElement('div')
        body_div.setAttribute('class', 'uk-card-body')
        body_div.innerHTML = `<p>${lists[i].description}</p>`
        body_div.style = 'border: none;'

        let footer_div = document.createElement('div')
        footer_div.setAttribute('class', 'uk-card-footer')
        footer_div.style = 'height: 40px; border: none;'

        let editOp = document.createElement('a')
        editOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        editOp.innerHTML = '<span uk-icon="icon: pencil"></span>   Edit'
        editOp.style = "margin-right: 10px;"
        editOp.href = `/shopping-list/edit/${lists[i].id}`

        let viewOp = document.createElement('a')
        viewOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        viewOp.innerHTML = '<span uk-icon="icon: eye"></span>    View'
        viewOp.href = `/shopping-list/view/${lists[i].id}`
        //viewOp.style = "margin-right: 20px;"

        
        footer_div.append(editOp, viewOp)

        main_div.append(card_header_div, body_div, footer_div)

        shopping_list_lists.append(main_div)

    }
}

async function openAddListModal() {
    UIkit.modal(document.getElementById('addListModal')).show();
}

var listLimit = 5;
async function getShoppingLists(){
    console.log(pagination_current)
    const url = new URL('/shopping-lists/getLists', window.location.origin);
    url.searchParams.append('page', pagination_current);
    url.searchParams.append('limit', listLimit);
    response = await fetch(url)
    data = await response.json()
    pagination_end = data.end
    console.log(pagination_end)
    return data.shopping_lists
};

async function addList() {
    let list_name = document.getElementById('addListName').value
    let list_description = document.getElementById('addListDescription').value
    let list_type = document.getElementById('list_type').value

    const response = await fetch(`/shopping-lists/addList`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            list_name: list_name,
            list_description: list_description,
            list_type: list_type
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
}

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

async function updatePaginationElement() {
    let paginationElement = document.getElementById("paginationElement");
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
        firstElement.innerHTML = `<a>1</a>`;
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
        lastElement.innerHTML = `<a onclick=setPage(${pagination_current-1})>${pagination_current-1}</a>`
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
        nextElement.innerHTML = `<a onclick=setPage(${pagination_current+1})>${pagination_current+1}</a>`
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
        endElement.innerHTML = `<a>${pagination_end}</a>`;
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
    }
    paginationElement.append(nextElement)
}

async function setPage(pageNumber){
    pagination_current = pageNumber;
    let lists = await getShoppingLists()
    await replenishShoppingListCards(lists)
    await updatePaginationElement()
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
