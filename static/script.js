async function loadImages(func, page, query = "", voteEndpoint = "vote") {
    try {
        const response = await fetch(`/api/${func}?page=${page}&${query}`);
        const images = await response.json();
        displayImages(images, voteEndpoint);
    } catch (error) {
        console.error('Error loading images:', error);
    }
}

function displayImages(images, voteEndpoint) {
    const gallery = document.getElementById('gallery');
    gallery.innerHTML = '';

    images.forEach(image => {
        let hrefs = '';
        image.tags.forEach(tag => {
            displayed_tag=tag.replace(/^tag_/, '').toUpperCase();
            const href = `<a href="/tag/${tag}">${displayed_tag}</a>`;
            hrefs += href + '\n';
        });
        
        const imageCard = document.createElement('div');
        imageCard.className = 'image-card';

        imageCard.innerHTML = `
            <div class="image-top">
                <a>${image.title}</a>
                <span>${hrefs}</span>
            </div>
            <img src="${image.url}" alt="Unable to load image">
            <div class="voting-oval">
                <div class="voting-controls">
                    <button class="vote-button" onclick="vote(${image.postid}, 1, '${voteEndpoint}')">+</button>
                    <div class="score" id="score-${image.postid}">${image.score}</div>
                    <button class="vote-button" onclick="vote(${image.postid}, -1, '${voteEndpoint}')">-</button>
                </div>
                <div class="postername">
                    <a href="/user?name=${image.username}">${image.username}</a>
                </div>
            </div>
        `;

        gallery.appendChild(imageCard);
    });
}

function vote(postID, delta, voteEndpoint) {
    fetch(`/api/${voteEndpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ postID, delta })
    })
    .then(response => {
        if (response.ok) {
            scoreText = document.getElementById(`score-${postID}`)
            scoreText.textContent = parseInt(scoreText.textContent) + delta;
            return;
        }
        return Promise.reject(response);
    })
    .catch(response => {
        response.json().then((json) => {
            console.log(json.message);
            alert(json.message);
        })
    });
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
            window.location.href = '/';
        }
        return Promise.reject(response);
    })
    .catch(response => {
        response.json().then((json) => {
            console.log(json.message);
            alert(json.message);
        })
    });
}

function submitRegister() {
    const checkbox = document.getElementById('data-policy-checkbox');
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    const email = document.getElementById('register-email').value;
    
    if (!checkbox.checked) {
        alert('You must accept the data policy to register.');
        return;
    }

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
        return Promise.reject(response);
    })
    .then(data => {
        alert(data)
        window.location.href = '/'; // Redirect on success
    })
    .catch((response) => {
        response.json().then((json) => {
            for (const key in json) {
                json[key].forEach(item => alert(`${key}: ${item}`));
            }
        })
    });
}

function loadPageSelector(func, page) {
    const pageSelector = document.getElementById('pageSelector');
    pageSelector.innerHTML = '';

    let pageNumber = parseInt(page);
    let start = (pageNumber <= 4) ? 1 : pageNumber - 3;
    let end = (pageNumber <= 4) ? 7 : pageNumber + 3;
    for (let i = start; i <= end; i++) {
        pageHTML = `
            <form action="/${func}">
                <input type="submit" value="${i}" class="pagerButton" />
                <input type="hidden" name="page" value="${i}" />
            </form>
        `;
        currentPageHTML = `
            <form action="javascript:void(0);">
                <input type="submit" value="${i}" class="pagerButtonCurrent" />
            </form>
        `;
        const pageButton = document.createElement('div');
        pageButton.innerHTML = i==page ? currentPageHTML : pageHTML;
        pageSelector.appendChild(pageButton);
    }
}

function showProfile(username) {
    var profile = document.getElementById('profileMenu');
    var usernameSpan = document.getElementById('username');
    var loginForm = document.getElementById('formContainer');
    
    if (username=='') {
        profile.style.display = 'none';
        loginForm.style.display = '';
    } 
    else {
        profile.style.display = '';
        loginForm.style.display = 'none';
        usernameSpan.textContent = username;
    }
}

function init(func, page, username) {
    loadPageSelector(func, page)
    showProfile(username)
}