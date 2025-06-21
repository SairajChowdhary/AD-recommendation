function recommend() {
    fetch('/recommend', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({content: document.getElementById('content').value})
    })
    .then(resp => {
        if (resp.status === 401) {
            alert('Please log in to get recommendations.');
            return [];
        }
        return resp.json();
    })
    .then(data => {
        let html = '<h3>Recommended Ads:</h3>';
        data.forEach(ad => {
            html += `<div>
                <b>${ad.title}</b> [${ad.category}] (Bid: $${ad.bid})
                <button onclick="adClick(${ad.id})">Click</button>
            </div>`;
        });
        document.getElementById('ads').innerHTML = html;
    });
}

function adClick(ad_id) {
    fetch('/ad_click', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ad_id: ad_id})
    });
    alert('Ad click logged!');
}

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            fetch('/login', {
                method: 'POST',
                body: new FormData(loginForm)
            }).then(resp => {
                if (resp.redirected) {
                    window.location.href = resp.url;
                } else if (resp.status === 401) {
                    alert('Invalid credentials!');
                }
            });
        });
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            fetch('/register', {
                method: 'POST',
                body: new FormData(registerForm)
            }).then(resp => {
                if (resp.redirected) {
                    window.location.href = resp.url;
                } else if (resp.status === 400) {
                    alert('User already exists!');
                }
            });
        });
    }
});
// raj.js - JavaScript for Raj's Ad Recommendation System