async function getTopPicks() {
    // Fetch the top restaurants using the cosine similarity algorithm
    const topRestaurants = await fetchTopRestaurants();

    // Select the .restaurant-list div
    const restaurantList = document.querySelector('.restaurant-list');

    // Iterate through the topRestaurants array and create the HTML elements
    topRestaurants.forEach(restaurant => {
        const restaurantDiv = document.createElement('div');
        restaurantDiv.className = 'restaurant';

        const restaurantName = document.createElement('h2');
        restaurantName.textContent = restaurant.name;
        restaurantDiv.appendChild(restaurantName);

        const restaurantRating = document.createElement('p');
        restaurantRating.textContent = `Rating: ${restaurant.rating}`;
        restaurantDiv.appendChild(restaurantRating);

        // Add any additional restaurant information you'd like to display

        // Add the restaurantDiv to the .restaurant-list
        restaurantList.appendChild(restaurantDiv);
    });
}

// Call the function when the page loads
getTopPicks();
