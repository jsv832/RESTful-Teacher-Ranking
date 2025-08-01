from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg

from .models import Professor, Rating, Module, ModuleInstance, TeachingAssignment
from django.views.decorators.csrf import csrf_exempt

# Class to Disable CSRF and have session authentication for the whole app
# Disable csrfMiddleware method found and learnt in the following link
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation

class DisableCSRFMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        response = self.get_response(request)
        return response

# Register API
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):

    #Register with username, email and password
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    # Only username and password required
    # If same username has already been used then not allow to create new account with that username
    if not username or not password:
        return Response({"error": "Username and password are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists."},
                        status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    return Response({"message": "User registered successfully."},
                    status=status.HTTP_201_CREATED)

# Login API
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):

    #To login username and password are required
    username = request.data.get('username')
    password = request.data.get('password')

    #Authenticate if an user with following username and password combination exists
    #then set session cookie
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({"message": "Login successful."})
    else:
        return Response({"error": "Invalid credentials."},
                        status=status.HTTP_401_UNAUTHORIZED)


# Logout API
@csrf_exempt
@api_view(['POST'])
def logout_user(request):

    #Logout
    logout(request)
    return Response({"message": "Logout successful."})


# List of Modules and Teachers which professor teachs it
# Option 1
# GET /api/list/
@api_view(['GET'])
@permission_classes([AllowAny])
def list_module_instances(request):

    module_instances = ModuleInstance.objects.all().order_by('module__code','year','semester')
    data = []
    for mi in module_instances:
        tas = TeachingAssignment.objects.filter(module_instance=mi)

        # Create list of professors
        professor_list = [f"{ta.professor.id}, {ta.professor.name}" for ta in tas]
        data.append({
            "module_code": mi.module.code,
            "module_name": mi.module.name,
            "year": mi.year,
            "semester": mi.semester,
            "taught_by": professor_list,
        })
    return Response(data)


# List of all professors and also show their ratings
# Option 2
# GET /api/view/
@api_view(['GET'])
@permission_classes([AllowAny])
def view_all_professor_ratings(request):

    professors = Professor.objects.all()
    response_data = []

    for prof in professors:
        # Get all ratings corresponding to a professor
        tas = TeachingAssignment.objects.filter(professor=prof)
        ratings = Rating.objects.filter(teaching_assignment__in=tas)

        # Get ratings and then get it's average and round it to visualise through stars
        if ratings.exists():
            avg_val = ratings.aggregate(Avg('rating'))['rating__avg']
            avg_val = round(avg_val)
        else:
            avg_val = 0

        rating = '*' * avg_val if avg_val > 0 else 'No rating'
        response_data.append({
            "professor_id": prof.id,
            "professor_name": prof.name,
            "rating": rating,
        })

    return Response(response_data)

# Get specific teacher and their average in a certain module
# Option 3
# GET /api/average/professor_id/module_code/
@api_view(['GET'])
@permission_classes([AllowAny])
def average_rating_professor_module(request, professor_id, module_code):

    professor = get_object_or_404(Professor, pk=professor_id)
    module = get_object_or_404(Module, pk=module_code)

    # Get all ModuleInstances for this module
    module_instances = ModuleInstance.objects.filter(module=module)

    # Get all teaching assignments of that professor for a module instance
    tas = TeachingAssignment.objects.filter(professor=professor, module_instance__in=module_instances)

    # Get all ratings
    ratings = Rating.objects.filter(teaching_assignment__in=tas)

    if ratings.exists():
        avg_val = ratings.aggregate(Avg('rating'))['rating__avg']
        avg_val = round(avg_val)
    else:
        avg_val = 0

    rating = '*' * avg_val if avg_val > 0 else 'No rating'

    return Response({
        "professor_id": professor.id,
        "professor_name": professor.name,
        "module_code": module.code,
        "module_name": module.name,
        "rating": rating,
    })

# Rate the professor in a module instance
# Option 4
# POST /api/rate-professor/
# It requires the user to be logged in

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_professor(request):

    #Process all data provided through user input
    professor_id = request.data.get('professor_id')
    module_code = request.data.get('module_code')
    year = request.data.get('year')
    semester = request.data.get('semester')
    rating_value = request.data.get('rating')

    # Check if all fields are filled before rating can be added
    if not all([professor_id, module_code, year, semester, rating_value]):
        return Response({"error": "Missing required fields."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Convert year,semester and rating to integers
    try:
        year = int(year)
        semester = int(semester)
        rating_value = int(rating_value)
    except ValueError:
        return Response({"error": "year, semester, and rating must be integers."},
                        status=status.HTTP_400_BAD_REQUEST)

    #Check if Semester is 1 or 2. There can't be more than 2 semesters
    if semester not in [1, 2]:
            return Response({"error": "Semester must be 1 or 2."},
                            status=status.HTTP_400_BAD_REQUEST)

    if rating_value < 1 or rating_value > 5:
        return Response({"error": "Rating must be between 1 and 5."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Check objects all if it doesn't exist give 404 error
    professor = get_object_or_404(Professor, pk=professor_id)
    module = get_object_or_404(Module, pk=module_code)
    module_instance = get_object_or_404(ModuleInstance, module=module, year=year, semester=semester)
    ta = get_object_or_404(TeachingAssignment, module_instance=module_instance, professor=professor)

    # If user has already rate a module instance it cannot do again
    existing_rating = Rating.objects.filter(user=request.user, teaching_assignment=ta).first()
    if existing_rating:
        return Response({"error": "You have already rated this professor for this module instance."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Create new rating
    new_rating = Rating.objects.create(
        user=request.user,
        teaching_assignment=ta,
        rating=rating_value
    )

    return Response({
        "message": "Rating created successfully.",
        "rating_id": new_rating.id
    }, status=status.HTTP_201_CREATED)
