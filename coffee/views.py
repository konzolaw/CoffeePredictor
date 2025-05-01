from django.contrib.auth.models import User # type: ignore
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib import messages # type: ignore
from .forms import FarmInfoForm
from .models import YieldPrediction
from django.http import JsonResponse # type: ignore
from .models import FarmInfo
from django.core.exceptions import ValidationError
from .algorithm import predict_coffee_yield  # type: ignore # Import the provided algorithm
from django.http import HttpResponse
import io
from django.core.mail import send_mail
from decouple import config

def index(request):
    if request.method == 'POST':
        form = FarmInfoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # Create a success template or message
    else:
        form = FarmInfoForm()
    return render(request, 'coffee/index.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username:
            messages.error(request, "Username is required.")
            return redirect('index')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('index')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('index')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created. You can now log in.")
        return redirect('index')
    return redirect('index')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Log successful login
            print("[INFO] Login successful for user:", username)
            messages.success(request, "Login successful. Welcome back!")
            return redirect('predictions')
        else:
            # Log failed login attempt
            print("[WARNING] Login failed for username:", username)
            messages.error(request, "Invalid login credentials. Please try again.")
            return redirect('index')
    else:
        messages.warning(request, "You are not authorized to access this page. Please log in.")
    return redirect('index')

@login_required(login_url='index')
def predictions(request):
    if request.user.is_authenticated:
        context = {
            'user': request.user,  # Pass the logged-in user to the template
            'form': FarmInfoForm(),
        }
        return render(request, 'coffee/predictions.html', context)
    else:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('index')

@login_required(login_url='index')
def predict_yield(request):
    # Log the request method for debugging
    print(f"[DEBUG] Request method: {request.method}")

    if request.method == 'POST':
        try:
            # Extract form data
            input_parameters = {
                'farmer_id': request.POST.get('farmer_id', 'Unknown'),
                'coffee_variety': request.POST.get('coffee_variety', 'Unknown'),
                'fertilizer_amount': float(request.POST.get('fertilizer_amount', 0)),
                'hectares_of_land': float(request.POST.get('hectares_of_land', 0)),
                'previous_yield': float(request.POST.get('previous_yield', 0)),
                'presence_of_buds': request.POST.get('presence_of_buds', 'No') == 'Yes',
                'weather_condition': request.POST.get('weather_condition', 'Unknown'),
            }

            # Log the input parameters for debugging
            print("[DEBUG] Input Parameters:", input_parameters)

            # Save the form data to the FarmInfo model
            farm_info = FarmInfo.objects.create(
                user=request.user,
                farmer_id=input_parameters['farmer_id'],
                coffee_variety=input_parameters['coffee_variety'],
                fertilizer_amount=input_parameters['fertilizer_amount'],
                hectares_of_land=input_parameters['hectares_of_land'],
                previous_yield=input_parameters['previous_yield'],
                presence_of_buds=input_parameters['presence_of_buds'],
                weather_condition=input_parameters['weather_condition']
            )

            # Log the saved FarmInfo instance
            print("[INFO] Saved FarmInfo:", farm_info)

            # Pass the input parameters through the algorithm
            predicted_yield, confidence_level = predict_coffee_yield(
                variety=input_parameters['coffee_variety'],
                fertilizer_kg=input_parameters['fertilizer_amount'],
                hectares=input_parameters['hectares_of_land'],
                prev_yield=input_parameters['previous_yield'],
                has_buds=input_parameters['presence_of_buds'],
                weather=input_parameters['weather_condition'],
                rainfall=None,  # Optional parameters can be added later
                temperature=None,
                soil_ph=None
            )

            # Log the algorithm output
            print("[DEBUG] Algorithm Output - Predicted Yield:", predicted_yield)
            print("[DEBUG] Algorithm Output - Confidence Level:", confidence_level)

            # Save the prediction to the YieldPrediction model
            YieldPrediction.objects.create(
                user=request.user,
                predicted_yield=predicted_yield,
                confidence_level=confidence_level,
                input_parameters=input_parameters
            )

            # Log the prediction save operation
            print("[INFO] Prediction saved to YieldPrediction model.")

            return JsonResponse({'success': True, 'message': 'Prediction process completed successfully.'})

        except Exception as e:
            # Log any errors during the process
            print("[ERROR] Failed to process prediction:", e)
            return JsonResponse({'success': False, 'error': 'Failed to process prediction.'})

    elif request.method == 'GET':
        # Handle GET requests (optional)
        return JsonResponse({'success': False, 'error': 'GET method is not supported for this endpoint.'})

    # Ensure all code paths return a valid response
    return JsonResponse({'success': False, 'error': 'Unhandled case in predict_yield view.'})

def logout_user(request):
    logout(request)
    logout(request)
    return redirect('index')

def success(request):
    return render(request, 'success.html')

def prediction_results(request):
    # Log the request method for debugging
    print(f"[DEBUG] Request method: {request.method}")

    if request.method == 'POST':
        try:
            # Use FarmInfoForm to validate and save form data
            form = FarmInfoForm(request.POST)
            if form.is_valid():
                farm_info = form.save(commit=False)
                farm_info.user = request.user  # Associate with logged-in user
                farm_info.save()

                # Log the saved FarmInfo instance
                print("[INFO] Saved FarmInfo:", farm_info)

                # Extract input parameters for the algorithm
                input_parameters = {
                    'farmer_id': farm_info.farmer_id,
                    'coffee_variety': farm_info.coffee_variety,
                    'fertilizer_amount': farm_info.fertilizer_amount,
                    'hectares_of_land': farm_info.hectares_of_land,
                    'previous_yield': farm_info.previous_yield,
                    'presence_of_buds': farm_info.presence_of_buds == 'Yes',
                    'weather_condition': farm_info.weather_condition,
                }

                # Call the provided algorithm to predict yield
                predicted_yield, confidence_level = predict_coffee_yield(
                    variety=input_parameters['coffee_variety'],
                    fertilizer_kg=input_parameters['fertilizer_amount'],
                    hectares=input_parameters['hectares_of_land'],
                    prev_yield=input_parameters['previous_yield'],
                    has_buds=input_parameters['presence_of_buds'],
                    weather=input_parameters['weather_condition'],
                    rainfall=None,  # Optional parameters can be added later
                    temperature=None,
                    soil_ph=None
                )

                # Log the algorithm output
                print("[DEBUG] Algorithm Output - Predicted Yield:", predicted_yield)
                print("[DEBUG] Algorithm Output - Confidence Level:", confidence_level)

                # Save the prediction to the database
                YieldPrediction.objects.create(
                    user=request.user,
                    predicted_yield=predicted_yield,
                    confidence_level=confidence_level,
                    input_parameters=input_parameters
                )
                print("[INFO] Prediction saved to database.")

                # Return a JSON response with prediction data
                return JsonResponse({
                    'success': True,
                    'predicted_yield': predicted_yield,
                    'confidence_level': confidence_level,
                    'previous_yield': input_parameters['farm_info.previous_yield'],
                })
            else:
                # Log form validation errors
                print("[ERROR] Form validation failed:", form.errors)
                return JsonResponse({
                    'success': False,
                    'error': 'Form validation failed. Please check your inputs.',
                    'form_errors': form.errors
                })

        except Exception as e:
            # Log the error for debugging purposes
            print("[ERROR] Unexpected Error in prediction_results:", e)
            return JsonResponse({
                'success': False,
                'error': 'An unexpected error occurred. Please try again.'
            })

    elif request.method == 'GET':
        try:
            # Log the start of the GET request handling
            print("[DEBUG] Handling GET request for prediction results.")

            # Retrieve only the latest prediction for the current user
            latest_prediction = YieldPrediction.objects.filter(user=request.user).order_by('-id').first()

            if latest_prediction:
                # Extract input parameters from the latest prediction
                input_parameters = latest_prediction.input_parameters

                # Log the input parameters for debugging
                print("[DEBUG] Input Parameters:", input_parameters)

                # Ensure all required keys are present in input_parameters
                required_keys = ['coffee_variety', 'fertilizer_amount', 'hectares_of_land', 'previous_yield', 'presence_of_buds', 'weather_condition']
                for key in required_keys:
                    if key not in input_parameters:
                        print(f"[ERROR] Missing key in input parameters: {key}")
                        return render(request, 'coffee/results.html', {'error': f'Missing key in input parameters: {key}'})

                # Pass the input parameters through the algorithm
                predicted_yield, confidence_level = predict_coffee_yield(
                    variety=input_parameters['coffee_variety'],
                    fertilizer_kg=input_parameters['fertilizer_amount'],
                    hectares=input_parameters['hectares_of_land'],
                    prev_yield=input_parameters['previous_yield'],
                    has_buds=input_parameters['presence_of_buds'],
                    weather=input_parameters['weather_condition'],
                    rainfall=None,  # Optional parameters can be added later
                    temperature=None,
                    soil_ph=None
                )

                # Include 'previous_yield' in the context for the results.html template
                context = {
                    'predicted_yield': predicted_yield,
                    'confidence_level': confidence_level,
                    'previous_yield': input_parameters['previous_yield'],
                    'input_parameters': input_parameters,
                }

                # Log the inclusion of 'previous_yield' in the context
                print("[DEBUG] Included 'previous_yield' in the context:", input_parameters['previous_yield'])

                # Log the successfully prepared result
                print("[DEBUG] Successfully prepared result after running the algorithm.")
                return render(request, 'coffee/results.html', context)
            else:
                # Log if no predictions are found
                print("[DEBUG] No predictions found for the current user.")
                return render(request, 'coffee/results.html', {'error': 'No predictions found.'})
        except Exception as e:
            # Log the error for debugging purposes
            print("[ERROR] Failed to fetch predictions:", e)
            return render(request, 'coffee/results.html', {'error': 'Failed to fetch predictions.'})

    # Log invalid request method
    print("[WARNING] Invalid request method used in prediction_results.")
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })

