"""Weight-trend forecasting over logged progress entries.

Deliberately simple: ordinary least-squares linear regression over
(day_offset, weight) pairs. With the handful of sparse, noisy points a real
user logs, a simple linear trend is both more honest and more stable than a
deep model would be — this is legitimate time-series forecasting, just not
over-engineered for the amount of data actually available.
"""

from datetime import datetime, timedelta

from app.models.entities import HealthProfile, ProgressLog

_MIN_POINTS_FOR_TREND = 3


def _linear_regression(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Returns (slope, intercept) for y = slope*x + intercept via least squares."""
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = sum((x - mean_x) ** 2 for x in xs) or 1e-9
    slope = numerator / denominator
    intercept = mean_y - slope * mean_x
    return slope, intercept


class ProgressService:
    @staticmethod
    def compute_trend(logs: list[ProgressLog], profile: HealthProfile | None) -> dict | None:
        weight_logs = [log for log in logs if log.weight_kg is not None]
        if len(weight_logs) < _MIN_POINTS_FOR_TREND:
            return None

        weight_logs = sorted(weight_logs, key=lambda log: log.log_date)
        origin = weight_logs[0].log_date
        xs = [(log.log_date - origin).total_seconds() / 86400 for log in weight_logs]  # days since first log
        ys = [log.weight_kg for log in weight_logs]

        slope_per_day, intercept = _linear_regression(xs, ys)
        slope_per_week = slope_per_day * 7

        last_x = xs[-1]
        projected_30d = slope_per_day * (last_x + 30) + intercept

        on_track = None
        message = f"Weight is changing by about {slope_per_week:+.2f} kg/week based on your logs."
        if profile and profile.goal != "maintain" and profile.goal_rate_kg_per_week:
            target_sign = -1 if profile.goal == "lose" else 1
            actual_sign = -1 if slope_per_week < 0 else (1 if slope_per_week > 0 else 0)
            on_track = actual_sign == target_sign and abs(slope_per_week) >= 0.5 * profile.goal_rate_kg_per_week
            direction = "losing" if profile.goal == "lose" else "gaining"
            message = (
                f"You're {direction} about {abs(slope_per_week):.2f} kg/week "
                f"(goal: {profile.goal_rate_kg_per_week:.2f} kg/week). "
                + ("On track." if on_track else "Below your target pace — consider revisiting your plan or adherence.")
            )

        return {
            "slope_kg_per_week": round(slope_per_week, 3),
            "projected_weight_kg": round(projected_30d, 1),
            "projected_date": origin + timedelta(days=last_x + 30),
            "on_track": on_track,
            "message": message,
        }
