from django.shortcuts import render

def home(request):
    return render(request, 'branches/home.html')