async function clickRoleRow(role_id){
    const roleurl = new URL(`/admin/editRole/${role_id}`, window.location.origin);
    window.location.href = roleurl.toString();
}

async function fetchSites() {
    const url = new URL('/admin/getSites', window.location.origin);
    const response = await fetch(url);
    const data = await response.json();
    return data.sites;
}

async function fetchUsers(limit, page) {
    const url = new URL('/admin/getUsers', window.location.origin);
    const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                limit: limit,
                page: page
            }),
        });
    const data = await response.json();
    return data.users;
}

