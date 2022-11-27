function b4Delete(btn) {
    btn.parentElement.parentElement.classList.add("confirm");
}

function cancel(btn) {
    btn.parentElement.parentElement.classList.remove("confirm");
}

function destroy() {
    fetch(location.href, {
        method: "DELETE",
        headers: {'Content-Type':'application/json'}
    }).then(res => {
        if(res.ok) {
            res.json().then(data => {
                location.assign(data.url);
            });
        } else throw Error("Something went wrong.");
    }).catch(data => alert(data.msg));
}