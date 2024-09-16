const starRatingForm = document.querySelector(".star-rating")
          
const handleFormChange = (e) => {
  console.log(e.target.value)
  return e.target.value
}

starRatingForm.addEventListener("change", handleFormChange)