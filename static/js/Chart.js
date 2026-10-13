<script>

const childId = {{ child.id }};


// --------------------------
// SUBJECT CHART
// --------------------------

fetch(
    `/parent/api/subject-progress?child_id=${childId}`
)
.then(response => response.json())
.then(data => {

    const labels =
        data.map(item => item.subject);

    const values =
        data.map(
            item => item.completion
        );

    new Chart(
        document.getElementById(
            "subjectChart"
        ),
        {
            type: "bar",

            data: {
                labels: labels,

                datasets: [{
                    label:
                        "Completion %",
                    data: values
                }]
            },

            options: {
                responsive: true,

                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        }
    );

});


// --------------------------
// WEEKLY CHART
// --------------------------

fetch(
    `/parent/api/weekly-activity?child_id=${childId}`
)
.then(response => response.json())
.then(data => {

    const labels =
        data.map(item => item.date);

    const values =
        data.map(item => item.games);

    new Chart(
        document.getElementById(
            "weeklyChart"
        ),
        {
            type: "line",

            data: {
                labels: labels,

                datasets: [{
                    label:
                        "Games Played",
                    data: values,
                    tension: 0.3
                }]
            },

            options: {
                responsive: true,

                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        }
    );

});

</script>