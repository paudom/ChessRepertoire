from django.shortcuts import render
from django.http import HttpResponse

def repertoire_home(request):
    return HttpResponse("Welcome to Chess Repertoire.")
