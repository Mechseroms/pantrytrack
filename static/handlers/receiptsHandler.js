var pagination_current = 1;
var pagination_end = 10

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

document.addEventListener('DOMContentLoaded', async function() {
    let receipts = await getReceipts()
    await replenishReceiptsTable(receipts)
    updatePaginationElement()
})


async function replenishReceiptsTable(receipts) {
    let receiptsTableBody = document.getElementById("receiptsTableBody")
    receiptsTableBody.innerHTML = ""

    for(let i = 0; i < receipts.length; i++){
        let tableRow = document.createElement('tr')

        let receiptIDCell = document.createElement('td')
        receiptIDCell.innerHTML = receipts[i].receipt_id

        let statusCell = document.createElement('td')
        statusCell.innerHTML = receipts[i].receipt_status

        let dateCell = document.createElement('td')
        dateCell.innerHTML = receipts[i].date_submitted
        dateCell.classList.add("uk-visible@m")

        let submittedByCell = document.createElement('td')
        submittedByCell.innerHTML = receipts[i].submitted_by
        submittedByCell.classList.add("uk-visible@m")


        tableRow.append(
            receiptIDCell,
            statusCell,
            dateCell,
            submittedByCell
        )

        tableRow.onclick = async function() {
            let url = `${window.location.origin}/receipt/${receipts[i].id}`;
            window.location.href = url;
        }

        tableRow.style = "cursor: pointer;"

        receiptsTableBody.append(tableRow)
    }
}


var receipts_limit = 10
async function getReceipts() {
    const url = new URL('/receipts/getReceipts', window.location.origin);
    url.searchParams.append('page', pagination_current);
    url.searchParams.append('limit', receipts_limit);
    const response = await fetch(url);
    data =  await response.json();
    pagination_end = data.end
    let receipts = data.receipts;
    return receipts;
}

async function setPage(page) {
    pagination_current = page
    let receipts = await getReceipts()
    replenishReceiptsTable(receipts)
    updatePaginationElement()
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
        firstElement.innerHTML = `<a><strong>1</strong></a>`;
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
        lastElement.innerHTML = `<a onclick="setPage(${pagination_current-1})">${pagination_current-1}</a>`
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
        nextElement.innerHTML = `<a onclick="setPage(${pagination_current+1})">${pagination_current+1}</a>`
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
        console.log(nextElement.innerHTML)
    }
    paginationElement.append(nextElement)
}
