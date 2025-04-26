# This file is needed for  passing variable to base.html
from .models import Car, Privacy
from .models import Ads

def ad_processor(request):
    popup_ad = Ads.objects.all()  # Fetch all ads

    return {
        'ad': popup_ad[0] if popup_ad.exists() else None  # Check if there is at least one ad
    }
