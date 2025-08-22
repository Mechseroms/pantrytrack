var year = 2025
var month = 8
const monthNames = ["", "January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"];

var eventsByDay = {
  3: ["Chicken Stir Fry", "Salad"],
  8: ["Spaghetti Bolognese"],
  12: ["Fish Tacos", "Rice", "Beans"],
  31: ['Brats']
};

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

async function getEventsByMonth() {
    const url = new URL('/planner/api/getEventsByMonth', window.location.origin);
    url.searchParams.append('year', year);
    url.searchParams.append('month', month);
    const response = await fetch(url);
    data =  await response.json();
    return data.events; 
}

async function getEventByUUID(event_uuid) {
    const url = new URL('/planner/api/getEventByUUID', window.location.origin);
    url.searchParams.append('event_uuid', event_uuid);
    const response = await fetch(url);
    data =  await response.json();
    return data.event; 
}

async function parseEvents(events) {
    eventsByDay = {}
    for (let i = 0; i < events.length; i++){
        console.log(`new event -- ${events[i].event_shortname}`)
        let event_date_start = new Date(events[i].event_date_start)
        let event_date_end = new Date(events[i].event_date_end)

        let this_month = month
        let start_day = event_date_start.getUTCDate()
        let start_month = event_date_start.getUTCMonth() + 1
        let end_day = event_date_end.getUTCDate()
        let end_month = event_date_end.getUTCMonth() + 1

        if(start_month !== this_month){
            start_day = 1
        }

        if(end_month !== this_month){
            end_day = new Date(year, month, 0).getUTCDate();

        }

        for (let y = start_day; y <= end_day; y++){
            if (!eventsByDay[y]) {
                eventsByDay[y] = [];
            }
            let dayarray = eventsByDay[y]
            dayarray.push(events[i])
            eventsByDay[y] = dayarray
        }

    }
    console.log(eventsByDay)
}

document.addEventListener('DOMContentLoaded', async function() {
    let today = new Date();
    year = today.getFullYear();
    month = today.getMonth() + 1; 
    await setupCalendarAndEvents()
})

async function setupCalendarAndEvents(){
    console.log(year, month)
    events = await getEventsByMonth()
    await parseEvents(events)
    
    await createCalender()
    document.getElementById('calender_table').addEventListener('contextmenu', function(e) {
        e.preventDefault();
        let recipeLabel = e.target.closest('.recipe-label');
        let calendarCell = e.target.closest('.calendar-cell');
        let customLabel = e.target.closest('.custom-label');
        let takeOutLabel = e.target.closest('.take-out-label')
        if (recipeLabel) {
            recipeLabel.classList.add('recipe-label-selected')
            let rect = recipeLabel.getBoundingClientRect();
            let scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            let menuX = rect.left + scrollLeft;
            let menuY = rect.bottom + scrollTop;
            showContextMenuForEvent(recipeLabel, menuX, menuY);
        } else if (customLabel) {
            customLabel.classList.add('custom-label-selected')
            let rect = customLabel.getBoundingClientRect();
            let scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            let menuX = rect.left + scrollLeft;
            let menuY = rect.bottom + scrollTop;
            showContextMenuForEvent(customLabel, menuX, menuY);
        } else if (takeOutLabel) {
            takeOutLabel.classList.add('take-out-label-selected')
            let rect = takeOutLabel.getBoundingClientRect();
            let scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            let menuX = rect.left + scrollLeft;
            let menuY = rect.bottom + scrollTop;
            showContextMenuForTOEvent(takeOutLabel, menuX, menuY);
        } else if (calendarCell) {
            calendarCell.classList.add('calendar-cell-selected')
            let rect = calendarCell.getBoundingClientRect();
            let scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            let menuX = rect.left + scrollLeft;
            let menuY = rect.bottom + scrollTop;
            showContextMenuForCell(calendarCell, menuX, menuY);
        } else {
            hideContextMenu();
        }
    });
}

