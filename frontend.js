document.getElementById("form1").addEventListener("submit", async function (e) {
    e.preventDefault();
    const form = e.target;
    const data = {
        name: form.name.value,
        email: form.email.value,
        message: form.message.value
    };

    const response = await fetch("http://localhost:8000/submit", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        alert("Заявка отправлена!");
        form.reset();
    } else {
        alert("Ошибка отправки.");
    }
});