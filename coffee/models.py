from django.db import models # type: ignore

class coffee(models.Model):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField('Created', auto_now_add=True)
    update_at = models.DateTimeField('Updated', auto_now=True)
    isCompleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


from django.contrib.auth.models import User # type: ignore

class FarmInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Associate with logged-in user
    farmer_id = models.CharField(max_length=20)
    
    COFFEE_VARIETIES = [
        ('Ruiru 11', 'Ruiru 11'),
        ('Batian', 'Batian'),
        ('SL24', 'SL24'),
        ('SL38', 'SL38'),
    ]

    coffee_variety = models.CharField(max_length=100, choices=COFFEE_VARIETIES)
    fertilizer_amount = models.FloatField(default=0)
    hectares_of_land = models.FloatField()
    previous_yield = models.FloatField()
    presence_of_buds = models.CharField(max_length=10)
    weather_condition = models.CharField(max_length=100)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.farmer_id} - {self.coffee_variety}"

    # Added a method to retrieve all coffee varieties associated with a user
    @staticmethod
    def get_all_varieties_for_user(user):
        return FarmInfo.objects.filter(user=user).values_list('coffee_variety', flat=True).distinct()


from django.contrib.auth.models import User # type: ignore
class YieldPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    predicted_yield = models.FloatField()
    confidence_level = models.FloatField()
    input_parameters = models.JSONField()  # Store all input parameters
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prediction: {self.predicted_yield} kgs ({self.confidence_level}% confidence)"