async function createCalender() {
    let calender_container = document.getElementById('calendar_container')
    calender_container.innerHTML = ""

    let firstDay = new Date(year, month - 1, 1);
    let numDays = new Date(year, month, 0).getDate();
    let startDay = firstDay.getDay();

    let calender_table = document.createElement('table')
    calender_table.setAttribute('id', 'calender_table')
    calender_table.setAttribute('class', 'uk-table uk-table-middle uk-table-large uk-table-responsive')
    let table_headers = document.createElement('thead')
    table_headers.innerHTML = `<tr><th class="uk-text-center">Sunday</th><th class="uk-text-center">Monday</th><th class="uk-text-center">Tuesday</th><th class="uk-text-center">Wednesday</th><th class="uk-text-center">Thursday</th><th class="uk-text-center">Friday</th><th class="uk-text-center">Saturday</th></tr>`

    calender_table.append(table_headers)
    let tableRow = document.createElement('tr')

    for (let i = 0; i < startDay; i++){    
        let table_cell = document.createElement('td')
        table_cell.setAttribute('class', 'uk-table-expand uk-visible@m calendar-cell-empty')
        tableRow.append(table_cell)
    }
    console.log(eventsByDay)
    for (let day = 1; day <= numDays; day++) {
        let table_cell = document.createElement('td')
        let eventsHTML = "";
        if (eventsByDay[day]) {
        eventsByDay[day].forEach(event => {
            if(event.event_type==="recipe" && event.has_missing_ingredients){
                eventsHTML += `<div class="recipe-label recipe-error" data-event_uuid="${event.event_uuid}" data-day="${day}">${event.event_shortname}</div>`;
            }  else if (event.event_type==="recipe" && !event.has_missing_ingredients){
                eventsHTML += `<div class="recipe-label recipe-success" data-event_uuid="${event.event_uuid}" data-day="${day}">${event.event_shortname}</div>`;
            } else if (event.event_type==="take out"){
                eventsHTML += `<div class="take-out-label" data-event_uuid="${event.event_uuid}" data-day="${day}">${event.event_shortname}</div>`;
            } else {
                eventsHTML += `<div class="custom-label" data-event_uuid="${event.event_uuid}" data-day="${day}">${event.event_shortname}</div>`;
            }

        });
        }

        table_cell.innerHTML = `<div class="date-box" data-day="${day}">${day}</div><div class="recipes-box">${eventsHTML}</div>`;
        table_cell.classList.add("calendar-cell");
        table_cell.dataset.day = day;

        tableRow.append(table_cell)
        if ((startDay + day) % 7 === 0 && day !== numDays){
            calender_table.append(tableRow)
            tableRow = document.createElement('tr')
        };
    }

    let lastDayOfWeek = (startDay + numDays - 1) % 7;
    for (let i = lastDayOfWeek + 1; i <= 6; i++) {
        let table_cell = document.createElement('td')
        table_cell.setAttribute('class', 'uk-visible@m calendar-cell-empty')
        tableRow.append(table_cell)
    }

    calender_table.append(tableRow)
    
    let table_footer = document.createElement('tr')
    table_footer.innerHTML = `<th></th><th></th><th></th><th></th><th></th><th></th><th></th>`

    calender_table.append(table_footer)
    calender_container.append(calender_table)

    document.getElementById("month-year-title").innerHTML = `${monthNames[month]} ${year}`;
}

function showContextMenuForEvent(eventLabel, x, y) {
    const menu = document.getElementById('calendarContextMenu');
    // Set only "Edit" and "Remove" (and optionally "Add Another")
    menu.className = "uk-dropdown uk-open";
    menu.innerHTML = `
    <ul class="uk-nav uk-dropdown-nav">
        <li><a href="#" onclick="editEvent('${eventLabel.dataset.event_uuid}')">Edit Event</a></li>
        <li><a href="#" onclick="postRemoveEvent('${eventLabel.dataset.event_uuid}')">Remove Event</a></li>
    </ul>
    `;
    menu.style.display = 'block';
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
}

function showContextMenuForTOEvent(eventLabel, x, y) {
    const menu = document.getElementById('calendarContextMenu');
    // Set only "Edit" and "Remove" (and optionally "Add Another")
    menu.className = "uk-dropdown uk-open";
    menu.innerHTML = `
    <ul class="uk-nav uk-dropdown-nav">
        <li><a href="#" onclick="postRemoveEvent('${eventLabel.dataset.event_uuid}')">Remove Event</a></li>
    </ul>
    `;
    menu.style.display = 'block';
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
}


