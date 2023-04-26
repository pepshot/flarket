from requests import get, post, put, delete


url = 'http://localhost:8080'
print(get(f'http://localhost:8080/api/posts').json())
