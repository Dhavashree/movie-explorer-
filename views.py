import requests
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse

def get_tmdb_base_url():
    return 'https://api.themoviedb.org/3'

def home(request):
    api_key = settings.TMDB_API_KEY
    url = f"{get_tmdb_base_url()}/movie/popular?api_key={api_key}&language=en-US&page=1"
    
    # Check if a dummy key is still present
    if api_key == "YOUR_API_KEY_HERE":
        movies = []
        error_message = "Please configure your TMDB_API_KEY in settings.py"
    else:
        response = requests.get(url)
        movies = response.json().get('results', []) if response.status_code == 200 else []
        error_message = None
        
    return render(request, 'movies/home.html', {
        'movies': movies,
        'error_message': error_message
    })

def search(request):
    query = request.GET.get('q', '')
    movies = []
    error_message = None
    
    if query:
        api_key = settings.TMDB_API_KEY
        if api_key == "YOUR_API_KEY_HERE":
            error_message = "Please configure your TMDB_API_KEY in settings.py"
        else:
            url = f"{get_tmdb_base_url()}/search/movie?api_key={api_key}&query={query}&language=en-US&page=1"
            response = requests.get(url)
            movies = response.json().get('results', []) if response.status_code == 200 else []
            
    return render(request, 'movies/search_results.html', {
        'movies': movies, 
        'query': query,
        'error_message': error_message
    })

def movie_detail(request, movie_id):
    api_key = settings.TMDB_API_KEY
    movie = None
    error_message = None
    
    if api_key == "YOUR_API_KEY_HERE":
        error_message = "Please configure your TMDB_API_KEY in settings.py"
    else:
        url = f"{get_tmdb_base_url()}/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        movie = response.json() if response.status_code == 200 else None
        
    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'error_message': error_message
    })

def movie_ai_summary(request, movie_id):
    tmdb_api_key = settings.TMDB_API_KEY
    gemini_api_key = settings.GEMINI_API_KEY
    
    if not tmdb_api_key or tmdb_api_key == "YOUR_API_KEY_HERE" or not gemini_api_key:
        return JsonResponse({'error': 'API keys not configured'}, status=400)
        
    # Get movie title
    url = f"{get_tmdb_base_url()}/movie/{movie_id}?api_key={tmdb_api_key}&language=en-US"
    response = requests.get(url)
    
    if response.status_code != 200:
        return JsonResponse({'error': 'Movie not found'}, status=404)
        
    movie_title = response.json().get('title', 'Unknown Movie')
    
    # Request summary from Gemini
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={gemini_api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": f"Provide a short, fascinating fun fact or thematic analysis about the movie '{movie_title}'. Keep it under 3 sentences."}]}]}
    
    try:
        g_response = requests.post(gemini_url, headers=headers, json=data)
        g_response.raise_for_status()
        result_text = g_response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No insights available.')
        return JsonResponse({'summary': result_text})
    except Exception as e:
        return JsonResponse({'error': f'Failed to fetch AI insights: {str(e)}'}, status=500)
