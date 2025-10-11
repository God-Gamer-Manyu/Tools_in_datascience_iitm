const questions = [
  {
    id: 1,
    text: "Which programming language was created by Guido van Rossum?",
    choices: ["Python", "Java", "Ruby", "Scala", "Go"],
    answerIndex: 0
  },
  {
    id: 2,
    text: "Which language runs in a web browser and is primarily used for client-side web development?",
    choices: ["C#", "JavaScript", "Kotlin", "Swift", "Rust"],
    answerIndex: 1
  },
  {
    id: 3,
    text: "Which language is known for its `write once, run anywhere` philosophy?",
    choices: ["C++", "Java", "Perl", "Haskell", "Elixir"],
    answerIndex: 1
  },
  {
    id: 4,
    text: "Which programming language was created by Yukihiro Matsumoto (Matz)?",
    choices: ["Ruby", "Go", "PHP", "TypeScript", "D"],
    answerIndex: 0
  }
];

let current = 0;
const answers = new Array(questions.length).fill(null);

const container = document.getElementById('question-container');
const prevBtn = document.getElementById('prev');
const nextBtn = document.getElementById('next');
const resultDiv = document.getElementById('result');

function renderQuestion(index) {
  const q = questions[index];
  container.innerHTML = '';

  const qEl = document.createElement('div');
  qEl.className = 'question';

  const h2 = document.createElement('h2');
  h2.textContent = `Question ${index + 1} of ${questions.length}`;
  qEl.appendChild(h2);

  const p = document.createElement('p');
  p.textContent = q.text;
  qEl.appendChild(p);

  const list = document.createElement('div');
  list.className = 'choices';

  q.choices.forEach((c, i) => {
    const label = document.createElement('label');
    label.className = 'choice';

    const input = document.createElement('input');
    input.type = 'radio';
    input.name = 'choice';
    input.value = i;
    input.checked = answers[index] === i;
    input.addEventListener('change', () => {
      answers[index] = i;
    });

    const span = document.createElement('span');
    span.textContent = c;

    label.appendChild(input);
    label.appendChild(span);
    list.appendChild(label);
  });

  qEl.appendChild(list);

  container.appendChild(qEl);

  prevBtn.disabled = index === 0;
  nextBtn.textContent = index === questions.length - 1 ? 'Submit' : 'Next';
  resultDiv.classList.add('hidden');
}

function showResult() {
  let score = 0;
  questions.forEach((q, i) => {
    if (answers[i] === q.answerIndex) score++;
  });

  resultDiv.classList.remove('hidden');
  resultDiv.innerHTML = `<h3>Your score: ${score} / ${questions.length}</h3>`;

  const details = document.createElement('ul');
  questions.forEach((q, i) => {
    const li = document.createElement('li');
    const chosen = answers[i] === null ? 'No answer' : q.choices[answers[i]];
    const correct = q.choices[q.answerIndex];
    li.textContent = `Q${i+1}: ${q.text} — Your answer: ${chosen} — Correct: ${correct}`;
    details.appendChild(li);
  });
  resultDiv.appendChild(details);
}

prevBtn.addEventListener('click', () => {
  if (current > 0) {
    current--;
    renderQuestion(current);
  }
});

nextBtn.addEventListener('click', () => {
  if (current < questions.length - 1) {
    current++;
    renderQuestion(current);
  } else {
    showResult();
  }
});

// initial render
renderQuestion(current);
