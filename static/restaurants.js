const restaurantsRef = db.collection("restaurants");
restaurantsRef.get().then((querySnapshot) => {
    querySnapshot.forEach((doc) => {
        const restaurant = doc.data();
        console.log(restaurant.Name);
        // Display the restaurant data in your application as needed
    });
});
