from urllib import request
from django.shortcuts import get_object_or_404, render
from hh.rag import process_input
from hh.models import Message
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from hh.models import Message, Sim
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def home(request):
    sim=Sim.objects.all()
    return render(request, 'index.html', {'sim': sim})

def mail(request):
    return render(request, 'mail.html')

def works(request):
    return render(request, 'role.html')

def register(request):
    return render(request, 'register.html')
 
def teams(request):
    return render(request, 'teams.html')

def ide(request):
    return render(request, 'IDE.html')

def login(request):
    return render(request, 'login.html')


def chat_page(request):
    messages = Message.objects.all().order_by("created_at")
    return render(request, "teams.html", {"messages": messages})
 

@require_POST
def save_message(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        message = request.POST.get('mbox')
        chat_id = request.POST.get('chat_id', 'sarah')
        
        Message.objects.create(content=message)        
        llm_response = process_input(message)
        return JsonResponse({
            'status': 'success',
            'response': llm_response,
            'chat_id': chat_id
        })
    else:
        message = request.POST.get('mbox')
        chat_id = request.POST.get('chat_id', 'sarah')
        Message.objects.create(content=message)
        llm_response = process_input(message)
        return render(request, 'teams.html', {
            'response': llm_response,
            'active_chat': chat_id
        })

def chat_page(request):
    messages = Message.objects.all().order_by("created_at")
    return render(request, "teams.html", {"messages": messages})

def sim(request):
    simulation_data = request.session.get('simulation_data', {})
    
    role_id = simulation_data.get('role_id')
    role_name = simulation_data.get('role_name')
    level = simulation_data.get('level')
    language = simulation_data.get('language')
    
    try:
        sim_object = Sim.objects.get(id=role_id) if role_id else None
    except Sim.DoesNotExist:
        sim_object = None
    
    return render(request, 'tt.html', {
        'role_id': role_id,
        'role_name': role_name,
        'level': level,
        'language': language,
        'sim_object': sim_object
    })

def begin(request):
    return render(request, 'welcome.html')  

def roles(request):
    return render(request, 'role.html')

def result(request):
    return render(request, 'result.html')

@csrf_exempt
@require_POST
def trial(request):
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            
            role_id = data.get('role_id')
            role_name = data.get('role_name')
            level = data.get('level')
            language = data.get('language')
            frontend_roles = ['Frontend Developer', 'Backend Developer', 'Data Analyst']
            request.session['simulation_data'] = {
                'role_id': role_id,
                'role_name': role_name,
                'level': level,
                'language': language
            }
            return JsonResponse({
                'status': 'success',
                'message': 'Simulation started successfully',
                'role_name': role_name,
                'redirect_to': 'sim' if role_name in frontend_roles else f'simulation/{role_id}'
            })
        else:
            role_id = request.POST.get('role_id')
            role_name = request.POST.get('role_name')
            level = request.POST.get('level')
            language = request.POST.get('language')
            request.session['simulation_data'] = {
                'role_id': role_id,
                'role_name': role_name,
                'level': level,
                'language': language
            }
            
            frontend_roles = ['Frontend Developer', 'Backend Developer', 'Data Analyst']
            if role_name in frontend_roles:
                return render(request, 'tt.html', {
                    'role_id': role_id,
                    'role_name': role_name,
                    'level': level,
                    'language': language
                })
            else:
                return render(request, f'{role_name.lower().replace(" ", "_")}.html', {
                    'role_id': role_id,
                    'role_name': role_name,
                    'level': level,
                    'language': language
                })
                
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

