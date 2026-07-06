import os

class CircuitBreakerTrip(Exception):
    pass

class CircuitBreaker:
    def __init__(self, max_tokens: int = 100000, max_iterations: int = 20):
        self.max_tokens = max_tokens
        self.max_iterations = max_iterations
        self._runs = {}

    def check_and_accumulate(self, run_id: str, tokens: int, is_iteration: bool = False):
        if run_id not in self._runs:
            self._runs[run_id] = {"tokens": 0, "iterations": 0}
        
        self._runs[run_id]["tokens"] += tokens
        if is_iteration:
            self._runs[run_id]["iterations"] += 1
            
        if self._runs[run_id]["tokens"] > self.max_tokens:
            raise CircuitBreakerTrip(f"Token limit exceeded for run {run_id}")
            
        if self._runs[run_id]["iterations"] > self.max_iterations:
            raise CircuitBreakerTrip(f"Iteration limit exceeded for run {run_id}")

    def reset(self, run_id: str):
        if run_id in self._runs:
            del self._runs[run_id]

# Singleton instance
breaker = CircuitBreaker()