function showContextMenuForCell(calendarCell, x, y) {
    const menu = document.getElementById('calendarContextMenu');
    // Only "Add Event"
    menu.className = "uk-dropdown uk-open";
    menu.innerHTML = `
    <ul class="uk-nav uk-dropdown-nav">
        <li><a href="#" onclick="addEvent('${calendarCell.dataset.day}')">Add Event</a></li>
        <li><a href="#" onclick="addTakeOut('${calendarCell.dataset.day}')">Add Take Out</a></li>
    </ul>
    `;
    menu.style.display = 'block';
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
}

window.addEventListener('click', function() {
    document.getElementById('calendarContextMenu').style.display = 'none';
    document.querySelectorAll('.calendar-cell-selected').forEach(el => el.classList.remove('calendar-cell-selected'));
    document.querySelectorAll('.custom-label-selected').forEach(el => el.classList.remove('custom-label-selected'));
    document.querySelectorAll('.recipe-label-selected').forEach(el => el.classList.remove('recipe-label-selected'));
    document.querySelectorAll('.take-out-label-selected').forEach(el => el.classList.remove('recipe-label-selected'));
});

async function addEvent(day) {
    let menu = document.getElementById('calendarContextMenu');
    //let day = menu.getAttribute('data-day')
    console.log(year, month, day)
    let customDate = new Date(year, month-1, day);
    document.getElementById('event_date_start').value = customDate.toISOString().split('T')[0];
    document.getElementById('event_date_end').value = customDate.toISOString().split('T')[0];
    UIkit.modal(document.getElementById('eventModal')).show();
}

async function editEvent(event_uuid) {
    console.log(event_uuid)
    let event = await getEventByUUID(event_uuid)
    console.log(event)

    document.getElementById('event_uuid_edit').value = event_uuid

    let event_date_start = new Date(event.event_date_start)
    let y = event_date_start.getFullYear();
    let m = event_date_start.getUTCMonth();
    let d = event_date_start.getUTCDate();
    event_date_start = new Date(y, m, d);

    let event_date_end = new Date(event.event_date_end)
    let end_y = event_date_end.getFullYear();
    let end_m = event_date_end.getUTCMonth();
    let end_d = event_date_end.getUTCDate();
    event_date_end = new Date(end_y, end_m, end_d);
    
    document.getElementById('event_date_edit_start').value = event_date_start.toISOString().split('T')[0]
    document.getElementById('event_date_edit_end').value = event_date_end.toISOString().split('T')[0]
    document.getElementById('event_type_edit').value = event.event_type
    document.getElementById('recipe_label_modal_edit').value = event.recipe_uuid
    document.getElementById('event_description_edit').value = event.event_description
    document.getElementById('event_name_edit').value = event.event_shortname

    if(event.event_type==="recipe"){
        document.getElementById('event_name_edit').classList.add('uk-disabled')
        document.getElementById('event_name_edit').classList.add('uk-form-blank')
        document.getElementById('recipe_label_edit_parent').hidden = false
    } else {
        document.getElementById('event_name_edit').classList.remove('uk-disabled')
        document.getElementById('event_name_edit').classList.remove('uk-form-blank')
        document.getElementById('recipe_label_edit_parent').hidden = true
    }

    UIkit.modal(document.getElementById('eventEditModal')).show();
}

async function postNewEvent(){
    let event_shortname = document.getElementById('event_name').value
    let event_description = document.getElementById('event_description').value
    let event_date_start = document.getElementById('event_date_start').value
    let event_date_end = document.getElementById('event_date_end').value
    let event_type = document.getElementById('event_type').value
    
    let recipe_uuid = null
    if (event_type === "recipe"){
        recipe_uuid = document.getElementById('selected-recipe').value
    }

    const response = await fetch('/planner/api/addEvent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            event_shortname: event_shortname,
            event_description: event_description,
            event_date_start: event_date_start,
            event_date_end: event_date_end,
            recipe_uuid: recipe_uuid,
            event_type: event_type
        })
    });

    data =  await response.json();
    response_status = 'primary'
    if (!data.status === 201){
        response_status = 'danger'
    }

    UIkit.notification({
        message: data.message,
        status: response_status,
        pos: 'top-right',
        timeout: 5000
    });

    await setupCalendarAndEvents()
    UIkit.modal(document.getElementById('eventModal')).hide();

}

