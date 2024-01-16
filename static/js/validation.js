function validateIdFormat() {
    var idInput = document.getElementById('id');
    var idValue = idInput.value;
    var idPattern = /^F-\d{4}$/;  // Regular expression for the format "F-1234"

    if (!idPattern.test(idValue)) {
        alert('ID must be in the F-1234 format');
        idInput.focus();
        return false;
    }
    return true;
}