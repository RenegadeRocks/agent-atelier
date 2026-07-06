import pytest
from app.circuit_breaker import breaker, CircuitBreakerTrip

def test_circuit_breaker_token_limit():
    breaker.reset("test_run_1")
    
    # Below limit
    breaker.check_and_accumulate("test_run_1", 50000, is_iteration=False)
    
    # Exceed limit
    with pytest.raises(CircuitBreakerTrip) as exc:
        breaker.check_and_accumulate("test_run_1", 60000, is_iteration=False)
        
    assert "Token limit exceeded" in str(exc.value)

def test_circuit_breaker_iteration_limit():
    breaker.reset("test_run_2")
    
    # 20 iterations is the default max
    for _ in range(20):
        breaker.check_and_accumulate("test_run_2", 100, is_iteration=True)
        
    # 21st iteration should trip
    with pytest.raises(CircuitBreakerTrip) as exc:
        breaker.check_and_accumulate("test_run_2", 100, is_iteration=True)
        
    assert "Iteration limit exceeded" in str(exc.value)
