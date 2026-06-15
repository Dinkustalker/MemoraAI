from django.shortcuts import render, redirect
from groq import Groq
from dotenv import load_dotenv
from .models import Appointment, UserProfile
from django.http import JsonResponse
import os
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2
import requests

env_path = Path(__file__).resolve().parent.parent / "myproject" / ".env"
load_dotenv(env_path)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def home(request):
    return render(request, "myapp/home.html")


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        request.session["user_email"] = email

        print("LOGIN EMAIL =", email)

        return redirect("dashboard")

    return redirect("home")


def dashboard(request):
    email = request.session.get("user_email")

    print("DASHBOARD EMAIL =", email)

    if not email:
        return redirect("home")

    profile = UserProfile.objects.filter(email=email).first()

    print("DASHBOARD PROFILE =", profile)

    return render(request, "myapp/dashboard.html", {
        "profile": profile,
        "email": email
    })


def settings(request):
    email = request.session.get("user_email")

    print("SETTINGS EMAIL =", email)

    if not email:
        return redirect("home")

    if request.method == "POST":
        print("SETTINGS POST DATA =", request.POST)

        profile, created = UserProfile.objects.get_or_create(email=email)

        profile.full_name = request.POST.get("full_name")
        profile.emergency_contact = request.POST.get("emergency_contact")
        profile.primary_doctor = request.POST.get("primary_doctor")
        profile.current_medications = request.POST.get("current_medications")
        profile.blood_group = request.POST.get("blood_group")
        profile.allergies = request.POST.get("allergies")

        profile.save()

        print("PROFILE SAVED =", profile.full_name)

        return redirect("dashboard")

    profile = UserProfile.objects.filter(email=email).first()

    return render(request, "myapp/settings.html", {
        "profile": profile
    })


def reminders(request):
    return render(request, "myapp/reminders.html")


def ai_assistant(request):
    answer = None

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        if question:
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are MemoraAI, an AI healthcare assistant.
Suggest possible causes only.
Do not confirm a diagnosis.
"""
                        },
                        {
                            "role": "user",
                            "content": question
                        }
                    ]
                )

                answer = response.choices[0].message.content

            except Exception as e:
                answer = f"Error: {str(e)}"
        else:
            answer = "Please enter a question."

    return render(request, "myapp/ai_assistant.html", {
        "answer": answer
    })


def analytics(request):
    return render(request, "myapp/analytics.html")


def profile(request):
    return render(request, "myapp/profile.html")


def about(request):
    return render(request, "myapp/about.html")


def appointments(request):
    if request.method == "POST":
        Appointment.objects.create(
            doctor=request.POST.get("doctor"),
            hospital=request.POST.get("hospital"),
            date=request.POST.get("date"),
            time=request.POST.get("time"),
            department=request.POST.get("department"),
            purpose=request.POST.get("purpose")
        )

        return redirect("appointment_details")

    return render(request, "myapp/appointments.html")


def appointment_details(request):
    appointments = Appointment.objects.all().order_by("-id")

    return render(request, "myapp/appointment_details.html", {
        "appointments": appointments
    })


def prescriptions(request):
    medicine_info = ""

    if request.method == "POST":
        medicine_name = request.POST.get("medicine_name")

        url = (
            f"https://api.fda.gov/drug/label.json"
            f"?search=openfda.brand_name:{medicine_name}"
            f"+openfda.generic_name:{medicine_name}"
            f"&limit=1"
        )

        try:
            response = requests.get(url)
            data = response.json()

            if "results" not in data:
                medicine_info = "Medicine not found in OpenFDA database"
            else:
                result = data["results"][0]

                medicine_info = f"""
Brand Name:
{result.get('openfda', {}).get('brand_name', ['N/A'])[0]}

Generic Name:
{result.get('openfda', {}).get('generic_name', ['N/A'])[0]}

Manufacturer:
{result.get('openfda', {}).get('manufacturer_name', ['N/A'])[0]}

Purpose:
{result.get('purpose', ['N/A'])[0]}

Warnings:
{result.get('warnings', ['N/A'])[0][:500] if result.get('warnings') else 'N/A'}
"""

        except Exception as e:
            medicine_info = f"Error: {e}"

    return render(request, "myapp/prescriptions.html", {
        "medicine_info": medicine_info
    })


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(R * c, 2)


def get_location_name(lat, lon):
    url = (
        f"https://nominatim.openstreetmap.org/reverse"
        f"?format=json&lat={lat}&lon={lon}"
    )

    headers = {
        "User-Agent": "MemoraAI/1.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})

            return (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("county")
                or "Unknown Location"
            )

    except Exception as e:
        print("LOCATION ERROR:", e)

    return "Unknown Location"


def nearest_hospitals(request):
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    if not lat or not lon:
        return JsonResponse({"error": "Location not provided"}, status=400)

    location_name = get_location_name(lat, lon)

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": f"hospital near {lat},{lon}",
        "format": "json",
        "limit": 10,
        "addressdetails": 1
    }

    headers = {
        "User-Agent": "MemoraAI/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        data = response.json()

        hospitals = []

        for item in data:
            hospital_lat = float(item["lat"])
            hospital_lon = float(item["lon"])

            distance = calculate_distance(
                float(lat),
                float(lon),
                hospital_lat,
                hospital_lon
            )

            hospitals.append({
                "name": item.get("display_name", "Hospital").split(",")[0],
                "distance": distance
            })

        hospitals.sort(key=lambda x: x["distance"])

        return JsonResponse({
            "location": location_name,
            "hospitals": hospitals
        })

    except Exception as e:
        print("HOSPITAL ERROR:", e)

        return JsonResponse({
            "location": location_name,
            "hospitals": [],
            "message": "Unable to fetch hospitals"
        })


def hospitals(request):
    return render(request, "myapp/hospitals.html")