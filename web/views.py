from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.http import HttpResponseRedirect
from .models import Profile, Bell, main_current, pg_current, ke_current,ClientCommand 

# At the top of web/views.py, add these new imports:
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProfileSerializer

# At the top of web/views.py, add these imports
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# At the top of web/views.py, add the 'messages' import
from django.contrib import messages

# ... keep all your other views ...

# Add this new view function at the end of the file
def system_control(request):
    if not request.user.is_authenticated:
        return render(request, 'login.html', {'obj': 'Please login first'})

    if request.method == 'POST':
        command_type = request.POST.get('command')
        if command_type in ['AMP_ON', 'AMP_OFF', 'TEST_BELL']:
            # Create the command object in the database
            ClientCommand.objects.create(command=command_type)
            messages.success(request, f"Command '{command_type.replace('_', ' ').title()}' sent successfully!")
        return redirect('system_control') # Redirect to the same page to prevent re-posting

    context = {'username': str(request.user.username)}
    return render(request, 'system_control.html', context)

# ... keep all your existing views (login_view, home, etc.) ...

# Add this new function at the end of the file
@csrf_exempt # Exempt from CSRF token check since it's a simple GET API
def check_for_command(request):
    """
    API endpoint for the client script to check for new commands.
    """
    # Find the latest command that has not been acknowledged yet
    command = ClientCommand.objects.filter(acknowledged=False).order_by('-created_at').first()

    if command:
        # Mark it as acknowledged so it doesn't run again
        command.acknowledged = True
        command.save()
        # Return the command as JSON
        return JsonResponse({'status': 'command_found', 'command': command.command})
    else:
        # No new commands
        return JsonResponse({'status': 'no_command'})


