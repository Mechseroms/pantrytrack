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

document.addEventListener('DOMContentLoaded', async function() {
    let sites = await fetchSites()
    await updateSitesPagination()
    await replenishSitesTable(sites)

    let roles = await fetchRoles()
    await updateRolesPagination()
    await replenishRolesTable(roles)

    let logins = await fetchLogins()
    console.log(logins)
    await updateLoginsPagination()
    await replenishLoginsTable(logins)
})

async function openDeleteModal(item_name, item_type, site_id) {
    document.getElementById('delete_item_name').innerHTML = item_name

    if(item_type == "site"){
        document.getElementById("deleteSubmitButton").onclick = async function() {
            await postDeleteSite(site_id, item_name)
        }
    }
    UIkit.modal(document.getElementById('deleteConfirmation')).show();
}

// Site functions
var sites_current_page = 1
var sites_end_page = 10
var sites_limit = 25
async function fetchSites(){
    const url = new URL('/admin/getSites', window.location.origin)
    url.searchParams.append('page', sites_current_page)
    url.searchParams.append('limit', sites_limit)
    const response = await fetch(url)
    data = await response.json()
    sites_end_page = data.end
    return data.sites
}

async function replenishSitesTable(sites){
    let sitesTableBody = document.getElementById('sitesTableBody')
    sitesTableBody.innerHTML = ""

    for(let i=0; i < sites.length; i++){
        let tableRow = document.createElement('tr')


        let idCell = document.createElement('td')
        idCell.innerHTML = `${sites[i].id}`
        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${sites[i].site_name}`
        let descriptionCell = document.createElement('td')
        descriptionCell.innerHTML = `${sites[i].site_description}`
        let opCell = document.createElement('td')
        opCell.innerHTML = ``

        let editOp = document.createElement('a')
        editOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        editOp.innerHTML = "edit"
        editOp.href = `/admin/site/${sites[i].id}`

        let deleteOp = document.createElement('a')
        deleteOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        deleteOp.innerHTML = "delete"
        deleteOp.onclick = async function() {
            await openDeleteModal(sites[i].site_name, "site", sites[i].id)
        }

        opCell.append(editOp, deleteOp)
        tableRow.append(idCell, nameCell, descriptionCell, opCell)
        sitesTableBody.append(tableRow)
    }
}

async function updateSitesPagination() {
    let paginationElement = document.getElementById("sitesPagination");
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(sites_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setSitesPage(${sites_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(sites_current_page<=1){
        firstElement.innerHTML = `<a>1</a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setSitesPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(sites_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(sites_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick=setSitesPage(${sites_current_page-1})>${sites_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(sites_current_page!=1 && sites_current_page != sites_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${sites_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(sites_current_page+2<sites_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick=setSitesPage(${sites_current_page+1})>${sites_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(sites_current_page+2<=sites_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(sites_current_page>=sites_end_page){
        endElement.innerHTML = `<a>${sites_end_page}</a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setSitesPage(${sites_end_page})">${sites_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(sites_current_page>=sites_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setSitesPage(${sites_current_page+1})"><span uk-pagination-next></span></a>`;
    }
    paginationElement.append(nextElement)
}

async function setSitesPage(pageNumber){
    sites_current_page = pageNumber;
    let sites = await fetchSites()
    await updateSitesPagination()
    await replenishSitesTable(sites)
}

async function postDeleteSite(site_id, item_name){
    let valid = document.getElementById('delete_input')
    if(valid.value==item_name){
        valid.classList.remove('uk-form-danger')
        const response = await fetch(`/admin/site/postDeleteSite`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                site_id: site_id
            }),
        });
        data =  await response.json();
        transaction_status = "success"
        if (data.error){
            transaction_status = "danger"
        }
    } else {
        valid.classList.add('uk-form-danger')
        data = {'message': 'You did not confirm the item correctly!!'}
        transaction_status = "danger"
    }

    UIkit.notification({
        message: data.message,
        status: transaction_status,
        pos: 'top-right',
        timeout: 5000
    });
    let sites = await fetchSites()
    await updateSitesPagination()
    await replenishSitesTable(sites)
    UIkit.modal(document.getElementById('deleteConfirmation')).hide();

}

// Roles functions
var roles_current_page = 1
var roles_end_page = 10
var roles_limit = 25
async function fetchRoles(){
    const url = new URL('/admin/getRoles', window.location.origin)
    url.searchParams.append('page', roles_current_page)
    url.searchParams.append('limit', roles_limit)
    const response = await fetch(url)
    data = await response.json()
    roles_end_page = data.end
    return data.roles
}

async function replenishRolesTable(roles){
    let rolesTableBody = document.getElementById('rolesTableBody')
    rolesTableBody.innerHTML = ""

    for(let i=0; i < roles.length; i++){
        let tableRow = document.createElement('tr')


        let idCell = document.createElement('td')
        idCell.innerHTML = `${roles[i].id}`
        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${roles[i].role_name}`
        let descriptionCell = document.createElement('td')
        descriptionCell.innerHTML = `${roles[i].role_description}`
        let siteCell = document.createElement('td')
        siteCell.innerHTML = `${roles[i].site.site_name}`
        let opCell = document.createElement('td')
        opCell.innerHTML = ``

        let editOp = document.createElement('a')
        editOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        editOp.innerHTML = "edit"
        editOp.href = `/admin/role/${roles[i].id}`

        let deleteOp = document.createElement('a')
        deleteOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        deleteOp.innerHTML = "delete"
        deleteOp.onclick = async function() {
            await openDeleteModal(roles[i].role_name, "role", roles[i].id)
        }

        opCell.append(editOp, deleteOp)
        tableRow.append(idCell, nameCell, descriptionCell, siteCell, opCell)
        rolesTableBody.append(tableRow)
    }
}

async function updateRolesPagination() {
    let paginationElement = document.getElementById("rolesPagination");
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(roles_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setRolesPage(${roles_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(roles_current_page<=1){
        firstElement.innerHTML = `<a>1</a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setRolesPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(roles_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(roles_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick=setRolesPage(${roles_current_page-1})>${roles_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(roles_current_page!=1 && roles_current_page != roles_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${roles_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(roles_current_page+2<roles_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick=setRolesPage(${roles_current_page+1})>${roles_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(roles_current_page+2<=roles_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(roles_current_page>=roles_end_page){
        endElement.innerHTML = `<a>${roles_end_page}</a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setRolesPage(${roles_end_page})">${roles_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(roles_current_page>=roles_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setRolesPage(${roles_current_page+1})"><span uk-pagination-next></span></a>`;
    }
    paginationElement.append(nextElement)
}

async function setRolesPage(pageNumber){
    roles_current_page = pageNumber;
    let roles = await fetchRoles()
    await updateRolesPagination()
    await replenishRolesTable(roles)
}


// users/devices functions
var logins_current_page = 1
var logins_end_page = 10
var logins_limit = 25
async function fetchLogins(){
    const url = new URL('/admin/getLogins', window.location.origin)
    url.searchParams.append('page', logins_current_page)
    url.searchParams.append('limit', logins_limit)
    const response = await fetch(url)
    data = await response.json()
    logins_end_page = data.end
    return data.logins
}

async function replenishLoginsTable(logins){
    let usersTableBody = document.getElementById('usersTableBody')
    usersTableBody.innerHTML = ""

    for(let i=0; i < logins.length; i++){
        let tableRow = document.createElement('tr')


        let idCell = document.createElement('td')
        idCell.innerHTML = `${logins[i].id}`
        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${logins[i].username}`

        let emailCell = document.createElement('td')
        emailCell.innerHTML = `${logins[i].email}`

        let typeCell = document.createElement('td')
        typeCell.innerHTML = `${logins[i].row_type}`

    
        let opCell = document.createElement('td')
        opCell.innerHTML = ``

        let editOp = document.createElement('a')
        editOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        editOp.innerHTML = "edit"
        editOp.href = `/admin/user/${logins[i].id}`

        let deleteOp = document.createElement('a')
        deleteOp.setAttribute('class', 'uk-button uk-button-small uk-button-default')
        deleteOp.innerHTML = "delete"
        deleteOp.onclick = async function() {
            await openDeleteModal(logins[i].username, "login", logins[i].id)
        }

        opCell.append(editOp, deleteOp)
        tableRow.append(idCell, nameCell, emailCell, typeCell, opCell)
        usersTableBody.append(tableRow)
    }
}

async function updateLoginsPagination() {
    let paginationElement = document.getElementById("usersPagination");
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(logins_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setLoginsPage(${logins_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(logins_current_page<=1){
        firstElement.innerHTML = `<a>1</a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setLoginsPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(logins_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(logins_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick=setLoginsPage(${logins_current_page-1})>${logins_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(logins_current_page!=1 && logins_current_page != logins_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${logins_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(logins_current_page+2<logins_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick=setLoginsPage(${logins_current_page+1})>${logins_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(logins_current_page+2<=logins_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(logins_current_page>=logins_end_page){
        endElement.innerHTML = `<a>${logins_end_page}</a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setLoginsPage(${logins_end_page})">${logins_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(logins_current_page>=logins_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setLoginsPage(${logins_current_page+1})"><span uk-pagination-next></span></a>`;
    }
    paginationElement.append(nextElement)
}

async function setLoginsPage(pageNumber){
    logins_current_page = pageNumber;
    let logins = await fetchLogins()
    await updateLoginsPagination()
    await replenishLoginsTable(logins)
}



// uom functions
async function test() {
    console.log('test')
}