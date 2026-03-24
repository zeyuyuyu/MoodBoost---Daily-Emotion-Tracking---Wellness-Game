import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

class MoodAnalyzer:
    def __init__(self):
        self.mood_scores = {
            'very_happy': 5,
            'happy': 4,
            'neutral': 3,
            'sad': 2,
            'very_sad': 1
        }
        self.trend_window = 7  # Default 7-day window for trend analysis

    def calculate_mood_score(self, mood_entry: str) -> float:
        """Convert mood string to numerical score"""
        return self.mood_scores.get(mood_entry.lower(), 3)

    def detect_mood_trend(self, mood_history: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Analyze mood trends over time and detect patterns
        Returns insights about mood trajectory
        """
        if not mood_history or len(mood_history) < 3:
            return {'status': 'insufficient_data'}

        scores = [self.calculate_mood_score(entry['mood']) for entry in mood_history]
        dates = [datetime.fromisoformat(entry['timestamp']) for entry in mood_history]

        # Calculate moving average
        window = min(self.trend_window, len(scores))
        moving_avg = np.convolve(scores, np.ones(window)/window, mode='valid')

        # Detect trend direction
        trend_slope = np.polyfit(range(len(moving_avg)), moving_avg, 1)[0]

        # Calculate volatility
        volatility = np.std(scores)

        # Find mood patterns
        weekday_moods = self._analyze_weekday_patterns(dates, scores)
        
        return {
            'trend_direction': 'improving' if trend_slope > 0.1 else 'declining' if trend_slope < -0.1 else 'stable',
            'volatility': float(volatility),
            'avg_mood': float(np.mean(scores)),
            'weekday_patterns': weekday_moods,
            'streak': self._calculate_positive_streak(scores),
            'last_updated': datetime.now().isoformat()
        }

    def _analyze_weekday_patterns(self, dates: List[datetime], scores: List[float]) -> Dict[str, float]:
        """Analyze average mood by day of week"""
        weekday_scores = {i: [] for i in range(7)}
        for date, score in zip(dates, scores):
            weekday_scores[date.weekday()].append(score)

        return {
            day: float(np.mean(scores)) if scores else 0
            for day, scores in weekday_scores.items()
        }

    def _calculate_positive_streak(self, scores: List[float]) -> int:
        """Calculate current streak of above-neutral moods"""
        streak = 0
        for score in reversed(scores):
            if score > 3:
                streak += 1
            else:
                break
        return streak

    def generate_insights(self, mood_history: List[Dict[str, any]]) -> List[str]:
        """Generate actionable insights based on mood patterns"""
        trends = self.detect_mood_trend(mood_history)
        insights = []

        if trends['status'] == 'insufficient_data':
            return ['Keep tracking your moods to receive personalized insights!']

        if trends['trend_direction'] == 'improving':
            insights.append('Your mood is showing an upward trend - keep up the good work!')
        elif trends['trend_direction'] == 'declining':
            insights.append('Your mood has been declining lately. Consider talking to someone or trying some mood-boosting activities.')

        if trends['volatility'] > 1.5:
            insights.append('Your mood shows high variability. Creating a consistent daily routine might help stabilize it.')

        # Analyze weekday patterns
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        best_day = max(trends['weekday_patterns'].items(), key=lambda x: x[1])
        worst_day = min(trends['weekday_patterns'].items(), key=lambda x: x[1])
        
        if best_day[1] - worst_day[1] > 1:
            insights.append(f'You tend to feel best on {weekday_names[best_day[0]]}s and worst on {weekday_names[worst_day[0]]}s.')

        if trends['streak'] >= 3:
            insights.append(f'You\'re on a {trends["streak"]}-day streak of positive moods!')

        return insights