import math


def manufactureUsersTable(rows):
    table = """<table>
                <thead>
                  <tr>
                    <th>Username</th>
                  </tr>
                </thead>
                <tbody>
                %%rows%%
                </tbody>
                </table>
                """
    
    string_rows = []
    for row in rows:
        string_row = f"""<tr>
                            <td>{row[1]}</td>
                        </tr>"""
        string_rows.append(string_row)

    table = table.replace("%%rows%%", "".join(string_rows))
    
    return table


def manufacturePagination(current_page:int , count:int, limit:int):
    total_pages = math.ceil(count/limit)
    pag = ""
    limits = "hx-vals='{" + f'"limit": "{str(limit)}"' + "}'"
    if count >= limit:
        pag += '<ul class="pagination">'

        if current_page > 1:
            pag += f'<li class="waves-effect my_btn"><a hx-post="/admin/users/{current_page - 1}" hx-target="#main_body" {limits}><i class="material-icons">chevron_left</i></a></li>'

        p = [_ for _ in [current_page-2, current_page-1, current_page] if _ >= 1]
        y = [_ for _ in [current_page+1, current_page+2] if _ <= total_pages]
        _elems = p + y
        print(_elems)

        for _element in _elems:
            if _element == current_page:
                pag += f'<li class="active"><a hx-post="/admin/users/{_element}" hx-target="#main_body" {limits}>{_element}</a></li>'
            else:
                pag += f'<li class="my_btn waves-effect"><a hx-post="/admin/users/{_element}" hx-target="#main_body" {limits}>{_element}</a></li>'
        
        if current_page != total_pages:
            pag += f'<li class="waves-effect my_btn"><a hx-post="/admin/users/{current_page + 1}" hx-target="#main_body" {limits}><i class="material-icons">chevron_right</i></a></li>'
        
        pag += "</ul>"

    return pag
        