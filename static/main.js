document.addEventListener('DOMContentLoaded', function () {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const currentTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : 'light';

    setTheme(currentTheme);

    darkModeToggle.addEventListener('click', function () {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
    });

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }
});
async function saveRestaurant(event, button) {
    event.preventDefault();

    // Get the current user from the auth object
    const user = auth.currentUser;

    // Get the button that was clicked
    const saveButton = button;

    // Extract the restaurant's information from the data attributes
    const ID_TA = saveButton.getAttribute('data-id-ta');
    const name = saveButton.getAttribute('data-name');
    const description = saveButton.getAttribute('data-description');

    if (user) {
        if (ID_TA) {
            db.collection("users")
                .doc(user.uid)
                .collection("savedRestaurants")
                .doc(ID_TA)
                .set({ ID_TA, name, description })
                .then(() => {
                    // Changes the button to a checkmark
                    saveButton.innerHTML = '<i class="fas fa-check"></i>';
                    saveButton.disabled = true;
                })
                .catch((error) => {
                    console.error("Error saving restaurant: ", error);
                });
        } else {
            console.error("Error: ID_TA is empty");
        }
    } else {
        alert("Please log in to save restaurants.");
    }
}


