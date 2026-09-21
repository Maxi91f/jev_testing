"""Deterministic primality reference shared by the scenario and offline analysis."""

def is_prime(number):
    # These Miller–Rabin bases are deterministic below 2**64, not a random test.
    if not 0 <= number < 2**64:
        raise ValueError("Reference checker only supports unsigned 64-bit integers.")
    if number < 2:
        return False
    for divisor in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if number % divisor == 0:
            return number == divisor
    odd_part = number - 1
    powers_of_two = 0
    while odd_part % 2 == 0:
        odd_part //= 2
        powers_of_two += 1
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % number == 0:
            continue
        value = pow(base, odd_part, number)
        if value in (1, number - 1):
            continue
        for _ in range(powers_of_two - 1):
            value = value * value % number
            if value == number - 1:
                break
        else:
            return False
    return True
