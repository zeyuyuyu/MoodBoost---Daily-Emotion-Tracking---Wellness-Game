import numpy as np
from scipy.signal import find_peaks

class EmotionAnalyticsEngine:
    def __init__(self, mood_data):
        self.mood_data = mood_data

    def analyze_mood_trends(self):
        """
        Analyzes the user's mood data over time and identifies key trends and patterns.
        """
        mood_values = np.array(self.mood_data)
        peaks, _ = find_peaks(mood_values, height=0)
        valleys, _ = find_peaks(-mood_values, height=0)

        trend_data = {
            'peaks': peaks.tolist(),
            'valleys': valleys.tolist(),
            'avg_mood': np.mean(mood_values),
            'mood_volatility': np.std(mood_values)
        }

        return trend_data

    def provide_wellness_recommendations(self):
        """
        Provides personalized wellness recommendations based on the user's mood trends.
        """
        trend_data = self.analyze_mood_trends()
        recommendations = []

        if len(trend_data['peaks']) > 3:
            recommendations.append('Your mood seems to have frequent peaks and valleys. Consider trying meditation or other relaxation techniques to stabilize your emotions.')
        if trend_data['mood_volatility'] > 2:
            recommendations.append('Your mood appears to have high volatility. This could be a sign of underlying mental health issues. We suggest speaking with a mental health professional.')
        if trend_data['avg_mood'] < 3:
            recommendations.append('Your average mood is on the lower side. Engaging in regular exercise, spending time in nature, and connecting with loved ones may help boost your overall well-being.')

        return recommendations
