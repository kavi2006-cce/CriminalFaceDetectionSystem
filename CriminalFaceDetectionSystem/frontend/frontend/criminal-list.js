async function loadCriminals() {
    const tableBody = document.getElementById("criminalTableBody");

    try {
        const response = await fetch("http://localhost:8080/criminal/all");
        const criminals = await response.json();

        tableBody.innerHTML = "";

        criminals.forEach(criminal => {
            const row = `
                <tr>
                    <td>${criminal.id}</td>
                    <td>${criminal.name}</td>
                    <td>${criminal.age}</td>
                    <td>${criminal.gender}</td>
                    <td>${criminal.crimeType}</td>
                    <td>${criminal.location}</td>
                    <td>${criminal.photo}</td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });
    } catch (error) {
        tableBody.innerHTML = `<tr><td colspan="7">Failed to load data</td></tr>`;
        console.error(error);
    }
}

loadCriminals();