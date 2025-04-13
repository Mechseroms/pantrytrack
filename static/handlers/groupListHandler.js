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


if(session.user.flags.darkmode){
    toggleDarkMode()
}

async function changeSite(site){
    console.log(site)
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

// Beginning of site specific code!
document.addEventListener('DOMContentLoaded', async function() {
    let groups = await getGroups()
    await replenishGroups(groups)
    await updatePaginationElement()
});


async function replenishGroups(groups) {
    if(!detailedList){
        await replenishGroupsTable(groups)
    }

    if(detailedList){
        await replenishGroupsCards(groups)
    }
}

async function replenishGroupsTable(groups) {
    document.getElementById('groups_list').innerHTML = ''

    console.log('table')
    let main_table = document.createElement('table')
    main_table.setAttribute('class', 'uk-table uk-table-striped')

    let table_head = document.createElement('thead')

    let head_row = document.createElement('tr')
    let nameCell = document.createElement('th')
    nameCell.innerHTML="Name"
    let descriptionCell = document.createElement('th')
    descriptionCell.innerHTML = 'Description'
    let typeCell = document.createElement('th')
    typeCell.innerHTML = 'Type'
    let opsCell = document.createElement('th')
    opsCell.innerHTML = 'Operations'

    head_row.append(nameCell, descriptionCell, typeCell, opsCell)
    table_head.append(head_row)
    main_table.append(table_head)


    let table_body = document.createElement('tbody')
    for(let i = 0; i < groups.length; i++){
        let table_row = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = groups[i].name
        let descriptionCell = document.createElement('td')
        descriptionCell.innerHTML = groups[i].description
        let typeCell = document.createElement('td')
        typeCell.innerHTML = groups[i].group_type
        let opsCell = document.createElement('td')


        let buttonGroup = document.createElement('div')
        buttonGroup.setAttribute('class', 'uk-button-group')

        let viewOp = document.createElement('a')
        viewOp.innerHTML = `view <span uk-icon="icon: eye"></span>`
        viewOp.setAttribute('class', 'uk-button uk-button-default uk-button-small')

        let editOp = document.createElement('a')
        editOp.innerHTML = `edit <span uk-icon="icon: pencil"></span>`
        editOp.setAttribute('class', 'uk-button uk-button-default uk-button-small')
        editOp.href = `/group/${groups[i].id}`

        buttonGroup.append(viewOp, editOp)
        opsCell.append(buttonGroup)

        table_row.append(nameCell, descriptionCell, typeCell, opsCell)
        table_body.append(table_row)
    }

    main_table.append(table_body)

    document.getElementById('groups_list').append(main_table)

}

async function replenishGroupsCards(groups) {
    document.getElementById('groups_list').innerHTML = ''
    console.log('cards')

    for(let i=0; i < groups.length; i++){
        let main_div = document.createElement('div')
        main_div.setAttribute('class', 'uk-card uk-card-default uk-card-small uk-margin')

        let card_header_div = document.createElement('div')
        card_header_div.setAttribute('class', 'uk-card-header')
        card_header_div.style = "border: none;"

        let header_grid_div = document.createElement('div')
        header_grid_div.setAttribute('class', 'uk-flex-middle uk-grid uk-grid-small')

        let title_div = document.createElement('div')
        title_div.setAttribute('class', '')
        title_div.innerHTML = `
            <h3 class="my-card uk-card-title uk-margin-remove-bottom">${groups[i].name}</h3>`

        header_grid_div.append(title_div)
        card_header_div.append(header_grid_div)

        let body_div = document.createElement('div')
        body_div.setAttribute('class', 'uk-card-body')
        body_div.innerHTML = `<p>${groups[i].description}</p>`
        body_div.style = 'border: none;'

        let footer_div = document.createElement('div')
        footer_div.setAttribute('class', 'uk-card-footer')
        footer_div.style = 'height: 40px; border: none;'

        let editOp = document.createElement('a')
        editOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        editOp.innerHTML = '<span uk-icon="icon: pencil"></span>   Edit'
        editOp.style = "margin-right: 10px;"
        editOp.href = `/group/${groups[i].id}`

        let viewOp = document.createElement('a')
        viewOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        viewOp.innerHTML = '<span uk-icon="icon: eye"></span>    View'
        
        footer_div.append(editOp, viewOp)

        main_div.append(card_header_div, body_div, footer_div)

        document.getElementById('groups_list').append(main_div)
    }
}

var pagination_current = 1;
var pagination_end = 1;
var groupLimit = 5;
async function getGroups() {
    const url = new URL('/groups/getGroups', window.location.origin)
    url.searchParams.append('page', pagination_current);
    url.searchParams.append('limit', groupLimit);
    const response = await fetch(url)
    data = await response.json()
    pagination_end = data.end
    return data.groups
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
    let groups = await getGroups()
    await replenishGroups(groups)
    await updatePaginationElement()
}

var detailedList = false
async function setViewMode() {
    detailedList = !detailedList;
    let toggle = document.getElementById('view_mode_toggle')
    if(detailedList){
        toggle.innerHTML = `Table <span uk-icon="icon: table"></span>`
    } else {
        toggle.innerHTML = `Cards <span uk-icon="icon: thumbnails"></span>`
    }
    let groups = await getGroups()
    await replenishGroups(groups)
    await updatePaginationElement()
}