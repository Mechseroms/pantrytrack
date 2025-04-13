async function loginUser() {
    let username = document.getElementById('login_username').value
    let password = document.getElementById('login_password').value

    const response = await fetch(`/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password
        }),
    });
    
    data =  await response.json();
    transaction_status = "success"
    if (data.error){
        transaction_status = "danger"
    } else {
        window.location.href = '/';
    }

    UIkit.notification({
        message: data.message,
        status: transaction_status,
        pos: 'top-right',
        timeout: 5000
    });
}

function validateEmail(email) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
}

function isNotEmpty(inputValue) {
    return inputValue.trim().length > 0;
}

async function signUpValidate() {
    
    let error_total = 0

    let user_email = document.getElementById('signup_email')
    if(!validateEmail(user_email.value)){
        user_email.classList.add('uk-form-danger')
        error_total = error_total + 1
    } else {
        user_email.classList.remove('uk-form-danger')
    }

    let password = document.getElementById('signup_password')
    let password_confirm = document.getElementById('signup_password_confirm')

    if(!isNotEmpty(password.value)){
        password.classList.add('uk-form-danger')
        password_confirm.classList.add('uk-form-danger')
        error_total = error_total + 1
    } else if (!isNotEmpty(password_confirm.value)){
        password.classList.add('uk-form-danger')
        password_confirm.classList.add('uk-form-danger')
        error_total = error_total + 1
    } else if (!password.value === password_confirm.value){
        password.classList.add('uk-form-danger')
        password_confirm.classList.add('uk-form-danger')
        error_total = error_total + 1
    } else {
        password.classList.remove('uk-form-danger')
        password_confirm.classList.remove('uk-form-danger')
    }

    let username = document.getElementById('signup_username')
    if(isNotEmpty(username.value)){
        username.classList.remove('uk-form-danger')
    } else {
        username.classList.add('uk-form-danger')
        error_total = error_total + 1
    }

    let valid = true
    if(error_total > 0){
        valid = false
    }
    return valid    
}

async function signupUser() {
    let valid = await signUpValidate()
    if(valid){
        let user_email = document.getElementById('signup_email').value
        let password = document.getElementById('signup_password').value
        let username = document.getElementById('signup_username').value
        const response = await fetch(`/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password,
                email: user_email
            }),
        });
        
        data =  await response.json();
        transaction_status = "success"
        if (data.error){
            transaction_status = "danger"
        }

        UIkit.notification({
            message: data.message,
            status: transaction_status,
            pos: 'top-right',
            timeout: 5000
        });

        if(!data.error){
            document.getElementById('signup_email').value = ""
            document.getElementById('signup_password').value = ""
            document.getElementById('signup_password_confirm').value = ""
            document.getElementById('signup_username').value = ""
        }
        
    } else {
        UIkit.notification({
            message: 'Please review the form!',
            status: 'danger',
            pos: 'top-right',
            timeout: 5000
        });
    }
}