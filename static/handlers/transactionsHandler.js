var pagination_current = 1;
var limit = 50;
var pagination_end = 10
var item;

document.addEventListener('DOMContentLoaded', async function() {
    item = await getItem(item_id);
    let transactions = await getTransactions()
    replenishTransactionsTable(transactions)
    updatePaginationElement()
})

async function populateTransactionReceipt(transaction) {
    document.getElementById('trans_barcode').innerHTML = transaction.barcode
    document.getElementById('trans_database_id').innerHTML = transaction.id
    document.getElementById('trans_timestamp').innerHTML = transaction.timestamp
    document.getElementById('trans_name').innerHTML = transaction.name
    document.getElementById('trans_type').innerHTML = transaction.transaction_type
    document.getElementById('trans_qty').innerHTML = transaction.quantity
    document.getElementById('trans_description').innerHTML = transaction.description
    document.getElementById('trans_user').innerHTML = transaction.user_id
    
    let receiptTableBody = document.getElementById('receiptTableBody')
    receiptTableBody.innerHTML = ""

    for(let key in transaction.data){
        let tableRow = document.createElement('tr')

        let keyCell = document.createElement('td')
        keyCell.innerHTML = key

        let valueCell = document.createElement('td')
        valueCell.innerHTML = transaction.data[key]

        tableRow.append(keyCell, valueCell)

        receiptTableBody.append(tableRow)
    }
}

async function inspectTransactions(id) {
    let transaction = await getTransaction(id)
    await populateTransactionReceipt(transaction)
    UIkit.modal(document.getElementById("transactionModal")).show();

}

async function replenishTransactionsTable(transactions) {
    let transactionsTableBody = document.getElementById("transactionsTableBody")
    transactionsTableBody.innerHTML = ""

    for(let i = 0; i < transactions.length; i++){
        let tableRow = document.createElement('tr')




        let timestampCell = document.createElement('td')
        timestampCell.innerHTML = transactions[i].timestamp

        let barcodeCell = document.createElement('td')
        barcodeCell.innerHTML = transactions[i].barcode

        let nameCell = document.createElement('td')
        nameCell.innerHTML = transactions[i].name

        let typeCell = document.createElement('td')
        typeCell.innerHTML = transactions[i].transaction_type

        let qtyCell = document.createElement('td')
        qtyCell.innerHTML = transactions[i].quantity

        let descriptionCell = document.createElement('td')
        descriptionCell.innerHTML = transactions[i].description

        let userCell = document.createElement('td')
        userCell.innerHTML = transactions[i].user_id


        tableRow.append(
            timestampCell,
            barcodeCell,
            nameCell,
            typeCell,
            qtyCell,
            descriptionCell,
            userCell
        )

        tableRow.onclick = async function() {
            await inspectTransactions(transactions[i].id)
        }

        transactionsTableBody.append(tableRow)
    }
}

async function getItem(id) {
    const url = new URL('/external/getItem', window.location.origin);
    url.searchParams.append('id', id);
    const response = await fetch(url);
    data =  await response.json();
    item = data.item;
    return item;
}

async function getTransaction(id) {
    const url = new URL('/item/getTransaction', window.location.origin);
    url.searchParams.append('id', id);
    const response = await fetch(url);
    data =  await response.json();
    let transaction = data.transaction;
    return transaction;
}

async function getTransactions(){
    const url = new URL('/item/getTransactions', window.location.origin);
    url.searchParams.append('page', pagination_current);
    url.searchParams.append('limit', limit);
    url.searchParams.append('logistics_info_id', item.logistics_info_id)
    const response = await fetch(url);
    data =  await response.json();
    pagination_end = data.end
    let transactions = data.transactions;
    return transactions;
}

async function setPage(page) {
    pagination_current = page
    let transactions = await getTransactions()
    replenishTransactionsTable(transactions)
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