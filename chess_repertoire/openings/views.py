from django.shortcuts import render
from django.http import HttpResponse

def openings_home(request):
    return HttpResponse("Welcome to Chess Repertoire")
