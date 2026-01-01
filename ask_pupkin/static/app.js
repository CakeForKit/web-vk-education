
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

const likeQuestionButtons = document.querySelectorAll('button[data-question-id]');
for (const button of likeQuestionButtons) {
button.addEventListener('click', (e) => {
    const request = new Request(
        `/question/${button.dataset.questionId}/like`,
        {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            mode: 'same-origin' // Do not send CSRF token to another domain.
        }
    );
    fetch(request).then(function(response) {
        response.json().then((data) => {
                console.log(data)
                button.innerHTML = `${data.likeCount} Likes`;
                
                if (data.user_vote == 1) {
                    button.classList.remove('btn-light');
                    button.classList.add('btn-primary');
                } else if (data.user_vote == -1) {
                    button.classList.remove('btn-primary');
                    button.classList.add('btn-danger');
                } else {
                    button.classList.remove('btn-danger');
                    button.classList.add('btn-light');
                }
            }
        )
    });
    })
}

const likeAnswerButtons = document.querySelectorAll('button[data-answer-id]');
for (const button of likeAnswerButtons) {
button.addEventListener('click', (e) => {
    const request = new Request(
        `/answer/${button.dataset.answerId}/like`,
        {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            mode: 'same-origin' // Do not send CSRF token to another domain.
        }
    );
    fetch(request).then(function(response) {
        response.json().then((data) => {
                console.log(data)
                button.innerHTML = `${data.likeCount} Likes`;
                
                if (data.user_vote == 1) {
                    button.classList.remove('btn-light');
                    button.classList.add('btn-primary');
                } else if (data.user_vote == -1) {
                    button.classList.remove('btn-primary');
                    button.classList.add('btn-danger');
                } else {
                    button.classList.remove('btn-danger');
                    button.classList.add('btn-light');
                }
            }
        )
    });
    })
}


const correctCheckboxes = document.querySelectorAll('input[type="checkbox"][data-answer-id]');
for (const checkbox of correctCheckboxes) {
    checkbox.addEventListener('change', (e) => {
        const answerId = checkbox.dataset.answerId;
        const isChecked = checkbox.checked;
        console.log(`Изменение ответа ${answerId}: is_correct = ${isChecked}`);

        const request = new Request(
            `/answer/${answerId}/mark-correct`, 
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                },
                mode: 'same-origin',
                body: JSON.stringify({ is_correct: isChecked })
            }
        );
        
        fetch(request).then(function(response) {
            if (!response.ok) {
                checkbox.checked = !isChecked;
                throw new Error('Ошибка сети');
            }
            return response.json();
        }).catch((error) => {
            console.error('Ошибка:', error);
        });
    });
}