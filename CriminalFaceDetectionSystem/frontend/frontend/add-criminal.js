async function addCriminal() {
    const criminal = {
        name: document.getElementById("name").value,
        age: parseInt(document.getElementById("age").value),
        gender: document.getElementById("gender").value,
        crimeType: document.getElementById("crimeType").value,
        location: document.getElementById("location").value,
        photo: document.getElementById("photo").value
    };

    const result = document.getElementById("result");

    try {
        const response = await fetch("http://localhost:8080/criminal/add", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(criminal)
        });

        if (response.ok) {
            result.style.color = "green";
            result.textContent = "Criminal added successfully!";
            document.getElementById("name").value = "";
            document.getElementById("age").value = "";
            document.getElementById("gender").value = "";
            document.getElementById("crimeType").value = "";
            document.getElementById("location").value = "";
            document.getElementById("photo").value = "";
        } else {
            result.style.color = "red";
            result.textContent = "Failed to add criminal.";
        }
    } catch (error) {
        result.style.color = "red";
        result.textContent = "Error connecting to backend.";
        console.error(error);
    }
}