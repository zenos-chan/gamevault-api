from rest_framework.throttling import UserRateThrottle


class PerMinuteUserRateThrottle(UserRateThrottle):
    """
    Dynamic per-minute rate throttle based on the user's API subscription tier.
    Defaults to 60 calls/minute for Free Tier users.
    """
    scope = 'user'

    def get_rate(self):
        # We will determine the rate dynamically in allow_request
        return '60/minute'

    def allow_request(self, request, view):
        if request.user and request.user.is_authenticated:
            # Check user's api_profile for customized or tiered rate limit
            rate_limit = 60
            if hasattr(request.user, 'api_profile') and request.user.api_profile.rate_limit_per_minute:
                rate_limit = request.user.api_profile.rate_limit_per_minute
            self.rate = f"{rate_limit}/minute"
            self.num_requests, self.duration = self.parse_rate(self.rate)

        return super().allow_request(request, view)
