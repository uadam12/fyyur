function addMockData() {
    fetch(location.href, {
        method: "POST",
        headers: {'Content-Type':'application/json'}
    }).then(res => {
        if(res.ok) {
            res.json().then(data => {
                location.assign(data.url);
            });
        } else throw Error("Something went wrong.");
    }).catch(data => alert(data.msg));
}