async function postEditEvent(){
    let event_uuid = document.getElementById('event_uuid_edit').value

    let event_shortname = document.getElementById('event_name_edit').value
    let event_description = document.getElementById('event_description_edit').value
    let event_date_start = document.getElementById('event_date_edit_start').value
    let event_date_end = document.getElementById('event_date_edit_end').value
    let event_type = document.getElementById('event_type_edit').value

    const response = await fetch('/planner/api/saveEvent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            event_uuid: event_uuid,
            update: {
                event_shortname: event_shortname,
                event_description: event_description,
                event_date_start: event_date_start,
                event_date_end: event_date_end,
                event_type: event_type
            }
        })
    });

    data =  await response.json();
    response_status = 'primary'
    if (!data.status === 201){
        response_status = 'danger'
    }

    UIkit.notification({
        message: data.message,
        status: response_status,
        pos: 'top-right',
        timeout: 5000
    });

    await setupCalendarAndEvents()
    UIkit.modal(document.getElementById('eventEditModal')).hide();

}

async function postRemoveEvent(event_uuid){

    const response = await fetch('/planner/api/removeEvent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            event_uuid: event_uuid
        })
    });

    data =  await response.json();
    response_status = 'primary'
    if (!data.status === 201){
        response_status = 'danger'
    }

    UIkit.notification({
        message: data.message,
        status: response_status,
        pos: 'top-right',
        timeout: 5000
    });

    await setupCalendarAndEvents()
}


// main window functions
async function backOneMonth() {
    if(month === 1){
        year = year - 1
        month = 12
    } else {
        month = month - 1
    }
    await setupCalendarAndEvents()
}

async function forwardOneMonth() {
    if(month === 12){
        year = year + 1
        month = 1
    } else {
        month = month + 1
    }
    await setupCalendarAndEvents()
}


// Main Modal Functions
var eventModal_type = "recipe"

async function setEventTypeForm(){
    let event_type = document.getElementById('event_type').value
    document.getElementById('event_name').value = ""
    document.getElementById('event_description').value = ""
    document.getElementById('selected-recipe').value = ""
    if(event_type === "custom"){
        eventModal_type = "custom"
        document.getElementById('recipe_button_modal').hidden = true
        document.getElementById('recipe_label_modal').hidden = true
        document.getElementById('event_name').classList.remove('uk-disabled')

    } else if (event_type === "recipe"){
        eventModal_type = "recipe"
        document.getElementById('recipe_button_modal').hidden = false
        document.getElementById('recipe_label_modal').hidden = false
        document.getElementById('event_name').classList.add('uk-disabled')
    }
}

// Select Row Modal Handlers
var eventModal_page = 1
var eventModal_end = 1
var eventModal_search = ""
var eventModal_limit = 50


async function selectRecipeEvent() {
    document.getElementById('mainEventBody').hidden = true
    document.getElementById('paginationModalBody').hidden = false
    document.getElementById('eventsModalFooter').hidden = true
    let recipes = await fetchRecipes()
    await updateEventsPaginationElement()
    await updateEventsTableWithRecipes(recipes)
}

async function fetchRecipes() {
    const url = new URL('/planner/api/getRecipes', window.location.origin);
    url.searchParams.append('page', eventModal_page);
    url.searchParams.append('limit', eventModal_limit);
    url.searchParams.append('search_string', eventModal_search);
    const response = await fetch(url);
    data =  await response.json();
    eventModal_end = data.end
    return data.recipes; 
}


