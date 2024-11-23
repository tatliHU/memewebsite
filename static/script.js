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
    images.forEach(image => {        
        const imageCard = document.createElement('div');
        imageCard.classList.add('image-card');

        const imageTop = document.createElement('div');
        imageTop.classList.add('image-top');

        const imageTopLeft = document.createElement('div');
        imageTopLeft.classList.add('image-top-left');

        const imageTopMiddle = document.createElement('div');
        imageTopMiddle.classList.add('image-top-middle');
        const titleAnchor = document.createElement('a');
        titleAnchor.textContent = image.title;
        titleAnchor.href = `/post?id=${image.postid}`;
        imageTopMiddle.appendChild(titleAnchor);

        const imageTopRight = document.createElement('div');
        imageTopRight.classList.add('image-top-right');
        const hrefSpan = document.createElement('span');
        image.tags.forEach(tag => {
            displayedTag=tag.replace(/^tag_/, '').toUpperCase();
            const anchorElement = document.createElement('a');
            anchorElement.href = `/tag?name=${encodeURIComponent(tag)}`;
            anchorElement.textContent = displayedTag;
            anchorElement.style.marginRight = '8px';
            hrefSpan.appendChild(anchorElement);
        });
        imageTopRight.appendChild(hrefSpan);

        imageTop.appendChild(imageTopLeft);
        imageTop.appendChild(imageTopMiddle);
        imageTop.appendChild(imageTopRight);
        imageCard.appendChild(imageTop);

        const imgElement = document.createElement('img');
        imgElement.src = image.url;
        imgElement.alt = 'Unable to load image';
        imageCard.appendChild(imgElement);

        const votingOval = document.createElement('div');
        votingOval.classList.add('voting-oval');

        const votingControls = document.createElement('div');
        votingControls.classList.add('voting-controls');

        const upvoteButton = document.createElement('button');
        upvoteButton.classList.add('vote-button');
        upvoteButton.textContent = '+';
        upvoteButton.id = `upvote-${image.postid}`;
        upvoteButton.onclick = () => vote(image.postid, 1, voteEndpoint);

        const scoreDiv = document.createElement('div');
        scoreDiv.classList.add('score');
        scoreDiv.id = `score-${image.postid}`;
        scoreDiv.textContent = image.score;

        const downvoteButton = document.createElement('button');
        downvoteButton.classList.add('vote-button');
        downvoteButton.textContent = '-';
        downvoteButton.id = `downvote-${image.postid}`;
        downvoteButton.onclick = () => vote(image.postid, -1, voteEndpoint);
        if (image.vote === 1) {
            upvoteButton.classList.add('upvote-active');
        } else if (image.vote === -1) {
            downvoteButton.classList.add('downvote-active');
        }

        votingControls.appendChild(upvoteButton);
        votingControls.appendChild(scoreDiv);
        votingControls.appendChild(downvoteButton);
        votingOval.appendChild(votingControls);

        const posterNameDiv = document.createElement('div');
        posterNameDiv.classList.add('postername');
        const userLink = document.createElement('a');
        userLink.href = `/user?name=${encodeURIComponent(image.username)}`;
        userLink.textContent = image.username;

        posterNameDiv.appendChild(userLink);
        votingOval.appendChild(posterNameDiv);
        imageCard.appendChild(votingOval);

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
            upvoteButton = document.getElementById(`upvote-${postID}`)
            downvoteButton = document.getElementById(`downvote-${postID}`)
            state_upvote = upvoteButton.classList.contains('upvote-active')
            state_downvote = downvoteButton.classList.contains('downvote-active')
            if (delta === 1) {
                if (state_upvote) {
                    scoreText.textContent = parseInt(scoreText.textContent) - 1;
                }
                else if (state_downvote) {
                    scoreText.textContent = parseInt(scoreText.textContent) + 2;
                }
                else {
                    scoreText.textContent = parseInt(scoreText.textContent) + 1;
                }
                upvoteButton.classList.toggle('upvote-active');
                downvoteButton.classList.remove('downvote-active');
            }
            if (delta == -1) {
                if (state_downvote) {
                    scoreText.textContent = parseInt(scoreText.textContent) + 1;
                }
                else if (state_upvote) {
                    scoreText.textContent = parseInt(scoreText.textContent) - 2;
                }
                else {
                    scoreText.textContent = parseInt(scoreText.textContent) - 1;
                }
                upvoteButton.classList.remove('upvote-active');
                downvoteButton.classList.toggle('downvote-active');
            }
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
        alert(data.message)
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

    let pageNumber = parseInt(page);
    let start = (pageNumber <= 4) ? 1 : pageNumber - 3;
    let end = (pageNumber <= 4) ? 7 : pageNumber + 3;
    for (let i = start; i <= end; i++) {
        const pageButton = document.createElement('div');
        if (i == page) {
            // Create form for the current page
            const currentForm = document.createElement('form');
            currentForm.setAttribute('action', 'javascript:void(0);');
        
            const currentInput = document.createElement('input');
            currentInput.setAttribute('type', 'submit');
            currentInput.setAttribute('value', i);
            currentInput.classList.add('pagerButtonCurrent');
        
            currentForm.appendChild(currentInput);
            pageButton.appendChild(currentForm);
        } else {
            // Create form for other pages
            const form = document.createElement('form');
            form.setAttribute('action', `/${encodeURIComponent(func)}`);
        
            const submitInput = document.createElement('input');
            submitInput.setAttribute('type', 'submit');
            submitInput.setAttribute('value', i);
            submitInput.classList.add('pagerButton');
        
            const hiddenInput = document.createElement('input');
            hiddenInput.setAttribute('type', 'hidden');
            hiddenInput.setAttribute('name', 'page');
            hiddenInput.setAttribute('value', i);
        
            form.appendChild(submitInput);
            form.appendChild(hiddenInput);
            pageButton.appendChild(form);
        }
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