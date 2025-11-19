let chart;  // Variabel för att lagra Chart.js-diagrammet

// Funktion för att hämta data från servern och uppdatera sidan
async function fetchData() {
    try {
        // Skicka GET-förfrågan till PHP-skriptet som returnerar JSON-data
        const response = await fetch('/get_data.php');
        const data = await response.json(); // Tolka JSON-svaret till JavaScript-objekt

        // Hitta tabellens tbody-element
        const tbody = document.querySelector('#data-table tbody');
        tbody.innerHTML = ''; // Rensa tidigare tabellinnehåll

        // Loopar igenom varje mätobjekt i data och skapar en tabellrad
        data.forEach(item => {
            const tr = document.createElement('tr'); // Skapa en ny tabellrad
            tr.innerHTML = `
                <td>${item.timestamp}</td>  <!-- Sätt in tidsstämpeln -->
                <td>${parseFloat(item.temperature).toFixed(2)}</td> <!-- Temperatur med 2 decimaler -->
                <td>${parseFloat(item.humidity).toFixed(2)}</td> <!-- Luftfuktighet med 2 decimaler -->
            `;  
            tbody.appendChild(tr); // Lägg till raden i tabellen
        });

        // Uppdatera status-texten med aktuell tidpunkt
        document.getElementById('status').textContent = `Senaste uppdateringen: ${new Date().toLocaleTimeString()}`;

        // Ta ut de senaste 10 mätningarna och vänd ordningen så äldsta visas först
        const latestTen = data.slice(0, 10).reverse();

        // Skapa arrayer med etiketter (tidsstämplar) och data för temperatur och luftfuktighet
        const labels = latestTen.map(item => item.timestamp);
        const temperatures = latestTen.map(item => parseFloat(item.temperature));
        const humidities = latestTen.map(item => parseFloat(item.humidity));

        if (!chart) {
            // Om diagrammet inte finns, skapa det från början
            const ctx = document.getElementById('sensorChart').getContext('2d');
            chart = new Chart(ctx, {
                type: 'line', // Linjediagram
                data: {
                    labels: labels, // X-axel etiketter (tidsstämplar)
                    datasets: [
                        {
                            label: 'Temperatur (°C)', // Dataset för temperatur
                            data: temperatures, // Temperaturdata
                            borderColor: 'rgba(255, 99, 132, 1)', // Röd linje
                            backgroundColor: 'rgba(255, 99, 132, 0.2)', // Transparent röd fyllning
                            fill: false, // Fyll inte under linjen
                            tension: 0.3, // Kurvighet på linjen
                            yAxisID: 'y1', // Kopplad till y-axel 1 (vänster)
                        },
                        {
                            label: 'Luftfuktighet (%)', // Dataset för luftfuktighet
                            data: humidities, // Luftfuktighetsdata
                            borderColor: 'rgba(54, 162, 235, 1)', // Blå linje
                            backgroundColor: 'rgba(54, 162, 235, 0.2)', // Transparent blå fyllning
                            fill: false, // Ingen fyllning under linjen
                            tension: 0.3, // Kurvighet
                            yAxisID: 'y2', // Kopplad till y-axel 2 (höger)
                        }
                    ]
                },
                options: {
                    responsive: true, // Anpassa diagrammets storlek efter skärm
                    interaction: {
                        mode: 'index', // Visa tooltip för båda dataset när mus är över en punkt på x-axeln
                        intersect: false, // Tooltip visas även om musen inte exakt träffar en datapunkt
                    },
                    stacked: false, // Ej staplade linjer
                    scales: {
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'left', // Vänster y-axel
                            title: {
                                display: true,
                                text: 'Temperatur (°C)' // Titel för y-axel 1
                            }
                        },
                        y2: {
                            type: 'linear',
                            display: true,
                            position: 'right', // Höger y-axel
                            grid: {
                                drawOnChartArea: false, // Rita inte rutnät på höger y-axel
                            },
                            title: {
                                display: true,
                                text: 'Luftfuktighet (%)' // Titel för y-axel 2
                            }
                        }
                    }
                }
            });
        } else {
            // Om diagrammet redan finns, uppdatera det med ny data
            chart.data.labels = labels; // Uppdatera etiketter
            chart.data.datasets[0].data = temperatures; // Uppdatera temperaturdata
            chart.data.datasets[1].data = humidities; // Uppdatera luftfuktighetsdata
            chart.update(); // Rita om diagrammet med uppdaterad data
        }
    } catch (error) {
        // Om något går fel vid hämtning av data, logga i konsolen och visa felmeddelande
        console.error('Kunde inte hämta data:', error);
        document.getElementById('status').textContent = 'Fel vid hämtning av data.';
    }
}

fetchData(); // Kör funktionen direkt när sidan laddas

// Sätt intervallet för att uppdatera data var 5:e sekund
setInterval(fetchData, 5000);

