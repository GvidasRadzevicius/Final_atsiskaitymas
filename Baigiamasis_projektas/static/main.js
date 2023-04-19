function toggleCategories() {
    const categoriesList = document.getElementById("categories-list");
    if (categoriesList.style.display === "none") {
        categoriesList.style.display = "block";
    } else {
        categoriesList.style.display = "none";
    }
}

