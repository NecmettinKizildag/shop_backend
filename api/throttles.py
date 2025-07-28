from rest_framework.throttling import UserRateThrottle

class BurstRateThrottle(UserRateThrottle):
    """
    Throttle class that allows a burst of requests followed by a slower rate.
    """
    scope = 'burst'

class SustainedRateThrottle(UserRateThrottle):
    """
    Throttle class that allows a sustained rate of requests.
    """
    scope = 'sustained'