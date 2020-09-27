var password = document.querySelector("#password"), confirmation = document.querySelector("#confirmation");

function validatePassword() {
  if (password.value != confirmation.value) {
    confirmation.setCustomValidity("Passwords do not match");
  } else {
    confirmation.setCustomValidity('');
  }
}

password.onchange = validatePassword;
confirmation.onkeyup = validatePassword;
