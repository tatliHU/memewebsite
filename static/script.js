async function loadImages(func, page) {
    try {
        const response = await fetch(`http://localhost:5000/api/${func}/${page}`);
        const images = await response.json();
        displayImages(images);
    } catch (error) {
        console.error('Error loading images:', error);
    }
}

function displayImages(images) {
    const gallery = document.getElementById('gallery');
    gallery.innerHTML = '';

    images.forEach(image => {
        const imageCard = document.createElement('div');
        imageCard.className = 'image-card';

        imageCard.innerHTML = `
            <div class="title">${image.title}</div>
            <img src="${image.url}" alt="${image.title}">
            <div class="voting">
                <button onclick="vote(${image.postid}, 1)">Upvote</button>
                <div class="score" id="score-${image.postid}">${image.score}</div>
                <button onclick="vote(${image.postid}, -1)">Downvote</button>
            </div>
        `;

        gallery.appendChild(imageCard);
    });
}

async function vote(postID, delta) {
    try {
        const response = await fetch(`http://localhost:5000/api/vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ postID, delta })
        });

        if (response.ok) {
            scoreText = document.getElementById(`score-${postID}`)
            scoreText.textContent = parseInt(scoreText.textContent) + delta;
        } else {
            console.error('Error voting:', response.statusText);
        }
    } catch (error) {
        console.error('Error voting:', error);
    }
}

function showLoginForm(form) {
    var loginForm = document.getElementById('loginForm');
    var registerForm = document.getElementById('registerForm');
    var loginTab = document.getElementById('loginTab');
    var registerTab = document.getElementById('registerTab');

    if (form === 'login') {
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
    } else {
        registerForm.classList.add('active');
        loginForm.classList.remove('active');
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
    }
}

function submitLogin() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    // Encode credentials in base64
    const credentials = btoa(`${username}:${password}`);

    fetch('/api/login', {
        method: 'POST',
        headers: {
            'Authorization': `Basic ${credentials}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Authentication failed');
    })
    .then(data => {
        // Handle success
        console.log('Login successful', data);
        window.location.href = '/'; // Redirect on success
    })
    .catch(error => {
        // Handle error
        console.error('Error:', error);
        alert('Login failed');
    });
}

function submitRegister() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    const email = document.getElementById('register-email').value;

    fetch('/api/register', {
        method: 'POST',
        body: JSON.stringify({ username, password, email }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Registration failed');
    })
    .then(data => {
        // Handle success
        console.log('Login successful', data);
        window.location.href = '/'; // Redirect on success
    })
    .catch(error => {
        // Handle error
        console.error('Error:', error);
        alert('Registration failed');
    });
}