const classes = {

    primary: [
        "Class 1",
        "Class 2",
        "Class 3",
        "Class 4",
        "Class 5"
    ],

    middle: [
        "Class 6",
        "Class 7",
        "Class 8"
    ],

    secondary: [
        "Class 9",
        "Class 10"
    ]
};


const levelSelect =
    document.getElementById("education_level");

const classSelect =
    document.getElementById("class_name");


if (levelSelect) {

    levelSelect.addEventListener("change", function () {

        classSelect.innerHTML =
            '<option value="">Select Class</option>';

        const selectedClasses =
            classes[this.value] || [];

        selectedClasses.forEach(function(className) {

            const option =
                document.createElement("option");

            option.value = className;
            option.textContent = className;

            classSelect.appendChild(option);
        });

    });

}