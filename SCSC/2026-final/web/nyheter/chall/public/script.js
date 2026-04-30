const newsGrid = document.getElementById('news-grid');
const articleView = document.getElementById('article-view');
const backBtn = document.getElementById('back-btn');
const articleTitle = document.getElementById('article-title');
const articleText = document.getElementById('article-text');
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');

async function loadNews() {
    try {
        const response = await fetch('/api/news');
        if (!response.ok) throw new Error('Misslyckades att hämta nyheter');

        const news = await response.json();
        displayNewsGrid(news);
    } catch (error) {
        newsGrid.innerHTML = '<div class="error">Misslyckades med att ladda nyheter. Försök igen senare.</div>';
        console.error('Fel vid laddning av nyheter:', error);
    }
}

async function searchNews(query) {
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Misslyckades att söka nyheter');

        const data = await response.json();
        displayNewsGrid(data.results, data.count);
    } catch (error) {
        newsGrid.innerHTML = '<div class="error">Misslyckades med att söka nyheter. Försök igen senare.</div>';
        console.error('Fel vid sökning av nyheter:', error);
    }
}

function displayNewsGrid(news, count) {
    newsGrid.innerHTML = '';

    if (count !== undefined) {
        const countDiv = document.createElement('div');
        countDiv.className = 'search-count';
        countDiv.textContent = `${count} ${count === 1 ? 'resultat' : 'resultat'} hittades`;
        newsGrid.appendChild(countDiv);
    }

    if (news.length === 0) {
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'loading';
        emptyDiv.textContent = 'Inga nyheter tillgängliga';
        newsGrid.appendChild(emptyDiv);
        return;
    }

    news.forEach(article => {
        const card = document.createElement('div');
        card.className = 'news-card';
        card.innerHTML = `<h3>${escapeHtml(article.title).replace(/([a-zA-Zä]+):/, '<span class="bryt">$1</span>:')}</h3>`;
        card.addEventListener('click', () => loadArticle(article.id));
        newsGrid.appendChild(card);
    });
}

async function loadArticle(id) {
    try {
        const response = await fetch(`/api/news/${id}`);
        if (!response.ok) throw new Error('Misslyckades att hämta artikel');

        const article = await response.json();
        displayArticle(article);
    } catch (error) {
        alert('Misslyckades med att ladda artikel');
        console.error('Fel vid laddning av artikel:', error);
    }
}

function displayArticle(article) {
    articleTitle.textContent = article.title;
    articleText.textContent = article.content;

    newsGrid.classList.add('hidden');
    articleView.classList.remove('hidden');
}

function showNewsGrid() {
    articleView.classList.add('hidden');
    newsGrid.classList.remove('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

backBtn.addEventListener('click', showNewsGrid);

searchBtn.addEventListener('click', () => {
    const query = searchInput.value.trim();
    if (query) {
        searchNews(query);
    } else {
        loadNews();
    }
});

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const query = searchInput.value.trim();
        if (query) {
            searchNews(query);
        } else {
            loadNews();
        }
    }
});

loadNews();
