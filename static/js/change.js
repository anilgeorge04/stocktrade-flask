var newpassword = document.querySelector("#newpassword"), confirmation = document.querySelector("#confirmation");

function validatePassword() {
  if (newpassword.value != confirmation.value) {
    confirmation.setCustomValidity("Passwords do not match");
  } else {
    confirmation.setCustomValidity('');
  }
}

newpassword.onchange = validatePassword;
confirmation.onkeyup = validatePassword;