@login_required(login_url='index')
def save_farm_info(request):
    if request.method == 'POST':
        form = FarmInfoForm(request.POST)
        if form.is_valid():
            farm_info = form.save(commit=False)  # Do not save to DB yet
            farm_info.user = request.user  # Associate with logged-in user
            farm_info.save()  # Save to DB
            messages.success(request, "Farm information saved successfully.")
        else:
            messages.error(request, "Error saving farm information. Please check your inputs.")
    return redirect('predictions')  # Redirect to predictions page instead of rendering the form again

@login_required(login_url='index')
def save_all_inputs(request):
    if request.method == 'POST':
        try:
            # Collect all input parameters from the form
            input_parameters = {
                'farmer_id': request.POST.get('farmer_id', ''),
                'coffee_variety': request.POST.get('coffee_variety', ''),
                'fertilizer_amount': request.POST.get('fertilizer_amount', ''),
                'hectares_of_land': request.POST.get('hectares_of_land', ''),
                'previous_yield': request.POST.get('previous_yield', ''),
                'presence_of_buds': request.POST.get('presence_of_buds', ''),
                'weather_condition': request.POST.get('weather_condition', ''),
            }

            # Save the inputs to the FarmInfo model
            farm_info = FarmInfo.objects.create(
                user=request.user,
                farmer_id=input_parameters['farmer_id'],
                coffee_variety=input_parameters['coffee_variety'],
                fertilizer_amount=input_parameters['fertilizer_amount'],
                hectares_of_land=input_parameters['hectares_of_land'],
                previous_yield=input_parameters['previous_yield'],
                presence_of_buds=input_parameters['presence_of_buds'],
                weather_condition=input_parameters['weather_condition']
            )

            # Log the saved FarmInfo instance
            print("Saved FarmInfo with all inputs:", farm_info)

            return JsonResponse({'success': False, 'message': 'All inputs saved successfully.'})
        except Exception as e:
            print("Error saving inputs:", e)
            return JsonResponse({'success': False, 'error': 'Failed to save inputs.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def submit_farm_info(request):
    if request.method == 'POST':
        form = FarmInfoForm(request.POST)
        if form.is_valid():
            farm_info = form.save(commit=False)
            farm_info.user = request.user
            farm_info.save()
            # Log successful database update
            print("[INFO] Database updated with new FarmInfo entry for user:", request.user.username)
            return JsonResponse({'success': True, 'message': 'Farm information saved successfully.'})
        else:
            # Log form validation errors
            print("[ERROR] Form validation failed:", form.errors)
            return JsonResponse({'success': False, 'errors': form.errors, 'message': 'Form validation failed.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required(login_url='index')
def download_report(request):
    try:
        # Retrieve the latest prediction for the user
        latest_prediction = YieldPrediction.objects.filter(user=request.user).order_by('-id').first()

        if not latest_prediction:
            return HttpResponse("No predictions found.", content_type="text/plain")

        # Prepare the report content
        report_content = f"Prediction Report\n\n"
        report_content += f"Name: {request.user.username}\n"
        report_content += f"Farmer ID: {latest_prediction.input_parameters.get('farmer_id', 'N/A')}\n"
        report_content += f"Coffee Variety: {latest_prediction.input_parameters.get('coffee_variety', 'N/A')}\n"
        report_content += f"Fertilizer Amount: {latest_prediction.input_parameters.get('fertilizer_amount', 'N/A')}\n"
        report_content += f"Hectares of Land: {latest_prediction.input_parameters.get('hectares_of_land', 'N/A')}\n"
        report_content += f"Previous Yield: {latest_prediction.input_parameters.get('previous_yield', 'N/A')}\n"
        report_content += f"Weather Condition: {latest_prediction.input_parameters.get('weather_condition', 'N/A')}\n\n"
        report_content += f"Predicted Yield: {latest_prediction.predicted_yield} Kgs\n"
        report_content += f"Confidence Level: {latest_prediction.confidence_level}%\n"

        # Create a response with the report content
        response = HttpResponse(report_content, content_type="text/plain")
        response['Content-Disposition'] = 'attachment; filename="prediction_report.txt"'
        return response

    except Exception as e:
        print("[ERROR] Failed to generate report:", e)
        return HttpResponse("Failed to generate report.", content_type="text/plain")

@login_required(login_url='index')
def send_feedback(request):
    if request.method == 'POST':
        feedback_message = request.POST.get('feedback', '').strip()
        if feedback_message:
            try:
                send_mail(
                    subject='User Feedback',
                    message=feedback_message,
                    from_email=request.user.email,
                    # recipient_list=[config('EMAIL_HOST_USER')],
                    fail_silently=False,
                )
                messages.success(request, "Feedback sent successfully.")
            except Exception as e:
                print("[ERROR] Failed to send feedback:", e)
                messages.error(request, "Failed to send feedback. Please try again later.")
        else:
            messages.error(request, "Feedback message cannot be empty.")
    return render(request, 'coffee/results.html')