async function updateEventsTableWithRecipes(recipes) {
    let eventsTableBody = document.getElementById('eventsTableBody')
    eventsTableBody.innerHTML = ""


    for (let i = 0; i < recipes.length; i++){
        let tableRow = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${recipes[i].name}`


        let opCell = document.createElement('td')

        let selectButton = document.createElement('button')
        selectButton.setAttribute('class', 'uk-button uk-button-primary uk-button-small')
        selectButton.innerHTML = "Select"
        selectButton.onclick = async function() {
            document.getElementById('selected-recipe').value = recipes[i].recipe_uuid
            document.getElementById('event_name').value = recipes[i].name
            document.getElementById('mainEventBody').hidden = false
            document.getElementById('paginationModalBody').hidden = true
            document.getElementById('eventsModalFooter').hidden = false
        }

        opCell.append(selectButton)

        tableRow.append(nameCell, opCell)
        eventsTableBody.append(tableRow)   
    }
}

async function setEventModalPage(pageNumber){
    eventModal_page = pageNumber;
    if (eventModal_type == "recipe"){
        let records = await fetchRecipes()
    }
    await updateItemsModalTable(records)
    await updateItemsPaginationElement()
}

async function updateEventsPaginationElement() {
    let paginationElement = document.getElementById('eventPage');
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(eventModal_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setEventModalPage(${eventModal_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(eventModal_page<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setEventModalPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(eventModal_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(eventModal_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="setEventModalPage(${eventModal_page-1})">${eventModal_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(eventModal_page!=1 && eventModal_page != eventModal_end){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${eventModal_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(eventModal_page+2<eventModal_end+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="setEventModalPage(${eventModal_page+1})">${eventModal_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(eventModal_page+2<=eventModal_end){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(eventModal_page>=eventModal_end){
        endElement.innerHTML = `<a><strong>${eventModal_end}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setEventModalPage(${eventModal_end})">${eventModal_end}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(eventModal_page>=eventModal_end){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setEventModalPage(${eventModal_page+1})"><span uk-pagination-next></span></a>`;
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}

// Take Out Event Functions
var TO_current_page = 1;
var TO_end_page = 1;
var TO_Limit = 10;
var TO_search_string = "";

async function addTakeOut(day) {
    TO_current_page = 1;
    TO_end_page = 1;
    TO_Limit = 10;
    TO_search_string = "";
    let menu = document.getElementById('calendarContextMenu');
    //let day = menu.getAttribute('data-day')
    console.log(year, month, day)
    let customDate = new Date(year, month-1, day);
    document.getElementById('TO_date_start').value = customDate.toISOString().split('T')[0];
    document.getElementById('TO_date_end').value = customDate.toISOString().split('T')[0];
    UIkit.modal(document.getElementById('takeOutOrderModal')).show();
}

async function selectTOEvent() {
    document.getElementById('TOModalBody').hidden = true
    document.getElementById('paginationTOModalBody').hidden = false
    document.getElementById('TOModalFooter').hidden = true
    let vendors = await fetchVendors()
    await updateTOPaginationElement()
    await updateTOTableWithVendors(vendors)
}

async function fetchVendors() {
    const url = new URL('/planner/api/getVendors', window.location.origin);
    url.searchParams.append('page', TO_current_page);
    url.searchParams.append('limit', TO_Limit);
    url.searchParams.append('search_string', TO_search_string);
    const response = await fetch(url);
    data =  await response.json();
    TO_end_page = data.end
    return data.vendors; 
}

async function updateTOTableWithVendors(vendors) {
    let vendorsTableBody = document.getElementById('vendorsTableBody')
    vendorsTableBody.innerHTML = ""


    for (let i = 0; i < vendors.length; i++){
        let tableRow = document.createElement('tr')

        let nameCell = document.createElement('td')
        nameCell.innerHTML = `${vendors[i].vendor_name}`


        let opCell = document.createElement('td')

        let selectButton = document.createElement('button')
        selectButton.setAttribute('class', 'uk-button uk-button-primary uk-button-small')
        selectButton.innerHTML = "Select"
        selectButton.onclick = async function() {
            document.getElementById('vendor_id').value = vendors[i].id
            document.getElementById('selected_vendor_name').value = vendors[i].vendor_name
            document.getElementById('TOModalBody').hidden = false
            document.getElementById('paginationTOModalBody').hidden = true
            document.getElementById('TOModalFooter').hidden = false
        }

        opCell.append(selectButton)

        tableRow.append(nameCell, opCell)
        vendorsTableBody.append(tableRow)   
    }
}

async function setTOModalPage(pageNumber){
    TO_current_page = pageNumber;
    let vendors = await fetchVendors()
    await updateTOTableWithVendors(vendors)
    await updateTOPaginationElement()
}

async function updateTOPaginationElement() {
    let paginationElement = document.getElementById('takeOutOrderPage');
    paginationElement.innerHTML = "";
    // previous
    let previousElement = document.createElement('li')
    if(TO_current_page<=1){
        previousElement.innerHTML = `<a><span uk-pagination-previous></span></a>`;
        previousElement.classList.add('uk-disabled');
    }else {
        previousElement.innerHTML = `<a onclick="setTOModalPage(${TO_current_page-1})"><span uk-pagination-previous></span></a>`;
    }
    paginationElement.append(previousElement)
    
    //first
    let firstElement = document.createElement('li')
    if(TO_current_page<=1){
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
        firstElement.classList.add('uk-disabled');
    }else {
        firstElement.innerHTML = `<a onclick="setTOModalPage(1)">1</a>`;
    }
    paginationElement.append(firstElement)
    
    // ...
    if(TO_current_page-2>1){
        let firstDotElement = document.createElement('li')
        firstDotElement.classList.add('uk-disabled')
        firstDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(firstDotElement)
    }
    // last
    if(TO_current_page-2>0){
        let lastElement = document.createElement('li')
        lastElement.innerHTML = `<a onclick="setTOModalPage(${TO_current_page-1})">${TO_current_page-1}</a>`
        paginationElement.append(lastElement)
    }
    // current
    if(TO_current_page!=1 && TO_current_page != TO_end_page){
    let currentElement = document.createElement('li')
    currentElement.innerHTML = `<li class="uk-active"><span aria-current="page"><strong>${TO_current_page}</strong></span></li>`
    paginationElement.append(currentElement)
    }
    // next
    if(TO_current_page+2<TO_end_page+1){
        let nextElement = document.createElement('li')
        nextElement.innerHTML = `<a onclick="setTOModalPage(${TO_current_page+1})">${TO_current_page+1}</a>`
        paginationElement.append(nextElement)
    }
    // ...
    if(TO_current_page+2<=TO_end_page){
        let secondDotElement = document.createElement('li')
        secondDotElement.classList.add('uk-disabled')
        secondDotElement.innerHTML = `<span>…</span>`;
        paginationElement.append(secondDotElement)
    }
    //end
    let endElement = document.createElement('li')
    if(TO_current_page>=TO_end_page){
        endElement.innerHTML = `<a><strong>${TO_end_page}</strong></a>`;
        endElement.classList.add('uk-disabled');
    }else {
        endElement.innerHTML = `<a onclick="setTOModalPage(${TO_end_page})">${TO_end_page}</a>`;
    }
    paginationElement.append(endElement)
    //next button
    let nextElement = document.createElement('li')
    if(TO_current_page>=TO_end_page){
        nextElement.innerHTML = `<a><span uk-pagination-next></span></a>`;
        nextElement.classList.add('uk-disabled');
    }else {
        nextElement.innerHTML = `<a onclick="setTOModalPage(${TO_current_page+1})"><span uk-pagination-next></span></a>`;
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}

async function postTOEvent(){
    let event_shortname = `Take Out: ${document.getElementById('selected_vendor_name').value}`
    let event_description = `Take out dining at ${event_shortname}`
    let event_date_start = document.getElementById('TO_date_start').value
    let event_date_end = document.getElementById('TO_date_end').value
    let event_type = 'take out'
    let recipe_uuid = null

    let vendor_id = parseInt(document.getElementById('vendor_id').value)
    let attendees = parseInt(document.getElementById('TO_attendees').value)
    let cost = parseFloat(document.getElementById('TO_cost').value)

    const response = await fetch('/planner/api/addTOEvent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            event_shortname: event_shortname,
            event_description: event_description,
            event_date_start: event_date_start,
            event_date_end: event_date_end,
            recipe_uuid: recipe_uuid,
            event_type: event_type,
            vendor_id: vendor_id,
            attendees: attendees,
            cost: cost
        })
    });

    data =  await response.json();
    response_status = 'primary'
    if (!data.status === 201){
        response_status = 'danger'
    }

    UIkit.notification({
        message: data.message,
        status: response_status,
        pos: 'top-right',
        timeout: 5000
    });

    await setupCalendarAndEvents()
    UIkit.modal(document.getElementById('takeOutOrderModal')).hide();

}