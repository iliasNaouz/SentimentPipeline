document.addEventListener("DOMContentLoaded", function() {
    console.log("JavaScript is loaded and working!");

    const kd = document.querySelectorAll(".key");
    const textbox = document.querySelector(".textbox");

    let keyPressed = (e) => {
        let kc = e.keyCode;

        if ((kc >= 65 && kc <= 90) || kc == 32) {
            if (kc == 81) { kd[0].classList.add("key__down"); }
            else if (kc == 87) { kd[1].classList.add("key__down"); }
            else if (kc == 69) { kd[2].classList.add("key__down"); }
            else if (kc == 82) { kd[3].classList.add("key__down"); }
            else if (kc == 84) { kd[4].classList.add("key__down"); }
            else if (kc == 89) { kd[5].classList.add("key__down"); }
            else if (kc == 85) { kd[6].classList.add("key__down"); }
            else if (kc == 73) { kd[7].classList.add("key__down"); }
            else if (kc == 79) { kd[8].classList.add("key__down"); }
            else if (kc == 80) { kd[9].classList.add("key__down"); }
            else if (kc == 65) { kd[10].classList.add("key__down"); }
            else if (kc == 83) { kd[11].classList.add("key__down"); }
            else if (kc == 68) { kd[12].classList.add("key__down"); }
            else if (kc == 70) { kd[13].classList.add("key__down"); }
            else if (kc == 71) { kd[14].classList.add("key__down"); }
            else if (kc == 72) { kd[15].classList.add("key__down"); }
            else if (kc == 74) { kd[16].classList.add("key__down"); }
            else if (kc == 75) { kd[17].classList.add("key__down"); }
            else if (kc == 76) { kd[18].classList.add("key__down"); }
            else if (kc == 90) { kd[19].classList.add("key__down"); }
            else if (kc == 88) { kd[20].classList.add("key__down"); }
            else if (kc == 67) { kd[21].classList.add("key__down"); }
            else if (kc == 86) { kd[22].classList.add("key__down"); }
            else if (kc == 66) { kd[23].classList.add("key__down"); }
            else if (kc == 78) { kd[24].classList.add("key__down"); }
            else if (kc == 77) { kd[25].classList.add("key__down"); }
            else if (kc == 32) {
                kd[26].classList.add("key__down");
                textbox.innerHTML += "&nbsp;";
            }
        }
    }

    let keyReleased = (e) => {
        let kc = e.keyCode;
        if (kc == 81) { kd[0].classList.remove("key__down"); }
        else if (kc == 87) { kd[1].classList.remove("key__down"); }
        else if (kc == 69) { kd[2].classList.remove("key__down"); }
        else if (kc == 82) { kd[3].classList.remove("key__down"); }
        else if (kc == 84) { kd[4].classList.remove("key__down"); }
        else if (kc == 89) { kd[5].classList.remove("key__down"); }
        else if (kc == 85) { kd[6].classList.remove("key__down"); }
        else if (kc == 73) { kd[7].classList.remove("key__down"); }
        else if (kc == 79) { kd[8].classList.remove("key__down"); }
        else if (kc == 80) { kd[9].classList.remove("key__down"); }
        else if (kc == 65) { kd[10].classList.remove("key__down"); }
        else if (kc == 83) { kd[11].classList.remove("key__down"); }
        else if (kc == 68) { kd[12].classList.remove("key__down"); }
        else if (kc == 70) { kd[13].classList.remove("key__down"); }
        else if (kc == 71) { kd[14].classList.remove("key__down"); }
        else if (kc == 72) { kd[15].classList.remove("key__down"); }
        else if (kc == 74) { kd[16].classList.remove("key__down"); }
        else if (kc == 75) { kd[17].classList.remove("key__down"); }
        else if (kc == 76) { kd[18].classList.remove("key__down"); }
        else if (kc == 90) { kd[19].classList.remove("key__down"); }
        else if (kc == 88) { kd[20].classList.remove("key__down"); }
        else if (kc == 67) { kd[21].classList.remove("key__down"); }
        else if (kc == 86) { kd[22].classList.remove("key__down"); }
        else if (kc == 66) { kd[23].classList.remove("key__down"); }
        else if (kc == 78) { kd[24].classList.remove("key__down"); }
        else if (kc == 77) { kd[25].classList.remove("key__down"); }
        else if (kc == 32) { kd[26].classList.remove("key__down"); }
    }

    const updateProgress = () => {
        const maxLength = 200; // Example max length for 100% completion
        const currentLength = textbox.value.length;
        const percentage = Math.min((currentLength / maxLength) * 100, 100); // Ensure it doesn't go over 100%

        // Update the circular progress bar
        const circle = document.querySelector('.progress-circle__fg');
        const radius = circle.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (percentage / 100) * circumference;
        circle.style.strokeDashoffset = offset;
        document.querySelector('.stat__percentage').textContent = `${Math.round(percentage)}%`;
    };

    textbox.addEventListener('input', updateProgress);

    // Add functionality to the new button
    const buttonKey = document.querySelector(".key__button");
    buttonKey.addEventListener("click", function() {
        const message = textbox.value;
        fetch("/button-click", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({message: message})
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            textbox.value = data.message;  // Update the textbox with the response message
            updateProgress();  // Update the progress bar based on the new content
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Initialize the progress on page load
    updateProgress();

    window.addEventListener("keydown", keyPressed);
    window.addEventListener("keyup", keyReleased);
});
