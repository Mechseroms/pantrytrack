# Database Management

- the way I look at it is

## Adding a new item
- item info, food info, logistics info created using the barcode and then attached to item.
- Transcation created against logistics info description "Item added", qty X into primary location within logistics info.
- QTY of X inserted into sites default location with {logistics_info_id: X}
- returns location_id and adds the location to the logistics info, location_data {location_id: X}





## Associating a item to a linkedItem

All transaction history needs to have its associated logistic id changed to the new number (barcode stays the same?) and the new items location info and qty on hand needs to be updated.