@ensure_csrf_cookie
def login_user(request):
    """
    Handles user login. Uses modern authentication checks and redirects.
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'obj': 'Invalid username or password'})
    
    return render(request, 'login.html', {})

@csrf_protect
def home(request):
    """
    Displays the main dashboard for authenticated users.
    """
    if request.user.is_authenticated:
        return render(request, 'home.html', {'username': str(request.user.username)})
    else:
        return render(request, 'login.html', {'obj': 'Please login first'})

def logout_user(request):
    """
    Logs the user out and redirects to the login page.
    """
    logout(request)
    return render(request, 'login.html', {'obj': 'Logged out successfully'})

@csrf_protect
def apply(request):
    """
    Handles applying a saved Profile to a specific block (Main, PG, KE).
    Now queries the new `Profile` model.
    """
    if not request.user.is_authenticated:
        return render(request, 'login.html', {'obj': 'Please login first'})

    currentvalues = {
        "main": main_current.objects.get(id=1).name,
        "pg": pg_current.objects.get(id=1).name,
        "ke": ke_current.objects.get(id=1).name,
    }
    
    if request.method == 'POST':
        main_str = request.POST.get('main')
        pg_str = request.POST.get('pg')
        ke_str = request.POST.get('ke')
        
        if main_str:
            obj1 = main_current.objects.get(id=1)
            obj1.name = main_str
            obj1.save()
            currentvalues["main"] = main_str
        if pg_str:
            obj2 = pg_current.objects.get(id=1)
            obj2.name = pg_str
            obj2.save()
            currentvalues["pg"] = pg_str
        if ke_str:
            obj3 = ke_current.objects.get(id=1)
            obj3.name = ke_str
            obj3.save()
            currentvalues["ke"] = ke_str
            
        profiles = Profile.objects.all()
        return render(request, 'apply.html', {'obj': profiles, 'status': 'Successfully applied', 'username': str(request.user.username), 'currvals': currentvalues})

    profiles = Profile.objects.all()
    return render(request, 'apply.html', {'obj': profiles, 'username': str(request.user.username), 'currvals': currentvalues})

@csrf_protect
def create(request):
    """
    Handles the creation of a new Profile and its associated Bell objects.
    This is the robust replacement for the old, iterative logic.
    """
    if not request.user.is_authenticated:
        return render(request, 'login.html', {'obj': 'Please login first'})

    if request.method == 'POST':
        profile_name = request.POST.get('name')
        if not profile_name:
            return render(request, 'create.html', {'error': 'Profile name cannot be empty.', 'username': str(request.user.username)})

        if Profile.objects.filter(name=profile_name).exists():
            return render(request, 'create.html', {'error': f"A profile named '{profile_name}' already exists.", 'username': str(request.user.username)})
        
        profile = Profile.objects.create(name=profile_name)

        bell_times = request.POST.getlist('bell_time')
        
        for i in range(len(bell_times)):
            if bell_times[i]:
                bell_type_value = request.POST.get(f'bell_type_{i}')

                Bell.objects.create(
                    profile=profile,
                    time=bell_times[i],
                    is_long=(bell_type_value == 'L'),
                    play_anthem=(f'play_anthem_{i}' in request.POST),
                    monday=(f'monday_{i}' in request.POST),
                    tuesday=(f'tuesday_{i}' in request.POST),
                    wednesday=(f'wednesday_{i}' in request.POST),
                    thursday=(f'thursday_{i}' in request.POST),
                    friday=(f'friday_{i}' in request.POST),
                    saturday=(f'saturday_{i}' in request.POST),
                    sunday=(f'sunday_{i}' in request.POST),
                )
        return redirect('home')

    return render(request, 'create.html', {'username': str(request.user.username)})


@csrf_protect
# In web/views.py
def view_profiles(request):
    if not request.user.is_authenticated:
        return render(request, 'login.html', {'obj': 'Please login first'})

    all_profiles = Profile.objects.all()
    selected_profile = None

    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        if profile_id:
            # Use prefetch_related for efficiency when getting the selected profile
            selected_profile = Profile.objects.prefetch_related('bells').get(id=profile_id)

    context = {
        'profiles': all_profiles,
        'selected_profile': selected_profile,
        'username': str(request.user.username),
    }
    return render(request, 'profiles.html', context)


# In web/views.py

@csrf_protect
def edit_profile(request, profile_id):
    """
    Handles editing an existing profile and its associated bells.
    """
    if not request.user.is_authenticated:
        return render(request, 'login.html', {'obj': 'Please login first'})

    # Get the specific profile object we want to edit
    profile = get_object_or_404(Profile, id=profile_id)

    if request.method == 'POST':
        # Get the new name from the form
        new_name = request.POST.get('name')
        if not new_name:
            # Handle error
            return render(request, 'edit_profile.html', {'error': 'Profile name cannot be empty.', 'profile': profile})

        # Update the profile's name
        profile.name = new_name
        profile.save()

        # "Delete and Recreate" strategy: Delete all old bells for this profile
        profile.bells.all().delete()

        # Now, create the new bells from the form data, just like in the 'create' view
        bell_times = request.POST.getlist('bell_time')
        for i in range(len(bell_times)):
            if bell_times[i]:
                bell_type_value = request.POST.get(f'bell_type_{i}')
                Bell.objects.create(
                    profile=profile,
                    time=bell_times[i],
                    is_long=(bell_type_value == 'L'),
                    play_anthem=(f'play_anthem_{i}' in request.POST),
                    monday=(f'monday_{i}' in request.POST),
                    tuesday=(f'tuesday_{i}' in request.POST),
                    wednesday=(f'wednesday_{i}' in request.POST),
                    thursday=(f'thursday_{i}' in request.POST),
                    friday=(f'friday_{i}' in request.POST),
                    saturday=(f'saturday_{i}' in request.POST),
                    sunday=(f'sunday_{i}' in request.POST),
                )
        # Redirect to the list of profiles to see the changes
        return redirect('profiles')

    # If it's a GET request, render the form with the existing data
    context = {
        'profile': profile,
        'username': str(request.user.username)
    }
    return render(request, 'edit_profile.html', context)


# Add this new function at the end of the file:
@api_view(['GET'])
def get_schedule_api(request, block_name):
    """
    API endpoint for clients to fetch their current active schedule.
    """
    active_profile_name = None
    block_name = block_name.lower()

    try:
        if block_name == 'main':
            active_profile_name = main_current.objects.get(id=1).name
        elif block_name == 'pg':
            active_profile_name = pg_current.objects.get(id=1).name
        elif block_name == 'ke':
            active_profile_name = ke_current.objects.get(id=1).name
        else:
            return Response({'error': 'Invalid block name'}, status=404)

        profile = Profile.objects.get(name=active_profile_name)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    except Profile.DoesNotExist:
        return Response({'error': f'Active profile "{active_profile_name}" not found.'}, status=404)